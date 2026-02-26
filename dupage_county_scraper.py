#!/usr/bin/env python3
"""
Illinois Primary Election 2026 - DuPage County Scraper
Handles DuPage County (2nd largest Illinois county)

Platform: Scytl Election Night Reporting
Base URL: https://www.dupageresults.gov/IL/DuPage
Coverage: DuPage County (~930,000 residents, 600,000+ voters)

Scytl is a major election technology vendor. Their platform provides JSON endpoints
for summary and detailed results. This scraper accesses those endpoints directly.
"""

import requests
import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional

class DuPageCountyScraper:
    """Scraper for DuPage County Scytl election results"""
    
    def __init__(self, election_id: Optional[str] = None):
        """Initialize scraper
        
        Args:
            election_id: Scytl election ID (e.g., '114729')
                        If None, must be provided later or found from election list
        """
        self.county_name = 'DuPage County'
        self.state_code = 'IL'
        self.county_code = 'DuPage'
        self.base_url = 'https://www.dupageresults.gov'
        
        self.election_id = election_id or 'UPDATE_ON_ELECTION_DAY'
        
        if self.election_id == 'UPDATE_ON_ELECTION_DAY':
            print("⚠️  WARNING: Election ID not set!")
            print("   On election day, visit: https://www.dupageresults.gov/IL/DuPage")
            print("   Find March 17, 2026 Primary, click to view results")
            print("   URL will be: /IL/DuPage/[ELECTION_ID]/")
            print("   Extract and use that ELECTION_ID")
            print()
        
        # Construct API endpoints
        if self.election_id != 'UPDATE_ON_ELECTION_DAY':
            self.summary_url = f"{self.base_url}/{self.state_code}/{self.county_code}/{self.election_id}/json/en/summary.json"
            self.electionsettings_url = f"{self.base_url}/{self.state_code}/{self.county_code}/{self.election_id}/json/en/electionsettings.json"
            self.results_base = f"{self.base_url}/{self.state_code}/{self.county_code}/{self.election_id}/json/en"
    
    def detect_party(self, contest_name: str) -> str:
        """Detect party affiliation from contest name
        
        Args:
            contest_name: Name of the contest
            
        Returns:
            Party string: 'Democratic', 'Republican', or 'Non-Partisan'
        """
        contest_upper = contest_name.upper()
        
        # Scytl often includes party in contest name
        if 'DEM ' in contest_upper or 'DEMOCRATIC' in contest_upper or '(D)' in contest_upper:
            return 'Democratic'
        elif 'REP ' in contest_upper or 'REPUBLICAN' in contest_upper or '(R)' in contest_upper:
            return 'Republican'
        else:
            return 'Non-Partisan'
    
    def list_elections(self) -> List[Dict]:
        """List available elections from Scytl platform
        
        Returns:
            List of election dictionaries with IDs and names
        """
        try:
            # Try to fetch elections list (format may vary)
            elections_url = f"{self.base_url}/{self.state_code}/{self.county_code}/json/en/elections.json"
            
            response = requests.get(elections_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract election info (structure varies)
            elections = []
            if isinstance(data, list):
                for item in data:
                    elections.append({
                        'id': item.get('ElectionID') or item.get('id'),
                        'name': item.get('ElectionName') or item.get('name'),
                        'date': item.get('Date') or item.get('date')
                    })
            elif isinstance(data, dict) and 'elections' in data:
                for item in data['elections']:
                    elections.append({
                        'id': item.get('ElectionID') or item.get('id'),
                        'name': item.get('ElectionName') or item.get('name'),
                        'date': item.get('Date') or item.get('date')
                    })
            
            return elections
            
        except Exception as e:
            print(f"Unable to fetch elections list: {e}")
            return []
    
    def scrape_summary(self) -> Dict:
        """Scrape summary results from Scytl platform
        
        Returns:
            Dictionary with scraped results
        """
        if self.election_id == 'UPDATE_ON_ELECTION_DAY':
            return {
                'error': 'Election ID not configured',
                'county': self.county_name,
                'message': 'Visit https://www.dupageresults.gov/IL/DuPage to find election ID',
                'scraped_at': datetime.now().isoformat()
            }
        
        print(f"Scraping {self.county_name} from Scytl platform...")
        print(f"Election ID: {self.election_id}")
        print(f"Summary URL: {self.summary_url}")
        
        try:
            # Fetch summary results
            response = requests.get(self.summary_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse Scytl summary format
            results = self._parse_scytl_summary(data)
            results['county'] = self.county_name
            results['scraped_at'] = datetime.now().isoformat()
            results['source'] = 'Scytl summary JSON'
            results['election_id'] = self.election_id
            
            print(f"✓ Successfully scraped {len(results.get('contests', []))} contests")
            return results
            
        except requests.RequestException as e:
            print(f"✗ Error fetching results: {e}")
            return {
                'error': str(e),
                'county': self.county_name,
                'scraped_at': datetime.now().isoformat()
            }
    
    def _parse_scytl_summary(self, data: Dict) -> Dict:
        """Parse Scytl summary JSON format
        
        Scytl format typically includes:
        - Contests array with candidate results
        - Precinct reporting info
        - Turnout statistics
        
        Args:
            data: Raw JSON data from Scytl
            
        Returns:
            Normalized results dictionary
        """
        results = {
            'contests': [],
            'summary': {}
        }
        
        # Extract summary statistics
        if 'Precincts' in data:
            results['summary']['precincts_reporting'] = data.get('PrecinctsReporting', 0)
            results['summary']['total_precincts'] = data.get('Precincts', 0)
        
        if 'BallotsCount' in data or 'BallotsCast' in data:
            results['summary']['ballots_cast'] = data.get('BallotsCount') or data.get('BallotsCast', 0)
        
        if 'RegisteredVoters' in data:
            results['summary']['registered_voters'] = data.get('RegisteredVoters', 0)
        
        # Extract contests
        # Scytl can have contests at various levels in the JSON
        contests_data = data.get('Contests') or data.get('contests') or []
        
        for contest in contests_data:
            parsed_contest = self._parse_scytl_contest(contest)
            if parsed_contest:
                results['contests'].append(parsed_contest)
        
        return results
    
    def _parse_scytl_contest(self, contest: Dict) -> Optional[Dict]:
        """Parse a single contest from Scytl format
        
        Args:
            contest: Contest dictionary from Scytl JSON
            
        Returns:
            Normalized contest dictionary or None if invalid
        """
        # Extract contest name (various possible keys)
        contest_name = (contest.get('C') or 
                       contest.get('Contest') or 
                       contest.get('ContestName') or
                       contest.get('Name') or '')
        
        if not contest_name:
            return None
        
        parsed = {
            'name': contest_name,
            'party': self.detect_party(contest_name),
            'candidates': []
        }
        
        # Extract candidates/choices
        # Scytl uses various field names
        candidates_data = (contest.get('CH') or  # Choices
                          contest.get('Candidates') or
                          contest.get('Choices') or [])
        
        for candidate in candidates_data:
            # Extract candidate info (field names vary)
            name = (candidate.get('N') or 
                   candidate.get('Candidate') or
                   candidate.get('Name') or 
                   candidate.get('Choice') or '')
            
            votes = (candidate.get('V') or 
                    candidate.get('Votes') or
                    candidate.get('VoteCount') or 0)
            
            percent = (candidate.get('P') or
                      candidate.get('Percent') or
                      candidate.get('Percentage') or 0.0)
            
            # Convert votes to int if string
            if isinstance(votes, str):
                votes = int(votes.replace(',', ''))
            
            # Convert percent to float if string
            if isinstance(percent, str):
                percent = float(percent.replace('%', ''))
            
            if name:
                parsed['candidates'].append({
                    'name': name,
                    'votes': votes,
                    'percent': percent
                })
        
        return parsed if parsed['candidates'] else None
    
    def save_results(self, results: Dict, output_dir: str = '.'):
        """Save results to JSON file
        
        Args:
            results: Results dictionary
            output_dir: Directory to save file
        """
        filename = f"{output_dir}/dupage_results.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Saved results to {filename}")

def print_instructions():
    """Print detailed usage instructions"""
    print("=" * 70)
    print("DuPage County Election Results Scraper")
    print("Illinois Primary Election - March 17, 2026")
    print("=" * 70)
    print()
    print("DuPage County uses Scytl Election Night Reporting platform")
    print("Base URL: https://www.dupageresults.gov/IL/DuPage")
    print()
    print("ELECTION DAY SETUP:")
    print()
    print("1. Visit: https://www.dupageresults.gov/IL/DuPage")
    print("2. Find 'March 17, 2026 Primary' in the elections list")
    print("3. Click to view results - URL will be: /IL/DuPage/[ID]/")
    print("4. Extract the election ID from the URL")
    print()
    print("USAGE:")
    print()
    print("  # Scrape with election ID")
    print("  python dupage_county_scraper.py --id 123456")
    print()
    print("  # List available elections (if endpoint accessible)")
    print("  python dupage_county_scraper.py --list")
    print()
    print("The scraper will fetch JSON data from Scytl's summary endpoint")
    print("and normalize it to the standard format.")
    print()
    print("Note: Election ID changes for each election!")
    print()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DuPage County Scytl Election Results Scraper')
    parser.add_argument('--id', '--election-id', dest='election_id', 
                       help='Scytl election ID (e.g., 123456)')
    parser.add_argument('--list', action='store_true',
                       help='List available elections')
    parser.add_argument('--output', default='.', 
                       help='Output directory for JSON results')
    
    args = parser.parse_args()
    
    if args.list:
        # List available elections
        scraper = DuPageCountyScraper()
        elections = scraper.list_elections()
        
        if elections:
            print("Available elections:")
            for election in elections:
                print(f"  ID: {election['id']}")
                print(f"  Name: {election['name']}")
                print(f"  Date: {election.get('date', 'N/A')}")
                print()
        else:
            print("Could not retrieve elections list.")
            print("Visit https://www.dupageresults.gov/IL/DuPage manually")
        
    elif args.election_id:
        # Scrape with provided election ID
        scraper = DuPageCountyScraper(args.election_id)
        results = scraper.scrape_summary()
        scraper.save_results(results, args.output)
    else:
        # Show instructions
        print_instructions()

if __name__ == '__main__':
    main()
