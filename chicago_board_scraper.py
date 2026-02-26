#!/usr/bin/env python3
"""
Illinois Primary Election 2026 - Chicago Board of Election Commissioners Scraper
Handles City of Chicago election results (Chicago proper only)

Platform: Custom Azure-hosted PDF system
Base URL: https://chicagoelections.gov
Coverage: City of Chicago (~1.5M voters, ~1,290 precincts)

IMPORTANT: Chicago Board handles ONLY the City of Chicago.
Suburban Cook County is handled by Cook County Clerk (separate scraper).

The Chicago Board publishes results as PDF files hosted on Azure blob storage.
PDFs contain clean text that can be extracted and parsed.
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import io

# PDF parsing libraries
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: pdfplumber not installed. Install with: pip install pdfplumber")

class ChicagoBoardScraper:
    """Scraper for Chicago Board of Election Commissioners results"""
    
    def __init__(self, election_date: str = '2026-03-17'):
        """Initialize scraper
        
        Args:
            election_date: Election date in YYYY-MM-DD format
        """
        self.county_name = 'Chicago (City)'
        self.authority = 'Chicago Board of Election Commissioners'
        self.election_date = election_date
        
        # Azure blob storage base URLs
        # Results PDFs are at: cboeresults.blob.core.usgovcloudapi.net
        # Proclamations at: cboeprod.blob.core.usgovcloudapi.net
        self.results_base = 'https://cboeresults.blob.core.usgovcloudapi.net/results'
        self.proclamation_base = 'https://cboeprod.blob.core.usgovcloudapi.net/prod'
        
        # Common PDF filenames
        self.summary_pdf_names = [
            'Summary Report (2 Column).pdf',
            'Summary%20Report%20(2%20Column).pdf',
            'Summary Report.pdf',
            'Summary%20Report.pdf'
        ]
    
    def detect_party(self, contest_name: str, candidate_line: str = '') -> str:
        """Detect party affiliation
        
        Chicago Board uses party prefixes like "DEM -", "REP -", "NON -"
        
        Args:
            contest_name: Name of the contest
            candidate_line: Candidate name line (may have party prefix)
            
        Returns:
            Party string: 'Democratic', 'Republican', or 'Non-Partisan'
        """
        # Check candidate line first (more reliable)
        if 'DEM -' in candidate_line or 'DEM-' in candidate_line:
            return 'Democratic'
        elif 'REP -' in candidate_line or 'REP-' in candidate_line:
            return 'Republican'
        elif 'NON -' in candidate_line or 'NON-' in candidate_line:
            return 'Non-Partisan'
        elif 'GRN -' in candidate_line:
            return 'Green'
        elif 'LIB -' in candidate_line:
            return 'Libertarian'
        elif 'IND -' in candidate_line:
            return 'Independent'
        
        # Fall back to contest name
        contest_upper = contest_name.upper()
        if 'DEM ' in contest_upper or 'DEMOCRATIC' in contest_upper:
            return 'Democratic'
        elif 'REP ' in contest_upper or 'REPUBLICAN' in contest_upper:
            return 'Republican'
        else:
            return 'Non-Partisan'
    
    def scrape_from_pdf_url(self, pdf_url: str) -> Dict:
        """Scrape results from a specific PDF URL
        
        Args:
            pdf_url: Direct URL to the PDF file
            
        Returns:
            Dictionary with scraped results
        """
        if not PDF_AVAILABLE:
            return {
                'error': 'pdfplumber not installed',
                'message': 'Install with: pip install pdfplumber',
                'authority': self.authority,
                'scraped_at': datetime.now().isoformat()
            }
        
        print(f"Scraping {self.authority}...")
        print(f"PDF URL: {pdf_url}")
        
        try:
            # Fetch PDF
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            # Parse PDF
            pdf_file = io.BytesIO(response.content)
            results = self._parse_pdf(pdf_file)
            
            results['authority'] = self.authority
            results['jurisdiction'] = self.county_name
            results['election_date'] = self.election_date
            results['scraped_at'] = datetime.now().isoformat()
            results['source'] = 'Chicago Board PDF'
            results['pdf_url'] = pdf_url
            
            print(f"✓ Successfully scraped {len(results.get('contests', []))} contests")
            return results
            
        except requests.RequestException as e:
            print(f"✗ Error fetching PDF: {e}")
            return {
                'error': str(e),
                'authority': self.authority,
                'scraped_at': datetime.now().isoformat()
            }
    
    def scrape_summary_report(self) -> Dict:
        """Scrape summary report PDF (try common filenames)
        
        Returns:
            Dictionary with scraped results
        """
        # Try common PDF URLs
        for pdf_name in self.summary_pdf_names:
            pdf_url = f"{self.results_base}/{pdf_name}"
            
            print(f"Trying: {pdf_url}")
            try:
                response = requests.head(pdf_url, timeout=10)
                if response.status_code == 200:
                    print(f"✓ Found PDF at: {pdf_url}")
                    return self.scrape_from_pdf_url(pdf_url)
            except:
                continue
        
        # If no PDF found, return error with instructions
        return {
            'error': 'PDF not found',
            'authority': self.authority,
            'message': 'Could not find summary PDF. Check chicagoelections.gov/elections/results for the correct URL.',
            'tried_urls': [f"{self.results_base}/{name}" for name in self.summary_pdf_names],
            'scraped_at': datetime.now().isoformat()
        }
    
    def _parse_pdf(self, pdf_file: io.BytesIO) -> Dict:
        """Parse Chicago Board PDF format
        
        Args:
            pdf_file: BytesIO object containing PDF data
            
        Returns:
            Normalized results dictionary
        """
        results = {
            'contests': [],
            'summary': {}
        }
        
        with pdfplumber.open(pdf_file) as pdf:
            # Extract text from all pages
            full_text = ''
            for page in pdf.pages:
                full_text += page.extract_text() + '\n'
        
        # Parse summary statistics from first page
        self._parse_summary_stats(full_text, results)
        
        # Parse contests
        self._parse_contests(full_text, results)
        
        return results
    
    def _parse_summary_stats(self, text: str, results: Dict):
        """Extract summary statistics from PDF text
        
        Args:
            text: Full PDF text
            results: Results dictionary to update
        """
        # Look for "Total Registration and Turnout" line
        reg_match = re.search(r'Total Registration and Turnout\s+(\d[\d,]*)\s+(\d[\d,]*)', text)
        if reg_match:
            results['summary']['registered_voters'] = int(reg_match.group(1).replace(',', ''))
            results['summary']['total_votes_cast'] = int(reg_match.group(2).replace(',', ''))
        
        # Look for precinct count
        precinct_match = re.search(r'\(\s*(\d+)\s+of\s+(\d+)\s+precincts reported\s*\)', text)
        if precinct_match:
            results['summary']['precincts_reporting'] = int(precinct_match.group(1))
            results['summary']['total_precincts'] = int(precinct_match.group(2))
    
    def _parse_contests(self, text: str, results: Dict):
        """Parse contests from PDF text
        
        Chicago Board format:
        Contest Name
        ( X of Y precincts reported )
        PARTY - Candidate Name   votes   percent%
        PARTY - Another Candidate votes   percent%
        Total   total_votes
        
        Args:
            text: Full PDF text
            results: Results dictionary to update
        """
        # Split text into lines
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and header/footer
            if not line or 'Printed:' in line or 'Data Refreshed:' in line or 'Page ' in line:
                i += 1
                continue
            
            # Check if this line looks like a contest name
            # Contest names are typically all caps or Title Case, not starting with DEM/REP/NON
            if self._is_contest_header(line, lines, i):
                contest = self._parse_single_contest(lines, i)
                if contest and contest.get('candidates'):
                    results['contests'].append(contest)
                    # Skip past the lines we just parsed
                    i += contest.get('_lines_consumed', 1)
                else:
                    i += 1
            else:
                i += 1
    
    def _is_contest_header(self, line: str, lines: List[str], index: int) -> bool:
        """Check if a line is a contest header
        
        Args:
            line: Current line
            lines: All lines
            index: Current index
            
        Returns:
            True if this is a contest header
        """
        # Skip if starts with party prefix
        if line.startswith(('DEM ', 'REP ', 'NON ', 'GRN ', 'LIB ', 'IND ', 'Yes ', 'No ', 'Total ')):
            return False
        
        # Skip if it's numbers/percentages
        if re.match(r'^\d[\d,]*\s+[\d.]+%?\s*$', line):
            return False
        
        # Look ahead for precinct reporting line
        if index + 1 < len(lines):
            next_line = lines[index + 1].strip()
            if '(' in next_line and 'precincts reported' in next_line:
                return True
        
        # Or look for "Vote For" pattern (multi-winner contests)
        if index + 1 < len(lines):
            next_line = lines[index + 1].strip()
            if next_line.startswith('Vote For '):
                return True
        
        return False
    
    def _parse_single_contest(self, lines: List[str], start_index: int) -> Optional[Dict]:
        """Parse a single contest from lines
        
        Args:
            lines: All text lines
            start_index: Index where contest starts
            
        Returns:
            Contest dictionary or None
        """
        contest_name = lines[start_index].strip()
        
        contest = {
            'name': contest_name,
            'party': 'Unknown',  # Will be determined from candidates
            'candidates': [],
            '_lines_consumed': 1
        }
        
        i = start_index + 1
        
        # Check for "Vote For X" line
        if i < len(lines) and lines[i].strip().startswith('Vote For '):
            i += 1
            contest['_lines_consumed'] += 1
        
        # Check for precinct reporting line
        if i < len(lines):
            precinct_line = lines[i].strip()
            precinct_match = re.search(r'\(\s*(\d+)\s+of\s+(\d+)\s+precincts reported\s*\)', precinct_line)
            if precinct_match:
                contest['precincts_reporting'] = int(precinct_match.group(1))
                contest['total_precincts'] = int(precinct_match.group(2))
                i += 1
                contest['_lines_consumed'] += 1
        
        # Parse candidates until we hit "Total" line
        while i < len(lines):
            line = lines[i].strip()
            
            # Stop at Total line
            if line.startswith('Total ') or line == 'Total':
                contest['_lines_consumed'] += 1
                break
            
            # Stop at next contest (new header)
            if self._is_contest_header(line, lines, i):
                break
            
            # Try to parse as candidate line
            candidate = self._parse_candidate_line(line)
            if candidate:
                contest['candidates'].append(candidate)
                # Determine party from first candidate if not set
                if contest['party'] == 'Unknown':
                    contest['party'] = self.detect_party(contest_name, line)
            
            i += 1
            contest['_lines_consumed'] += 1
        
        return contest if contest['candidates'] else None
    
    def _parse_candidate_line(self, line: str) -> Optional[Dict]:
        """Parse a candidate line
        
        Format: PARTY - Candidate Name   votes   percent%
        or: Candidate Name   votes   percent%
        
        Args:
            line: Line to parse
            
        Returns:
            Candidate dictionary or None
        """
        # Skip non-candidate lines
        if not line or line.startswith(('Printed:', 'Data Refreshed:', 'CHI ', 'CITY OF CHICAGO', 'Page ')):
            return None
        
        # Pattern: PARTY - Name  votes  percent%
        # or: Name  votes  percent%
        match = re.match(r'^(?:([A-Z]{3})\s+-\s+)?(.+?)\s+(\d[\d,]*)\s+([\d.]+)%?\s*$', line)
        
        if match:
            party_prefix = match.group(1)  # May be None
            name = match.group(2).strip()
            votes = int(match.group(3).replace(',', ''))
            percent = float(match.group(4))
            
            return {
                'name': name,
                'votes': votes,
                'percent': percent,
                '_party_prefix': party_prefix
            }
        
        return None
    
    def save_results(self, results: Dict, output_dir: str = '.'):
        """Save results to JSON file
        
        Args:
            results: Results dictionary
            output_dir: Directory to save file
        """
        filename = f"{output_dir}/chicago_board_results.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Saved results to {filename}")

def print_instructions():
    """Print detailed usage instructions"""
    print("=" * 70)
    print("Chicago Board of Election Commissioners Scraper")
    print("Illinois Primary Election - March 17, 2026")
    print("=" * 70)
    print()
    print("JURISDICTION: City of Chicago ONLY (not suburban Cook County)")
    print()
    print("The Chicago Board publishes results as PDF files on Azure storage.")
    print("Base URL: https://chicagoelections.gov/elections/results")
    print()
    print("USAGE:")
    print()
    print("  # Try to auto-find PDF (tries common filenames)")
    print("  python chicago_board_scraper.py")
    print()
    print("  # Scrape from specific PDF URL")
    print("  python chicago_board_scraper.py --url https://cboeresults.blob.core.usgovcloudapi.net/results/Summary%20Report.pdf")
    print()
    print("FINDING THE PDF URL:")
    print()
    print("1. Visit: https://chicagoelections.gov/elections/results")
    print("2. Find '2026 Primary' election")
    print("3. Look for PDF download link (usually 'Summary Report')")
    print("4. Right-click and copy link address")
    print("5. Use that URL with --url parameter")
    print()
    print("Note: Results typically posted 30-60 minutes after polls close (7 PM)")
    print()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Chicago Board Election Results Scraper')
    parser.add_argument('--url', '--pdf-url', dest='pdf_url',
                       help='Direct URL to PDF file')
    parser.add_argument('--date', default='2026-03-17',
                       help='Election date in YYYY-MM-DD format')
    parser.add_argument('--output', default='.',
                       help='Output directory for JSON results')
    
    args = parser.parse_args()
    
    scraper = ChicagoBoardScraper(args.date)
    
    if args.pdf_url:
        # Scrape from specific URL
        results = scraper.scrape_from_pdf_url(args.pdf_url)
    else:
        # Try to auto-find PDF
        results = scraper.scrape_summary_report()
    
    scraper.save_results(results, args.output)
    
    # Print summary
    if 'error' not in results:
        print()
        print("Summary:")
        print(f"  Jurisdiction: {results.get('jurisdiction')}")
        print(f"  Authority: {results.get('authority')}")
        print(f"  Election: {results.get('election_date')}")
        print(f"  Contests: {len(results.get('contests', []))}")
        if 'registered_voters' in results.get('summary', {}):
            print(f"  Registered voters: {results['summary']['registered_voters']:,}")
        if 'total_votes_cast' in results.get('summary', {}):
            print(f"  Total votes cast: {results['summary']['total_votes_cast']:,}")
        if 'total_precincts' in results.get('summary', {}):
            print(f"  Precincts: {results['summary'].get('precincts_reporting', '?')}/{results['summary']['total_precincts']}")

if __name__ == '__main__':
    main()
