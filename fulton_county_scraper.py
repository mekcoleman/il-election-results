#!/usr/bin/env python3
"""
Illinois Primary Election 2026 - Fulton County Scraper
Handles Fulton County Cumulative Results Report PDF results

Platform: Custom PDF - Cumulative Results Report
System: Structured PDF with tabular format
Coverage: Fulton County (~25K voters)

Fulton posts clean "Cumulative Results Report" PDFs with structured formatting.
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import pdfplumber

class FultonCountyScraper:
    """Scraper for Fulton County Cumulative Results Report PDFs"""
    
    def __init__(self, election_date: str = '2026-03-17'):
        self.county_name = 'Fulton'
        self.election_date = election_date
        self.base_url = 'https://fultoncountyilelections.gov'
        self.results_page = f'{self.base_url}/election-results/'
    
    def detect_party(self, contest_name: str, candidate_text: str = '') -> Optional[str]:
        """Detect party from contest or candidate text"""
        # Check contest name for party suffix
        if ' - REPUBLICAN PARTY' in contest_name or ' - REPUBLICAN' in contest_name:
            return 'Republican'
        elif ' - DEMOCRATIC PARTY' in contest_name or ' - DEMOCRATIC' in contest_name:
            return 'Democratic'
        elif 'NONPARTISAN' in contest_name.upper():
            return 'Non-Partisan'
        
        # Check candidate text
        if '(REP)' in candidate_text or 'REPUBLICAN' in candidate_text.upper():
            return 'Republican'
        elif '(DEM)' in candidate_text or 'DEMOCRATIC' in candidate_text.upper():
            return 'Democratic'
        
        return None
    
    def scrape_from_pdf_url(self, pdf_url: str) -> Dict:
        """Scrape results from Fulton County PDF"""
        print(f"Scraping Fulton County...")
        print(f"PDF URL: {pdf_url}")
        
        try:
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            temp_pdf = '/tmp/fulton_results.pdf'
            with open(temp_pdf, 'wb') as f:
                f.write(response.content)
            
            text = self._extract_pdf_text(temp_pdf)
            results = self._parse_cumulative_report(text)
            
            results['county'] = self.county_name
            results['election_date'] = self.election_date
            results['scraped_at'] = datetime.now().isoformat()
            results['source'] = 'Fulton County Cumulative Results Report PDF'
            results['pdf_url'] = pdf_url
            
            print(f"✓ Successfully scraped {len(results.get('contests', []))} contests")
            return results
            
        except requests.RequestException as e:
            print(f"✗ Error fetching PDF: {e}")
            return {
                'error': str(e),
                'county': self.county_name,
                'scraped_at': datetime.now().isoformat()
            }
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text())
        return '\n'.join(text_parts)
    
    def _parse_cumulative_report(self, text: str) -> Dict:
        """Parse Fulton Cumulative Results Report format
        
        Format:
        Cumulative Results Report
        ELECTION DAY
        Run Date: MM/DD/YYYY
        Fulton County, IL
        Fulton 2024 General Primary Election
        
        Registered Voters 3336 of 24200 = 13.79%
        Precincts Reporting 44 of 44 = 100.00%
        
        FOR CONTEST NAME - PARTY - (Vote for one)
        Precincts Counted Total Percent
        44 44 100.00%
        Voters Ballots Registered Percent
        1,989 24,200 8.22%
        
        Choice Party Election Day Early-Grace Vote By Mail Total
        CANDIDATE NAME 1,487 87.11% 91 87.50% 106 67.09% 1,684 85.53%
        ANOTHER CANDIDATE 147 8.61% 11 10.58% 39 24.68% 197 10.01%
        """
        results = {'contests': [], 'summary': {}, 'metadata': {}}
        
        lines = text.split('\n')
        
        # Extract metadata
        for i, line in enumerate(lines[:50]):
            if 'Registered Voters' in line and 'of' in line:
                match = re.search(r'(\d+) of (\d+)', line)
                if match:
                    results['metadata']['ballots_cast'] = int(match.group(1))
                    results['metadata']['registered_voters'] = int(match.group(2))
            
            if 'Precincts Reporting' in line and 'of' in line:
                match = re.search(r'(\d+) of (\d+)', line)
                if match:
                    results['metadata']['precincts_reporting'] = int(match.group(1))
                    results['metadata']['total_precincts'] = int(match.group(2))
        
        # Parse contests
        current_contest = None
        in_candidate_section = False
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for contest header
            if line.startswith('FOR ') and (' - ' in line or '(' in line):
                # Save previous contest
                if current_contest and current_contest.get('candidates'):
                    results['contests'].append(current_contest)
                
                # Extract contest name and party
                contest_name = line.replace('FOR ', '').strip()
                
                # Clean up vote-for notation
                vote_for_match = re.search(r'\(Vote for (.*?)\)', contest_name)
                vote_for = 1
                if vote_for_match:
                    vote_for_text = vote_for_match.group(1).lower()
                    if 'not more than' in vote_for_text:
                        vote_for = int(re.search(r'(\d+)', vote_for_text).group(1))
                    elif vote_for_text != 'one':
                        try:
                            vote_for = int(vote_for_text)
                        except:
                            vote_for = 1
                    contest_name = contest_name[:vote_for_match.start()].strip()
                
                party = self.detect_party(contest_name)
                
                current_contest = {
                    'name': contest_name,
                    'party': party or 'Non-Partisan',
                    'vote_for': vote_for,
                    'candidates': []
                }
                in_candidate_section = False
                i += 1
                continue
            
            # Check for candidate section start
            if current_contest and 'Choice' in line and 'Party' in line:
                in_candidate_section = True
                i += 1
                continue
            
            # Parse candidate lines
            if current_contest and in_candidate_section and line:
                # Skip metadata lines
                if ('Precincts' in line or 'Counted' in line or 'Voters' in line or 
                    'Ballots' in line or 'Cast Votes' in line or 'Undervotes' in line or 
                    'Overvotes' in line):
                    # Check for end of contest
                    if 'Cast Votes' in line:
                        in_candidate_section = False
                    i += 1
                    continue
                
                # Try to parse candidate line
                # Format: CANDIDATE NAME votes% votes% votes% total_votes total%
                parts = line.split()
                
                if len(parts) >= 2:
                    # Find the last percentage (total %)
                    total_percent = None
                    total_votes = None
                    
                    for j in range(len(parts) - 1, -1, -1):
                        part = parts[j]
                        # Check for percentage
                        if '%' in part and total_percent is None:
                            try:
                                total_percent = float(part.replace('%', ''))
                            except:
                                pass
                        # Check for votes (before percentage)
                        elif total_percent is not None and total_votes is None:
                            try:
                                total_votes = int(part.replace(',', ''))
                                break
                            except:
                                pass
                    
                    if total_votes is not None:
                        # Everything before votes is candidate name
                        name_parts = []
                        for j in range(len(parts)):
                            if parts[j] == str(total_votes) or (parts[j].replace(',', '') == str(total_votes)):
                                break
                            name_parts.append(parts[j])
                        
                        candidate_name = ' '.join(name_parts)
                        
                        if candidate_name and not candidate_name.startswith('No Candidate'):
                            current_contest['candidates'].append({
                                'name': candidate_name,
                                'votes': total_votes,
                                'percent': total_percent if total_percent else 0
                            })
            
            i += 1
        
        # Add last contest
        if current_contest and current_contest.get('candidates'):
            results['contests'].append(current_contest)
        
        # Calculate missing percentages
        for contest in results['contests']:
            total_votes = sum(c['votes'] for c in contest['candidates'])
            if total_votes > 0:
                for candidate in contest['candidates']:
                    if candidate['percent'] == 0:
                        candidate['percent'] = round(candidate['votes'] / total_votes * 100, 2)
        
        return results
    
    def scrape_election(self, pdf_url: str = None) -> Dict:
        """Scrape election results"""
        if pdf_url:
            return self.scrape_from_pdf_url(pdf_url)
        
        return {
            'error': 'PDF URL required',
            'county': self.county_name,
            'message': 'Visit https://fultoncountyilelections.gov/election-results/ and find the 2026 Primary PDF link',
            'instructions': [
                '1. Visit: https://fultoncountyilelections.gov/election-results/',
                '2. Find "2026 Primary Election OFFICIAL Results" PDF',
                '3. Right-click and copy link address',
                '4. Run: python fulton_county_scraper.py --url [URL]'
            ],
            'scraped_at': datetime.now().isoformat()
        }
    
    def save_results(self, results: Dict, output_dir: str = '.'):
        """Save results to JSON file"""
        filename = f"{output_dir}/fulton_county_results.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Saved results to {filename}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fulton County Election Results Scraper')
    parser.add_argument('--url', '--pdf-url', dest='pdf_url',
                       help='Direct URL to Fulton County PDF results')
    parser.add_argument('--date', default='2026-03-17',
                       help='Election date in YYYY-MM-DD format')
    parser.add_argument('--output', default='.',
                       help='Output directory for JSON results')
    
    args = parser.parse_args()
    
    scraper = FultonCountyScraper(args.date)
    
    if args.pdf_url:
        results = scraper.scrape_from_pdf_url(args.pdf_url)
    else:
        print("=" * 70)
        print("Fulton County Scraper - Cumulative Results Report")
        print("Illinois Primary Election - March 17, 2026")
        print("=" * 70)
        print()
        print("Visit: https://fultoncountyilelections.gov/election-results/")
        print("Find: 2026 Primary Election OFFICIAL Results PDF")
        print("Copy the PDF URL and run:")
        print("  python fulton_county_scraper.py --url [URL]")
        print()
        results = scraper.scrape_election()
    
    scraper.save_results(results, args.output)
    
    if 'error' not in results:
        print()
        print("Summary:")
        print(f"  County: {results.get('county')}")
        print(f"  Election: {results.get('election_date')}")
        print(f"  Contests: {len(results.get('contests', []))}")
        
        if 'metadata' in results:
            meta = results['metadata']
            if 'registered_voters' in meta:
                print(f"  Registered Voters: {meta['registered_voters']:,}")
            if 'ballots_cast' in meta:
                print(f"  Ballots Cast: {meta['ballots_cast']:,}")

if __name__ == '__main__':
    main()
