#!/usr/bin/env python3
"""
Pre-Election Candidate Name Validator
Illinois Primary Election — March 17, 2026

Run this the morning of the election to catch any candidate name mismatches
between the widget PENDING_CANDIDATES lists and the live county results JSON
before a single reader sees the widgets.

For each widget, it:
  1. Parses PENDING_CANDIDATES from the widget HTML
  2. Fetches the statewide_results.json from GitHub Pages
  3. Normalizes and compares all candidate names
  4. Reports any names in the live JSON that won't match a pending entry

Usage:
    python validate_candidates.py
    python validate_candidates.py --widgets-dir ./widgets --json-url https://...
    python validate_candidates.py --local-json ./statewide_results.json

Fix any reported mismatches by updating PENDING_CANDIDATES in the relevant widget.
"""

import re
import json
import sys
import argparse
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ── Configuration ─────────────────────────────────────────────────────────────

GITHUB_JSON_URL = 'https://mekcoleman.github.io/il-election-results/statewide_results.json'

# All widget files to validate
WIDGET_FILES = [
    'slm_widget.html',
    'ddc_widget.html',
    'kdj_widget.html',
    'svm_widget.html',
    'ocn_widget.html',
    'ilv_widget.html',
    'mhn_widget.html',
    'kcc_widget.html',
    'kcn_widget.html',
    'nwh_widget.html',
    'jhn_widget.html',
]

# ── Name normalization ─────────────────────────────────────────────────────────

def normalize(name: str) -> str:
    """
    Strip (i), nickname quotes, and extra whitespace for matching purposes.
    e.g. 'Daniel Hebreard (i)' → 'DANIEL HEBREARD'
         'Jacalynn "Jax" West' → 'JACALYNN JAX WEST'
         "Barbara A. O'Meara"  → "BARBARA A. OMEARA"
    """
    s = name
    s = re.sub(r'\s*\(i\)\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(u'[\u201c\u201d\u2018\u2019\'"`]', '', s)
    s = re.sub(r'\s+', ' ', s).strip().upper()
    return s
    s = re.sub(r'\s*\(i\)\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip().upper()
    return s

# ── Parse PENDING_CANDIDATES from widget HTML ──────────────────────────────────

def parse_pending_candidates(html: str, widget_name: str) -> Dict[str, Set[str]]:
    """
    Extract all candidate names from the PENDING_CANDIDATES JS object in a widget.
    Returns a dict mapping normalized name → original formatted name.
    """
    match = re.search(
        r'const\s+PENDING_CANDIDATES\s*=\s*\{(.+?)\n\};',
        html,
        re.DOTALL
    )
    if not match:
        print(f"  ⚠️  Could not find PENDING_CANDIDATES in {widget_name}")
        return {}

    block = match.group(1)

    # Match name: 'value' (single-quoted, may contain escaped single quotes or double quotes)
    # and name: "value" (double-quoted, may contain escaped double quotes or single quotes)
    names = []

    # Single-quoted: name: 'some name (i)' or name: 'O\'Meara' or name: '"Jax"'
    for m in re.finditer(r"name:\s*'((?:[^'\\]|\\.)*)'", block):
        names.append(m.group(1).replace("\\'", "'"))

    # Double-quoted: name: "some name" or name: "\"Jax\""
    for m in re.finditer(r'name:\s*"((?:[^"\\]|\\.)*)"', block):
        names.append(m.group(1).replace('\\"', '"'))

    name_map = {}
    for name in names:
        if name.strip().lower() in ('yes', 'no'):
            continue
        key = normalize(name)
        if key:
            name_map[key] = name

    return name_map

# ── Extract candidate names from statewide JSON ────────────────────────────────

def extract_json_candidates(data: dict) -> List[Tuple[str, str, str, str]]:
    """
    Extract all candidate names from the statewide results JSON.
    Returns list of (county, contest_name, party, candidate_name) tuples.
    """
    results = []

    county_results = data.get('county_results', {})
    for county, county_data in county_results.items():
        contests = []

        # Handle all three data shapes
        if 'by_party' in county_data:
            for party, bucket in county_data['by_party'].items():
                for c in bucket.get('contests', []):
                    contests.append((party, c))
        elif 'contests_by_party' in county_data:
            for party, bucket in county_data['contests_by_party'].items():
                for c in bucket.get('contests', []):
                    contests.append((party, c))
        elif 'contests' in county_data:
            for c in county_data.get('contests', []):
                contests.append((c.get('party', 'Unknown'), c))

        for party, contest in contests:
            contest_name = contest.get('contest_name') or contest.get('name') or ''
            for cand in contest.get('candidates', []):
                cand_name = cand.get('name', '').strip()
                if cand_name and cand_name.lower() not in ('yes', 'no'):
                    results.append((county, contest_name, party, cand_name))

    # Also check aggregated superintendent races
    supt_races = (data.get('multi_county_races') or {}).get('regional_superintendents', {})
    for race_id, race in supt_races.items():
        for cand in (race.get('candidates') or {}).values():
            cand_name = cand.get('name', '').strip()
            if cand_name and cand_name.lower() not in ('yes', 'no'):
                results.append(('(aggregated)', race.get('label', race_id), race_id, cand_name))

    return results

# ── Fetch JSON ────────────────────────────────────────────────────────────────

def fetch_json(url: str) -> Optional[dict]:
    if not REQUESTS_AVAILABLE:
        print("❌ requests library not installed. Run: pip install requests")
        return None
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def load_local_json(path: str) -> Optional[dict]:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load {path}: {e}")
        return None

# ── Main validation ───────────────────────────────────────────────────────────

def validate(widgets_dir: str, json_data: dict) -> bool:
    """
    Compare all widget PENDING_CANDIDATES against live JSON candidate names.
    Returns True if all clear, False if any mismatches found.
    """
    widgets_path = Path(widgets_dir)

    # Extract all candidates from the JSON once
    json_candidates = extract_json_candidates(json_data)
    print(f"  Found {len(json_candidates)} candidate entries in JSON\n")

    all_clear = True
    any_widget_found = False

    for widget_file in WIDGET_FILES:
        widget_path = widgets_path / widget_file
        if not widget_path.exists():
            continue

        any_widget_found = True
        print(f"── {widget_file} {'─' * max(0, 50 - len(widget_file))}")

        html = widget_path.read_text(encoding='utf-8')
        pending_map = parse_pending_candidates(html, widget_file)

        if not pending_map:
            print(f"  ⚠️  No PENDING_CANDIDATES found — skipping\n")
            continue

        print(f"  Pending candidates loaded: {len(pending_map)}")

        # Find JSON candidates that don't match any pending entry
        mismatches = []
        for county, contest, party, cand_name in json_candidates:
            key = normalize(cand_name)
            if key and key not in pending_map:
                mismatches.append((county, contest, party, cand_name))

        if mismatches:
            all_clear = False
            print(f"  ❌ {len(mismatches)} unmatched name(s):\n")
            for county, contest, party, name in mismatches:
                norm = normalize(name)
                print(f"     Name in JSON : \"{name}\"")
                print(f"     Normalized   : \"{norm}\"")
                print(f"     Contest      : {contest}")
                print(f"     County/Party : {county} / {party}")
                print(f"     Fix          : Add to PENDING_CANDIDATES in {widget_file}")
                print()
        else:
            print(f"  ✅ All {len(pending_map)} names matched\n")

    if not any_widget_found:
        print(f"⚠️  No widget files found in {widgets_dir}")
        print(f"   Looking for: {', '.join(WIDGET_FILES)}")
        return False

    return all_clear


def main():
    parser = argparse.ArgumentParser(
        description='Validate widget candidate names against live election JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch live JSON from GitHub and validate all widgets in current directory
  python validate_candidates.py

  # Use a local JSON file (useful before results are posted)
  python validate_candidates.py --local-json ./statewide_results.json

  # Specify widget directory
  python validate_candidates.py --widgets-dir ./widgets

  # Use a different JSON URL
  python validate_candidates.py --json-url https://your-url/statewide_results.json
        """
    )
    parser.add_argument('--widgets-dir', default='.',
                        help='Directory containing widget HTML files (default: current dir)')
    parser.add_argument('--json-url', default=GITHUB_JSON_URL,
                        help='URL to statewide_results.json')
    parser.add_argument('--local-json', default=None,
                        help='Path to local statewide_results.json (skips network fetch)')
    args = parser.parse_args()

    print()
    print('=' * 60)
    print('  PRE-ELECTION CANDIDATE NAME VALIDATOR')
    print('  Illinois Primary — March 17, 2026')
    print('=' * 60)
    print()

    # Load JSON
    if args.local_json:
        print(f"Loading local JSON: {args.local_json}")
        json_data = load_local_json(args.local_json)
    else:
        print(f"Fetching live JSON: {args.json_url}")
        json_data = fetch_json(args.json_url)

    if not json_data:
        sys.exit(1)

    print(f"JSON loaded — counties: {', '.join(json_data.get('counties_included', ['?']))}\n")

    # Validate
    all_clear = validate(args.widgets_dir, json_data)

    print('=' * 60)
    if all_clear:
        print('  ✅ ALL CLEAR — no name mismatches found')
        print('     All candidate names will display correctly on election night.')
    else:
        print('  ❌ MISMATCHES FOUND — fix before polls close!')
        print('     Update PENDING_CANDIDATES in the listed widgets,')
        print('     then re-run this script to confirm all clear.')
    print('=' * 60)
    print()

    sys.exit(0 if all_clear else 1)


if __name__ == '__main__':
    main()
