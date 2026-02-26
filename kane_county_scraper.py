#!/usr/bin/env python3
"""
Illinois Primary Election 2026 - Kane County Scraper
Handles Kane County (3rd largest Illinois county)

Platform: Custom Kane County platform
Base URL: https://electionresults.kanecountyil.gov
Coverage: Kane County (~550,000 residents, 350,000+ voters)

Kane County uses a simple, clean date-based URL structure with HTML tables
for contest results. Very reliable and easy to parse.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

class KaneCountyScraper:
    """Scraper for Kane County election results"""
    
    def __init__(self, election_date: str = '2026-03-17'):
        """Initialize scraper
        
        Args:
            election_date: Election date in YYYY-MM-DD format (default: 2026-03-17)
        """
        self.county_name = 'Kane County'
        self.base_url = 'https://electionresults.kanecountyil.gov'
        self.election_date = election_date
        
        # Build URLs
        self.contests_url = f"{self.base_url}/{election_date}/Contests/"
        self.precincts_url = f"{self.base_url}/{election_date}/Precincts/"
    
    def detect_party(self, contest_name: str) -> str:
        """Detect party affiliation from contest name
        
        Kane County uses " - REP", " - DEM", " - NP" suffixes
        
        Args:
            contest_name: Name of the contest
            
        Returns:
            Party string: 'Democratic', 'Republican', or 'Non-Partisan'
        """
        if ' - REP' in contest_name:
            return 'Republican'
        elif ' - DEM' in contest_name:
            return 'Democratic'
        elif ' - NP' in contest_name:
            return 'Non-Partisan'
        else:
            # Fallback detection
            contest_upper = contest_name.upper()
            if 'REPUBLICAN' in contest_upper or 'REP ' in contest_upper:
                return 'Republican'
            elif 'DEMOCRATIC' in contest_upper or 'DEM ' in contest_upper:
                return 'Democratic'
            else:
                return 'Non-Partisan'
    
    def scrape_contests(self) -> Dict:
        """Scrape contest results from Kane County
        
        Returns:
            Dictionary with scraped results
        """
        print(f"Scraping {self.county_name} from custom platform...")
        print(f"Election date: {self.election_date}")
        print(f"Contests URL: {self.contests_url}")
        
        try:
            # Fetch the contests page
            response = requests.get(self.contests_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse the page
            results = self._parse_contests_page(soup)
            results['county'] = self.county_name
            results['election_date'] = self.election_date
            results['scraped_at'] = datetime.now().isoformat()
            results['source'] = 'Kane County custom platform'
            
            print(f"✓ Successfully scraped {len(results.get('contests', []))} contests")
            return results
            
        except requests.RequestException as e:
            print(f"✗ Error fetching results: {e}")
            return {
                'error': str(e),
                'county': self.county_name,
                'election_date': self.election_date,
                'scraped_at': datetime.now().isoformat()
            }
    
    def _parse_contests_page(self, soup: BeautifulSoup) -> Dict:
        """Parse the contests page HTML
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary with contests and summary info
        """
        results = {
            'contests': [],
            'summary': {}
        }
        
        # Extract overall summary stats (at top of page)
        # Look for "Registered Voters:", "Ballots Cast:", "Turnout:"
        summary_text = soup.get_text()
        
        # Extract registered voters
        reg_match = re.search(r'Registered Voters:\s*\*?\*?(\d+(?:,\d+)*)', summary_text)
        if reg_match:
            results['summary']['registered_voters'] = int(reg_match.group(1).replace(',', ''))
        
        # Extract ballots cast
        ballots_match = re.search(r'Ballots Cast:\s*\*?\*?(\d+(?:,\d+)*)', summary_text)
        if ballots_match:
            results['summary']['ballots_cast'] = int(ballots_match.group(1).replace(',', ''))
        
        # Extract turnout
        turnout_match = re.search(r'Turnout:\s*\*?\*?([\d.]+)%', summary_text)
        if turnout_match:
            results['summary']['turnout_percent'] = float(turnout_match.group(1))
        
        # Find all contest headings (h2 elements)
        contests = soup.find_all('h2')
        
        for contest_heading in contests:
            # Get contest name from heading text
            contest_name = contest_heading.get_text().strip()
            
            # Skip if this is the main page heading
            if contest_name == '2024 General Primary Results - Official Contest Results':
                continue
            if not contest_name:
                continue
            
            # Parse this contest
            parsed_contest = self._parse_contest(contest_heading, contest_name)
            if parsed_contest:
                results['contests'].append(parsed_contest)
        
        return results
    
    def _parse_contest(self, heading_element, contest_name: str) -> Optional[Dict]:
        """Parse a single contest section
        
        Args:
            heading_element: BeautifulSoup element of the h2 heading
            contest_name: Name of the contest
            
        Returns:
            Contest dictionary or None if parsing failed
        """
        contest = {
            'name': contest_name,
            'party': self.detect_party(contest_name),
            'candidates': []
        }
        
        # Find the table that follows this heading
        # Kane County structure: h2 (contest name) -> p (stats) -> table (results)
        table = None
        current = heading_element.find_next_sibling()
        
        while current:
            if current.name == 'table':
                table = current
                break
            elif current.name == 'h2':
                # Hit next contest, no table found
                break
            current = current.find_next_sibling()
        
        if not table:
            return contest  # Return empty contest
        
        # Extract contest-level stats (precincts reporting)
        stats_p = heading_element.find_next('p')
        if stats_p:
            stats_text = stats_p.get_text()
            
            # Extract precincts reporting
            precinct_match = re.search(r'(\d+)\s+of\s+(\d+)\s+Precincts Reporting', stats_text)
            if precinct_match:
                contest['precincts_reporting'] = int(precinct_match.group(1))
                contest['total_precincts'] = int(precinct_match.group(2))
        
        # Parse candidate rows from table
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            
            # Each row should have 3 cells: candidate name, votes, percentage
            if len(cells) == 3:
                candidate_name = cells[0].get_text().strip()
                votes_text = cells[1].get_text().strip()
                percent_text = cells[2].get_text().strip()
                
                # Skip empty rows
                if not candidate_name:
                    continue
                
                # Parse votes (may have commas)
                try:
                    votes = int(votes_text.replace(',', ''))
                except (ValueError, AttributeError):
                    votes = 0
                
                # Parse percentage (remove % sign)
                try:
                    percent = float(percent_text.replace('%', ''))
                except (ValueError, AttributeError):
                    percent = 0.0
                
                contest['candidates'].append({
                    'name': candidate_name,
                    'votes': votes,
                    'percent': percent
                })
        
        return contest if contest['candidates'] else None
    
    def save_results(self, results: Dict, output_dir: str = '.'):
        """Save results to JSON file
        
        Args:
            results: Results dictionary
            output_dir: Directory to save file
        """
        filename = f"{output_dir}/kane_results.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Saved results to {filename}")

def print_instructions():
    """Print detailed usage instructions"""
    print("=" * 70)
    print("Kane County Election Results Scraper")
    print("Illinois Primary Election - March 17, 2026")
    print("=" * 70)
    print()
    print("Kane County uses a simple date-based URL structure")
    print("Base URL: https://electionresults.kanecountyil.gov")
    print()
    print("USAGE:")
    print()
    print("  # Scrape 2026 Primary (default)")
    print("  python kane_county_scraper.py")
    print()
    print("  # Scrape specific date")
    print("  python kane_county_scraper.py --date 2024-03-19")
    print()
    print("  # Specify output directory")
    print("  python kane_county_scraper.py --output /path/to/results/")
    print()
    print("URL PATTERN:")
    print("  Contest totals: /YYYY-MM-DD/Contests/")
    print("  Precinct results: /YYYY-MM-DD/Precincts/")
    print()
    print("Example: https://electionresults.kanecountyil.gov/2026-03-17/Contests/")
    print()
    print("The scraper will:")
    print("  1. Fetch HTML from the contests page")
    print("  2. Parse all contest tables")
    print("  3. Extract candidate names, votes, and percentages")
    print("  4. Detect party from contest names (uses ' - REP', ' - DEM' suffixes)")
    print("  5. Save to kane_results.json")
    print()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kane County Election Results Scraper')
    parser.add_argument('--date', default='2026-03-17',
                       help='Election date in YYYY-MM-DD format (default: 2026-03-17)')
    parser.add_argument('--output', default='.',
                       help='Output directory for JSON results')
    
    args = parser.parse_args()
    
    if args.date == '2026-03-17':
        print()
        print("⚠️  Using default date: 2026-03-17")
        print("    Make sure this is the correct election date!")
        print("    Check: https://electionresults.kanecountyil.gov")
        print()
    
    # Create scraper and run
    scraper = KaneCountyScraper(args.date)
    results = scraper.scrape_contests()
    scraper.save_results(results, args.output)
    
    # Print summary
    if 'error' not in results:
        print()
        print("Summary:")
        print(f"  County: {results.get('county')}")
        print(f"  Election: {results.get('election_date')}")
        print(f"  Contests: {len(results.get('contests', []))}")
        if 'registered_voters' in results.get('summary', {}):
            print(f"  Registered voters: {results['summary']['registered_voters']:,}")
        if 'ballots_cast' in results.get('summary', {}):
            print(f"  Ballots cast: {results['summary']['ballots_cast']:,}")
        if 'turnout_percent' in results.get('summary', {}):
            print(f"  Turnout: {results['summary']['turnout_percent']:.2f}%")

if __name__ == '__main__':
    main()
