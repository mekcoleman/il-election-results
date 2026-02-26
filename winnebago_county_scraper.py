#!/usr/bin/env python3
"""
Winnebago County Election Results Scraper
Illinois Primary Election — March 17, 2026

Winnebago County has TWO election authorities, both using Clarity Elections:
  1. Winnebago County Clerk — all of Winnebago County EXCEPT the City of Rockford
  2. Rockford Board of Elections — City of Rockford only

Both use the WRC (Winnebago-Rockford-County?) path on Clarity:
  https://results.enr.clarityelections.com/WRC/Winnebago/{id}/
  https://results.enr.clarityelections.com/WRC/Rockford/{id}/

This scraper fetches both, then merges their results by contest name so that
vote totals for county-wide races (like Regional Superintendent) reflect the
full county.

ELECTION DAY SETUP:
  1. Visit https://results.enr.clarityelections.com/WRC/Winnebago
     → Find March 17 Primary → note the election_id in the URL
  2. Visit https://results.enr.clarityelections.com/WRC/Rockford
     → Find March 17 Primary → note the election_id (may differ from County Clerk)
  3. Update config.json:
       "Winnebago": {
         "county_clerk_election_id": "XXXXX",
         "county_clerk_web_id": "XXXXX",
         "rockford_election_id": "XXXXX",
         "rockford_web_id": "XXXXX"
       }
  4. Run: python winnebago_county_scraper.py --output ./county_results

Usage:
    python winnebago_county_scraper.py --output ./county_results
    python winnebago_county_scraper.py  # saves to current directory
"""

import requests
import json
import re
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Optional


class WinnebagoCountyScraper:
    """Scraper for Winnebago County dual-authority Clarity Elections results."""

    COUNTY_CLERK_BASE = "https://results.enr.clarityelections.com/WRC/Winnebago"
    ROCKFORD_BASE     = "https://results.enr.clarityelections.com/WRC/Rockford"

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.county_name = "Winnebago"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        with open(config_path) as f:
            cfg = json.load(f)
        self.cfg = cfg["counties"].get("Winnebago", {})

    # ── Clarity fetch helpers ─────────────────────────────────────────────────

    def _fetch_clarity(self, base_url: str, election_id: str, web_id: str,
                       authority_label: str) -> List[Dict]:
        """Fetch and parse contests from one Clarity authority."""
        summary_url = f"{base_url}/{election_id}/json/en/summary.json"
        version_url = f"{base_url}/{election_id}/{web_id}/json/en/electionsettings.json"

        print(f"  [{authority_label}] Fetching: {summary_url}")
        try:
            # Some Clarity instances need the web_id in the path
            resp = self.session.get(summary_url, timeout=20)
            if resp.status_code == 404:
                # Try alternate path with web_id
                summary_url = f"{base_url}/{election_id}/{web_id}/json/en/summary.json"
                resp = self.session.get(summary_url, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [{authority_label}] ❌ Fetch failed: {e}")
            return []

        contests = []
        for contest_data in (data.get("Contests") or data.get("contests") or []):
            contest = self._parse_contest(contest_data, authority_label)
            if contest:
                contests.append(contest)

        print(f"  [{authority_label}] ✓ {len(contests)} contests")
        return contests

    def _parse_contest(self, data: Dict, source: str) -> Optional[Dict]:
        """Parse a single Clarity contest dict into normalized format."""
        name = (data.get("C") or data.get("N") or data.get("contest_name") or "").strip()
        if not name:
            return None

        party = self._detect_party(name)
        candidates = []

        for cand in (data.get("CH") or data.get("Candidates") or data.get("candidates") or []):
            cand_name = (cand.get("N") or cand.get("C") or cand.get("name") or "").strip()
            votes_raw = cand.get("V") or cand.get("votes") or 0
            try:
                votes = int(str(votes_raw).replace(",", ""))
            except (ValueError, TypeError):
                votes = 0

            pct_raw = cand.get("P") or cand.get("percentage") or 0.0
            try:
                pct = float(pct_raw)
            except (ValueError, TypeError):
                pct = 0.0

            if cand_name:
                candidates.append({
                    "name": cand_name,
                    "votes": votes,
                    "percentage": pct,
                    "party": (cand.get("PT") or party),
                })

        if not candidates:
            return None

        precincts_reporting = data.get("PR") or data.get("precincts_reporting") or 0
        total_precincts     = data.get("P")  or data.get("total_precincts") or 0

        return {
            "contest_name": name,
            "name": name,
            "party": party,
            "party_type": party,
            "candidates": candidates,
            "precincts_reporting": precincts_reporting,
            "total_precincts": total_precincts,
            "_source": source,
        }

    def _detect_party(self, name: str) -> str:
        u = name.upper()
        if "DEMOCRAT" in u or " - DEM" in u or "(DEM)" in u:
            return "Democratic"
        if "REPUBLICAN" in u or " - REP" in u or "(REP)" in u:
            return "Republican"
        return "Non-Partisan"

    # ── Merge logic ───────────────────────────────────────────────────────────

    def _merge_contests(self, clerk_contests: List[Dict],
                        rockford_contests: List[Dict]) -> List[Dict]:
        """
        Merge County Clerk and Rockford contests.

        For county-wide races (e.g. Regional Superintendent of Schools),
        both authorities will report the same contest name but different
        vote totals. We sum the candidates by name.

        For Rockford-only races (City Council, etc.), we include them as-is.
        """
        # Index clerk contests by normalized name
        merged: Dict[str, Dict] = {}
        for c in clerk_contests:
            key = self._normalize_contest_name(c["contest_name"])
            merged[key] = c

        for rc in rockford_contests:
            key = self._normalize_contest_name(rc["contest_name"])
            if key in merged:
                # Merge vote totals into existing contest
                existing = merged[key]
                existing_cands = {self._normalize_name(c["name"]): c
                                  for c in existing["candidates"]}
                for rc_cand in rc["candidates"]:
                    norm = self._normalize_name(rc_cand["name"])
                    if norm in existing_cands:
                        existing_cands[norm]["votes"] += rc_cand["votes"]
                    else:
                        # Candidate exists only in Rockford (write-ins, etc.)
                        existing["candidates"].append(rc_cand)

                # Update precinct counts
                existing["precincts_reporting"] = (
                    (existing.get("precincts_reporting") or 0) +
                    (rc.get("precincts_reporting") or 0)
                )
                existing["total_precincts"] = (
                    (existing.get("total_precincts") or 0) +
                    (rc.get("total_precincts") or 0)
                )
                existing["_source"] = "Winnebago County Clerk + Rockford Board"
            else:
                # Rockford-only race
                merged[key] = rc

        # Recalculate percentages after merge
        for contest in merged.values():
            total_votes = sum(c["votes"] for c in contest["candidates"])
            if total_votes > 0:
                for cand in contest["candidates"]:
                    cand["percentage"] = round(cand["votes"] / total_votes * 100, 1)

        return list(merged.values())

    def _normalize_contest_name(self, name: str) -> str:
        """Normalize contest name for matching across authorities."""
        return re.sub(r"\s+", " ", name.upper().strip())

    def _normalize_name(self, name: str) -> str:
        return re.sub(r"\s+", " ", name.upper().strip())

    # ── Main scrape ───────────────────────────────────────────────────────────

    def scrape(self) -> Dict:
        """Scrape both Clarity authorities and merge results."""
        print(f"\n{'='*60}")
        print(f"Winnebago County (Dual Authority)")
        print(f"{'='*60}")

        # Get election IDs from config
        clerk_eid = self.cfg.get("county_clerk_election_id",
                                 self.cfg.get("election_id", "UPDATE_ON_ELECTION_DAY"))
        clerk_wid = self.cfg.get("county_clerk_web_id",
                                 self.cfg.get("web_id", "UPDATE_ON_ELECTION_DAY"))
        rock_eid  = self.cfg.get("rockford_election_id",
                                 self.cfg.get("election_id", "UPDATE_ON_ELECTION_DAY"))
        rock_wid  = self.cfg.get("rockford_web_id",
                                 self.cfg.get("web_id", "UPDATE_ON_ELECTION_DAY"))

        if "UPDATE_ON_ELECTION_DAY" in str(clerk_eid):
            print("⚠️  Winnebago election IDs not configured.")
            print("   Update config.json with county_clerk_election_id and rockford_election_id")
            return self._empty_output("Election IDs not configured")

        print(f"County Clerk election ID : {clerk_eid}")
        print(f"Rockford election ID     : {rock_eid}")
        print()

        # Fetch both
        clerk_contests    = self._fetch_clarity(self.COUNTY_CLERK_BASE, clerk_eid, clerk_wid,
                                                "County Clerk")
        rockford_contests = self._fetch_clarity(self.ROCKFORD_BASE, rock_eid, rock_wid,
                                                "Rockford Board")

        # Merge
        all_contests = self._merge_contests(clerk_contests, rockford_contests)
        print(f"\n  Merged: {len(all_contests)} total contests")

        # Build output in standard format
        output = {
            "county": "Winnebago",
            "election_date": "2026-03-17",
            "scraped_at": datetime.now().isoformat(),
            "source": "Winnebago County Clerk + Rockford Board of Elections (Clarity)",
            "contests": all_contests,
        }
        return output

    def _empty_output(self, reason: str) -> Dict:
        return {
            "county": "Winnebago",
            "election_date": "2026-03-17",
            "scraped_at": datetime.now().isoformat(),
            "error": reason,
            "contests": [],
        }

    def save_results(self, results: Dict, output_dir: str = "."):
        filename = f"{output_dir}/winnebago_results.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print(f"✓ Saved to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Winnebago County dual-authority Clarity scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ELECTION DAY SETUP:
  1. Visit https://results.enr.clarityelections.com/WRC/Winnebago
     Find March 17 2026 Primary — note the election_id and web_id from the URL
  2. Visit https://results.enr.clarityelections.com/WRC/Rockford
     Do the same for Rockford
  3. Add to config.json under "Winnebago":
       "county_clerk_election_id": "XXXXX",
       "county_clerk_web_id":      "XXXXX",
       "rockford_election_id":     "XXXXX",
       "rockford_web_id":          "XXXXX"
  4. Run this script
        """
    )
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--config", default="config.json", help="Config file path")
    args = parser.parse_args()

    scraper = WinnebagoCountyScraper(config_path=args.config)
    results = scraper.scrape()
    scraper.save_results(results, args.output)

    if results.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
