#!/usr/bin/env python3
"""
Iroquois County Election Results Scraper

Scrapes primary election results from Iroquois County's custom web platform.
Supports multiple formats: PDF, HTML, and text-based results.

County: Iroquois County, Illinois (~20,000 voters)
Location: East-central Illinois (Watseka, Gilman, Onarga)
Platform: Custom web-based system at iroquoiscountyil.gov/elections

Usage:
    # With direct URL to results page or document
    python iroquois_county_scraper.py --url "https://iroquoiscountyil.gov/elections/results/2026-primary.pdf"
    
    # Without URL (shows instructions)
    python iroquois_county_scraper.py
"""

import requests
import json
import re
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Note: pdfplumber not installed. PDF parsing will not be available.")
    print("Install with: pip install pdfplumber")


class IroquoisCountyScraper:
    """Scraper for Iroquois County election results."""
    
    def __init__(self, url: Optional[str] = None, election_date: str = "2026-03-17"):
        """
        Initialize the scraper.
        
        Args:
            url: Direct URL to results page or document
            election_date: Election date in YYYY-MM-DD format
        """
        self.url = url
        self.election_date = election_date
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape(self) -> Dict:
        """
        Scrape election results from Iroquois County.
        
        Returns:
            Dictionary containing election results
        """
        if not self.url:
            return self._show_instructions()
        
        # Determine format based on URL
        if self.url.lower().endswith('.pdf'):
            return self._scrape_pdf()
        else:
            return self._scrape_html()
    
    def _show_instructions(self) -> Dict:
        """Show instructions when no URL provided."""
        instructions = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   IROQUOIS COUNTY SCRAPER - SETUP REQUIRED                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

To use this scraper, you need to provide the URL to Iroquois County's results.

STEP 1: Find the Results
────────────────────────────────────────────────────────────────────────────────
Visit: https://iroquoiscountyil.gov/elections

Look for:
  • "Election Results" link
  • "2026 Primary Election Results"
  • Results page or downloadable document

STEP 2: Get the URL
────────────────────────────────────────────────────────────────────────────────
Right-click the results link and select "Copy link address"

The URL might look like:
  • https://iroquoiscountyil.gov/elections/results/2026-primary.html
  • https://iroquoiscountyil.gov/wp-content/uploads/2026/03/results.pdf
  • Or similar format

STEP 3: Run the Scraper
────────────────────────────────────────────────────────────────────────────────
python iroquois_county_scraper.py --url "YOUR_URL_HERE"

EXAMPLE WITH HISTORICAL DATA:
────────────────────────────────────────────────────────────────────────────────
Test with 2024 or earlier results to verify scraper works:

1. Visit iroquoiscountyil.gov/elections
2. Find 2024 Primary results
3. Copy URL
4. Run: python iroquois_county_scraper.py --url "URL" --date 2024-03-19

This tests the scraper before election day!

SUPPORTED FORMATS:
────────────────────────────────────────────────────────────────────────────────
  ✓ HTML results pages
  ✓ PDF documents (requires pdfplumber)
  ✓ Table-based layouts
  ✓ Text-based reports

NEED HELP?
────────────────────────────────────────────────────────────────────────────────
See IROQUOIS_COUNTY_SETUP.md for detailed instructions and troubleshooting.

        """
        print(instructions)
        return {
            "error": "No URL provided",
            "instructions": "See output above for setup instructions"
        }
    
    def _scrape_html(self) -> Dict:
        """
        Scrape results from HTML page.
        
        Returns:
            Dictionary containing election results
        """
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize results structure
            results = {
                "county": "Iroquois",
                "election_date": self.election_date,
                "source": "Iroquois County Elections Website",
                "url": self.url,
                "scraped_at": datetime.now().isoformat(),
                "metadata": {},
                "contests": []
            }
            
            # Try to extract metadata
            results["metadata"] = self._extract_html_metadata(soup)
            
            # Try to parse contests from tables
            contests = self._parse_html_contests(soup)
            results["contests"] = contests
            
            return results
            
        except requests.RequestException as e:
            return {
                "error": f"Failed to fetch HTML: {str(e)}",
                "url": self.url
            }
        except Exception as e:
            return {
                "error": f"Failed to parse HTML: {str(e)}",
                "url": self.url
            }
    
    def _scrape_pdf(self) -> Dict:
        """
        Scrape results from PDF document.
        
        Returns:
            Dictionary containing election results
        """
        if not PDF_SUPPORT:
            return {
                "error": "PDF support not available. Install pdfplumber: pip install pdfplumber",
                "url": self.url
            }
        
        try:
            # Download PDF
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            
            # Save temporarily
            pdf_path = "/tmp/iroquois_results.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            # Extract text
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            
            # Initialize results
            results = {
                "county": "Iroquois",
                "election_date": self.election_date,
                "source": "Iroquois County Elections PDF",
                "pdf_url": self.url,
                "scraped_at": datetime.now().isoformat(),
                "metadata": {},
                "contests": []
            }
            
            # Parse contests from text
            results["metadata"] = self._extract_text_metadata(text)
            results["contests"] = self._parse_text_contests(text)
            
            return results
            
        except requests.RequestException as e:
            return {
                "error": f"Failed to download PDF: {str(e)}",
                "url": self.url
            }
        except Exception as e:
            return {
                "error": f"Failed to parse PDF: {str(e)}",
                "url": self.url
            }
    
    def _extract_html_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from HTML page."""
        metadata = {}
        text = soup.get_text()
        
        # Registered voters
        for pattern in [r'Registered Voters[:\s]+(\d+(?:,\d+)*)', r'Total Registered[:\s]+(\d+(?:,\d+)*)']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["registered_voters"] = int(match.group(1).replace(',', ''))
                break
        
        # Ballots cast
        for pattern in [r'Ballots Cast[:\s]+(\d+(?:,\d+)*)', r'Total Ballots[:\s]+(\d+(?:,\d+)*)']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["ballots_cast"] = int(match.group(1).replace(',', ''))
                break
        
        # Precincts
        match = re.search(r'Precincts Reporting[:\s]+(\d+)\s*(?:of|/)?\s*(\d+)', text, re.IGNORECASE)
        if match:
            metadata["precincts_reporting"] = int(match.group(1))
            metadata["total_precincts"] = int(match.group(2))
        
        # Turnout
        match = re.search(r'Turnout[:\s]+(\d+\.?\d*)%', text, re.IGNORECASE)
        if match:
            metadata["turnout_percent"] = float(match.group(1))
        
        return metadata
    
    def _parse_html_contests(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse contests from HTML tables."""
        contests = []
        
        # Look for tables containing results
        tables = soup.find_all('table')
        
        for table in tables:
            # Try to identify contest name
            contest_name = None
            
            # Check for caption or preceding heading
            caption = table.find('caption')
            if caption:
                contest_name = caption.get_text().strip()
            
            if not contest_name:
                prev = table.find_previous(['h1', 'h2', 'h3', 'h4', 'h5'])
                if prev:
                    contest_name = prev.get_text().strip()
            
            if not contest_name:
                continue
            
            # Parse candidates from table rows
            candidates = []
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    candidate_text = cells[0].get_text().strip()
                    votes_text = cells[-1].get_text().strip()
                    
                    # Skip header rows
                    if 'candidate' in candidate_text.lower() or 'name' in candidate_text.lower():
                        continue
                    
                    # Try to parse votes
                    votes_match = re.search(r'(\d+(?:,\d+)*)', votes_text.replace(',', ''))
                    if votes_match:
                        votes = int(votes_match.group(1))
                        
                        # Calculate percentage if available
                        percent = 0.0
                        percent_match = re.search(r'(\d+\.?\d*)%', votes_text)
                        if percent_match:
                            percent = float(percent_match.group(1))
                        
                        candidates.append({
                            "name": candidate_text,
                            "votes": votes,
                            "percent": percent
                        })
            
            if candidates:
                party = self._detect_party(contest_name, candidates)
                
                contests.append({
                    "name": contest_name,
                    "party": party,
                    "candidates": candidates
                })
        
        return contests
    
    def _extract_text_metadata(self, text: str) -> Dict:
        """Extract metadata from PDF/text."""
        metadata = {}
        
        # Registered voters
        match = re.search(r'Registered Voters[:\s]+(\d+(?:,\d+)*)', text, re.IGNORECASE)
        if match:
            metadata["registered_voters"] = int(match.group(1).replace(',', ''))
        
        # Ballots cast
        match = re.search(r'Ballots Cast[:\s]+(\d+(?:,\d+)*)', text, re.IGNORECASE)
        if match:
            metadata["ballots_cast"] = int(match.group(1).replace(',', ''))
        
        # Precincts
        match = re.search(r'Precincts Reporting[:\s]+(\d+)\s*(?:of|/)?\s*(\d+)', text, re.IGNORECASE)
        if match:
            metadata["precincts_reporting"] = int(match.group(1))
            metadata["total_precincts"] = int(match.group(2))
        
        # Turnout
        match = re.search(r'Turnout[:\s]+(\d+\.?\d*)%', text, re.IGNORECASE)
        if match:
            metadata["turnout_percent"] = float(match.group(1))
        
        return metadata
    
    def _parse_text_contests(self, text: str) -> List[Dict]:
        """Parse contests from plain text."""
        contests = []
        lines = text.split('\n')
        
        current_contest = None
        current_candidates = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                continue
            
            # Skip header/metadata lines
            if any(x in stripped for x in ['ELECTION', 'RUN DATE', 'RUN TIME', 'SUMMARY', 'PRECINCTS', 'REGISTERED', 'BALLOTS', 'TURNOUT', 'VOTES PERCENT']):
                continue
            
            # Check for contest header
            # Contest headers are typically all caps or title case
            if stripped.isupper() or (len(stripped) > 10 and not any(c.isdigit() for c in stripped)):
                # Save previous contest
                if current_contest and current_candidates:
                    party = self._detect_party(current_contest, current_candidates)
                    contests.append({
                        "name": current_contest,
                        "party": party,
                        "candidates": current_candidates
                    })
                
                # Start new contest
                current_contest = stripped
                current_candidates = []
                continue
            
            # Check for candidate line (has numbers)
            if re.search(r'\d+', stripped):
                # Try to parse: Name ... votes percent
                match = re.search(r'^(.+?)\s+(\d+(?:,\d+)*)\s+(\d+\.?\d*)%?', stripped)
                if match:
                    candidate_name = match.group(1).strip()
                    votes = int(match.group(2).replace(',', ''))
                    percent = float(match.group(3))
                    
                    # Skip totals and "No Candidate" with 0 votes
                    if 'total' in candidate_name.lower() or 'cast' in candidate_name.lower():
                        continue
                    if 'No Candidate' in candidate_name and votes == 0:
                        continue
                    
                    current_candidates.append({
                        "name": candidate_name,
                        "votes": votes,
                        "percent": percent
                    })
        
        # Save last contest
        if current_contest and current_candidates:
            party = self._detect_party(current_contest, current_candidates)
            contests.append({
                "name": current_contest,
                "party": party,
                "candidates": current_candidates
            })
        
        return contests
    
    def _detect_party(self, contest_name: str, candidates: List[Dict]) -> str:
        """
        Detect party affiliation from contest name or candidate names.
        
        Args:
            contest_name: Contest name
            candidates: List of candidate dictionaries
            
        Returns:
            Party name: "Republican", "Democratic", or "Non-Partisan"
        """
        name_upper = contest_name.upper()
        
        # Check contest name for party indicators
        if 'REPUBLICAN' in name_upper or '(REP)' in name_upper or ' - REP' in name_upper:
            return "Republican"
        elif 'DEMOCRATIC' in name_upper or 'DEMOCRAT' in name_upper or '(DEM)' in name_upper or ' - DEM' in name_upper:
            return "Democratic"
        
        # Check first candidate for party indicator
        if candidates:
            first_cand = candidates[0]['name'].upper()
            if '(REP)' in first_cand or 'REPUBLICAN' in first_cand:
                return "Republican"
            elif '(DEM)' in first_cand or 'DEMOCRAT' in first_cand or 'DEMOCRATIC' in first_cand:
                return "Democratic"
        
        # Default to non-partisan
        return "Non-Partisan"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Scrape Iroquois County election results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # With results URL
  %(prog)s --url "https://iroquoiscountyil.gov/elections/results/2026-primary.pdf"
  
  # Test with historical data
  %(prog)s --url "https://iroquoiscountyil.gov/elections/results/2024-primary.html" --date 2024-03-19
  
  # Save to specific file
  %(prog)s --url "URL" --output iroquois_results.json
        """
    )
    
    parser.add_argument(
        '--url',
        help='Direct URL to results page or document'
    )
    
    parser.add_argument(
        '--date',
        default='2026-03-17',
        help='Election date (YYYY-MM-DD, default: 2026-03-17)'
    )
    
    parser.add_argument(
        '--output',
        help='Output JSON file (default: iroquois_results.json)'
    )
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = IroquoisCountyScraper(
        url=args.url,
        election_date=args.date
    )
    
    # Scrape results
    print("Scraping Iroquois County election results...")
    if args.url:
        print(f"URL: {args.url}")
    print()
    
    results = scraper.scrape()
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        output_file = "iroquois_results.json"
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    if "error" in results:
        print(f"Error: {results['error']}")
        if "instructions" not in results:
            print(f"Check {output_file} for details")
    else:
        print(f"✓ Successfully scraped Iroquois County results")
        print(f"  Contests found: {len(results.get('contests', []))}")
        if results.get('metadata'):
            if 'ballots_cast' in results['metadata']:
                print(f"  Ballots cast: {results['metadata']['ballots_cast']:,}")
            if 'precincts_reporting' in results['metadata']:
                print(f"  Precincts reporting: {results['metadata']['precincts_reporting']}/{results['metadata'].get('total_precincts', '?')}")
        print(f"  Saved to: {output_file}")


if __name__ == "__main__":
    main()
