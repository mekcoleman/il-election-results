"""
Will County Election Results Scraper
Scrapes election results from Clarity Elections platform
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import time


class ClarityElectionsScraper:
    """Scraper for Clarity Elections platform used by Will County and others"""
    
    def __init__(self, base_url: str, election_id: str, web_id: str):
        """
        Initialize the scraper
        
        Args:
            base_url: Base URL for the county (e.g., "https://results.enr.clarityelections.com/IL/Will")
            election_id: Election ID (e.g., "123535")
            web_id: Web ID (e.g., "357754")
        """
        self.base_url = base_url
        self.election_id = election_id
        self.web_id = web_id
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
        Detect if a contest is Democratic, Republican, or Non-Partisan
        
        For primary elections, races are typically labeled:
        - "US Senator - Democratic Primary"
        - "Governor (Republican)"
        - Or all candidates share the same party
        
        Special cases:
        - Judicial RETENTION races are non-partisan
        - Judicial ELECTION races may have party affiliations
        - Referenda are always non-partisan
        
        Args:
            contest: Raw contest data
            
        Returns:
            'Democratic', 'Republican', or 'Non-Partisan'
        """
        contest_name = contest.get('C', '').upper()
        parties = contest.get('P', [])
        
        # Special case: Retention races are always non-partisan
        if 'RETENTION' in contest_name:
            return 'Non-Partisan'
        
        # Referenda are always non-partisan
        if 'REFERENDUM' in contest_name or 'BALLOT QUESTION' in contest_name:
            return 'Non-Partisan'
        
        # Primary keywords in race names
        dem_keywords = ['DEMOCRATIC', '(DEM)', 'DEM PRIMARY', 'DEMOCRAT']
        rep_keywords = ['REPUBLICAN', '(REP)', 'REP PRIMARY', 'GOP']
        
        # Check contest name for explicit party indicators
        for keyword in dem_keywords:
            if keyword in contest_name:
                return 'Democratic'
        
        for keyword in rep_keywords:
            if keyword in contest_name:
                return 'Republican'
        
        # Check if all candidates are from the same party
        # Filter out empty strings and normalize
        unique_parties = set()
        for p in parties:
            if p:
                p_upper = p.upper().strip()
                # Normalize party abbreviations
                if p_upper in ['DEM', 'DEMOCRATIC', 'D']:
                    unique_parties.add('DEM')
                elif p_upper in ['REP', 'REPUBLICAN', 'R', 'GOP']:
                    unique_parties.add('REP')
                elif p_upper not in ['IND', 'INDEPENDENT', 'NP', 'NONPARTISAN']:
                    unique_parties.add(p_upper)
        
        # If all candidates are from one party, it's a primary for that party
        if unique_parties == {'DEM'}:
            return 'Democratic'
        if unique_parties == {'REP'}:
            return 'Republican'
        
        # Mixed parties or no party = Non-Partisan
        # This includes: referenda, retention races, some local offices
        return 'Non-Partisan'
    
    def normalize_contest(self, contest: Dict, county: str) -> Dict:
        """
        Normalize a contest into our standard format
        
        Args:
            contest: Raw contest data from Clarity Elections
            county: County name
            
        Returns:
            Normalized contest dictionary
        """
        # Extract basic contest info
        contest_id = contest.get('K', '')  # Contest ID
        contest_name = contest.get('C', '')  # Contest name
        contest_category = contest.get('CAT', '')  # Category (Municipal, Township, etc.)
        
        # Detect party affiliation (for primaries)
        party_type = self.detect_contest_party(contest)
        
        # Extract candidates - CH is array of candidate names
        candidates = []
        candidate_names = contest.get('CH', [])
        parties = contest.get('P', [])
        votes = contest.get('V', [])
        percentages = contest.get('PCT', [])
        
        # Zip all the arrays together
        for i, name in enumerate(candidate_names):
            candidate = {
                'name': name,
                'party': parties[i] if i < len(parties) else '',
                'votes': votes[i] if i < len(votes) else 0,
                'percentage': round(percentages[i], 2) if i < len(percentages) else 0.0
            }
            candidates.append(candidate)
        
        # Extract reporting information
        precincts_reporting = contest.get('PR', 0)
        total_precincts = contest.get('TP', 0)
        
        # Calculate reporting percentage
        reporting_pct = 0
        if total_precincts > 0:
            reporting_pct = (precincts_reporting / total_precincts) * 100
        
        return {
            'contest_id': contest_id,
            'contest_name': contest_name,
            'contest_category': contest_category,
            'party_type': party_type,  # NEW: Democratic, Republican, or Non-Partisan
            'county': county,
            'candidates': candidates,
            'precincts_reporting': precincts_reporting,
            'total_precincts': total_precincts,
            'reporting_percentage': round(reporting_pct, 2),
            'last_updated': datetime.now().isoformat()
        }
    
    def scrape_all_contests(self, county: str = "Will") -> List[Dict]:
        """
        Scrape all contests for this election
        
        Args:
            county: County name (default: "Will")
            
        Returns:
            List of normalized contest dictionaries
        """
        print(f"Scraping {county} County election results...")
        
        # Get summary data
        summary = self.get_summary()
        if not summary:
            print("Failed to fetch summary data")
            return []
        
        # Get election settings for metadata
        settings = self.get_election_settings()
        election_name = settings.get('N', 'Unknown Election') if settings else 'Unknown Election'
        
        print(f"Election: {election_name}")
        
        # The summary.json is an array of contests
        contests = summary if isinstance(summary, list) else summary.get('Contests', [])
        print(f"Found {len(contests)} contests")
        
        # Normalize all contests
        normalized_contests = []
        for contest in contests:
            normalized = self.normalize_contest(contest, county)
            normalized_contests.append(normalized)
        
        return normalized_contests
    
    def save_to_json(self, contests: List[Dict], filename: str, county: str = "Will"):
        """
        Save contests to JSON file, separated by party type for primaries
        
        Args:
            contests: List of normalized contests
            filename: Output filename
            county: County name
        """
        # Separate contests by party type
        democratic = [c for c in contests if c['party_type'] == 'Democratic']
        republican = [c for c in contests if c['party_type'] == 'Republican']
        nonpartisan = [c for c in contests if c['party_type'] == 'Non-Partisan']
        
        output = {
            'county': county,
            'scraped_at': datetime.now().isoformat(),
            'total_contests': len(contests),
            'by_party': {
                'Democratic': {
                    'count': len(democratic),
                    'contests': democratic
                },
                'Republican': {
                    'count': len(republican),
                    'contests': republican
                },
                'Non-Partisan': {
                    'count': len(nonpartisan),
                    'contests': nonpartisan
                }
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Saved {len(contests)} contests to {filename}")
        print(f"  - Democratic: {len(democratic)}")
        print(f"  - Republican: {len(republican)}")
        print(f"  - Non-Partisan: {len(nonpartisan)}")


def scrape_will_county(config_path: str = "config.json"):
    """
    Scrape Will County election results using configuration file
    
    Args:
        config_path: Path to configuration JSON file
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    will_config = config['counties']['Will']
    
    # Check if URLs are configured
    if will_config['election_id'] == "UPDATE_ON_ELECTION_DAY":
        print("⚠️  WARNING: Election URLs not yet configured!")
        print("Please update election_id and web_id in config.json before election day")
        print(f"Example from notes: {will_config['notes']}")
        return None
    
    # Initialize scraper
    scraper = ClarityElectionsScraper(
        base_url=will_config['base_url'],
        election_id=will_config['election_id'],
        web_id=will_config['web_id']
    )
    
    # Scrape all contests
    contests = scraper.scrape_all_contests(county="Will")
    
    # Save to JSON (now organized by party)
    if contests:
        scraper.save_to_json(contests, "will_county_results.json", county="Will")
    
    return contests


if __name__ == "__main__":
    # Run the scraper
    results = scrape_will_county()
    
    # Print sample results
    if results:
        print(f"\n{'='*60}")
        print("Sample Results:")
        print(f"{'='*60}\n")
        
        # Show first contest as example
        first_contest = results[0]
        print(f"Contest: {first_contest['contest_name']}")
        print(f"Precincts Reporting: {first_contest['precincts_reporting']}/{first_contest['total_precincts']} ({first_contest['reporting_percentage']}%)")
        print("\nCandidates:")
        for candidate in first_contest['candidates']:
            print(f"  {candidate['name']} ({candidate['party']}): {candidate['votes']} votes ({candidate['percentage']}%)")
