"""
La Salle County Election Results Scraper
Scrapes election results from PDF posted to the county website.

La Salle County posts a "Election Summary Report" PDF to their document center.
The PDF URL pattern is:
  https://lasallecountyil.gov/DocumentCenter/View/{DOC_ID}/Election-Summary-Report

Usage:
    # Basic scrape (uses URL from config.json)
    python la_salle_county_scraper.py

    # Specify output directory
    python la_salle_county_scraper.py --output ./county_results

    # Specify a direct PDF URL (useful on election night before config is updated)
    python la_salle_county_scraper.py --url https://lasallecountyil.gov/DocumentCenter/View/9999/Election-Summary-Report

Election Night:
    1. Visit https://lasallecountyil.gov/elections and find the live results PDF link
    2. Copy the document ID from the URL (the number after /View/)
    3. Update config.json: set "doc_id" under La Salle county
    4. Run: python la_salle_county_scraper.py --output ./county_results

PDF Format (confirmed from April 2025 election):
    CONTEST NAME IN ALL CAPS
    Number of Precincts  N
    Precincts Reporting  N
    Vote For  N
    Candidate Name (PARTY)  votes  percent%
    ...
    Total Votes  N
    percent%
"""

import re
import json
import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing dependency: pip install requests")
    sys.exit(1)

try:
    import pdfplumber
except ImportError:
    print("Missing dependency: pip install pdfplumber")
    sys.exit(1)


# ── Constants ────────────────────────────────────────────────────────────────

COUNTY_NAME = "La Salle"
DEFAULT_OUTPUT_DIR = "."
CONFIG_PATH = "config.json"

# Party abbreviations found in La Salle County PDFs → normalized label
PARTY_MAP = {
    "DEM": "Democratic",
    "REP": "Republican",
    "IND": "Non-Partisan",
    "NP":  "Non-Partisan",
    "WI":  "Non-Partisan",   # write-in, treated as non-partisan
    "GRN": "Non-Partisan",
    "LIB": "Non-Partisan",
}

# Contest name keywords that indicate party even without a (PARTY) tag on candidates
PARTY_KEYWORDS = {
    "Democratic": ["- DEMOCRATIC", "DEMOCRATIC PRIMARY", "(DEMOCRATIC)"],
    "Republican": ["- REPUBLICAN", "REPUBLICAN PRIMARY", "(REPUBLICAN)"],
}

# Categories we care about for the March 2026 primary widget
# (township/city/village/library/school board are non-partisan local races,
#  kept in Non-Partisan bucket; county-level and judicial are the key ones)
CATEGORY_MAP = {
    "county clerk":        "County",
    "county treasurer":    "County",
    "county sheriff":      "County",
    "county board":        "County",
    "regional superintendent": "County",
    "appellate":           "Judicial",
    "circuit":             "Judicial",
    "subcircuit":          "Judicial",
    "referendum":          "Referendum",
    "proposition":         "Referendum",
    "advisory":            "Referendum",
    "tax rate":            "Referendum",
    "bond":                "Referendum",
}


# ── PDF Download ─────────────────────────────────────────────────────────────

def load_config() -> dict:
    """Load config.json if it exists."""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse {CONFIG_PATH}: {e}")
        return {}


def get_pdf_url(args) -> str:
    """
    Determine the PDF URL to fetch.
    Priority: --url CLI arg > config.json doc_id > config.json base_url
    """
    if args.url:
        return args.url

    config = load_config()
    county_cfg = config.get("counties", {}).get(COUNTY_NAME, {})

    # If config has a specific doc_id for the current election
    doc_id = county_cfg.get("doc_id") or county_cfg.get("election_doc_id")
    if doc_id and str(doc_id) != "UPDATE_ON_ELECTION_DAY":
        return f"https://lasallecountyil.gov/DocumentCenter/View/{doc_id}/Election-Summary-Report"

    # Fall back to base_url if set
    base_url = county_cfg.get("base_url", "")
    if base_url and "UPDATE_ON_ELECTION_DAY" not in base_url:
        return base_url

    # Nothing configured — tell user what to do
    print()
    print("=" * 60)
    print("La Salle County PDF URL not configured.")
    print()
    print("On election night:")
    print("  1. Go to https://lasallecountyil.gov/elections")
    print("  2. Find the 'Election Results' PDF link")
    print("  3. Note the document ID from the URL, e.g.:")
    print("     .../DocumentCenter/View/4294/Election-Summary-Report")
    print("     Document ID = 4294")
    print()
    print("  Then either:")
    print("  A) Run with --url flag:")
    print("     python la_salle_county_scraper.py --url https://lasallecountyil.gov/DocumentCenter/View/4294/Election-Summary-Report")
    print()
    print("  B) Update config.json under 'La Salle':")
    print('     "doc_id": "4294"')
    print("=" * 60)
    print()
    sys.exit(1)


def download_pdf(url: str) -> bytes:
    """Download PDF from URL and return raw bytes."""
    print(f"  Fetching: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ShawLocalElectionScraper/1.0)"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "pdf" not in content_type and len(resp.content) < 1000:
            raise ValueError(f"Response doesn't look like a PDF (content-type: {content_type})")
        print(f"  Downloaded {len(resp.content):,} bytes")
        return resp.content
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Could not connect to {url}")
        print("    Check your internet connection or verify the URL is correct.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"  ✗ HTTP error: {e}")
        print("    The PDF may not be posted yet, or the document ID may be wrong.")
        sys.exit(1)


# ── PDF Parsing ───────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract all text from PDF using pdfplumber."""
    import io
    lines = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        print(f"  PDF has {len(pdf.pages)} pages")
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.append(text)
    return "\n".join(lines)


def detect_party_from_name(contest_name: str) -> str:
    """Detect party from contest name keywords."""
    upper = contest_name.upper()
    for party, keywords in PARTY_KEYWORDS.items():
        for kw in keywords:
            if kw in upper:
                return party
    return None


def normalize_party(party_code: str, contest_party: str = None) -> str:
    """
    Normalize a party abbreviation to Democratic / Republican / Non-Partisan.
    Falls back to contest_party if candidate has no party tag.
    """
    if party_code:
        return PARTY_MAP.get(party_code.upper(), "Non-Partisan")
    if contest_party:
        return contest_party
    return "Non-Partisan"


def detect_category(contest_name: str) -> str:
    """Map a contest name to a broad category."""
    lower = contest_name.lower()
    for keyword, category in CATEGORY_MAP.items():
        if keyword in lower:
            return category
    return "Local"


def parse_candidate_line(line: str):
    """
    Parse a candidate line from the PDF.

    Expected formats:
        Mark S. Actis Jr. (IND) 120 55.30%
        John Smith (DEM) 1,234 52.3%
        Jane Doe 897 44.70%          ← no party tag
        No Candidate                  ← placeholder
        No Candidate (DEM)            ← placeholder with party

    Returns dict or None if line doesn't match.
    """
    line = line.strip()

    # Skip obvious non-candidate lines
    skip_patterns = [
        r"^Number of Precincts",
        r"^Precincts Reporting",
        r"^Vote For",
        r"^Total Votes",
        r"^\d+\.\d+%$",           # bare percentage line
        r"^Page \d+",
        r"^Date:",
        r"^Time:",
        r"^Election Summary",
        r"^CONSOLIDATED",
        r"^TUESDAY",
        r"^LaSALLE COUNTY",
        r"^FINAL RESULTS",
        r"^\d+ of \d+ Precincts",
        r"^Registered Voters",
    ]
    for pat in skip_patterns:
        if re.match(pat, line, re.IGNORECASE):
            return None

    # "No Candidate" lines — record with 0 votes so the contest is noted
    no_cand = re.match(r"^No Candidate(?:\s*\(([A-Z]+)\))?$", line, re.IGNORECASE)
    if no_cand:
        return {
            "name": "No Candidate",
            "party_code": no_cand.group(1) or "",
            "votes": 0,
            "percentage": 0.0,
            "is_placeholder": True,
        }

    # Full candidate line: Name (PARTY) votes percent%
    # votes can be formatted with comma: 1,234
    full = re.match(
        r"^(.+?)\s+\(([A-Z]+)\)\s+([\d,]+)\s+([\d.]+)%$",
        line
    )
    if full:
        name, party_code, votes_str, pct_str = full.groups()
        # Handle wrapped name lines like "Andrea L. Zadkovich-Blakemore (I\nND)"
        name = name.strip()
        return {
            "name": name,
            "party_code": party_code.upper(),
            "votes": int(votes_str.replace(",", "")),
            "percentage": float(pct_str),
            "is_placeholder": False,
        }

    # Candidate without party tag: Name votes percent%
    no_party = re.match(
        r"^(.+?)\s+([\d,]+)\s+([\d.]+)%$",
        line
    )
    if no_party:
        name, votes_str, pct_str = no_party.groups()
        # Guard against matching "Total Votes 5,000" style lines
        if name.upper().startswith("TOTAL"):
            return None
        return {
            "name": name.strip(),
            "party_code": "",
            "votes": int(votes_str.replace(",", "")),
            "percentage": float(pct_str),
            "is_placeholder": False,
        }

    return None


def parse_pdf_text(raw_text: str) -> list:
    """
    Parse the extracted PDF text into a list of contest dicts.

    PDF structure (per page, repeating):
        [page header lines]
        CONTEST NAME IN ALL CAPS
        Number of Precincts  N
        Precincts Reporting  N
        Vote For  N
        Candidate Name (PARTY)  votes  percent%
        ...
        Total Votes  N
        percent%
        [next contest]
    """
    lines = raw_text.splitlines()
    contests = []
    current_contest = None
    precincts_total = 0
    precincts_reporting = 0
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        i += 1

        if not line:
            continue

        # ── Detect contest name ───────────────────────────────────────────
        # Contest names are ALL CAPS and NOT purely numeric / header lines
        # They may span two lines when the name wraps (e.g. "MULTI-TOWNSHIP\nASSESSOR...")
        is_header_line = bool(re.match(
            r"^(Number of Precincts|Precincts Reporting|Vote For|Total Votes|"
            r"Date:|Time:|Page \d|Election Summary|CONSOLIDATED|TUESDAY|"
            r"LaSALLE COUNTY|FINAL RESULTS|\d+ of \d+|Registered Voters)",
            line, re.IGNORECASE
        ))

        is_all_caps_name = (
            line == line.upper()
            and len(line) > 4
            and not re.match(r"^[\d\s%,.]+$", line)   # not just numbers/punctuation
            and not is_header_line
        )

        if is_all_caps_name:
            # Save previous contest before starting new one
            if current_contest and current_contest["candidates"]:
                contests.append(current_contest)

            # Check if next line is also all-caps (wrapped contest name)
            full_name = line
            if i < len(lines):
                next_line = lines[i].strip()
                if (next_line == next_line.upper()
                        and len(next_line) > 2
                        and not re.match(r"^(Number of Precincts|Precincts Reporting|Vote For)", next_line, re.IGNORECASE)
                        and not re.match(r"^[\d\s%,.]+$", next_line)):
                    full_name = full_name + " " + next_line
                    i += 1

            party = detect_party_from_name(full_name)
            current_contest = {
                "contest_name": full_name,
                "contest_category": detect_category(full_name),
                "party_type": party or "Non-Partisan",
                "county": COUNTY_NAME,
                "precincts_reporting": 0,
                "total_precincts": 0,
                "candidates": [],
                "last_updated": datetime.now().isoformat(),
            }
            precincts_total = 0
            precincts_reporting = 0
            continue

        # ── Precinct metadata ─────────────────────────────────────────────
        m = re.match(r"^Number of Precincts\s+(\d+)", line, re.IGNORECASE)
        if m and current_contest:
            precincts_total = int(m.group(1))
            current_contest["total_precincts"] = precincts_total
            continue

        m = re.match(r"^Precincts Reporting\s+(\d+)", line, re.IGNORECASE)
        if m and current_contest:
            precincts_reporting = int(m.group(1))
            current_contest["precincts_reporting"] = precincts_reporting
            current_contest["reporting_percentage"] = (
                round(precincts_reporting / precincts_total * 100, 2)
                if precincts_total else 0.0
            )
            continue

        # ── Candidate lines ───────────────────────────────────────────────
        if current_contest:
            # Handle name-wrapping: PDF sometimes splits long candidate names
            # e.g. "Andrea L. Zadkovich-Blakemore (I" / "ND)  1,013  100.00%"
            combined = line
            if i < len(lines) and re.search(r"\(I$", line):
                combined = line + lines[i].strip()
                i += 1

            candidate = parse_candidate_line(combined)
            if candidate:
                # Skip "No Candidate" placeholders — they don't belong in results
                if not candidate["is_placeholder"]:
                    # Determine party for this candidate
                    party = normalize_party(
                        candidate["party_code"],
                        current_contest["party_type"]
                    )
                    # Update contest-level party if we can now determine it
                    if current_contest["party_type"] == "Non-Partisan" and party != "Non-Partisan":
                        current_contest["party_type"] = party

                    current_contest["candidates"].append({
                        "name": candidate["name"],
                        "party": candidate["party_code"] or "NP",
                        "votes": candidate["votes"],
                        "percentage": candidate["percentage"],
                    })

    # Don't forget the last contest
    if current_contest and current_contest["candidates"]:
        contests.append(current_contest)

    return contests


# ── Output Formatting ─────────────────────────────────────────────────────────

def build_output(contests: list, pdf_url: str) -> dict:
    """
    Build output JSON in the same shape as other county scrapers:
    {
      "county": "La Salle",
      "scraped_at": "...",
      "total_contests": N,
      "by_party": {
        "Democratic": { "count": N, "contests": [...] },
        "Republican":  { "count": N, "contests": [...] },
        "Non-Partisan":{ "count": N, "contests": [...] },
      }
    }
    """
    by_party = {
        "Democratic":  {"count": 0, "contests": []},
        "Republican":  {"count": 0, "contests": []},
        "Non-Partisan":{"count": 0, "contests": []},
    }

    contest_id = 1000
    for contest in contests:
        party_bucket = contest["party_type"]
        if party_bucket not in by_party:
            party_bucket = "Non-Partisan"

        entry = {
            "contest_id": str(contest_id),
            "contest_name": contest["contest_name"],
            "contest_category": contest["contest_category"],
            "party_type": party_bucket,
            "county": COUNTY_NAME,
            "candidates": contest["candidates"],
            "precincts_reporting": contest["precincts_reporting"],
            "total_precincts": contest["total_precincts"],
            "reporting_percentage": contest.get("reporting_percentage", 0.0),
            "last_updated": contest["last_updated"],
        }

        by_party[party_bucket]["contests"].append(entry)
        by_party[party_bucket]["count"] += 1
        contest_id += 1

    return {
        "county": COUNTY_NAME,
        "scraped_at": datetime.now().isoformat(),
        "source_url": pdf_url,
        "total_contests": len(contests),
        "by_party": by_party,
    }


def save_results(output: dict, output_dir: str) -> str:
    """Save results JSON and return the file path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filename = Path(output_dir) / "la_salle_results.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    return str(filename)


# ── Main ──────────────────────────────────────────────────────────────────────

def scrape(pdf_url: str, output_dir: str) -> dict:
    """Full scrape pipeline. Returns the output dict."""
    print()
    print("=" * 60)
    print("LA SALLE COUNTY ELECTION RESULTS SCRAPER")
    print("=" * 60)
    print()

    # Download PDF
    print("Step 1: Downloading PDF...")
    pdf_bytes = download_pdf(pdf_url)

    # Extract text
    print()
    print("Step 2: Extracting text from PDF...")
    raw_text = extract_text_from_pdf(pdf_bytes)

    # Parse contests
    print()
    print("Step 3: Parsing contests...")
    contests = parse_pdf_text(raw_text)
    print(f"  Found {len(contests)} contests")

    # Build output
    output = build_output(contests, pdf_url)

    # Save
    print()
    print("Step 4: Saving results...")
    filepath = save_results(output, output_dir)
    print(f"  Saved to: {filepath}")

    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total contests: {output['total_contests']}")
    for party, data in output["by_party"].items():
        print(f"  {party}: {data['count']} contests")

    # Spot-check: show first few contests from each party
    print()
    print("Sample contests:")
    for party, data in output["by_party"].items():
        if data["contests"]:
            c = data["contests"][0]
            print(f"  [{party}] {c['contest_name']}")
            for cand in c["candidates"][:2]:
                print(f"      {cand['name']}: {cand['votes']:,} ({cand['percentage']}%)")

    return output


def main():
    parser = argparse.ArgumentParser(
        description="La Salle County PDF Election Results Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic run (URL from config.json)
  python la_salle_county_scraper.py

  # Specify output directory
  python la_salle_county_scraper.py --output ./county_results

  # Use a specific PDF URL (election night, before config is updated)
  python la_salle_county_scraper.py --url https://lasallecountyil.gov/DocumentCenter/View/9999/Election-Summary-Report

  # Both
  python la_salle_county_scraper.py --url https://lasallecountyil.gov/DocumentCenter/View/9999/Election-Summary-Report --output ./county_results
        """
    )
    parser.add_argument(
        "--url",
        help="Direct URL to the election results PDF (overrides config.json)"
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save results JSON (default: {DEFAULT_OUTPUT_DIR})"
    )
    args = parser.parse_args()

    pdf_url = get_pdf_url(args)
    scrape(pdf_url, args.output)


if __name__ == "__main__":
    main()
