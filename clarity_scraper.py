#!/usr/bin/env python3
"""
Clarity Elections Scraper — canonical driver for all Illinois Clarity counties.

Fetches summary.json (contest metadata + candidate names) and details.json
(actual precinct-level vote totals) and merges them into a clean output.

Output shape (written to file and returned from scrape_county()):
  {
    "county":           "Will",
    "scraped_at":       "2026-03-17T20:15:30.123456",
    "total_contests":   47,
    "contests_by_party": {
      "Democratic":   {"count": N, "contests": [...]},
      "Republican":   {"count": N, "contests": [...]},
      "Non-Partisan": {"count": N, "contests": [...]}
    }
  }

Each contest dict:
  {
    "contest_id":           "1001",
    "contest_name":         "COUNTY CLERK",
    "party":                "Republican",
    "county":               "Will",
    "candidates": [
      {"name": "Jane Smith", "party": "REP", "votes": 12345, "percentage": 62.3}
    ],
    "precincts_reporting":  142,
    "total_precincts":      142,
    "reporting_percentage": 100.0
  }

Public API:
    from clarity_scraper import scrape_county, scrape_all_clarity_counties

    # Returns the output dict (also saves to <county_lower>_results.json)
    data = scrape_county("Will")
    data = scrape_county("McHenry", config_path="config.json", output_dir="./county_results")

    # Scrapes every county marked platform=clarity in config.json
    all_data = scrape_all_clarity_counties(output_dir="./county_results")
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests


# ── HTTP helpers ──────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
}


def _fetch(url: str, referer: str = "") -> Optional[Dict]:
    """GET a JSON URL, return parsed dict or None on failure."""
    headers = {**HEADERS, "Referer": referer}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        print(f"  ✗ Fetch failed {url}: {exc}")
        return None


# ── Vote lookup from details.json ─────────────────────────────────────────────

def _build_vote_lookup(details: Dict) -> Dict[str, Dict]:
    """
    Parse details.json into a lookup keyed by contest K string.

    details.json structure:
      Contests[i].K  = contest key (matches summary.json contest K field)
      Contests[i].V  = list of per-precinct sublists [[cand0_votes, cand1_votes, ...], ...]
      Contests[i].T  = list of per-precinct total-ballot counts (used for precinct count)

    Returns:
      { "1001": {"votes": [12345, 9876], "precincts_reporting": 142, "total_precincts": 142}, ... }
    """
    lookup: Dict[str, Dict] = {}

    for contest in details.get("Contests", []):
        k = str(contest.get("K", ""))
        v_data = contest.get("V", [])   # per-precinct vote matrix
        t_data = contest.get("T", [])   # per-precinct totals (just used for count)

        if not v_data:
            lookup[k] = {"votes": [], "precincts_reporting": 0,
                         "total_precincts": len(t_data)}
            continue

        first = v_data[0] if v_data else []
        num_candidates = len(first) if isinstance(first, list) else 1
        candidate_totals = [0] * num_candidates
        precincts_reporting = 0

        for precinct_row in v_data:
            if isinstance(precinct_row, list):
                if any(x > 0 for x in precinct_row):
                    precincts_reporting += 1
                for ci, votes in enumerate(precinct_row):
                    if ci < num_candidates:
                        candidate_totals[ci] += int(votes or 0)
            elif isinstance(precinct_row, (int, float)) and precinct_row > 0:
                precincts_reporting += 1
                if num_candidates == 1:
                    candidate_totals[0] += int(precinct_row)

        lookup[k] = {
            "votes": candidate_totals,
            "precincts_reporting": precincts_reporting,
            "total_precincts": len(t_data) if t_data else len(v_data),
        }

    return lookup


# ── Party detection ───────────────────────────────────────────────────────────

def _detect_party(contest: Dict) -> str:
    """
    Return 'Democratic', 'Republican', or 'Non-Partisan' for a summary contest.

    Checks (in order):
      1. P field (party list, e.g. ['REP'] or ['DEM'])
      2. Contest name keywords
      3. Special types (RETENTION → Non-Partisan, REFERENDUM → Non-Partisan)
    """
    name = str(contest.get("C", "")).upper()

    # Hard non-partisan types
    if "RETENTION" in name or "REFERENDUM" in name or "BALLOT QUESTION" in name:
        return "Non-Partisan"

    # P field: Clarity stores party as a list, e.g. ['REP'] or ['DEM', 'DEM']
    party_list = contest.get("P", [])
    if isinstance(party_list, list) and party_list:
        p = str(party_list[0]).upper()
    else:
        p = str(party_list).upper()

    if "DEM" in p:
        return "Democratic"
    if "REP" in p:
        return "Republican"

    # Fall back to name
    if "DEMOCRATIC" in name or "DEM " in name or "(DEM)" in name:
        return "Democratic"
    if "REPUBLICAN" in name or "REP " in name or "(REP)" in name:
        return "Republican"

    return "Non-Partisan"


# ── Contest parser ────────────────────────────────────────────────────────────

def _parse_contest(contest: Dict, vote_lookup: Dict, county: str) -> Dict:
    """
    Merge a summary.json contest with its details.json vote totals.

    Returns a normalized contest dict ready for output.
    """
    k = str(contest.get("K", ""))
    detail = vote_lookup.get(k, {})
    party = _detect_party(contest)

    precincts_reporting = detail.get("precincts_reporting",
                                     contest.get("PR", 0))
    total_precincts     = detail.get("total_precincts",
                                     contest.get("TP", 0))
    reporting_pct = (
        round(precincts_reporting / total_precincts * 100, 2)
        if total_precincts > 0 else 0.0
    )

    # Candidate names from summary CH[], votes from details lookup
    names       = contest.get("CH", [])
    votes_list  = detail.get("votes", [])
    pct_list    = contest.get("PCT", [])  # summary percentages (fallback only)
    raw_parties = contest.get("P", [])

    total_votes = sum(votes_list) if votes_list else 0
    candidates  = []

    for i, name in enumerate(names):
        name = str(name).strip()
        if not name:
            continue
        votes = int(votes_list[i]) if i < len(votes_list) else 0

        # Recalculate percentage from actual votes; fall back to summary PCT
        if total_votes > 0:
            pct = round(votes / total_votes * 100, 2)
        elif i < len(pct_list):
            try:
                pct = float(pct_list[i])
            except (TypeError, ValueError):
                pct = 0.0
        else:
            pct = 0.0

        cand_party = (
            str(raw_parties[i]) if isinstance(raw_parties, list) and i < len(raw_parties)
            else str(raw_parties) if raw_parties else ""
        )

        candidates.append({
            "name":       name,
            "party":      cand_party,
            "votes":      votes,
            "percentage": pct,
        })

    return {
        "contest_id":           k,
        "contest_name":         contest.get("C", ""),
        "party":                party,
        "county":               county,
        "candidates":           candidates,
        "precincts_reporting":  precincts_reporting,
        "total_precincts":      total_precincts,
        "reporting_percentage": reporting_pct,
    }


# ── Main scraper class ────────────────────────────────────────────────────────

class ClarityElectionsScraper:
    """
    Scrapes one Clarity Elections county using summary.json + details.json.

    Usage:
        scraper = ClarityElectionsScraper(
            base_url   = "https://results.enr.clarityelections.com/IL/Will",
            election_id= "126051",
            web_id     = "369020",
            county_name= "Will",
        )
        output = scraper.scrape()          # returns output dict
        scraper.save(output, "will_results.json")
    """

    def __init__(self, base_url: str, election_id: str, web_id: str,
                 county_name: str):
        self.base_url    = base_url.rstrip("/")
        self.election_id = election_id
        self.web_id      = web_id
        self.county_name = county_name
        self.json_base   = (
            f"{self.base_url}/{election_id}/{web_id}/json/en"
        )

    def _fetch_summary(self) -> Optional[List]:
        data = _fetch(f"{self.json_base}/summary.json", self.base_url)
        if data is None:
            return None
        return data if isinstance(data, list) else data.get("Contests", [])

    def _fetch_details(self) -> Optional[Dict]:
        # details.json lives one level up from json/en/
        url = f"{self.base_url}/{self.election_id}/{self.web_id}/json/details.json"
        return _fetch(url, self.base_url)

    def scrape(self) -> Dict:
        """Fetch, parse, and return the standardized output dict."""
        print(f"\n{'='*60}")
        print(f"Scraping {self.county_name} County (Clarity)")
        print(f"{'='*60}")

        summary = self._fetch_summary()
        if not summary:
            print(f"  ✗ No summary data for {self.county_name}")
            return self._empty_output("No summary data returned")

        print(f"  Found {len(summary)} contests in summary.json")

        details = self._fetch_details()
        if details:
            vote_lookup = _build_vote_lookup(details)
            print(f"  Vote data loaded for {len(vote_lookup)} contests from details.json")
        else:
            vote_lookup = {}
            print(f"  ⚠ No details.json — vote totals will be 0")

        contests: List[Dict] = []
        for raw in summary:
            parsed = _parse_contest(raw, vote_lookup, self.county_name)
            contests.append(parsed)

        print(f"  ✅ {len(contests)} contests parsed")
        return self._build_output(contests)

    def _build_output(self, contests: List[Dict]) -> Dict:
        dem = [c for c in contests if c["party"] == "Democratic"]
        rep = [c for c in contests if c["party"] == "Republican"]
        np  = [c for c in contests if c["party"] == "Non-Partisan"]

        return {
            "county":     self.county_name,
            "scraped_at": datetime.now().isoformat(),
            "total_contests": len(contests),
            "contests_by_party": {
                "Democratic":   {"count": len(dem), "contests": dem},
                "Republican":   {"count": len(rep), "contests": rep},
                "Non-Partisan": {"count": len(np),  "contests": np},
            },
        }

    def _empty_output(self, reason: str) -> Dict:
        return {
            "county":     self.county_name,
            "scraped_at": datetime.now().isoformat(),
            "error":      reason,
            "total_contests": 0,
            "contests_by_party": {
                "Democratic":   {"count": 0, "contests": []},
                "Republican":   {"count": 0, "contests": []},
                "Non-Partisan": {"count": 0, "contests": []},
            },
        }

    def save(self, output: Dict, filepath: str) -> None:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
        cbp = output.get("contests_by_party", {})
        print(f"  ✅ Saved to {filepath}")
        print(f"     Democratic:   {cbp.get('Democratic',   {}).get('count', 0)}")
        print(f"     Republican:   {cbp.get('Republican',   {}).get('count', 0)}")
        print(f"     Non-Partisan: {cbp.get('Non-Partisan', {}).get('count', 0)}")


# ── Public API ────────────────────────────────────────────────────────────────

def scrape_county(county_name: str,
                  config_path: str = "config.json",
                  output_dir:  str = ".") -> Optional[Dict]:
    """
    Scrape one Clarity county by name, save results, return output dict.

    Args:
        county_name: Must match a key in config.json counties with platform=clarity
        config_path: Path to config.json
        output_dir:  Directory to write <county_lower>_results.json

    Returns:
        Output dict, or None on configuration error.
    """
    with open(config_path) as f:
        config = json.load(f)

    cfg = config.get("counties", {}).get(county_name)
    if not cfg:
        print(f"✗ '{county_name}' not found in {config_path}")
        return None
    if cfg.get("platform") != "clarity":
        print(f"✗ '{county_name}' platform is '{cfg.get('platform')}', not clarity")
        return None
    if cfg.get("election_id", "").startswith("UPDATE"):
        print(f"⚠ Election IDs not yet configured for {county_name} in {config_path}")
        return None

    scraper = ClarityElectionsScraper(
        base_url    = cfg["base_url"],
        election_id = cfg["election_id"],
        web_id      = cfg["web_id"],
        county_name = county_name,
    )

    output   = scraper.scrape()
    slug     = county_name.lower().replace(" ", "_")
    filepath = str(Path(output_dir) / f"{slug}_results.json")
    scraper.save(output, filepath)
    return output


def scrape_all_clarity_counties(config_path: str = "config.json",
                                output_dir:  str = ".") -> Dict[str, Dict]:
    """
    Scrape every county in config.json with platform=clarity.

    Returns:
        Dict mapping county_name → output dict for successful scrapes.
    """
    with open(config_path) as f:
        config = json.load(f)

    clarity_counties = [
        name for name, cfg in config.get("counties", {}).items()
        if cfg.get("platform") == "clarity"
    ]

    print(f"\n{'='*60}")
    print(f"Found {len(clarity_counties)} Clarity counties:")
    for c in clarity_counties:
        print(f"  - {c}")
    print()

    results: Dict[str, Dict] = {}
    for county in clarity_counties:
        data = scrape_county(county, config_path=config_path, output_dir=output_dir)
        if data and "error" not in data:
            results[county] = data
        print()

    print(f"\n{'='*60}")
    print(f"Complete: {len(results)}/{len(clarity_counties)} counties scraped")
    for county in results:
        total = results[county].get("total_contests", 0)
        print(f"  ✅ {county}: {total} contests")
    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Scrape Illinois Clarity Elections counties",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clarity_scraper.py                          # all clarity counties
  python clarity_scraper.py Will                     # one county
  python clarity_scraper.py Will --output ./results  # specify output dir
        """,
    )
    parser.add_argument("county", nargs="?", help="County name (omit for all)")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    if args.county:
        result = scrape_county(args.county,
                               config_path=args.config,
                               output_dir=args.output)
        sys.exit(0 if result else 1)
    else:
        scrape_all_clarity_counties(config_path=args.config,
                                    output_dir=args.output)


if __name__ == "__main__":
    main()
