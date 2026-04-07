#!/usr/bin/env python3
"""
Winnebago County Election Results Scraper
Illinois Primary Election — March 17, 2026

Winnebago County has TWO Clarity election authorities:
  1. Winnebago County Clerk — all of Winnebago County EXCEPT City of Rockford
       https://results.enr.clarityelections.com/WRC/Winnebago
  2. Rockford Board of Elections — City of Rockford only
       https://results.enr.clarityelections.com/WRC/Rockford

Both use the WRC (Winnebago-Rockford County) Clarity subdomain.
This scraper fetches both using details.json for correct vote totals,
then merges overlapping contests by candidate name so county-wide races
(e.g. Regional Superintendent) reflect the full county.

Output file: winnebago_results.json  (contests_by_party shape)

Election Day Setup:
  1. Visit https://results.enr.clarityelections.com/WRC/Winnebago
     → Find March 17 Primary → note election_id and web_id from URL
  2. Visit https://results.enr.clarityelections.com/WRC/Rockford
     → Do the same
  3. Update config.json under "Winnebago":
       "county_clerk_election_id": "XXXXX",
       "county_clerk_web_id":      "XXXXX",
       "rockford_election_id":     "XXXXX",
       "rockford_web_id":          "XXXXX"
  4. Run: python winnebago_county_scraper.py --output ./county_results

Usage:
    python winnebago_county_scraper.py
    python winnebago_county_scraper.py --output ./county_results
    python winnebago_county_scraper.py --config /path/to/config.json
"""

import json
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import canonical vote-fetching helpers from clarity_scraper
from clarity_scraper import (
    ClarityElectionsScraper,
    _fetch,
    _build_vote_lookup,
    _parse_contest,
    _detect_party,
    HEADERS,
)


# ── Fetch one Clarity authority ───────────────────────────────────────────────

def _fetch_authority(base_url: str, election_id: str, web_id: str,
                     label: str, county_name: str) -> List[Dict]:
    """
    Fetch and parse one Clarity authority using summary + details.json.

    Winnebago/Rockford use Web02.XXXXX path format instead of web.XXXXX.
    """
    web_path   = f"Web02.{web_id}"
    json_base  = f"{base_url}/{election_id}/{web_path}/json/en"
    detail_url = f"{base_url}/{election_id}/{web_path}/json/details.json"

    print(f"  [{label}] Fetching summary...")
    raw = _fetch(f"{json_base}/summary.json", base_url)
    if not raw:
        print(f"  [{label}] ✗ No summary data")
        return []

    summary = raw if isinstance(raw, list) else raw.get("Contests", [])
    print(f"  [{label}] {len(summary)} contests found")

    print(f"  [{label}] Fetching details.json for vote totals...")
    details = _fetch(detail_url, base_url)
    if details:
        vote_lookup = _build_vote_lookup(details)
        print(f"  [{label}] Vote data loaded for {len(vote_lookup)} contests")
    else:
        vote_lookup = {}
        print(f"  [{label}] ⚠ No details.json — vote totals will be 0")

    contests = []
    for raw_contest in summary:
        parsed = _parse_contest(raw_contest, vote_lookup, county_name)
        contests.append(parsed)

    print(f"  [{label}] ✅ {len(contests)} contests parsed")
    return contests


# ── Merge two authority contest lists ─────────────────────────────────────────

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.upper().strip())


def _merge_authorities(clerk_contests: List[Dict],
                       rockford_contests: List[Dict]) -> List[Dict]:
    """
    Merge County Clerk and Rockford Board contests.

    County-wide races appear in both — sum vote totals by candidate name.
    Rockford-only races are included as-is.
    After merging, recalculate percentages from combined totals.
    """
    merged: Dict[str, Dict] = {}

    for c in clerk_contests:
        key = _norm(c["contest_name"])
        merged[key] = c

    for rc in rockford_contests:
        key = _norm(rc["contest_name"])
        if key in merged:
            existing = merged[key]
            existing_cands = {_norm(c["name"]): c for c in existing["candidates"]}

            for rc_cand in rc["candidates"]:
                norm = _norm(rc_cand["name"])
                if norm in existing_cands:
                    existing_cands[norm]["votes"] += rc_cand["votes"]
                else:
                    existing["candidates"].append(dict(rc_cand))

            existing["precincts_reporting"] = (
                (existing.get("precincts_reporting") or 0) +
                (rc.get("precincts_reporting") or 0)
            )
            existing["total_precincts"] = (
                (existing.get("total_precincts") or 0) +
                (rc.get("total_precincts") or 0)
            )
        else:
            merged[key] = rc

    # Recalculate percentages after merging vote totals
    for contest in merged.values():
        total = sum(c["votes"] for c in contest["candidates"])
        if total > 0:
            for cand in contest["candidates"]:
                cand["percentage"] = round(cand["votes"] / total * 100, 2)
        tp = contest.get("total_precincts") or 0
        pr = contest.get("precincts_reporting") or 0
        contest["reporting_percentage"] = round(pr / tp * 100, 2) if tp > 0 else 0.0

    return list(merged.values())


# ── Build standardized output ─────────────────────────────────────────────────

def _build_output(contests: List[Dict]) -> Dict:
    dem = [c for c in contests if c.get("party") == "Democratic"]
    rep = [c for c in contests if c.get("party") == "Republican"]
    np  = [c for c in contests if c.get("party") == "Non-Partisan"]

    return {
        "county":         "Winnebago",
        "scraped_at":     datetime.now().isoformat(),
        "total_contests": len(contests),
        "contests_by_party": {
            "Democratic":   {"count": len(dem), "contests": dem},
            "Republican":   {"count": len(rep), "contests": rep},
            "Non-Partisan": {"count": len(np),  "contests": np},
        },
    }


# ── Main entry point ──────────────────────────────────────────────────────────

def scrape_winnebago(config_path: str = "config.json",
                     output_dir:  str = ".") -> Optional[Dict]:
    """
    Scrape both Winnebago Clarity authorities and merge results.

    Returns the output dict (also saves winnebago_results.json).
    """
    with open(config_path) as f:
        config = json.load(f)

    cfg = config.get("counties", {}).get("Winnebago", {})

    clerk_eid = cfg.get("county_clerk_election_id",
                        cfg.get("election_id", "UPDATE_ON_ELECTION_DAY"))
    clerk_wid = cfg.get("county_clerk_web_id",
                        cfg.get("web_id", "UPDATE_ON_ELECTION_DAY"))
    rock_eid  = cfg.get("rockford_election_id",
                        cfg.get("election_id", "UPDATE_ON_ELECTION_DAY"))
    rock_wid  = cfg.get("rockford_web_id",
                        cfg.get("web_id", "UPDATE_ON_ELECTION_DAY"))

    print(f"\n{'='*60}")
    print("Winnebago County (Dual Authority — Clarity)")
    print(f"{'='*60}")

    if "UPDATE" in str(clerk_eid):
        print("⚠ Winnebago election IDs not configured in config.json")
        print("  Set county_clerk_election_id, county_clerk_web_id,")
        print("      rockford_election_id, rockford_web_id")
        return None

    print(f"County Clerk : election_id={clerk_eid}  web_id={clerk_wid}")
    print(f"Rockford     : election_id={rock_eid}  web_id={rock_wid}")
    print()

    CLERK_BASE   = "https://results.enr.clarityelections.com/WRC/Winnebago"
    ROCKFORD_BASE = "https://results.enr.clarityelections.com/WRC/Rockford"

    clerk_contests    = _fetch_authority(CLERK_BASE,    clerk_eid, clerk_wid,
                                         "County Clerk",  "Winnebago")
    rockford_contests = _fetch_authority(ROCKFORD_BASE, rock_eid,  rock_wid,
                                         "Rockford Board", "Winnebago")

    all_contests = _merge_authorities(clerk_contests, rockford_contests)
    print(f"\n  Merged: {len(all_contests)} total contests")

    output = _build_output(all_contests)
    filepath = str(Path(output_dir) / "winnebago_results.json")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(output, f, indent=2)

    cbp = output["contests_by_party"]
    print(f"  ✅ Saved to {filepath}")
    print(f"     Democratic:   {cbp['Democratic']['count']}")
    print(f"     Republican:   {cbp['Republican']['count']}")
    print(f"     Non-Partisan: {cbp['Non-Partisan']['count']}")
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Winnebago County dual-authority Clarity scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Election Day Setup:
  1. Update config.json with both sets of election IDs
  2. python winnebago_county_scraper.py --output ./county_results
        """,
    )
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--config", default="config.json", help="Config file")
    args = parser.parse_args()

    result = scrape_winnebago(config_path=args.config, output_dir=args.output)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
