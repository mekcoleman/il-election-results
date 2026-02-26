#!/usr/bin/env python3
"""
Illinois Primary Election 2026 - Rock Island County Scraper
Handles Rock Island County GEMS (Global Election Management System) results

Platform: GEMS - Text/PDF Format
System: Custom GEMS output posted as PDF/text documents
Coverage: Rock Island County (~100K voters)

Rock Island uses GEMS software which produces very clean, structured text output.
Results are posted as PDF files on the county website.
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import pdfplumber

class RockIslandCountyScraper:
    """Scraper for Rock Island County GEMS election results
    
    Rock Island posts results as PDF files with clean text formatting.
    GEMS (Global Election Management System) produces highly structured output.
    """
    
    def __init__(self, election_date: str = '2026-03-17'):
        """Initialize scraper
        
        Args:
            election_date: Election date in YYYY-MM-DD format
        """
        self.county_name = 'Rock Island'
        self.election_date = election_date
        
        # Rock Island County URLs
        self.base_url = 'https://www.rockislandcountyil.gov'
        self.results_page = f'{self.base_url}/272/Previous-Election-Results'
        self.document_base = f'{self.base_url}/DocumentCenter/View'
        
        # Expected document name for 2026 Primary
        # Format: "General Primary Election - March 19, 2024 (PDF)"
        # For 2026: "General Primary Election - March 17, 2026 (PDF)"
    
    def detect_party(self, contest_name: str, section_context: List[str] = None) -> str:
        """Detect party from contest name or context
        
        Args:
            contest_name: Name of the contest
            section_context: Recent lines for context
            
        Returns:
            Party string
        """
        contest_lower = contest_name.lower()
        
        # Check contest name
        if 'democratic' in contest_lower or '(dem)' in contest_lower or ' - dem' in contest_lower:
            return 'Democratic'
        elif 'republican' in contest_lower or '(rep)' in contest_lower or ' - rep' in contest_lower:
            return 'Republican'
        elif 'nonpartisan' in contest_lower or 'non-partisan' in contest_lower:
            return 'Non-Partisan'
        
        # Check section context if provided
        if section_context:
            context_text = ' '.join(section_context).lower()
            if 'democratic primary' in context_text or 'democrat primary' in context_text:
                return 'Democratic'
            elif 'republican primary' in context_text:
                return 'Republican'
        
        # Default for local races
        return 'Non-Partisan'
    
    def scrape_from_pdf_url(self, pdf_url: str) -> Dict:
        """Scrape results from Rock Island GEMS PDF
        
        Args:
            pdf_url: Direct URL to PDF results file
            
        Returns:
            Dictionary with scraped results
        """
        print(f"Scraping Rock Island County...")
        print(f"PDF URL: {pdf_url}")
        
        try:
            # Download PDF
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            # Save temporarily and extract text
            temp_pdf = '/tmp/rock_island_results.pdf'
            with open(temp_pdf, 'wb') as f:
                f.write(response.content)
            
            # Extract text from PDF
            text = self._extract_pdf_text(temp_pdf)
            
            # Parse the text
            results = self._parse_gems_text(text)
            
            results['county'] = self.county_name
            results['election_date'] = self.election_date
            results['scraped_at'] = datetime.now().isoformat()
            results['source'] = 'Rock Island County GEMS PDF'
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
        """Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text())
        
        return '\n'.join(text_parts)
    
    def _parse_gems_text(self, text: str) -> Dict:
        """Parse GEMS formatted text results
        
        GEMS format structure:
        SUMMARY REPORT        ROCK ISLAND COUNTY, ILLINOIS     OFFICIAL RESULTS
        RUN DATE:MM/DD/YY     GENERAL PRIMARY ELECTION
        RUN TIME:HH:MM PM     MARCH 17, 2026
        
        CONTEST NAME
        (VOTE FOR) N
         Candidate Name (PARTY) . . . . . .     votes  percent
         Another Candidate . . . . . . . .     votes  percent
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Results dictionary
        """
        results = {
            'contests': [],
            'summary': {},
            'metadata': {}
        }
        
        lines = text.split('\n')
        
        # Extract header info
        for i, line in enumerate(lines[:20]):
            if 'PRECINCTS COUNTED' in line:
                # Extract precincts
                match = re.search(r'(\d+)\s+100\.00', line)
                if match:
                    results['metadata']['precincts_counted'] = int(match.group(1))
            elif 'REGISTERED VOTERS - TOTAL' in line:
                # Extract registered voters
                match = re.search(r'([\d,]+)', line)
                if match:
                    results['metadata']['registered_voters'] = int(match.group(1).replace(',', ''))
            elif 'BALLOTS CAST - TOTAL' in line:
                # Extract ballots cast
                match = re.search(r'([\d,]+)', line)
                if match:
                    results['metadata']['ballots_cast'] = int(match.group(1).replace(',', ''))
            elif 'VOTER TURNOUT - TOTAL' in line:
                # Extract turnout
                match = re.search(r'([\d.]+)$', line)
                if match:
                    results['metadata']['turnout_percent'] = float(match.group(1))
        
        # Parse contests
        current_contest = None
        current_party = None
        section_context = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                # Empty line - save current contest if exists
                if current_contest and current_contest.get('candidates'):
                    results['contests'].append(current_contest)
                    current_contest = None
                section_context = []
                continue
            
            # Track recent lines for context
            section_context.append(line)
            if len(section_context) > 5:
                section_context.pop(0)
            
            # Detect party section headers
            if 'DEMOCRATIC PRIMARY' in line.upper() or 'DEMOCRAT PRIMARY' in line.upper():
                current_party = 'Democratic'
                continue
            elif 'REPUBLICAN PRIMARY' in line.upper():
                current_party = 'Republican'
                continue
            elif 'NONPARTISAN' in line.upper() or 'NON-PARTISAN' in line.upper():
                current_party = 'Non-Partisan'
                continue
            
            # Check for contest header - typically all caps, no numbers at start
            # Format: "CONTEST NAME" or "OFFICE NAME"
            # Followed by: "(VOTE FOR) N"
            if i + 1 < len(lines) and '(VOTE FOR)' in lines[i + 1]:
                # This is a contest header
                if current_contest and current_contest.get('candidates'):
                    results['contests'].append(current_contest)
                
                contest_name = line.strip()
                vote_for_line = lines[i + 1].strip()
                
                # Extract vote-for number
                vote_for = 1
                vote_for_match = re.search(r'\(VOTE FOR\)\s+(\d+)', vote_for_line)
                if vote_for_match:
                    vote_for = int(vote_for_match.group(1))
                
                current_contest = {
                    'name': contest_name,
                    'party': self.detect_party(contest_name, section_context) or current_party or 'Non-Partisan',
                    'vote_for': vote_for,
                    'candidates': []
                }
                continue
            
            # Check for candidate line
            # Format: " Candidate Name (PARTY) . . . . .   votes  percent"
            # or: " Candidate Name . . . . . . . . .   votes  percent"
            if current_contest and line.startswith(' ') and not line.startswith('  ('):
                # Parse candidate line
                # Split on dots or multiple spaces
                parts = re.split(r'\.{2,}|\s{2,}', line.strip())
                
                if len(parts) >= 2:
                    candidate_name = parts[0].strip()
                    
                    # Extract party from candidate name if present
                    party_match = re.search(r'\(([A-Z]{3})\)\s*$', candidate_name)
                    candidate_party = None
                    if party_match:
                        party_abbrev = party_match.group(1)
                        candidate_name = candidate_name[:party_match.start()].strip()
                        
                        # Map party abbreviations
                        party_map = {
                            'DEM': 'Democratic',
                            'REP': 'Republican',
                            'IND': 'Independent',
                            'INC': 'Independent',
                            'CON': 'Conservative',
                            'CIT': 'Citizens',
                            'PEO': 'People',
                            'PRO': 'Progressive',
                            'INP': 'Independent'
                        }
                        candidate_party = party_map.get(party_abbrev, party_abbrev)
                    
                    # Find votes and percent in remaining parts
                    votes = None
                    percent = None
                    
                    for part in parts[1:]:
                        part = part.strip()
                        if not part:
                            continue
                        
                        # Try to parse as votes (integer with possible commas)
                        if votes is None:
                            try:
                                votes = int(part.replace(',', ''))
                                continue
                            except ValueError:
                                pass
                        
                        # Try to parse as percent (decimal)
                        if percent is None:
                            try:
                                percent = float(part)
                                continue
                            except ValueError:
                                pass
                    
                    if candidate_name and votes is not None:
                        current_contest['candidates'].append({
                            'name': candidate_name,
                            'votes': votes,
                            'percent': percent if percent is not None else 0,
                            'party': candidate_party
                        })
        
        # Add last contest
        if current_contest and current_contest.get('candidates'):
            results['contests'].append(current_contest)
        
        # Calculate percentages if missing
        for contest in results['contests']:
            total_votes = sum(c['votes'] for c in contest['candidates'])
            if total_votes > 0:
                for candidate in contest['candidates']:
                    if candidate['percent'] == 0:
                        candidate['percent'] = round(candidate['votes'] / total_votes * 100, 2)
        
        return results
    
    def scrape_election(self, pdf_url: str = None) -> Dict:
        """Scrape election results
        
        Args:
            pdf_url: Direct URL to PDF results file
                    If None, returns instructions
            
        Returns:
            Dictionary with scraped results
        """
        if pdf_url:
            return self.scrape_from_pdf_url(pdf_url)
        
        # No URL provided - return instructions
        return {
            'error': 'PDF URL required',
            'county': self.county_name,
            'message': 'Visit https://www.rockislandcountyil.gov/272/Previous-Election-Results and find the 2026 Primary PDF link',
            'instructions': [
                '1. Visit: https://www.rockislandcountyil.gov/272/Previous-Election-Results',
                '2. Find "General Primary Election - March 17, 2026 (PDF)"',
                '3. Right-click link → Copy link address',
                '4. Run: python rock_island_county_scraper.py --url [URL]',
                '',
                'Example URL format:',
                'https://www.rockislandcountyil.gov/DocumentCenter/View/XXXXX/General-Primary-Election---March-17-2026-PDF'
            ],
            'scraped_at': datetime.now().isoformat()
        }
    
    def save_results(self, results: Dict, output_dir: str = '.'):
        """Save results to JSON file
        
        Args:
            results: Results dictionary
            output_dir: Directory to save file
        """
        filename = f"{output_dir}/rock_island_county_results.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Saved results to {filename}")

def print_instructions():
    """Print detailed usage instructions"""
    print("=" * 70)
    print("Rock Island County Scraper - GEMS System")
    print("Illinois Primary Election - March 17, 2026")
    print("=" * 70)
    print()
    print("Rock Island County uses GEMS (Global Election Management System)")
    print("Results are posted as clean, structured PDF files")
    print()
    print("SETUP INSTRUCTIONS:")
    print()
    print("1. Visit: https://www.rockislandcountyil.gov/272/Previous-Election-Results")
    print()
    print("2. Find 'General Primary Election - March 17, 2026 (PDF)'")
    print()
    print("3. Right-click the link → Copy link address")
    print()
    print("4. Run the scraper:")
    print("   python rock_island_county_scraper.py --url [COPIED_URL]")
    print()
    print("Example URL:")
    print("https://www.rockislandcountyil.gov/DocumentCenter/View/XXXXX/...")
    print()
    print("=" * 70)
    print("GEMS FORMAT DETAILS")
    print("=" * 70)
    print()
    print("Rock Island's GEMS system produces highly structured output:")
    print()
    print("- Clean text format with dots between candidate and votes")
    print("- Party affiliations in parentheses (DEM), (REP), etc.")
    print("- Vote counts and percentages clearly aligned")
    print("- Summary statistics at top (precincts, turnout, etc.)")
    print()
    print("This is one of the easiest Illinois county formats to parse!")
    print()
    print("=" * 70)
    print("TESTING WITH 2024 DATA")
    print("=" * 70)
    print()
    print("You can test the scraper with 2024 Primary results:")
    print()
    print("1. Visit the Previous Election Results page")
    print("2. Find 'General Primary Election - March 19, 2024 (PDF)'")
    print("3. Copy that URL and test:")
    print("   python rock_island_county_scraper.py --url [2024_URL] --date 2024-03-19")
    print()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rock Island County GEMS Election Results Scraper')
    parser.add_argument('--url', '--pdf-url', dest='pdf_url',
                       help='Direct URL to Rock Island County PDF results')
    parser.add_argument('--date', default='2026-03-17',
                       help='Election date in YYYY-MM-DD format')
    parser.add_argument('--output', default='.',
                       help='Output directory for JSON results')
    
    args = parser.parse_args()
    
    scraper = RockIslandCountyScraper(args.date)
    
    if args.pdf_url:
        results = scraper.scrape_from_pdf_url(args.pdf_url)
    else:
        print_instructions()
        results = scraper.scrape_election()
    
    scraper.save_results(results, args.output)
    
    # Print summary
    if 'error' not in results:
        print()
        print("Summary:")
        print(f"  County: {results.get('county')}")
        print(f"  Election: {results.get('election_date')}")
        print(f"  Contests: {len(results.get('contests', []))}")
        
        if 'metadata' in results:
            meta = results['metadata']
            if 'precincts_counted' in meta:
                print(f"  Precincts: {meta['precincts_counted']}")
            if 'registered_voters' in meta:
                print(f"  Registered Voters: {meta['registered_voters']:,}")
            if 'ballots_cast' in meta:
                print(f"  Ballots Cast: {meta['ballots_cast']:,}")
            if 'turnout_percent' in meta:
                print(f"  Turnout: {meta['turnout_percent']}%")
    else:
        print()
        print(f"Error: {results['error']}")
        if 'instructions' in results:
            print("\nInstructions:")
            for instruction in results['instructions']:
                print(f"  {instruction}")

if __name__ == '__main__':
    main()
