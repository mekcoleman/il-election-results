#!/usr/bin/env python3
"""
Woodford County Election Results Scraper

Scrapes primary election results from Woodford County's custom web platform.
Supports both HTML pages and PDF documents.

County: Woodford County, Illinois (~25,000 voters)
Location: Central Illinois (Eureka, El Paso, Metamora)
Platform: Custom web-based system at woodfordcountyelections.com

Usage:
    # With direct URL to results page or PDF
    python woodford_county_scraper.py --url "https://woodfordcountyelections.com/results/2026-primary.html"
    
    # Without URL (shows instructions)
    python woodford_county_scraper.py
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


class WoodfordCountyScraper:
    """Scraper for Woodford County election results."""
    
    def __init__(self, url: Optional[str] = None, election_date: str = "2026-03-17"):
        """
        Initialize the scraper.
        
        Args:
            url: Direct URL to results page or PDF
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
        Scrape election results from Woodford County.
        
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
║                    WOODFORD COUNTY SCRAPER - SETUP REQUIRED                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

To use this scraper, you need to provide the URL to Woodford County's results.

STEP 1: Find the Results
────────────────────────────────────────────────────────────────────────────────
Visit: https://woodfordcountyelections.com

Look for:
  • "Election Results" link
  • "2026 Primary Election Results"
  • Results page or downloadable document

STEP 2: Get the URL
────────────────────────────────────────────────────────────────────────────────
Right-click the results link and select "Copy link address"

The URL might look like:
  • https://woodfordcountyelections.com/results/2026-primary.html
  • https://woodfordcountyelections.com/wp-content/uploads/2026/03/results.pdf
  • Or similar format

STEP 3: Run the Scraper
────────────────────────────────────────────────────────────────────────────────
python woodford_county_scraper.py --url "YOUR_URL_HERE"

EXAMPLE WITH 2024 DATA:
────────────────────────────────────────────────────────────────────────────────
Test with 2024 Primary results to verify scraper works:

1. Visit woodfordcountyelections.com
2. Find 2024 Primary results
3. Copy URL
4. Run: python woodford_county_scraper.py --url "URL" --date 2024-03-19

This tests the scraper before election day!

SUPPORTED FORMATS:
────────────────────────────────────────────────────────────────────────────────
  ✓ HTML results pages
  ✓ PDF documents (requires pdfplumber)
  ✓ Table-based layouts
  ✓ Text-based reports

NEED HELP?
────────────────────────────────────────────────────────────────────────────────
See WOODFORD_COUNTY_SETUP.md for detailed instructions and troubleshooting.

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
                "county": "Woodford",
                "election_date": self.election_date,
                "source": "Woodford County Elections Website",
                "url": self.url,
                "scraped_at": datetime.now().isoformat(),
                "metadata": {},
                "contests": []
            }
            
            # Try to extract metadata from page
            results["metadata"] = self._extract_html_metadata(soup)
            
            # Try to parse contests from tables
            contests = self._parse_html_contests(soup)
            results["contests"] = contests
            
            # If no contests found, try alternative parsing
            if not contests:
                contests = self._parse_html_alternative(soup)
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
            pdf_path = "/tmp/woodford_results.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            # Extract text
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            
            # Initialize results
            results = {
                "county": "Woodford",
                "election_date": self.election_date,
                "source": "Woodford County Elections PDF",
                "pdf_url": self.url,
                "scraped_at": datetime.now().isoformat(),
                "metadata": {},
                "contests": []
            }
            
            # Parse contests from text
            results["metadata"] = self._extract_pdf_metadata(text)
            results["contests"] = self._parse_pdf_contests(text)
            
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
        
        # Look for common metadata patterns
        # Registered voters
        for pattern in [r'Registered Voters[:\s]+(\d+)', r'Total Registered[:\s]+(\d+)']:
            match = re.search(pattern, soup.get_text(), re.IGNORECASE)
            if match:
                metadata["registered_voters"] = int(match.group(1))
                break
        
        # Ballots cast
        for pattern in [r'Ballots Cast[:\s]+(\d+)', r'Total Ballots[:\s]+(\d+)']:
            match = re.search(pattern, soup.get_text(), re.IGNORECASE)
            if match:
                metadata["ballots_cast"] = int(match.group(1))
                break
        
        # Precincts
        for pattern in [r'Precincts Reporting[:\s]+(\d+)\s*(?:of|/)?\s*(\d+)', r'(\d+)\s*of\s*(\d+)\s*Precincts']:
            match = re.search(pattern, soup.get_text(), re.IGNORECASE)
            if match:
                metadata["precincts_reporting"] = int(match.group(1))
                metadata["total_precincts"] = int(match.group(2))
                break
        
        return metadata
    
    def _parse_html_contests(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse contests from HTML tables."""
        contests = []
        
        # Look for tables containing results
        tables = soup.find_all('table')
        
        for table in tables:
            # Try to identify contest name from headers or preceding text
            contest_name = None
            
            # Check for header row or caption
            caption = table.find('caption')
            if caption:
                contest_name = caption.get_text().strip()
            
            # Check preceding heading
            if not contest_name:
                prev = table.find_previous(['h1', 'h2', 'h3', 'h4'])
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
                    # Try to extract candidate name and votes
                    candidate_text = cells[0].get_text().strip()
                    votes_text = cells[-1].get_text().strip()
                    
                    # Skip header rows
                    if 'candidate' in candidate_text.lower() or 'name' in candidate_text.lower():
                        continue
                    
                    # Try to parse votes
                    votes_match = re.search(r'(\d+)', votes_text.replace(',', ''))
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
                # Detect party from contest name
                party = self._detect_party(contest_name)
                
                contests.append({
                    "name": contest_name,
                    "party": party,
                    "candidates": candidates
                })
        
        return contests
    
    def _parse_html_alternative(self, soup: BeautifulSoup) -> List[Dict]:
        """Alternative HTML parsing for non-table layouts."""
        contests = []
        text = soup.get_text()
        
        # Try to parse from plain text structure
        # This would need to be adapted based on actual format
        # For now, return empty and provide clear error
        
        return contests
    
    def _extract_pdf_metadata(self, text: str) -> Dict:
        """
        Extract metadata from Woodford County text format.
        
        Format:
           PRECINCTS COUNTED (OF 37) .  .  .  .  .        37  100.00
           REGISTERED VOTERS - TOTAL .  .  .  .  .    27,402
           BALLOTS CAST - TOTAL.  .  .  .  .  .  .     5,060
           VOTER TURNOUT - TOTAL  .  .  .  .  .  .             18.47
        """
        metadata = {}
        
        # Registered voters
        match = re.search(r'REGISTERED VOTERS - TOTAL\.?\s+\..*?(\d+(?:,\d+)*)', text)
        if match:
            metadata["registered_voters"] = int(match.group(1).replace(',', ''))
        
        # Ballots cast (note: field name has period: "BALLOTS CAST - TOTAL.")
        match = re.search(r'BALLOTS CAST - TOTAL\.?\s+\..*?(\d+(?:,\d+)*)', text)
        if match:
            metadata["ballots_cast"] = int(match.group(1).replace(',', ''))
        
        # Precincts - format: "PRECINCTS COUNTED (OF 37) . . . 37 100.00"
        match = re.search(r'PRECINCTS COUNTED \(OF (\d+)\)\s+\..*?(\d+)\s+', text)
        if match:
            metadata["total_precincts"] = int(match.group(1))
            metadata["precincts_reporting"] = int(match.group(2))
        
        # Turnout
        match = re.search(r'VOTER TURNOUT - TOTAL\.?\s+\..*?(\d+\.?\d*)', text)
        if match:
            metadata["turnout_percent"] = float(match.group(1))
        
        return metadata
    
    def _parse_pdf_contests(self, text: str) -> List[Dict]:
        """
        Parse contests from Woodford County text format.
        
        Format structure by indentation:
        - Contest headers: 10 spaces, no dots, not "(VOTE FOR)"
        - (VOTE FOR) lines: 10 spaces, contains "(VOTE FOR)"  
        - Candidate lines: 11+ spaces, contains dots
        
        Example:
          CONTEST NAME                    (10 spaces)
          (VOTE FOR)  1                   (10 spaces)
           Candidate Name .  .  . votes%  (11+ spaces)
        """
        contests = []
        lines = text.split('\n')
        
        current_contest = None
        current_vote_for = 1
        current_candidates = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                continue
            
            # Skip header lines (SUMMARY REPORT, RUN DATE, etc.)
            if any(x in stripped for x in ['SUMMARY REPORT', 'RUN DATE', 'RUN TIME', 'VOTES PERCENT']):
                continue
            
            # Skip metadata lines (heavily indented with dots, but no candidate name)
            if 'PRECINCTS COUNTED' in stripped or 'REGISTERED VOTERS' in stripped or 'BALLOTS CAST' in stripped or 'VOTER TURNOUT' in stripped:
                continue
            
            # Check for (VOTE FOR) line
            if '(VOTE FOR)' in stripped:
                vote_match = re.search(r'\(VOTE FOR\)\s+(\d+)', stripped, re.IGNORECASE)
                if vote_match:
                    current_vote_for = int(vote_match.group(1))
                continue
            
            # Candidate lines: 11+ leading spaces AND contains dots
            if line.startswith('           ') and '.' in line:
                # Parse candidate line using regex to separate name from alignment dots
                # Format: "           Name (PARTY)  .  .  .  .       votes  percent"
                # The key is that alignment dots have spaces between them
                
                match = re.search(r'^(\s+)(.+?)\s+\.(\s+\.)+\s+(.+)$', line)
                if not match:
                    continue
                
                candidate_name = match.group(2).strip()
                numbers_part = match.group(4).strip()
                
                if not candidate_name or 'WRITE-IN' in candidate_name:
                    continue
                
                # Extract votes and percent from numbers part
                # Format: "votes  percent" or just "votes"
                numbers = re.findall(r'(\d+(?:,\d+)*)', numbers_part)
                
                if numbers:
                    votes = int(numbers[0].replace(',', ''))
                    
                    # Try to get percentage (last number with potential decimal)
                    percent_match = re.search(r'(\d+\.?\d*)\s*$', numbers_part)
                    if percent_match:
                        percent = float(percent_match.group(1))
                    else:
                        percent = 0.0
                else:
                    continue
                
                # Skip "No Candidate" with 0 votes
                if 'No Candidate' in candidate_name and votes == 0:
                    continue
                
                current_candidates.append({
                    "name": candidate_name,
                    "votes": votes,
                    "percent": percent
                })
                continue
            
            # Contest header: 10 spaces (line.startswith('          ') but NOT 11+)
            # May have dots for abbreviations (TWP., HSD., etc.) but not alignment dots
            if line.startswith('          ') and not line.startswith('           '):
                # Check if this looks like a contest header (not a candidate line)
                # Candidate lines have many dots with spaces: ".  .  .  ."
                # Contest headers may have abbreviation dots but not alignment dots
                if '  .  ' not in line:  # No alignment dots
                    # Save previous contest
                    if current_contest and current_candidates:
                        party = self._detect_party_from_candidates(current_candidates, current_contest)
                        contests.append({
                            "name": current_contest,
                            "party": party,
                            "vote_for": current_vote_for,
                            "candidates": current_candidates
                        })
                    
                    # Start new contest
                    current_contest = stripped
                    current_candidates = []
                    current_vote_for = 1
                    continue
        
        # Save last contest
        if current_contest and current_candidates:
            party = self._detect_party_from_candidates(current_candidates, current_contest)
            contests.append({
                "name": current_contest,
                "party": party,
                "vote_for": current_vote_for,
                "candidates": current_candidates
            })
        
        return contests
    
    def _detect_party(self, contest_name: str) -> str:
        """
        Detect party affiliation from contest name.
        
        Args:
            contest_name: Contest name
            
        Returns:
            Party name: "Republican", "Democratic", or "Non-Partisan"
        """
        name_upper = contest_name.upper()
        
        # Check for explicit party indicators
        if 'REPUBLICAN' in name_upper or '(REP)' in name_upper or ' - REP' in name_upper:
            return "Republican"
        elif 'DEMOCRATIC' in name_upper or 'DEMOCRAT' in name_upper or '(DEM)' in name_upper or ' - DEM' in name_upper:
            return "Democratic"
        
        # Default to non-partisan for local races
        return "Non-Partisan"
    
    def _detect_party_from_candidates(self, candidates: List[Dict], contest_name: str) -> str:
        """
        Detect party affiliation from candidate names or contest name.
        
        For Woodford format, party appears in candidate names: "Name (REP)", "Name (DEM)", etc.
        
        Args:
            candidates: List of candidate dictionaries
            contest_name: Contest name
            
        Returns:
            Party name: "Republican", "Democratic", or "Non-Partisan"
        """
        if not candidates:
            return self._detect_party(contest_name)
        
        # Check first candidate for party indicator
        first_candidate = candidates[0]['name']
        
        if '(REP)' in first_candidate:
            return "Republican"
        elif '(DEM)' in first_candidate:
            return "Democratic"
        elif '(IND)' in first_candidate or '(PEO)' in first_candidate or '(PPL)' in first_candidate or '(CIT)' in first_candidate:
            return "Non-Partisan"
        
        # Fallback to contest name check
        return self._detect_party(contest_name)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Scrape Woodford County election results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # With results URL
  %(prog)s --url "https://woodfordcountyelections.com/results/2026-primary.html"
  
  # Test with 2024 data
  %(prog)s --url "https://woodfordcountyelections.com/results/2024-primary.pdf" --date 2024-03-19
  
  # Save to specific file
  %(prog)s --url "URL" --output woodford_results.json
        """
    )
    
    parser.add_argument(
        '--url',
        help='Direct URL to results page or PDF'
    )
    
    parser.add_argument(
        '--date',
        default='2026-03-17',
        help='Election date (YYYY-MM-DD, default: 2026-03-17)'
    )
    
    parser.add_argument(
        '--output',
        help='Output JSON file (default: woodford_results.json)'
    )
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = WoodfordCountyScraper(
        url=args.url,
        election_date=args.date
    )
    
    # Scrape results
    print("Scraping Woodford County election results...")
    if args.url:
        print(f"URL: {args.url}")
    print()
    
    results = scraper.scrape()
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        output_file = "woodford_results.json"
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    if "error" in results:
        print(f"Error: {results['error']}")
        if "instructions" not in results:
            print(f"Check {output_file} for details")
    else:
        print(f"✓ Successfully scraped Woodford County results")
        print(f"  Contests found: {len(results.get('contests', []))}")
        if results.get('metadata'):
            if 'ballots_cast' in results['metadata']:
                print(f"  Ballots cast: {results['metadata']['ballots_cast']:,}")
            if 'precincts_reporting' in results['metadata']:
                print(f"  Precincts reporting: {results['metadata']['precincts_reporting']}/{results['metadata'].get('total_precincts', '?')}")
        print(f"  Saved to: {output_file}")


if __name__ == "__main__":
    main()
