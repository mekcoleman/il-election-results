#!/usr/bin/env python3
"""
Chicago Board of Election Commissioners Scraper
Illinois Primary Election — March 17, 2026

Platform: HTML results page (NOT PDF this cycle)
URL: https://results.chicagoelections.gov/results/ElectionSummary.html

Page structure:
  Contest Name - PARTY (Vote for N)
  PARTY
  Precincts Reported: X of Y (Z%)
  Candidate        Total
  Name             votes   N/A
  ...
  Total Votes      total
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import Dict, List, Optional


RESULTS_URL = 'https://results.chicagoelections.gov/results/ElectionSummary.html'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


class ChicagoBoardScraper:
    """Scraper for Chicago Board of Election Commissioners HTML results."""

    def __init__(self, election_date: str = '2026-03-17'):
        self.election_date = election_date
        self.url = RESULTS_URL

    def detect_party(self, party_code: str, contest_name: str = '') -> str:
        code = party_code.strip().upper()
        if code == 'DEM':
            return 'Democratic'
        elif code == 'REP':
            return 'Republican'
        elif code == 'LIB':
            return 'Libertarian'
        elif code == 'GRN':
            return 'Green'
        elif code in ('IND', 'NON', 'NP'):
            return 'Non-Partisan'
        return 'Non-Partisan'

    def fetch(self) -> Optional[str]:
        try:
            resp = requests.get(self.url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            print(f"✗ Error fetching Chicago Board results: {e}")
            return None

    def parse(self, html: str) -> Dict:
        """Parse the full HTML results page."""
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n')
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        summary = self._parse_summary(lines)
        contests = self._parse_contests(lines)

        return {
            'authority': 'Chicago Board of Election Commissioners',
            'jurisdiction': 'Chicago (City)',
            'election_date': self.election_date,
            'scraped_at': datetime.now().isoformat(),
            'source': f'HTML — {self.url}',
            'summary': summary,
            'contests': contests,
        }

    def _parse_summary(self, lines: List[str]) -> Dict:
        summary = {}
        for line in lines[:20]:
            m = re.search(r'Precincts Reported:\s*(\d[\d,]*)\s+of\s+(\d[\d,]*)', line)
            if m:
                summary['precincts_reporting'] = int(m.group(1).replace(',', ''))
                summary['total_precincts'] = int(m.group(2).replace(',', ''))
                break
        return summary

    def _parse_contests(self, lines: List[str]) -> List[Dict]:
        """Parse all contests from the page text.

        Contest header format:
          "Senator, U.S. - DEM (Vote for  1)"
        Followed by party code line, precincts line, header row, candidate rows.

        Candidate row format:
          "Kevin Ryan    0    N/A"
          or with votes:
          "Kevin Ryan    12345    45.6%"
        """
        contests = []
        i = 0

        # Regex for contest header: "Contest Name - PARTY (Vote for N)"
        contest_header = re.compile(
            r'^(.+?)\s+-\s+(DEM|REP|LIB|GRN|IND|NON|NP)\s+\(Vote for\s+(\d+)\)$',
            re.IGNORECASE
        )
        # Regex for precincts line
        precincts_re = re.compile(
            r'Precincts Reported:\s*(\d[\d,]*)\s+of\s+(\d[\d,]*)'
        )
        # Candidate line: name then number then (N/A or percent)
        candidate_re = re.compile(
            r'^(.+?)\s{2,}(\d[\d,]*)\s+([\d.]+%|N/A)\s*$'
        )

        while i < len(lines):
            line = lines[i]
            m = contest_header.match(line)
            if m:
                contest_name = m.group(1).strip()
                party_code = m.group(2).upper()
                vote_for = int(m.group(3))
                party = self.detect_party(party_code)

                precincts_reporting = 0
                total_precincts = 0
                candidates = []

                # Scan ahead for precincts and candidates
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]

                    # Stop at next contest header
                    if contest_header.match(next_line):
                        break

                    # Precincts line
                    pm = precincts_re.search(next_line)
                    if pm:
                        precincts_reporting = int(pm.group(1).replace(',', ''))
                        total_precincts = int(pm.group(2).replace(',', ''))
                        j += 1
                        continue

                    # Skip non-data lines
                    if next_line in ('Candidate', 'Total', party_code,
                                     'City of Chicago', 'Unofficial Results',
                                     'Primary Election', 'Tuesday, March 17, 2026'):
                        j += 1
                        continue

                    # Skip "Total Votes  N" lines
                    if next_line.startswith('Total Votes'):
                        j += 1
                        continue

                    # Try candidate line
                    cm = candidate_re.match(next_line)
                    if cm:
                        cand_name = cm.group(1).strip()
                        votes = int(cm.group(2).replace(',', ''))
                        pct_str = cm.group(3)

                        if cand_name.lower().startswith('no candidate'):
                            j += 1
                            continue

                        pct = 0.0
                        if pct_str != 'N/A':
                            try:
                                pct = float(pct_str.replace('%', ''))
                            except ValueError:
                                pass

                        candidates.append({
                            'name': cand_name,
                            'votes': votes,
                            'percent': pct,
                        })
                        j += 1
                        continue

                    j += 1

                contests.append({
                    'name': contest_name,
                    'contest_name': contest_name,
                    'party': party,
                    'party_type': party,
                    'vote_for': vote_for,
                    'precincts_reporting': precincts_reporting,
                    'total_precincts': total_precincts,
                    'candidates': candidates,
                })
                i = j
                continue

            i += 1

        return contests

    def scrape(self) -> Dict:
        print(f"Scraping Chicago Board of Elections...")
        print(f"URL: {self.url}")
        html = self.fetch()
        if not html:
            return {
                'authority': 'Chicago Board of Election Commissioners',
                'jurisdiction': 'Chicago (City)',
                'error': 'Failed to fetch page',
                'contests': [],
                'scraped_at': datetime.now().isoformat(),
            }
        result = self.parse(html)
        print(f"✓ {len(result['contests'])} contests scraped")
        return result

    def save_results(self, results: Dict, output_dir: str = '.'):
        filename = f"{output_dir}/chicago_board_results.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Saved to {filename}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Chicago Board of Elections HTML scraper')
    parser.add_argument('--output', default='.', help='Output directory')
    parser.add_argument('--date', default='2026-03-17', help='Election date')
    # Keep --url for backwards compat but ignore it (URL is now hardcoded)
    parser.add_argument('--url', help='(ignored — URL is hardcoded for 2026)')
    args = parser.parse_args()

    scraper = ChicagoBoardScraper(args.date)
    results = scraper.scrape()
    scraper.save_results(results, args.output)

    if 'error' not in results:
        print()
        print(f"  Authority : {results['authority']}")
        print(f"  Contests  : {len(results['contests'])}")
        dem = sum(1 for c in results['contests'] if c['party'] == 'Democratic')
        rep = sum(1 for c in results['contests'] if c['party'] == 'Republican')
        other = len(results['contests']) - dem - rep
        print(f"  Dem/Rep/Other: {dem}/{rep}/{other}")


if __name__ == '__main__':
    main()
