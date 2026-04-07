#!/usr/bin/env python3
"""
McLean County Election Results Scraper
Illinois Primary Election — March 17, 2026

McLean County has TWO election authorities:
  1. McLean County Clerk — county EXCEPT City of Bloomington (~65K voters)
       Platform: text/PDF summary documents posted to county website
       URL: https://www.mcleancountyil.gov/231/Past-McLean-County-Election-Results
  2. Bloomington Election Commission — City of Bloomington only (~55K voters)
       Platform: Clarity Elections
       URL: https://results.enr.clarityelections.com/IL/Bloomington

This scraper handles Part 1 (County Clerk text docs).
Part 2 is handled automatically by clarity_scraper.py when you add
Bloomington to config.json as platform=clarity.

For complete McLean County results on election night, run BOTH and let
aggregate_results.py combine them.

Output: mclean_county_clerk_results.json  (contests_by_party shape)

Election Day Setup:
  PART 1 — County Clerk (this scraper):
    1. Visit https://www.mcleancountyil.gov/231/Past-McLean-County-Election-Results
    2. Find "2026 Primary summary results" — right-click → copy link address
    3. Run: python mclean_county_scraper.py --url [URL] --output ./county_results

  PART 2 — Bloomington (clarity_scraper.py):
    1. Visit https://results.enr.clarityelections.com/IL/Bloomington
    2. Find March 17 Primary — note election_id and web_id from the URL
    3. Add to config.json:
         "Bloomington": {
           "platform":    "clarity",
           "base_url":    "https://results.enr.clarityelections.com/IL/Bloomington",
           "election_id": "XXXXX",
           "web_id":      "XXXXX"
         }
    4. Run: python clarity_scraper.py Bloomington --output ./county_results

Usage:
    python mclean_county_scraper.py --url https://...summary.txt
    python mclean_county_scraper.py --url https://...summary.txt --output ./county_results
"""

import re
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


# ── Party detection ───────────────────────────────────────────────────────────

def _detect_party(contest_name: str, section_name: str = "") -> str:
    for s in (section_name, contest_name):
        u = s.upper()
        if "DEMOCRATIC" in u or "DEM " in u or "(DEM)" in u or " - DEM" in u:
            return "Democratic"
        if "REPUBLICAN" in u or "REP " in u or "(REP)" in u or " - REP" in u:
            return "Republican"
        if "RETENTION" in u or "REFERENDUM" in u or "NONPARTISAN" in u or "NON-PARTISAN" in u:
            return "Non-Partisan"
    return "Non-Partisan"


# ── Document parsers ──────────────────────────────────────────────────────────

def _parse_text(text: str) -> List[Dict]:
    """
    Parse McLean County Clerk plain-text summary results.

    Expected format (varies slightly year to year):

      DEMOCRATIC PRIMARY
      COUNTY CLERK
      Jane Smith ........... 4,321  62.3%
      John Doe ............. 2,614  37.7%

      REPUBLICAN PRIMARY
      COUNTY SHERIFF
      ...
    """
    contests: List[Dict] = []
    current_section = "Non-Partisan"
    current_contest: Optional[Dict] = None

    def _save_contest():
        nonlocal current_contest
        if current_contest and current_contest.get("candidates"):
            # Recalculate percentages from actual votes
            total = sum(c["votes"] for c in current_contest["candidates"])
            if total > 0:
                for cand in current_contest["candidates"]:
                    cand["percentage"] = round(cand["votes"] / total * 100, 2)
            contests.append(current_contest)
        current_contest = None

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            # Blank line can mark end of a contest block
            continue

        u = line.upper()

        # Section headers
        if re.search(r"\bDEMOCRATIC\b.*\bPRIMARY\b|\bDEM\b.*\bPRIMARY\b", u):
            _save_contest()
            current_section = "Democratic"
            continue
        if re.search(r"\bREPUBLICAN\b.*\bPRIMARY\b|\bREP\b.*\bPRIMARY\b", u):
            _save_contest()
            current_section = "Republican"
            continue
        if re.search(r"\bNONPARTISAN\b|\bNON-PARTISAN\b", u):
            _save_contest()
            current_section = "Non-Partisan"
            continue

        # Contest headers: all-caps, no leading digits, no vote-count pattern
        # Heuristic: >= 5 chars, mostly uppercase, no "%" sign
        if (u == line or line == line.upper()) and len(line) >= 5 and "%" not in line:
            # Make sure it's not a candidate line disguised as a header
            if not re.search(r"\d{1,3}(,\d{3})*\s+\d+\.\d", line):
                _save_contest()
                current_contest = {
                    "contest_name": line.strip(),
                    "party":        _detect_party(line, current_section),
                    "county":       "McLean",
                    "candidates":   [],
                    "precincts_reporting": 0,
                    "total_precincts":     0,
                    "reporting_percentage": 0.0,
                }
                continue

        # Candidate line: split on runs of dots or multiple spaces
        if current_contest:
            parts = re.split(r"\.{2,}|\s{2,}", line)
            parts = [p.strip() for p in parts if p.strip()]

            if len(parts) >= 2:
                name  = parts[0]
                votes = None
                pct   = None

                for part in parts[1:]:
                    clean = part.replace(",", "").replace("%", "").strip()
                    if votes is None:
                        try:
                            votes = int(clean)
                            continue
                        except ValueError:
                            pass
                    if pct is None:
                        try:
                            pct = float(clean)
                        except ValueError:
                            pass

                if name and votes is not None:
                    current_contest["candidates"].append({
                        "name":       name,
                        "party":      "",
                        "votes":      votes,
                        "percentage": pct if pct is not None else 0.0,
                    })

    _save_contest()
    return contests


def _parse_html(html: str) -> List[Dict]:
    """Extract text from HTML and pass to _parse_text."""
    soup = BeautifulSoup(html, "html.parser")
    return _parse_text(soup.get_text(separator="\n"))


# ── Build standardized output ─────────────────────────────────────────────────

def _build_output(contests: List[Dict], doc_url: str) -> Dict:
    dem = [c for c in contests if c.get("party") == "Democratic"]
    rep = [c for c in contests if c.get("party") == "Republican"]
    np  = [c for c in contests if c.get("party") == "Non-Partisan"]

    return {
        "county":      "McLean",
        "authority":   "McLean County Clerk",
        "note":        "Covers McLean County EXCEPT City of Bloomington. "
                       "For full county totals, combine with Bloomington "
                       "(clarity_scraper.py).",
        "source_url":  doc_url,
        "scraped_at":  datetime.now().isoformat(),
        "total_contests": len(contests),
        "contests_by_party": {
            "Democratic":   {"count": len(dem), "contests": dem},
            "Republican":   {"count": len(rep), "contests": rep},
            "Non-Partisan": {"count": len(np),  "contests": np},
        },
    }


# ── Main scrape function ──────────────────────────────────────────────────────

def scrape_mclean(doc_url: str, output_dir: str = ".") -> Optional[Dict]:
    """
    Fetch and parse a McLean County Clerk summary document.

    Args:
        doc_url:    Direct URL to the TXT or HTML summary results document.
        output_dir: Directory to write mclean_county_clerk_results.json.

    Returns:
        Output dict, or None on fetch failure.
    """
    print(f"\n{'='*60}")
    print("McLean County Clerk (text/PDF summary)")
    print(f"{'='*60}")
    print(f"  URL: {doc_url}")
    print(f"  ⚠  Covers McLean County EXCEPT City of Bloomington")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        resp = requests.get(doc_url, headers=headers, timeout=60)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  ✗ Fetch failed: {exc}")
        return None

    ct = resp.headers.get("content-type", "")
    if "html" in ct:
        contests = _parse_html(resp.text)
    else:
        contests = _parse_text(resp.text)

    print(f"  ✅ {len(contests)} contests parsed")

    output   = _build_output(contests, doc_url)
    filepath = str(Path(output_dir) / "mclean_county_clerk_results.json")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(output, f, indent=2)

    cbp = output["contests_by_party"]
    print(f"  ✅ Saved to {filepath}")
    print(f"     Democratic:   {cbp['Democratic']['count']}")
    print(f"     Republican:   {cbp['Republican']['count']}")
    print(f"     Non-Partisan: {cbp['Non-Partisan']['count']}")
    print()
    print("  ⚠  REMINDER: Also run clarity_scraper.py for Bloomington")
    print("     to get complete McLean County totals.")
    return output


def main():
    parser = argparse.ArgumentParser(
        description="McLean County Clerk text/PDF results scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Election Day:
  1. Visit https://www.mcleancountyil.gov/231/Past-McLean-County-Election-Results
  2. Find "2026 Primary summary results" — right-click → copy link address
  3. python mclean_county_scraper.py --url [URL] --output ./county_results
  4. Also run: python clarity_scraper.py Bloomington --output ./county_results
        """,
    )
    parser.add_argument("--url", required=True,
                        help="Direct URL to McLean County summary results document")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    result = scrape_mclean(doc_url=args.url, output_dir=args.output)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
