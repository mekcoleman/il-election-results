#!/usr/bin/env python3
"""
Illinois Primary Election 2026 - Integra Election Reporting Console Scraper
Handles DeKalb, Kendall, and Henry Counties

Platform: Integra Election Reporting Console (electionconsole.com)
Counties covered: 3
- DeKalb County
- Kendall County  
- Henry County

The Integra platform provides results in a plain text format at /electiontext.php
which is much simpler to parse than JavaScript-heavy platforms.
"""

import requests
import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional

class IntegraElectionScraper:
    """Scraper for Integra Election Reporting Console platform"""
    
    # County configurations
    COUNTIES = {
        'DeKalb': {
            'base_url': 'http://dekalb.il.electionconsole.com',
            'name': 'DeKalb County'
        },
        'Kendall': {
            'base_url': 'http://kendall.il.electionconsole.com',
            'name': 'Kendall County'
        },
        'Henry': {
            'base_url': 'http://henry.il.electionconsole.com',
            'name': 'Henry County'
        }
    }
    
    def __init__(self, county_key: str):
        """Initialize scraper for a specific county
        
        Args:
            county_key: County key from COUNTIES dict (e.g., 'DeKalb')
        """
        if county_key not in self.COUNTIES:
            raise ValueError(f"Unknown county: {county_key}. Valid options: {list(self.COUNTIES.keys())}")
        
        config = self.COUNTIES[county_key]
        self.county_key = county_key
        self.county_name = config['name']
        self.base_url = config['base_url']
        self.text_url = f"{self.base_url}/electiontext.php"
        
    def detect_party(self, contest_name: str) -> str:
        """Detect party affiliation from contest name
        
        Args:
            contest_name: Name of the contest
            
        Returns:
            Party string: 'Democratic', 'Republican', or 'Non-Partisan'
        """
        contest_upper = contest_name.upper()
        
        if 'DEMOCRATIC' in contest_upper or 'DEM ' in contest_upper:
            return 'Democratic'
        elif 'REPUBLICAN' in contest_upper or 'REP ' in contest_upper:
            return 'Republican'
        else:
            return 'Non-Partisan'
    
    def parse_text_results(self, text_content: str) -> Dict:
        """Parse plain text election results
        
        Args:
            text_content: Raw text content from electiontext.php
            
        Returns:
            Dictionary with parsed results
        """
        results = {
            'contests': [],
            'summary': {},
            'county': self.county_name,
            'scraped_at': datetime.now().isoformat()
        }
        
        lines = text_content.strip().split('\n')
        current_contest = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line or line == '```':
                continue
            
            # Extract summary information
            if 'PRECINCTS COUNTED' in line:
                match = re.search(r'(\d+)\s+100', line)
                if match:
                    results['summary']['precincts_counted'] = int(match.group(1))
            elif 'REGISTERED VOTERS' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    results['summary']['registered_voters'] = int(match.group(1))
            elif 'BALLOTS CAST - TOTAL' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    results['summary']['ballots_cast'] = int(match.group(1))
            elif 'VOTER TURNOUT' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    results['summary']['turnout_percent'] = int(match.group(1))
            
            # Detect contest headers (all caps, no leading dots)
            if line.isupper() and not line.startswith('.') and 'VOTE FOR' not in line:
                # Save previous contest
                if current_contest and current_contest.get('candidates'):
                    results['contests'].append(current_contest)
                
                # Start new contest
                current_contest = {
                    'name': line,
                    'party': self.detect_party(line),
                    'candidates': []
                }
            
            # Detect "VOTE FOR NO MORE THAN X"
            elif 'VOTE FOR NO MORE THAN' in line:
                if current_contest:
                    match = re.search(r'VOTE FOR NO MORE THAN (\d+)', line)
                    if match:
                        current_contest['seats'] = int(match.group(1))
            
            # Detect candidate results
            elif current_contest and '. . .' in line:
                # Pattern: Candidate Name (PARTY). . . . . votes percent
                parts = line.split('. . .')
                if len(parts) >= 2:
                    # Left side: candidate name and party
                    name_part = parts[0].strip()
                    
                    # Right side: votes and percent
                    vote_part = parts[-1].strip()
                    vote_match = re.findall(r'\d+', vote_part)
                    
                    # Extract party from name (appears in parentheses)
                    party_match = re.search(r'\(([^)]+)\)', name_part)
                    candidate_party = party_match.group(1) if party_match else 'UNK'
                    
                    # Remove party from name
                    candidate_name = re.sub(r'\s*\([^)]+\)\s*', '', name_part).strip()
                    
                    if vote_match:
                        votes = int(vote_match[0])
                        percent = float(vote_match[1]) if len(vote_match) > 1 else 0.0
                        
                        current_contest['candidates'].append({
                            'name': candidate_name,
                            'party': candidate_party,
                            'votes': votes,
                            'percent': percent
                        })
        
        # Add the last contest
        if current_contest and current_contest.get('candidates'):
            results['contests'].append(current_contest)
        
        return results
    
    def scrape(self) -> Dict:
        """Scrape election results from Integra platform
        
        Returns:
            Dictionary with scraped results
        """
        print(f"Scraping {self.county_name} from Integra platform...")
        print(f"URL: {self.text_url}")
        
        try:
            # Fetch the plain text results
            response = requests.get(self.text_url, timeout=30)
            response.raise_for_status()
            
            # Parse the results
            results = self.parse_text_results(response.text)
            
            print(f"✓ Successfully scraped {len(results['contests'])} contests")
            return results
            
        except requests.RequestException as e:
            print(f"✗ Error fetching results: {e}")
            return {
                'error': str(e),
                'county': self.county_name,
                'scraped_at': datetime.now().isoformat()
            }
    
    def save_results(self, results: Dict, output_dir: str = '.'):
        """Save results to JSON file
        
        Args:
            results: Results dictionary
            output_dir: Directory to save file
        """
        filename = f"{output_dir}/{self.county_key.lower()}_results.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Saved results to {filename}")

def scrape_all_integra_counties(output_dir: str = '.'):
    """Scrape all Integra counties
    
    Args:
        output_dir: Directory to save results files
    """
    print("=" * 60)
    print("Integra Election Results Scraper")
    print("Illinois Primary Election - March 17, 2026")
    print("=" * 60)
    print()
    
    counties = list(IntegraElectionScraper.COUNTIES.keys())
    print(f"Scraping {len(counties)} counties: {', '.join(counties)}")
    print()
    
    for county_key in counties:
        scraper = IntegraElectionScraper(county_key)
        results = scraper.scrape()
        scraper.save_results(results, output_dir)
        print()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Scrape specific county
        county_key = sys.argv[1]
        
        # Handle case-insensitive input
        county_map = {k.lower(): k for k in IntegraElectionScraper.COUNTIES.keys()}
        county_key_proper = county_map.get(county_key.lower())
        
        if not county_key_proper:
            print(f"Error: Unknown county '{county_key}'")
            print(f"Valid options: {', '.join(IntegraElectionScraper.COUNTIES.keys())}")
            sys.exit(1)
        
        scraper = IntegraElectionScraper(county_key_proper)
        results = scraper.scrape()
        scraper.save_results(results)
    else:
        # Scrape all counties
        scrape_all_integra_counties()

if __name__ == '__main__':
    main()
