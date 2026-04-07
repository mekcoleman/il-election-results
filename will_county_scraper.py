#!/usr/bin/env python3
"""
Will County Election Results Scraper
Illinois Primary Election — March 17, 2026

Will County uses Clarity Elections:
  https://results.enr.clarityelections.com/IL/Will

This scraper is a thin wrapper around clarity_scraper.py, which handles
the correct vote-fetching logic (summary.json for metadata + details.json
for actual vote totals).

Output file: will_results.json  (contests_by_party shape)

Election Day Setup:
  1. Visit https://results.enr.clarityelections.com/IL/Will
  2. Open the March 17 Primary — note election_id and web_id from the URL:
       .../IL/Will/{election_id}/web.{web_id}/...
  3. Update config.json:
       "Will": {
         "platform": "clarity",
         "base_url": "https://results.enr.clarityelections.com/IL/Will",
         "election_id": "XXXXXX",
         "web_id":      "XXXXXX"
       }
  4. Run: python will_county_scraper.py
         or: python will_county_scraper.py --output ./county_results

Usage:
    python will_county_scraper.py
    python will_county_scraper.py --output ./county_results
    python will_county_scraper.py --config /path/to/config.json
"""

import sys
import argparse
from clarity_scraper import scrape_county


def main():
    parser = argparse.ArgumentParser(
        description="Will County Clarity Elections scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Election Day Setup:
  1. Update config.json with Will County election_id and web_id
  2. python will_county_scraper.py --output ./county_results
        """,
    )
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--config", default="config.json", help="Config file")
    args = parser.parse_args()

    result = scrape_county("Will",
                           config_path=args.config,
                           output_dir=args.output)

    if result and "error" not in result:
        cbp = result.get("contests_by_party", {})
        print(f"\nWill County Results Summary:")
        print(f"  Democratic:   {cbp.get('Democratic',   {}).get('count', 0)} contests")
        print(f"  Republican:   {cbp.get('Republican',   {}).get('count', 0)} contests")
        print(f"  Non-Partisan: {cbp.get('Non-Partisan', {}).get('count', 0)} contests")
        sys.exit(0)
    else:
        print("\n✗ Will County scrape failed — check config.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
