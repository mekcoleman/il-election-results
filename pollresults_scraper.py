"""
pollresults.net Multi-County Scraper
Scrapes election results from pollresults.net (Liberty Systems/CSE Software) platform
Supports 13 Illinois counties: Whiteside, Lee, Ogle, Carroll, Putnam, Vermilion,
Tazewell, Stephenson, Boone, Bureau, Livingston, Ford, Mercer

NOTE: This platform serves plain HTML — no Selenium or JavaScript rendering needed.
Simple requests + BeautifulSoup is sufficient and much faster.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import time
import sys


# County URL map — all static, no election IDs needed
COUNTY_URLS = {
    'Whiteside':  'https://il-whiteside.pollresults.net/',
    'Lee':        'https://il-lee.pollresults.net/',
    'Ogle':       'https://il-ogle.pollresults.net/',
    'Carroll':    'https://il-carroll.pollresults.net/',
    'Putnam':     'https://il-putnam.pollresults.net/',
    'Vermilion':  'https://il-vermilion.pollresults.net/',
    'Tazewell':   'https://il-tazewell.pollresults.net/',
    'Stephenson': 'https://il-stephenson.pollresults.net/',
    'Boone':      'https://il-boone.pollresults.net/',
    'Bureau':     'https://il-bureau.pollresults.net/',
    'Livingston': 'https://il-livingston.pollresults.net/',
    'Ford':       'https://il-ford.pollresults.net/',
    'Mercer':     'https://il-mercer.pollresults.net/',
}


class PollResultsScraper:
    """Scraper for pollresults.net platform (Liberty Systems / CSE Software).

    The platform serves fully-rendered HTML — no JavaScript execution needed.
    Each contest block follows this pattern:

        D CONTEST NAME
        Number of Precincts  60
        Precincts Reporting   0
        Vote For              1
        ...
        CANDIDATE NAME (DEM)  123  45.6%
        CANDIDATE NAME (DEM)  150  54.4%
        Results updated at ...
    """

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    def __init__(self, county_name: str, base_url: str):
        self.county_name = county_name
        self.base_url = base_url.rstrip('/')

    # ── Fetch ─────────────────────────────────────────────────────────────────

    def fetch_page(self) -> Optional[str]:
        """Fetch the results page HTML."""
        try:
            resp = requests.get(self.base_url, headers=self.HEADERS, timeout=20)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            print(f"  ✗ [{self.county_name}] Fetch failed: {e}")
            return None

    # ── Parse ─────────────────────────────────────────────────────────────────

    def parse(self, html: str) -> Dict:
        """Parse the full page and return structured results."""
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n')

        summary = self._parse_summary(text)
        contests = self._parse_contests(text)

        return {
            'county': self.county_name,
            'election_date': '2026-03-17',
            'scraped_at': datetime.now().isoformat(),
            'source': f'pollresults.net — {self.base_url}',
            'summary': summary,
            'contests': contests,
        }

    def _parse_summary(self, text: str) -> Dict:
        summary = {}
        m = re.search(r'Total Voters:\s*([\d,]+)', text)
        if m:
            summary['registered_voters'] = int(m.group(1).replace(',', ''))
        m = re.search(r'Ballots Cast:\s*([\d,]+)', text)
        if m:
            summary['ballots_cast'] = int(m.group(1).replace(',', ''))
        m = re.search(r'Turnout:\s*([\d.]+)%', text)
        if m:
            summary['turnout_percent'] = float(m.group(1))
        m = re.search(r'Precincts:\s*(\d+)', text)
        if m:
            summary['total_precincts'] = int(m.group(1))
        m = re.search(r'Precincts Reporting:\s*(\d+)', text)
        if m:
            summary['precincts_reporting'] = int(m.group(1))
        return summary

    def _parse_contests(self, text: str) -> List[Dict]:
        """Split text into contest blocks and parse each one."""
        contests = []
        lines = [l.strip() for l in text.split('\n')]

        # Find all contest header positions
        # Headers look like: "D UNITED STATES SENATOR" or "R COUNTY CLERK"
        # or referendum: "LEE COUNTY FEDERAL SCHOLARSHIP TAX CREDIT ADVISORY REFERENDUM"
        contest_starts = []
        for i, line in enumerate(lines):
            # D/R party contests
            m = re.match(r'^([DR])\s+([A-Z][A-Z0-9\s\(\)\-/,\.#\'&]+)$', line)
            if m:
                name = m.group(2).strip()
                if any(skip in name for skip in [
                    'PRECINCTS', 'BALLOTS', 'VOTERS', 'TURNOUT',
                    'VOTE FOR', 'RESULTS UPDATED', 'UNOFFICIAL',
                    'POLLING', 'EARLY', 'PROVISIONAL'
                ]):
                    continue
                if len(name) < 4:
                    continue
                contest_starts.append((i, m.group(1), name))
                continue

            # Referendum contests (no D/R prefix, all caps, long name)
            if (re.match(r'^[A-Z][A-Z0-9\s\(\)\-/,\.#\'&]+$', line)
                    and len(line) > 15
                    and not any(skip in line for skip in [
                        'PRECINCTS', 'BALLOTS', 'VOTERS', 'TURNOUT',
                        'VOTE FOR', 'RESULTS UPDATED', 'UNOFFICIAL',
                        'POLLING', 'EARLY', 'PROVISIONAL', 'STATISTICS',
                        'GENERAL PRIMARY', 'SELECTED', 'PRECINCTS REPORTING',
                        'NUMBER OF', 'REGISTERED', 'TOTAL VOTES', 'TOTAL VOTERS'
                    ])
                    and not re.match(r'^[DR]\s+', line)):
                contest_starts.append((i, 'NP', line.strip()))

        # Extract each contest block
        for idx, (line_num, party_prefix, contest_name) in enumerate(contest_starts):
            end_line = contest_starts[idx + 1][0] if idx + 1 < len(contest_starts) else len(lines)
            block_lines = lines[line_num:end_line]
            contest = self._parse_contest_block(contest_name, party_prefix, block_lines)
            if contest:
                contests.append(contest)

        return contests

    def _parse_contest_block(self, name: str, party_prefix: str,
                              block_lines: List[str]) -> Optional[Dict]:
        """Parse one contest block into structured data."""
        block = '\n'.join(block_lines)

        # Determine party
        if party_prefix == 'D':
            party = 'Democratic'
        elif party_prefix == 'R':
            party = 'Republican'
        else:
            party = 'Non-Partisan'

        name_upper = name.upper()
        if 'NONPARTISAN' in name_upper or 'NON-PARTISAN' in name_upper:
            party = 'Non-Partisan'

        # Extract precinct info
        total_precincts = 0
        precincts_reporting = 0
        vote_for = 1

        # "Number of Precincts\n60" or "Number of Precincts  60"
        m = re.search(r'Number of Precincts\s+(\d+)', block)
        if m:
            total_precincts = int(m.group(1))
        m = re.search(r'Precincts Reporting\s+(\d+)', block)
        if m:
            precincts_reporting = int(m.group(1))
        m = re.search(r'Vote For\s+(\d+)', block)
        if m:
            vote_for = int(m.group(1))

        # Parse candidates
        # Live format (no spaces): "KEVIN RYAN (DEM)667.17 %"
        # or: "RAJA KRISHNAMOORTHI (DEM)39042.39 %"
        # or: "YES128962.63 %"  (referenda)
        # or: "NO CANDIDATE (DEM)" (no votes)
        candidates = []

        # Primary pattern: NAME (PARTY)votes pct %
        # Works when votes and pct are jammed right after the closing paren
        cand_nospace = re.compile(
            r'^(.+?)\s+\((DEM|REP|IND|NON|NP|LIB|GRN)\)(\d[\d,]*)([\d.]+)\s*%',
            re.MULTILINE
        )
        for m in cand_nospace.finditer(block):
            cand_name = m.group(1).strip()
            if cand_name.upper() == 'NO CANDIDATE':
                continue
            candidates.append({
                'name': cand_name,
                'party': m.group(2),
                'votes': int(m.group(3).replace(',', '')),
                'percent': float(m.group(4)),
            })

        # Referendum pattern: "YES128962.63 %" or "NO76937.37 %"
        if not candidates:
            ref_pattern = re.compile(
                r'^(YES|NO)(\d[\d,]*)([\d.]+)\s*%',
                re.MULTILINE
            )
            for m in ref_pattern.finditer(block):
                candidates.append({
                    'name': m.group(1),
                    'party': '',
                    'votes': int(m.group(2).replace(',', '')),
                    'percent': float(m.group(3)),
                })

        # Fallback: spaced format "NAME (PARTY)  votes  pct%"
        if not candidates:
            spaced = re.compile(
                r'^(.+?)\s+\((DEM|REP|IND|NON|NP|LIB|GRN)\)\s+(\d[\d,]*)\s+([\d.]+)\s*%',
                re.MULTILINE
            )
            for m in spaced.finditer(block):
                cand_name = m.group(1).strip()
                if cand_name.upper() == 'NO CANDIDATE':
                    continue
                candidates.append({
                    'name': cand_name,
                    'party': m.group(2),
                    'votes': int(m.group(3).replace(',', '')),
                    'percent': float(m.group(4)),
                })

        return {
            'name': name,
            'contest_name': name,
            'party': party,
            'party_type': party,
            'vote_for': vote_for,
            'precincts_reporting': precincts_reporting,
            'total_precincts': total_precincts,
            'candidates': candidates,
        }

    # ── Main entry ────────────────────────────────────────────────────────────

    def scrape(self) -> Dict:
        """Fetch and parse results. Returns structured dict."""
        print(f"  Scraping {self.county_name}... ", end='', flush=True)
        html = self.fetch_page()
        if not html:
            return {
                'county': self.county_name,
                'error': 'Failed to fetch page',
                'contests': [],
                'scraped_at': datetime.now().isoformat(),
            }
        result = self.parse(html)
        print(f"✓ {len(result['contests'])} contests")
        return result

    def save_results(self, results: Dict, output_dir: str = '.'):
        filename = f"{output_dir}/{self.county_name.lower()}_results.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"  ✓ Saved to {filename}")


# ── Multi-county helpers ───────────────────────────────────────────────────────

def scrape_pollresults_county(county_name: str, output_dir: str = '.') -> Optional[Dict]:
    """Scrape a single pollresults.net county by name."""
    url = COUNTY_URLS.get(county_name)
    if not url:
        print(f"✗ Unknown county: {county_name}. Valid: {', '.join(COUNTY_URLS)}")
        return None
    scraper = PollResultsScraper(county_name, url)
    results = scraper.scrape()
    scraper.save_results(results, output_dir)
    return results


def scrape_all_pollresults_counties(output_dir: str = '.') -> Dict:
    """Scrape all 13 pollresults.net counties."""
    print(f"\n{'='*60}")
    print(f"pollresults.net Scraper — {len(COUNTY_URLS)} counties")
    print(f"{'='*60}\n")

    all_results = {}
    failed = []

    for county_name, url in COUNTY_URLS.items():
        scraper = PollResultsScraper(county_name, url)
        results = scraper.scrape()
        if 'error' in results:
            failed.append(county_name)
        else:
            scraper.save_results(results, output_dir)
            all_results[county_name] = results
        time.sleep(0.5)  # polite pause between requests

    print(f"\n{'='*60}")
    print(f"Done: {len(all_results)} succeeded, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print(f"{'='*60}\n")

    return all_results


if __name__ == '__main__':
    if len(sys.argv) > 1:
        county_name = sys.argv[1]
        # Handle case-insensitive input
        match = {k.lower(): k for k in COUNTY_URLS}.get(county_name.lower())
        if not match:
            print(f"Unknown county: {county_name}")
            print(f"Valid options: {', '.join(COUNTY_URLS)}")
            sys.exit(1)
        scrape_pollresults_county(match)
    else:
        scrape_all_pollresults_counties()
