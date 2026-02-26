"""
Multi-County Clarity Elections Scraper
Scrapes election results from Clarity Elections platform for multiple Illinois counties
Supports: Will, McHenry, Lake, Kankakee, Winnebago (County & City of Rockford)
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import time
import sys


class ClarityElectionsScraper:
    """Scraper for Clarity Elections platform used by multiple Illinois counties"""
    
    def __init__(self, base_url: str, election_id: str, web_id: str, county_name: str):
        """
        Initialize the scraper
        
        Args:
            base_url: Base URL for the county (e.g., "https://results.enr.clarityelections.com/IL/Will")
            election_id: Election ID (e.g., "123535")
            web_id: Web ID (e.g., "357754")
            county_name: Name of the county for output labeling
        """
        self.base_url = base_url
        self.election_id = election_id
        self.web_id = web_id
        self.county_name = county_name
        self.json_base = f"{base_url}/{election_id}/{web_id}/json/en"
        
    def fetch_json(self, endpoint: str) -> Optional[Dict]:
        """Fetch JSON data from an endpoint"""
        url = f"{self.json_base}/{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def get_election_settings(self) -> Optional[Dict]:
        """Get election metadata and settings"""
        return self.fetch_json("electionsettings.json")
    
    def get_summary(self) -> Optional[Dict]:
        """Get summary of all contests"""
        return self.fetch_json("summary.json")
    
    def detect_contest_party(self, contest: Dict) -> str:
        """
        Detect the party affiliation of a contest for primary elections.
        
        For primary elections, contests are typically party-specific.
        This function looks for party indicators in contest names and types.
        
        Returns:
            "Democratic", "Republican", or "Non-Partisan"
        """
        contest_name = contest.get('C', '').upper()
        contest_type = contest.get('T', '').upper()
        
        # Check for party indicators in contest name
        if 'DEMOCRATIC' in contest_name or 'DEM ' in contest_name:
            return "Democratic"
        elif 'REPUBLICAN' in contest_name or 'REP ' in contest_name:
            return "Republican"
        
        # Check contest type
        if 'DEMOCRATIC' in contest_type:
            return "Democratic"
        elif 'REPUBLICAN' in contest_type:
            return "Republican"
        
        # Default to Non-Partisan for general contests
        return "Non-Partisan"
    
    def get_contest_details(self, contest_id: int) -> Optional[Dict]:
        """Get detailed results for a specific contest"""
        return self.fetch_json(f"detail/{contest_id}.json")
    
    def parse_contest(self, contest: Dict, detail: Optional[Dict] = None) -> Dict:
        """Parse contest data into a structured format"""
        
        # Basic contest info
        contest_data = {
            'contest_id': contest.get('A', ''),
            'contest_name': contest.get('C', ''),
            'contest_type': contest.get('T', ''),
            'party': self.detect_contest_party(contest),
            'precincts_reporting': contest.get('RP', 0),
            'total_precincts': contest.get('TP', 0),
            'reporting_percentage': round((contest.get('RP', 0) / contest.get('TP', 1)) * 100, 2) if contest.get('TP', 0) > 0 else 0,
            'candidates': []
        }
        
        # Parse candidates
        choices = contest.get('CH', [])
        for choice in choices:
            candidate = {
                'choice_id': choice.get('I', ''),
                'name': choice.get('D', ''),
                'party': choice.get('P', ''),
                'votes': choice.get('V', 0),
                'percentage': round(choice.get('E', 0), 2)
            }
            contest_data['candidates'].append(candidate)
        
        return contest_data
    
    def scrape_all_contests(self) -> List[Dict]:
        """
        Scrape all contests and return structured results
        
        Returns:
            List of contest dictionaries with detailed results
        """
        print(f"Fetching election summary for {self.county_name}...")
        summary = self.get_summary()
        
        if not summary:
            print(f"Failed to fetch summary for {self.county_name}")
            return []
        
        contests = []
        all_contests = summary.get('Contests', [])
        
        print(f"Found {len(all_contests)} contests")
        
        for i, contest in enumerate(all_contests):
            print(f"Processing contest {i+1}/{len(all_contests)}: {contest.get('C', 'Unknown')}")
            
            # Parse the contest
            contest_data = self.parse_contest(contest)
            contests.append(contest_data)
            
            # Small delay to be respectful
            time.sleep(0.1)
        
        print(f"✅ Completed scraping {len(contests)} contests for {self.county_name}")
        return contests
    
    def save_to_json(self, contests: List[Dict], filename: str):
        """
        Save contests to JSON file, organized by party for primaries
        
        Args:
            contests: List of contest dictionaries
            filename: Output filename
        """
        # Organize by party
        organized = {
            "Democratic": [],
            "Republican": [],
            "Non-Partisan": []
        }
        
        for contest in contests:
            party = contest.get('party', 'Non-Partisan')
            organized[party].append(contest)
        
        # Create output structure
        output = {
            "county": self.county_name,
            "scrape_time": datetime.now().isoformat(),
            "election_type": "Primary",
            "total_contests": len(contests),
            "contests_by_party": organized,
            "summary": {
                "democratic_contests": len(organized["Democratic"]),
                "republican_contests": len(organized["Republican"]),
                "non_partisan_contests": len(organized["Non-Partisan"])
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Results saved to {filename}")
        print(f"   - Democratic: {output['summary']['democratic_contests']} contests")
        print(f"   - Republican: {output['summary']['republican_contests']} contests")
        print(f"   - Non-Partisan: {output['summary']['non_partisan_contests']} contests")


def scrape_clarity_county(county_name: str, config_path: str = 'config.json'):
    """
    Scrape election results for a specific Clarity Elections county
    
    Args:
        county_name: Name of the county to scrape (e.g., "Will", "McHenry")
        config_path: Path to configuration file
        
    Returns:
        List of contest results
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    county_config = config['counties'].get(county_name)
    
    if not county_config:
        print(f"❌ County '{county_name}' not found in configuration")
        return None
    
    if county_config.get('platform') != 'clarity':
        print(f"❌ County '{county_name}' does not use Clarity Elections platform")
        return None
    
    # Check if URLs are configured
    if county_config.get('election_id') == "UPDATE_ON_ELECTION_DAY":
        print(f"⚠️  WARNING: Election URLs not yet configured for {county_name}!")
        print("Please update election_id and web_id in config.json before election day")
        return None
    
    # Initialize scraper
    print(f"\n{'='*60}")
    print(f"Scraping {county_name} County")
    print(f"{'='*60}\n")
    
    scraper = ClarityElectionsScraper(
        base_url=county_config['base_url'],
        election_id=county_config['election_id'],
        web_id=county_config['web_id'],
        county_name=county_name
    )
    
    # Scrape all contests
    contests = scraper.scrape_all_contests()
    
    # Save to JSON
    if contests:
        filename = f"{county_name.lower()}_results.json"
        scraper.save_to_json(contests, filename)
    
    return contests


def scrape_all_clarity_counties(config_path: str = 'config.json'):
    """
    Scrape all counties that use Clarity Elections platform
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary mapping county names to their results
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Find all Clarity counties
    clarity_counties = []
    for county_name, county_config in config['counties'].items():
        if county_config.get('platform') == 'clarity':
            clarity_counties.append(county_name)
    
    print(f"\n{'='*60}")
    print(f"Found {len(clarity_counties)} counties using Clarity Elections:")
    print(f"{'='*60}")
    for county in clarity_counties:
        print(f"  - {county}")
    print()
    
    # Scrape each county
    all_results = {}
    for county_name in clarity_counties:
        results = scrape_clarity_county(county_name, config_path)
        if results:
            all_results[county_name] = results
        print()  # Blank line between counties
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Scraping Complete")
    print(f"{'='*60}")
    print(f"Successfully scraped {len(all_results)} of {len(clarity_counties)} counties")
    for county, results in all_results.items():
        print(f"  ✅ {county}: {len(results)} contests")
    
    return all_results


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Scrape specific county
        county_name = sys.argv[1]
        scrape_clarity_county(county_name)
    else:
        # Scrape all Clarity counties
        scrape_all_clarity_counties()
