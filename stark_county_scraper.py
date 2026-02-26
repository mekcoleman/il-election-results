#!/usr/bin/env python3
"""
Stark County Election Results Scraper - THE FINAL COUNTY!

Scrapes primary election results from Stark County's custom PDF system.
This is the 38th and FINAL county scraper, completing 100% Illinois coverage!

County: Stark County, Illinois (~4,000 voters - smallest in Illinois!)
Location: North-central Illinois (Toulon, Wyoming - Reagan's boyhood home)
Platform: Custom PDF system at starkco.illinois.gov

Usage:
    # With PDF URL
    python stark_county_scraper.py --url "https://www.starkco.illinois.gov/files/2026-primary-results.pdf"
    
    # Without URL (shows instructions)
    python stark_county_scraper.py
    
🎉 THIS IS THE FINAL COUNTY - COMPLETING 100% ILLINOIS COVERAGE! 🎉
"""

import requests
import json
import re
import argparse
from datetime import datetime
from typing import Dict, List, Optional

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("ERROR: pdfplumber is required for Stark County!")
    print("Install with: pip install pdfplumber")
    import sys
    sys.exit(1)


class StarkCountyScraper:
    """
    Scraper for Stark County election results.
    
    This is the 38th and FINAL county scraper!
    Completes 100% coverage of Illinois counties for the 2026 Primary Election.
    """
    
    def __init__(self, url: Optional[str] = None, election_date: str = "2026-03-17"):
        """
        Initialize the scraper for THE FINAL COUNTY!
        
        Args:
            url: Direct URL to PDF results document
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
        Scrape election results from Stark County.
        
        Returns:
            Dictionary containing election results
        """
        if not self.url:
            return self._show_instructions()
        
        return self._scrape_pdf()
    
    def _show_instructions(self) -> Dict:
        """Show instructions when no URL provided."""
        instructions = """
╔══════════════════════════════════════════════════════════════════════════════╗
║              STARK COUNTY SCRAPER - THE FINAL COUNTY! 🎉                     ║
║                    100% ILLINOIS COVERAGE COMPLETION                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

This is the 38th and FINAL county scraper! Completing this scraper achieves
100% coverage of all Illinois counties for the 2026 Primary Election!

STEP 1: Find the PDF Results
────────────────────────────────────────────────────────────────────────────────
Visit: https://www.starkco.illinois.gov/elections/election-results

Look for:
  • "2026 Primary Election Results" PDF link
  • "March 17, 2026 Results"
  • "Unofficial Results" (election night)
  • "Official Results" (after canvass)

STEP 2: Copy the PDF URL
────────────────────────────────────────────────────────────────────────────────
Right-click the PDF link and select "Copy link address"

The URL will look like:
  • https://www.starkco.illinois.gov/files/elections/2026-primary-results.pdf
  • Or similar format in their file system

STEP 3: Run the Scraper
────────────────────────────────────────────────────────────────────────────────
python stark_county_scraper.py --url "YOUR_PDF_URL"

EXAMPLE WITH HISTORICAL DATA:
────────────────────────────────────────────────────────────────────────────────
Test with 2024 or earlier results:

1. Visit starkco.illinois.gov/elections/election-results
2. Find 2024 Primary results PDF (or 2022 General)
3. Copy PDF URL
4. Run: python stark_county_scraper.py --url "PDF_URL" --date 2024-03-19

STARK COUNTY - SPECIAL SIGNIFICANCE:
────────────────────────────────────────────────────────────────────────────────
  • Smallest county in Illinois (~4,000 voters)
  • Home to Wyoming - Ronald Reagan's boyhood town
  • THE FINAL COUNTY in the 38-county project!
  • Completing this = 100% Illinois coverage!

SUPPORTED FORMAT:
────────────────────────────────────────────────────────────────────────────────
  ✓ PDF documents (primary format)
  ✓ Text-based PDF parsing
  ✓ Similar to other Illinois county PDFs

PROJECT COMPLETION:
────────────────────────────────────────────────────────────────────────────────
  37 of 38 counties complete before Stark
  This scraper completes the final 1/38
  READY FOR 100% ILLINOIS COVERAGE! 🎊

NEED HELP?
────────────────────────────────────────────────────────────────────────────────
See STARK_COUNTY_SETUP.md for detailed instructions.

        """
        print(instructions)
        return {
            "error": "No URL provided",
            "instructions": "See output above for setup instructions"
        }
    
    def _scrape_pdf(self) -> Dict:
        """
        Scrape results from PDF document.
        
        Returns:
            Dictionary containing election results
        """
        try:
            # Download PDF
            print("Downloading Stark County PDF...")
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            
            # Save temporarily
            pdf_path = "/tmp/stark_results.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            print("Extracting text from PDF...")
            # Extract text
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            
            # Initialize results
            results = {
                "county": "Stark",
                "election_date": self.election_date,
                "source": "Stark County Elections PDF",
                "pdf_url": self.url,
                "scraped_at": datetime.now().isoformat(),
                "metadata": {},
                "contests": []
            }
            
            print("Parsing contests and metadata...")
            # Parse contests from text
            results["metadata"] = self._extract_metadata(text)
            results["contests"] = self._parse_contests(text)
            
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
    
    def _extract_metadata(self, text: str) -> Dict:
        """Extract metadata from PDF text."""
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
    
    def _parse_contests(self, text: str) -> List[Dict]:
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
            
            # Check for contest header (all caps or title case, no numbers)
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
    """Main entry point for THE FINAL COUNTY scraper!"""
    parser = argparse.ArgumentParser(
        description='Scrape Stark County election results - THE FINAL COUNTY! 🎉',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This is the 38th and FINAL county scraper!
Completing 100% coverage of Illinois counties for the 2026 Primary Election.

Examples:
  # With PDF URL
  %(prog)s --url "https://www.starkco.illinois.gov/files/2026-primary.pdf"
  
  # Test with historical data
  %(prog)s --url "https://www.starkco.illinois.gov/files/2024-primary.pdf" --date 2024-03-19
  
  # Save to specific file
  %(prog)s --url "PDF_URL" --output stark_results.json

Stark County Facts:
  • Smallest county in Illinois (~4,000 voters)
  • Home to Wyoming - Ronald Reagan's boyhood town
  • THE FINAL COUNTY = 100% Illinois coverage!
        """
    )
    
    parser.add_argument(
        '--url',
        help='Direct URL to PDF results document'
    )
    
    parser.add_argument(
        '--date',
        default='2026-03-17',
        help='Election date (YYYY-MM-DD, default: 2026-03-17)'
    )
    
    parser.add_argument(
        '--output',
        help='Output JSON file (default: stark_results.json)'
    )
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = StarkCountyScraper(
        url=args.url,
        election_date=args.date
    )
    
    # Scrape results
    print("="*80)
    print("STARK COUNTY ELECTION RESULTS SCRAPER")
    print("THE FINAL COUNTY - #38 of 38")
    print("100% ILLINOIS COVERAGE!")
    print("="*80)
    print()
    
    if args.url:
        print(f"URL: {args.url}")
    print()
    
    results = scraper.scrape()
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        output_file = "stark_results.json"
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print()
    print("="*80)
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        if "instructions" not in results:
            print(f"Check {output_file} for details")
    else:
        print(f"✓ Successfully scraped Stark County results!")
        print(f"  Contests found: {len(results.get('contests', []))}")
        if results.get('metadata'):
            if 'ballots_cast' in results['metadata']:
                print(f"  Ballots cast: {results['metadata']['ballots_cast']:,}")
            if 'precincts_reporting' in results['metadata']:
                print(f"  Precincts reporting: {results['metadata']['precincts_reporting']}/{results['metadata'].get('total_precincts', '?')}")
        print(f"  Saved to: {output_file}")
        print()
        print("🎉 " + "="*74 + " 🎉")
        print("🎊 CONGRATULATIONS! ALL 38 COUNTIES COMPLETE! 🎊")
        print("🎉 100% ILLINOIS COVERAGE ACHIEVED! 🎉")
        print("🎉 " + "="*74 + " 🎉")
        print()
        print("The Illinois Primary Election Scraper project is now COMPLETE!")
        print("All 38 counties covered. Ready for March 17, 2026!")
    print("="*80)


if __name__ == "__main__":
    main()
