"""
pollresults.net Multi-County Scraper
Scrapes election results from pollresults.net (Liberty Systems/CSE Software) platform
Supports 12 Illinois counties: Whiteside, Lee, Ogle, Carroll, Putnam, Vermilion, 
Tazewell, Stephenson, Boone, Bureau, Livingston, Ford, Mercer
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
from datetime import datetime
from typing import Dict, List, Optional
import time
import sys


class PollResultsScraper:
    """Scraper for pollresults.net platform"""
    
    def __init__(self, county_name: str, base_url: str, use_selenium: bool = False):
        """
        Initialize the scraper
        
        Args:
            county_name: Name of the county
            base_url: Base URL (e.g., "https://il-whiteside.pollresults.net")
            use_selenium: Whether to use Selenium for JavaScript-heavy sites
        """
        self.county_name = county_name
        self.base_url = base_url.rstrip('/')
        self.use_selenium = use_selenium
        self.driver = None
        
    def init_selenium(self):
        """Initialize Selenium WebDriver with headless Chrome"""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        self.driver = webdriver.Chrome(options=options)
        
    def close_selenium(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def try_json_api(self) -> Optional[Dict]:
        """
        Try to fetch results via JSON API endpoints
        pollresults.net may expose JSON data at common paths
        """
        # Common JSON endpoint patterns to try
        json_endpoints = [
            '/api/results',
            '/api/election',
            '/data/results.json',
            '/json/summary.json',
            '/results.json'
        ]
        
        for endpoint in json_endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Found JSON API at {endpoint}")
                    return data
            except:
                continue
        
        return None
    
    def scrape_with_selenium(self) -> List[Dict]:
        """
        Scrape results using Selenium for JavaScript-rendered content
        
        Returns:
            List of contest dictionaries
        """
        if not self.driver:
            self.init_selenium()
        
        print(f"Loading page: {self.base_url}")
        self.driver.get(self.base_url)
        
        # Wait for the page to load
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait a bit more for Angular to render
            time.sleep(3)
            
        except TimeoutException:
            print(f"❌ Timeout waiting for page to load")
            return []
        
        # Try to find contests - pollresults.net typically has a list structure
        contests = []
        
        # Look for common element patterns
        # These are guesses based on typical election result sites
        contest_selectors = [
            '.race',
            '.contest',
            '[ng-repeat*="race"]',
            '[ng-repeat*="contest"]',
            '.election-race',
            'div[class*="race"]',
            'div[class*="contest"]'
        ]
        
        for selector in contest_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    contests = self._parse_contest_elements(elements)
                    if contests:
                        break
            except:
                continue
        
        if not contests:
            # Fallback: parse the entire page HTML
            print("⚠️  No structured contests found, attempting full page parse...")
            page_source = self.driver.page_source
            contests = self._parse_html_fallback(page_source)
        
        return contests
    
    def _parse_contest_elements(self, elements) -> List[Dict]:
        """Parse contest elements from Selenium"""
        contests = []
        
        for element in elements:
            try:
                contest_data = {
                    'contest_name': '',
                    'candidates': [],
                    'precincts_reporting': 0,
                    'total_precincts': 0
                }
                
                # Try to extract contest name
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, '.race-name, .contest-name, h3, h4')
                    contest_data['contest_name'] = name_elem.text.strip()
                except:
                    pass
                
                # Try to extract candidates
                candidate_selectors = ['.candidate', '[class*="candidate"]', 'tr', 'li']
                for selector in candidate_selectors:
                    try:
                        candidate_elems = element.find_elements(By.CSS_SELECTOR, selector)
                        if candidate_elems:
                            for cand in candidate_elems:
                                text = cand.text.strip()
                                if text and len(text) > 3:  # Avoid empty elements
                                    # Try to parse candidate info
                                    # Format is usually: "Name - Votes (Percentage)"
                                    contest_data['candidates'].append({
                                        'raw_text': text
                                    })
                            if contest_data['candidates']:
                                break
                    except:
                        continue
                
                if contest_data['contest_name']:
                    contests.append(contest_data)
                    
            except Exception as e:
                continue
        
        return contests
    
    def _parse_html_fallback(self, html: str) -> List[Dict]:
        """
        Fallback HTML parsing when structured elements aren't found
        This is a basic implementation - may need refinement based on actual HTML structure
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract any text content that looks like election data
        # This is a very basic fallback
        text_content = soup.get_text()
        
        return [{
            'note': 'Fallback parsing - manual review needed',
            'raw_content': text_content[:1000]  # First 1000 chars
        }]
    
    def detect_contest_party(self, contest_name: str) -> str:
        """Detect party from contest name"""
        name_upper = contest_name.upper()
        
        if 'DEMOCRATIC' in name_upper or 'DEM ' in name_upper:
            return "Democratic"
        elif 'REPUBLICAN' in name_upper or 'REP ' in name_upper:
            return "Republican"
        
        return "Non-Partisan"
    
    def scrape_all_contests(self) -> List[Dict]:
        """
        Main scraping method - tries JSON API first, then falls back to Selenium
        
        Returns:
            List of contest dictionaries
        """
        print(f"\n{'='*60}")
        print(f"Scraping {self.county_name} County")
        print(f"URL: {self.base_url}")
        print(f"{'='*60}\n")
        
        # Try JSON API first (faster and cleaner)
        print("Attempting JSON API access...")
        json_data = self.try_json_api()
        
        if json_data:
            print("✅ Successfully retrieved data via JSON API")
            # Parse JSON data structure
            # This will need to be implemented based on actual API structure
            contests = self._parse_json_response(json_data)
            return contests
        
        print("⚠️  No JSON API found, falling back to Selenium scraping...")
        
        # Fallback to Selenium
        try:
            contests = self.scrape_with_selenium()
            return contests
        finally:
            self.close_selenium()
    
    def _parse_json_response(self, data: Dict) -> List[Dict]:
        """
        Parse JSON response from API
        This will need to be implemented based on actual API structure
        """
        # Placeholder - needs actual API structure
        contests = []
        
        # Common JSON structures to look for
        if 'races' in data:
            contests = data['races']
        elif 'contests' in data:
            contests = data['contests']
        elif 'results' in data:
            contests = data['results']
        
        return contests
    
    def save_to_json(self, contests: List[Dict], filename: str):
        """Save contests to JSON file"""
        # Organize by party
        organized = {
            "Democratic": [],
            "Republican": [],
            "Non-Partisan": []
        }
        
        for contest in contests:
            party = self.detect_contest_party(contest.get('contest_name', ''))
            contest['party'] = party
            organized[party].append(contest)
        
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
        
        print(f"\n✅ Results saved to {filename}")
        print(f"   - Democratic: {output['summary']['democratic_contests']} contests")
        print(f"   - Republican: {output['summary']['republican_contests']} contests")
        print(f"   - Non-Partisan: {output['summary']['non_partisan_contests']} contests")


def scrape_pollresults_county(county_name: str, config_path: str = 'config.json'):
    """
    Scrape election results for a specific pollresults.net county
    
    Args:
        county_name: Name of the county to scrape
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
    
    if county_config.get('platform') != 'pollresults':
        print(f"❌ County '{county_name}' does not use pollresults.net platform")
        return None
    
    # Initialize scraper
    scraper = PollResultsScraper(
        county_name=county_name,
        base_url=county_config['base_url']
    )
    
    # Scrape contests
    contests = scraper.scrape_all_contests()
    
    # Save to JSON
    if contests:
        filename = f"{county_name.lower()}_results.json"
        scraper.save_to_json(contests, filename)
    
    return contests


def scrape_all_pollresults_counties(config_path: str = 'config.json'):
    """
    Scrape all counties that use pollresults.net platform
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary mapping county names to their results
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Find all pollresults counties
    pollresults_counties = []
    for county_name, county_config in config['counties'].items():
        if county_config.get('platform') == 'pollresults':
            pollresults_counties.append(county_name)
    
    print(f"\n{'='*60}")
    print(f"Found {len(pollresults_counties)} counties using pollresults.net:")
    print(f"{'='*60}")
    for county in sorted(pollresults_counties):
        print(f"  - {county}")
    print()
    
    # Scrape each county
    all_results = {}
    for county_name in sorted(pollresults_counties):
        try:
            results = scrape_pollresults_county(county_name, config_path)
            if results:
                all_results[county_name] = results
            print()  # Blank line between counties
        except Exception as e:
            print(f"❌ Error scraping {county_name}: {e}\n")
            continue
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Scraping Complete")
    print(f"{'='*60}")
    print(f"Successfully scraped {len(all_results)} of {len(pollresults_counties)} counties")
    for county, results in sorted(all_results.items()):
        print(f"  ✅ {county}: {len(results)} contests")
    
    return all_results


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║     pollresults.net Scraper for Illinois Elections        ║
║                                                            ║
║  Covers 12 counties: Whiteside, Lee, Ogle, Carroll,       ║
║  Putnam, Vermilion, Tazewell, Stephenson, Boone,          ║
║  Bureau, Livingston, Ford, Mercer                          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Scrape specific county
        county_name = sys.argv[1]
        scrape_pollresults_county(county_name)
    else:
        # Scrape all pollresults counties
        scrape_all_pollresults_counties()
