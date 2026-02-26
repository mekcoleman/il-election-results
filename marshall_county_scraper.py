#!/usr/bin/env python3
"""
Marshall County Election Results Scraper
Illinois Primary Election — March 17, 2026

Marshall County (~6,500 voters) — North-central Illinois (Lacon)
Platform: Unknown — needs verification on election day.
County website: https://www.marshallcountyil.gov

Common platforms for small Illinois counties:
  - PDF posted to county website
  - GEMS (election management system with web export)
  - pollresults.net
  - Simple HTML page

ELECTION DAY SETUP:
  1. Visit: https://www.marshallcountyil.gov
     Look for "Elections" or "County Clerk" section → results link
  2. Note the URL format (PDF, HTML, or platform link)
  3. Run: python marshall_county_scraper.py --url "URL_HERE" --output ./county_results

This scraper handles HTML pages and PDFs automatically based on URL extension.

Note: Marshall County only appears in two races for our markets:
  - Regional Superintendent of Schools for La Salle/Marshall/Putnam counties (ILV market)
  - Regional Superintendent of Schools for Bureau/Henry/Stark counties (ILV market)
"""

import requests
import json
import re
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


class MarshallCountyScraper:
    """Scraper for Marshall County election results."""

    COUNTY_WEBSITE = "https://www.marshallcountyil.gov"
    CLERK_PAGE     = "https://www.marshallcountyil.gov/county-clerk"

    def __init__(self, url: Optional[str] = None, election_date: str = "2026-03-17"):
        self.url = url
        self.election_date = election_date
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def scrape(self) -> Dict:
        if not self.url:
            return self._no_url_output()

        print(f"\n{'='*60}")
        print(f"Marshall County")
        print(f"{'='*60}")
        print(f"URL: {self.url}\n")

        if self.url.lower().endswith(".pdf"):
            return self._scrape_pdf()
        else:
            return self._scrape_html()

    # ── HTML scraping ─────────────────────────────────────────────────────────

    def _scrape_html(self) -> Dict:
        try:
            resp = self.session.get(self.url, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            return self._error_output(f"Failed to fetch: {e}")

        soup = BeautifulSoup(resp.text, "html.parser")

        # Check for a PDF link on the page
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True).lower()
            if href.lower().endswith(".pdf") and any(
                k in text or k in href.lower()
                for k in ["result", "election", "primary", "2026"]
            ):
                full_url = href if href.startswith("http") else self.COUNTY_WEBSITE + href
                print(f"  Found PDF link: {full_url}")
                self.url = full_url
                return self._scrape_pdf()

        # Parse HTML directly
        contests = self._parse_html(soup)
        metadata = self._extract_html_metadata(soup)
        print(f"  ✓ {len(contests)} contests found")
        return self._build_output(contests, metadata)

    def _extract_html_metadata(self, soup: BeautifulSoup) -> Dict:
        meta = {}
        text = soup.get_text()
        m = re.search(r"(\d+)\s+of\s+(\d+)\s+precincts", text, re.I)
        if m:
            meta["precincts_reporting"] = int(m.group(1))
            meta["total_precincts"]     = int(m.group(2))
        m = re.search(r"Ballots?\s+Cast[:\s]+([\d,]+)", text, re.I)
        if m:
            meta["ballots_cast"] = int(m.group(1).replace(",", ""))
        return meta

    def _parse_html(self, soup: BeautifulSoup) -> List[Dict]:
        contests = []
        for table in soup.find_all("table"):
            contest = self._parse_table(table)
            if contest:
                contests.append(contest)
        if contests:
            return contests
        # Fallback: text parsing
        return self._parse_text(soup.get_text(separator="\n"))

    def _parse_table(self, table) -> Optional[Dict]:
        name = None
        caption = table.find("caption")
        if caption:
            name = caption.get_text(strip=True)
        if not name:
            for tag in ["h1","h2","h3","h4","h5"]:
                prev = table.find_previous(tag)
                if prev:
                    name = prev.get_text(strip=True)
                    break
        if not name:
            return None

        candidates = []
        for row in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all(["td","th"])]
            if len(cells) < 2:
                continue
            if any(h in cells[0].lower() for h in ["candidate","name","office"]):
                continue
            cand_name = cells[0]
            votes, pct = 0, 0.0
            for cell in reversed(cells[1:]):
                m = re.search(r"([\d,]+)", cell)
                if m:
                    votes = int(m.group(1).replace(",",""))
                    break
            for cell in cells[1:]:
                m = re.search(r"(\d+\.?\d*)%", cell)
                if m:
                    pct = float(m.group(1))
                    break
            if cand_name:
                candidates.append({"name": cand_name, "votes": votes, "percentage": pct})

        if not candidates:
            return None

        return {
            "contest_name": name, "name": name,
            "party": self._detect_party(name),
            "party_type": self._detect_party(name),
            "candidates": candidates,
            "precincts_reporting": 0, "total_precincts": 0,
        }

    # ── PDF scraping ──────────────────────────────────────────────────────────

    def _scrape_pdf(self) -> Dict:
        if not PDF_SUPPORT:
            return self._error_output("pdfplumber not installed. Run: pip install pdfplumber")

        try:
            resp = self.session.get(self.url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            return self._error_output(f"Failed to download PDF: {e}")

        tmp = "/tmp/marshall_results.pdf"
        with open(tmp, "wb") as f:
            f.write(resp.content)

        try:
            with pdfplumber.open(tmp) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            return self._error_output(f"Failed to parse PDF: {e}")

        contests = self._parse_text(text)
        metadata = self._extract_text_metadata(text)
        print(f"  ✓ {len(contests)} contests found")
        return self._build_output(contests, metadata)

    # ── Text parser ───────────────────────────────────────────────────────────

    def _parse_text(self, text: str) -> List[Dict]:
        contests = []
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        current_name   = None
        current_cands  = []
        current_pr, current_tp = 0, 0

        SKIP = re.compile(
            r"^(RUN DATE|RUN TIME|ELECTION|SUMMARY|PAGE|VOTES PERCENT|"
            r"REGISTERED|BALLOTS CAST|TURNOUT|TOTAL VOTES|OFFICIAL|UNOFFICIAL)",
            re.I
        )

        def flush():
            if current_name and current_cands:
                party = self._detect_party(current_name)
                contests.append({
                    "contest_name": current_name, "name": current_name,
                    "party": party, "party_type": party,
                    "candidates": current_cands[:],
                    "precincts_reporting": current_pr,
                    "total_precincts": current_tp,
                })

        for line in lines:
            if SKIP.match(line):
                continue

            m = re.search(r"(\d+)\s+of\s+(\d+)\s+precincts", line, re.I)
            if m:
                current_pr = int(m.group(1))
                current_tp = int(m.group(2))
                continue

            m = re.match(r"^(.+?)\s{2,}([\d,]+)\s+([\d]+\.[\d]+)%?\s*$", line) or \
                re.match(r"^(.+?)\s+([\d,]+)\s+([\d]+\.[\d]+)%?\s*$", line)
            if m:
                cname = m.group(1).strip()
                votes = int(m.group(2).replace(",",""))
                pct   = float(m.group(3))
                if not re.search(r"\btotal\b|\bcast\b", cname, re.I):
                    current_cands.append({"name": cname, "votes": votes, "percentage": pct})
                continue

            if (line.isupper() or re.match(r"^[A-Z][A-Za-z\s\-/(),.#]+$", line)) \
               and len(line) > 5 and not re.search(r"\d", line):
                flush()
                current_name  = line
                current_cands = []
                current_pr    = 0
                current_tp    = 0

        flush()
        return contests

    def _extract_text_metadata(self, text: str) -> Dict:
        meta = {}
        m = re.search(r"(\d+)\s+of\s+(\d+)\s+precincts", text, re.I)
        if m:
            meta["precincts_reporting"] = int(m.group(1))
            meta["total_precincts"]     = int(m.group(2))
        m = re.search(r"Ballots?\s+Cast[:\s]+([\d,]+)", text, re.I)
        if m:
            meta["ballots_cast"] = int(m.group(1).replace(",",""))
        return meta

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _detect_party(self, name: str) -> str:
        u = name.upper()
        if "DEMOCRAT" in u or " - DEM" in u or "(DEM)" in u:
            return "Democratic"
        if "REPUBLICAN" in u or " - REP" in u or "(REP)" in u:
            return "Republican"
        return "Non-Partisan"

    def _build_output(self, contests: List[Dict], metadata: Dict) -> Dict:
        return {
            "county": "Marshall",
            "election_date": self.election_date,
            "scraped_at": datetime.now().isoformat(),
            "source": f"Marshall County Elections — {self.url}",
            "metadata": metadata,
            "contests": contests,
        }

    def _error_output(self, msg: str) -> Dict:
        print(f"  ❌ {msg}")
        return {
            "county": "Marshall",
            "election_date": self.election_date,
            "scraped_at": datetime.now().isoformat(),
            "error": msg,
            "contests": [],
        }

    def _no_url_output(self) -> Dict:
        print("""
╔══════════════════════════════════════════════════════════════╗
║          MARSHALL COUNTY SCRAPER — SETUP REQUIRED            ║
╚══════════════════════════════════════════════════════════════╝

Marshall County's results platform is not yet confirmed.

ELECTION DAY:
  1. Visit: https://www.marshallcountyil.gov
     Navigate to County Clerk → Elections → Results
  2. Find the March 17, 2026 Primary results (PDF or web page)
  3. Run:
       python marshall_county_scraper.py --url "URL_HERE" --output ./county_results

Note: Marshall County only affects two Regional Superintendent races
in the Illinois Valley market. If results cannot be found, those
races will show partial totals with a disclaimer.
        """)
        return {"county": "Marshall", "error": "No URL provided", "contests": []}

    def save_results(self, results: Dict, output_dir: str = "."):
        filename = f"{output_dir}/marshall_results.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print(f"✓ Saved to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Marshall County IL election results scraper"
    )
    parser.add_argument("--url",    help="Direct URL to results page or PDF")
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--date",   default="2026-03-17", help="Election date")
    args = parser.parse_args()

    scraper = MarshallCountyScraper(url=args.url, election_date=args.date)
    results = scraper.scrape()
    scraper.save_results(results, args.output)

    if results.get("error") and not args.url:
        sys.exit(0)
    elif results.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
