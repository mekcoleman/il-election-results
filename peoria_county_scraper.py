#!/usr/bin/env python3
"""
Illinois Primary Election 2026 - Peoria County Scraper
Handles Peoria County Election Commission results via ElectionStats database

Platform: ElectionStats (Custom database)
Base URL: https://electionarchive.peoriaelections.gov
Coverage: Peoria County (~130K voters)

The ElectionStats database is a custom system by Peoria County with:
- Searchable web interface
- Individual contest pages
- CSV download capability
- No documented API

Strategy: This scraper can work in two modes:
1. With contest IDs: Download CSV data directly (fastest, requires IDs)
2. HTML scraping: Parse contest pages to extract results
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

class PeoriaCountyScraper:
    """Scraper for Peoria County ElectionStats database"""
    
    def __init__(self, election_date: str = '2026-03-17'):
        """Initialize scraper
        
        Args:
            election_date: Election date in YYYY-MM-DD format
        """
        self.county_name = 'Peoria'
        self.authority = 'Peoria County Election Commission'
        self.election_date = election_date
        
        # ElectionStats URLs
        self.base_url = 'https://electionarchive.peoriaelections.gov/eng'
        self.contest_view_url = f'{self.base_url}/contests/view'
        self.contest_download_url = f'{self.base_url}/contests/download'
        self.contest_search_url = f'{self.base_url}/contests/search'
        
        # Format election date for URLs (YYYY-MM-DD)
        self.url_date = election_date  # Already in correct format
        
        # Map for party detection
        self.party_map = {
            'democratic': 'Democratic',
            'republican': 'Republican',
            'dem': 'Democratic',
            'rep': 'Republican',
            'primary': '',  # Will be determined by contest name
        }
    
    def detect_party(self, contest_name: str, election_type: str = '') -> str:
        """Detect party from contest name or election type
        
        Args:
            contest_name: Name of the contest
            election_type: Type of election (e.g., "Republican Primary")
            
        Returns:
            Party string
        """
        # Check election type first
        election_lower = election_type.lower()
        if 'republican' in election_lower:
            return 'Republican'
        elif 'democratic' in election_lower:
            return 'Democratic'
        elif 'non-partisan' in election_lower or 'nonpartisan' in election_lower:
            return 'Non-Partisan'
        
        # Check contest name
        contest_lower = contest_name.lower()
        if 'republican' in contest_lower or ' rep ' in contest_lower or '(rep)' in contest_lower:
            return 'Republican'
        elif 'democratic' in contest_lower or ' dem ' in contest_lower or '(dem)' in contest_lower:
            return 'Democratic'
        else:
            return 'Non-Partisan'
    
    def scrape_by_contest_ids(self, contest_ids: List[int]) -> Dict:
        """Scrape results using specific contest IDs
        
        Most reliable method if you know the contest IDs.
        
        Args:
            contest_ids: List of contest IDs to fetch
            
        Returns:
            Dictionary with scraped results
        """
        print(f"Scraping {self.authority} by contest IDs...")
        print(f"Fetching {len(contest_ids)} contests")
        
        results = {
            'contests': [],
            'summary': {}
        }
        
        for contest_id in contest_ids:
            try:
                contest = self._fetch_contest(contest_id)
                if contest:
                    results['contests'].append(contest)
                    print(f"  ✓ Contest {contest_id}: {contest.get('name', 'Unknown')}")
            except Exception as e:
                print(f"  ✗ Error fetching contest {contest_id}: {e}")
        
        results['authority'] = self.authority
        results['jurisdiction'] = self.county_name
        results['election_date'] = self.election_date
        results['scraped_at'] = datetime.now().isoformat()
        results['source'] = 'ElectionStats Database'
        
        print(f"✓ Successfully scraped {len(results['contests'])} contests")
        return results
    
    def scrape_election_page(self, election_name: str = None) -> Dict:
        """Scrape all contests for an election
        
        This attempts to find and scrape all contests for the given election.
        
        Args:
            election_name: Election name (e.g., "2024 Mar 19 - Primary")
                          If None, uses self.election_date
            
        Returns:
            Dictionary with scraped results
        """
        print(f"Scraping {self.authority} for entire election...")
        print(f"Note: This method requires finding contest IDs via web interface")
        print(f"For election day, provide contest IDs directly to scrape_by_contest_ids()")
        
        results = {
            'contests': [],
            'summary': {},
            'error': 'Full election scraping requires contest IDs',
            'message': 'Visit https://electionarchive.peoriaelections.gov to browse elections and find contest IDs'
        }
        
        results['authority'] = self.authority
        results['jurisdiction'] = self.county_name
        results['election_date'] = self.election_date
        results['scraped_at'] = datetime.now().isoformat()
        
        return results
    
    def _fetch_contest(self, contest_id: int) -> Optional[Dict]:
        """Fetch a single contest by ID
        
        Args:
            contest_id: Contest ID number
            
        Returns:
            Contest dictionary or None
        """
        # Try CSV download first (more structured)
        csv_url = f"{self.contest_download_url}/{contest_id}/show_granularity_dt_id:7/.csv"
        
        try:
            response = requests.get(csv_url, timeout=30)
            if response.status_code == 200 and 'text/csv' in response.headers.get('content-type', ''):
                return self._parse_csv_contest(contest_id, response.text)
        except:
            pass
        
        # Fall back to HTML parsing
        html_url = f"{self.contest_view_url}/{contest_id}"
        
        try:
            response = requests.get(html_url, timeout=30)
            response.raise_for_status()
            return self._parse_html_contest(contest_id, response.text)
        except Exception as e:
            print(f"Error fetching contest {contest_id}: {e}")
            return None
    
    def _parse_csv_contest(self, contest_id: int, csv_text: str) -> Optional[Dict]:
        """Parse contest from CSV format
        
        CSV format typically has columns: Precinct, Candidate1, Candidate2, ...
        
        Args:
            contest_id: Contest ID
            csv_text: CSV content
            
        Returns:
            Contest dictionary
        """
        lines = csv_text.strip().split('\n')
        if len(lines) < 2:
            return None
        
        # First line is headers (precinct name, candidate names, etc.)
        headers = [h.strip().strip('"') for h in lines[0].split(',')]
        
        # Find candidate columns (skip Precinct, Total Votes Cast, etc.)
        candidate_cols = []
        for i, header in enumerate(headers):
            if header and header not in ['Precinct', 'Total Votes Cast', 'Undervotes', 
                                          'Overvotes', 'Total Ballots Cast', 'Registered Voters']:
                candidate_cols.append((i, header))
        
        # Sum up votes from all rows
        candidate_votes = {name: 0 for _, name in candidate_cols}
        
        for line in lines[1:]:
            if not line.strip():
                continue
            
            values = line.split(',')
            for col_idx, name in candidate_cols:
                try:
                    votes = int(values[col_idx].strip().strip('"'))
                    candidate_votes[name] += votes
                except (ValueError, IndexError):
                    pass
        
        # Calculate total
        total_votes = sum(candidate_votes.values())
        
        # Build candidates list
        candidates = []
        for name, votes in candidate_votes.items():
            percent = (votes / total_votes * 100) if total_votes > 0 else 0
            candidates.append({
                'name': name,
                'votes': votes,
                'percent': round(percent, 2)
            })
        
        # Contest name needs to come from HTML (CSV doesn't have it)
        # For now, use a placeholder
        contest = {
            'id': contest_id,
            'name': f'Contest {contest_id}',
            'party': 'Unknown',
            'candidates': candidates
        }
        
        return contest if candidates else None
    
    def _parse_html_contest(self, contest_id: int, html: str) -> Optional[Dict]:
        """Parse contest from HTML page
        
        Args:
            contest_id: Contest ID
            html: HTML content
            
        Returns:
            Contest dictionary
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract contest title from h1
        title_elem = soup.find('h1')
        if not title_elem:
            return None
        
        contest_title = title_elem.text.strip()
        
        # Title format: "2024 Mar 19 :: Republican Primary :: Office :: District"
        # Parse to extract: date, election type, office, district
        parts = [p.strip() for p in contest_title.split('::')]
        
        election_date = parts[0] if len(parts) > 0 else ''
        election_type = parts[1] if len(parts) > 1 else ''
        office = parts[2] if len(parts) > 2 else 'Unknown'
        district = parts[3] if len(parts) > 3 else ''
        
        # Build contest name
        contest_name = office
        if district:
            contest_name = f"{office} - {district}"
        
        # Determine party
        party = self.detect_party(contest_name, election_type)
        
        # Find candidates section
        candidates = []
        
        # Look for "Candidates" section
        candidates_header = soup.find(string=re.compile(r'Candidates', re.IGNORECASE))
        if candidates_header:
            # Find the parent and look for links to candidate pages
            parent = candidates_header.find_parent()
            if parent:
                candidate_links = parent.find_all('a', href=re.compile(r'/candidates/view/\d+'))
                for link in candidate_links:
                    candidates.append({
                        'name': link.text.strip().replace(' - winner', ''),
                        'votes': 0,  # Will need to extract from table
                        'percent': 0
                    })
        
        # Try to find results table
        table = soup.find('table')
        if table:
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [th.text.strip() for th in header_row.find_all('th')]
            
            # Look for Totals row
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if cells and cells[0].text.strip().lower() == 'totals':
                    # Extract vote counts
                    for i, header in enumerate(headers):
                        if i < len(cells) and header and header not in ['Totals', 'Total Votes Cast', 
                                                                         'Undervotes', 'Overvotes', 
                                                                         'Total Ballots Cast', 
                                                                         'Registered Voters']:
                            try:
                                votes = int(cells[i].text.strip().replace(',', ''))
                                # Match to candidate
                                for candidate in candidates:
                                    if header in candidate['name'] or candidate['name'] in header:
                                        candidate['votes'] = votes
                            except (ValueError, IndexError):
                                pass
        
        # Calculate percentages
        total_votes = sum(c['votes'] for c in candidates)
        for candidate in candidates:
            if total_votes > 0:
                candidate['percent'] = round(candidate['votes'] / total_votes * 100, 2)
        
        contest = {
            'id': contest_id,
            'name': contest_name,
            'party': party,
            'election_type': election_type,
            'candidates': candidates
        }
        
        return contest if candidates else None
    
    def save_results(self, results: Dict, output_dir: str = '.'):
        """Save results to JSON file
        
        Args:
            results: Results dictionary
            output_dir: Directory to save file
        """
        filename = f"{output_dir}/peoria_county_results.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Saved results to {filename}")

def print_instructions():
    """Print detailed usage instructions"""
    print("=" * 70)
    print("Peoria County Election Commission Scraper")
    print("Illinois Primary Election - March 17, 2026")
    print("=" * 70)
    print()
    print("Peoria County uses ElectionStats, a custom searchable database.")
    print("Base URL: https://electionarchive.peoriaelections.gov")
    print()
    print("⚠️  IMPORTANT: Contest IDs Required")
    print()
    print("This scraper works best with contest IDs. To get these:")
    print()
    print("1. Visit: https://electionarchive.peoriaelections.gov")
    print("2. Select the 2026 Primary election date")
    print("3. Browse contests and note the ID numbers from URLs")
    print("   Example: /eng/contests/view/5432 → ID is 5432")
    print("4. Provide IDs to the scraper")
    print()
    print("USAGE:")
    print()
    print("  # With contest IDs (recommended)")
    print("  python peoria_county_scraper.py --ids 5432,5433,5434,5435")
    print()
    print("  # Without IDs (instructions only)")
    print("  python peoria_county_scraper.py")
    print()
    print("FINDING CONTEST IDs:")
    print()
    print("The ElectionStats interface shows contests individually.")
    print("On election night:")
    print("- Browse to the 2026 Primary results")
    print("- Click on each major race (President, Governor, etc.)")
    print("- Note the contest ID from the URL")
    print("- Provide all IDs to scraper for complete results")
    print()
    print("Alternative: Use the search/filter interface to find all contests,")
    print("then note their IDs manually.")
    print()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Peoria County Election Results Scraper')
    parser.add_argument('--ids', '--contest-ids', dest='contest_ids',
                       help='Comma-separated list of contest IDs (e.g., 5432,5433,5434)')
    parser.add_argument('--date', default='2026-03-17',
                       help='Election date in YYYY-MM-DD format')
    parser.add_argument('--output', default='.',
                       help='Output directory for JSON results')
    
    args = parser.parse_args()
    
    scraper = PeoriaCountyScraper(args.date)
    
    if args.contest_ids:
        # Parse contest IDs
        try:
            contest_ids = [int(id.strip()) for id in args.contest_ids.split(',')]
            results = scraper.scrape_by_contest_ids(contest_ids)
        except ValueError:
            print("Error: Invalid contest IDs. Please provide comma-separated integers.")
            return
    else:
        # No IDs provided - show instructions
        print_instructions()
        results = scraper.scrape_election_page()
    
    scraper.save_results(results, args.output)
    
    # Print summary
    if 'error' not in results:
        print()
        print("Summary:")
        print(f"  Jurisdiction: {results.get('jurisdiction')}")
        print(f"  Authority: {results.get('authority')}")
        print(f"  Election: {results.get('election_date')}")
        print(f"  Contests: {len(results.get('contests', []))}")
    else:
        print()
        print(f"Error: {results['error']}")
        print(f"Message: {results['message']}")

if __name__ == '__main__':
    main()
