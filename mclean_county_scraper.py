#!/usr/bin/env python3
"""
Illinois Primary Election 2026 - McLean County Scraper
Handles McLean County dual-authority results

Platform: DUAL AUTHORITY SYSTEM
- McLean County Clerk: Custom text/PDF files (county except Bloomington)
- Bloomington Election Commission: Clarity Elections (City of Bloomington only)

Coverage: McLean County (~120K voters total)
- County Clerk jurisdiction: ~65K voters (Normal + unincorporated areas)
- Bloomington jurisdiction: ~55K voters (City of Bloomington)

NOTE: This scraper handles the County Clerk portion only.
For Bloomington, use the existing clarity_scraper.py with Bloomington's election ID.
To get complete McLean County results, you need BOTH scrapers.
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

class McLeanCountyScraper:
    """Scraper for McLean County Clerk election results
    
    Handles McLean County EXCEPT City of Bloomington.
    For complete county coverage, also run clarity_scraper.py for Bloomington.
    """
    
    def __init__(self, election_date: str = '2026-03-17'):
        """Initialize scraper
        
        Args:
            election_date: Election date in YYYY-MM-DD format
        """
        self.county_name = 'McLean'
        self.authority = 'McLean County Clerk'
        self.jurisdiction = 'McLean County (except Bloomington)'
        self.election_date = election_date
        
        # McLean County Clerk URLs
        self.base_url = 'https://www.mcleancountyil.gov'
        self.results_page = f'{self.base_url}/231/Past-McLean-County-Election-Results'
        self.document_base = f'{self.base_url}/DocumentCenter/View'
        
        # Document name patterns for 2026 Primary
        # Format: "2024 Primary summary results"
        year = election_date[:4]
        self.summary_patterns = [
            f'{year} Primary summary results',
            f'{year} Primary summary results with group details',
            f'{year}_Primary_Summary_Results'
        ]
    
    def detect_party(self, contest_name: str, section_name: str = '') -> str:
        """Detect party from contest or section name
        
        Args:
            contest_name: Name of the contest
            section_name: Section/category name if available
            
        Returns:
            Party string
        """
        # Check section name first (McLean often groups by party)
        section_lower = section_lower.lower()
        if 'democratic' in section_lower or 'dem ' in section_lower:
            return 'Democratic'
        elif 'republican' in section_lower or 'rep ' in section_lower:
            return 'Republican'
        
        # Check contest name
        contest_lower = contest_name.lower()
        if 'democratic' in contest_lower or '(dem)' in contest_lower or ' - dem' in contest_lower:
            return 'Democratic'
        elif 'republican' in contest_lower or '(rep)' in contest_lower or ' - rep' in contest_lower:
            return 'Republican'
        elif 'nonpartisan' in contest_lower or 'non-partisan' in contest_lower:
            return 'Non-Partisan'
        
        # Default
        return 'Non-Partisan'
    
    def scrape_from_document_url(self, doc_url: str) -> Dict:
        """Scrape results from McLean County document
        
        McLean posts text-formatted documents (TXT or HTML-rendered text).
        
        Args:
            doc_url: Direct URL to summary results document
            
        Returns:
            Dictionary with scraped results
        """
        print(f"Scraping {self.authority}...")
        print(f"Document URL: {doc_url}")
        print(f"⚠️  Note: This covers McLean County EXCEPT Bloomington")
        print(f"    For complete county results, also scrape Bloomington (Clarity)")
        
        try:
            response = requests.get(doc_url, timeout=60)
            response.raise_for_status()
            
            # Parse the document (could be HTML or plain text)
            if 'text/html' in response.headers.get('content-type', ''):
                results = self._parse_html_document(response.text)
            else:
                results = self._parse_text_document(response.text)
            
            results['authority'] = self.authority
            results['jurisdiction'] = self.jurisdiction
            results['election_date'] = self.election_date
            results['scraped_at'] = datetime.now().isoformat()
            results['source'] = 'McLean County Clerk Document'
            results['document_url'] = doc_url
            results['note'] = 'This covers McLean County EXCEPT City of Bloomington. Bloomington has separate results via Clarity Elections.'
            
            print(f"✓ Successfully scraped {len(results.get('contests', []))} contests")
            return results
            
        except requests.RequestException as e:
            print(f"✗ Error fetching document: {e}")
            return {
                'error': str(e),
                'authority': self.authority,
                'scraped_at': datetime.now().isoformat()
            }
    
    def scrape_election(self, summary_url: str = None) -> Dict:
        """Scrape election results
        
        Args:
            summary_url: Direct URL to summary results document
                        If None, returns instructions
            
        Returns:
            Dictionary with scraped results
        """
        if summary_url:
            return self.scrape_from_document_url(summary_url)
        
        # No URL provided - return instructions
        return {
            'error': 'Summary results URL required',
            'authority': self.authority,
            'message': 'Visit https://www.mcleancountyil.gov/231/Past-McLean-County-Election-Results and find the summary results link for 2026 Primary',
            'instructions': [
                '1. Visit the Past McLean County Election Results page',
                '2. Find "2026 Primary summary results" or similar',
                '3. Right-click and copy link address',
                '4. Run: python mclean_county_scraper.py --url [URL]',
                '',
                '⚠️  IMPORTANT: This scraper handles McLean County Clerk jurisdiction only!',
                'For complete McLean County results, you also need Bloomington results:',
                '5. Find Bloomington election ID at results.enr.clarityelections.com/IL/Bloomington/',
                '6. Run: python clarity_scraper.py --county Bloomington --election-id [ID]'
            ],
            'scraped_at': datetime.now().isoformat()
        }
    
    def _parse_html_document(self, html: str) -> Dict:
        """Parse HTML-formatted document
        
        Args:
            html: HTML content
            
        Returns:
            Results dictionary
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract text content
        text = soup.get_text()
        
        # Parse as text document
        return self._parse_text_document(text)
    
    def _parse_text_document(self, text: str) -> Dict:
        """Parse text-formatted results document
        
        McLean's text format typically looks like:
        
        CONTEST NAME
        Candidate Name ................ Votes Percent
        Another Candidate .............. Votes Percent
        
        Args:
            text: Plain text content
            
        Returns:
            Results dictionary
        """
        results = {
            'contests': [],
            'summary': {}
        }
        
        lines = text.split('\n')
        current_contest = None
        current_party = 'Unknown'
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Empty line might mark end of contest
                if current_contest and current_contest.get('candidates'):
                    results['contests'].append(current_contest)
                    current_contest = None
                continue
            
            # Check for party section headers
            if 'DEMOCRATIC' in line.upper() or 'DEM PRIMARY' in line.upper():
                current_party = 'Democratic'
                continue
            elif 'REPUBLICAN' in line.upper() or 'REP PRIMARY' in line.upper():
                current_party = 'Republican'
                continue
            elif 'NONPARTISAN' in line.upper() or 'NON-PARTISAN' in line.upper():
                current_party = 'Non-Partisan'
                continue
            
            # Check if this is a contest header
            # Contest headers are typically all caps or title case, no numbers
            if line.isupper() and len(line) > 10 and not any(char.isdigit() for char in line[:20]):
                # Save previous contest
                if current_contest and current_contest.get('candidates'):
                    results['contests'].append(current_contest)
                
                # Start new contest
                current_contest = {
                    'name': line,
                    'party': self.detect_party(line) or current_party,
                    'candidates': []
                }
                continue
            
            # Check if this is a candidate line
            # Format: "Candidate Name .......... votes percent%"
            # or: "Candidate Name    votes    percent%"
            if current_contest:
                # Try to extract candidate, votes, percent
                # Split on multiple spaces or dots
                parts = re.split(r'\.{2,}|\s{2,}', line)
                parts = [p.strip() for p in parts if p.strip()]
                
                if len(parts) >= 2:
                    candidate_name = parts[0]
                    
                    # Try to find votes and percent in remaining parts
                    votes = None
                    percent = None
                    
                    for part in parts[1:]:
                        # Remove commas and try to parse as int (votes)
                        if votes is None:
                            try:
                                votes = int(part.replace(',', '').replace('%', ''))
                                continue
                            except ValueError:
                                pass
                        
                        # Try to parse as percent
                        if percent is None and '%' in part:
                            try:
                                percent = float(part.replace('%', '').strip())
                                continue
                            except ValueError:
                                pass
                    
                    if candidate_name and votes is not None:
                        current_contest['candidates'].append({
                            'name': candidate_name,
                            'votes': votes,
                            'percent': percent if percent is not None else 0
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
    
    def save_results(self, results: Dict, output_dir: str = '.'):
        """Save results to JSON file
        
        Args:
            results: Results dictionary
            output_dir: Directory to save file
        """
        filename = f"{output_dir}/mclean_county_clerk_results.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Saved results to {filename}")
        print()
        print("⚠️  REMINDER: This is McLean County Clerk jurisdiction only!")
        print("    For complete McLean County results, also scrape Bloomington:")
        print("    python clarity_scraper.py --county Bloomington --election-id [ID]")

def print_instructions():
    """Print detailed usage instructions"""
    print("=" * 70)
    print("McLean County Scraper - DUAL AUTHORITY SYSTEM")
    print("Illinois Primary Election - March 17, 2026")
    print("=" * 70)
    print()
    print("⚠️  CRITICAL: McLean County has TWO election authorities!")
    print()
    print("1. McLean County Clerk")
    print("   - Jurisdiction: County EXCEPT City of Bloomington")
    print("   - Voters: ~65,000")
    print("   - Platform: Text/PDF documents")
    print("   - This scraper handles this authority")
    print()
    print("2. Bloomington Election Commission")
    print("   - Jurisdiction: City of Bloomington ONLY")
    print("   - Voters: ~55,000")
    print("   - Platform: Clarity Elections")
    print("   - Use clarity_scraper.py for this authority")
    print()
    print("FOR COMPLETE MCLEAN COUNTY RESULTS, YOU NEED BOTH!")
    print()
    print("=" * 70)
    print("PART 1: McLean County Clerk (this scraper)")
    print("=" * 70)
    print()
    print("1. Visit: https://www.mcleancountyil.gov/231/Past-McLean-County-Election-Results")
    print("2. Find '2026 Primary summary results'")
    print("3. Right-click link → Copy link address")
    print("4. Run:")
    print("   python mclean_county_scraper.py --url [COPIED_URL]")
    print()
    print("=" * 70)
    print("PART 2: Bloomington (use Clarity scraper)")
    print("=" * 70)
    print()
    print("1. Visit: https://results.enr.clarityelections.com/IL/Bloomington/")
    print("2. Find 2026 Primary election (note the election ID from URL)")
    print("3. Run:")
    print("   python clarity_scraper.py --county Bloomington --election-id [ID]")
    print()
    print("=" * 70)
    print("COMBINING RESULTS")
    print("=" * 70)
    print()
    print("To get complete McLean County totals:")
    print("- Add vote totals from both scrapers")
    print("- Note: Some races may only appear in one jurisdiction")
    print("- Countywide races (President, U.S. Rep, etc.) need both combined")
    print()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='McLean County Clerk Election Results Scraper')
    parser.add_argument('--url', '--summary-url', dest='summary_url',
                       help='Direct URL to McLean County summary results document')
    parser.add_argument('--date', default='2026-03-17',
                       help='Election date in YYYY-MM-DD format')
    parser.add_argument('--output', default='.',
                       help='Output directory for JSON results')
    
    args = parser.parse_args()
    
    scraper = McLeanCountyScraper(args.date)
    
    if args.summary_url:
        results = scraper.scrape_from_document_url(args.summary_url)
    else:
        print_instructions()
        results = scraper.scrape_election()
    
    scraper.save_results(results, args.output)
    
    # Print summary
    if 'error' not in results:
        print()
        print("Summary:")
        print(f"  Authority: {results.get('authority')}")
        print(f"  Jurisdiction: {results.get('jurisdiction')}")
        print(f"  Election: {results.get('election_date')}")
        print(f"  Contests: {len(results.get('contests', []))}")
        print()
        print(f"  ⚠️  {results.get('note', '')}")
    else:
        print()
        print(f"Error: {results['error']}")
        if 'instructions' in results:
            print("\nInstructions:")
            for instruction in results['instructions']:
                print(f"  {instruction}")

if __name__ == '__main__':
    main()
