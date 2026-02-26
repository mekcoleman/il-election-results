#!/usr/bin/env python3
"""
Election Night Conductor
Illinois Primary Election — March 17, 2026

Runs all county scrapers in order, aggregates results, and pushes to GitHub.
Repeats automatically every N minutes until you press Ctrl+C.

Usage:
    # Start election night (runs every 10 minutes)
    python run_election_night.py

    # Custom interval
    python run_election_night.py --interval 5

    # Run once and exit (good for testing before election night)
    python run_election_night.py --once

    # Dry run: scrape but don't push to GitHub
    python run_election_night.py --no-push

    # Skip the pre-flight config check (if you've already verified)
    python run_election_night.py --skip-preflight
"""

import os
import sys
import time
import json
import signal
import argparse
import subprocess
import traceback
from pathlib import Path
from datetime import datetime


# ── Configuration ─────────────────────────────────────────────────────────────

RESULTS_DIR    = "./county_results"
OUTPUT_FILE    = "statewide_results.json"
LOG_FILE       = "election_night.log"
CONFIG_FILE    = "config.json"
INTERVAL_MIN   = 10          # default minutes between scrape cycles
GITHUB_PAGES   = "https://mekcoleman.github.io/il-election-results/"

# Counties covered on March 17, 2026, grouped by scraper
# Each entry: (display_name, scraper_module, invoke_method, extra_args)
#
# invoke_method options:
#   "clarity"    → calls scrape_clarity_county(county, config_path, output_dir)
#   "pollresults"→ calls scrape_pollresults_county(county, config_path, output_dir)
#   "integra"    → calls scrape_all_integra_counties(output_dir) [scrapes DeKalb+Kendall]
#   "subprocess" → runs the script as a subprocess with --output flag
#   "lasalle"    → calls la_salle_county_scraper.scrape(pdf_url, output_dir)

SCRAPERS = [
    # ── Clarity platform (3 counties) ────────────────────────────────────────
    {"name": "Will",      "type": "clarity",     "county_key": "Will"},
    {"name": "McHenry",   "type": "clarity",     "county_key": "McHenry"},
    {"name": "Kankakee",  "type": "clarity",     "county_key": "Kankakee"},

    # ── pollresults.net platform (9 counties) ─────────────────────────────────
    {"name": "Whiteside", "type": "pollresults", "county_key": "Whiteside"},
    {"name": "Carroll",   "type": "pollresults", "county_key": "Carroll"},
    {"name": "Lee",       "type": "pollresults", "county_key": "Lee"},
    {"name": "Bureau",    "type": "pollresults", "county_key": "Bureau"},
    {"name": "Putnam",    "type": "pollresults", "county_key": "Putnam"},
    {"name": "Ogle",      "type": "pollresults", "county_key": "Ogle"},
    {"name": "Ford",      "type": "pollresults", "county_key": "Ford"},
    {"name": "Livingston","type": "pollresults", "county_key": "Livingston"},
    {"name": "Stephenson","type": "pollresults", "county_key": "Stephenson"},

    # ── Integra platform (DeKalb + Kendall + Henry) ───────────────────────────
    {"name": "DeKalb + Kendall + Henry", "type": "integra", "county_key": None},

    # ── Custom scrapers ───────────────────────────────────────────────────────
    {"name": "Kane",      "type": "subprocess",  "script": "kane_county_scraper.py",      "args": ["--output", RESULTS_DIR]},
    {"name": "DuPage",    "type": "subprocess",  "script": "dupage_county_scraper.py",    "args": ["--output", RESULTS_DIR]},
    {"name": "Grundy",    "type": "subprocess",  "script": "gbs_scraper.py",              "args": ["--output", RESULTS_DIR]},
    {"name": "La Salle",  "type": "lasalle",     "county_key": "La Salle"},

    # ── Superintendent-only counties (not in any single market) ───────────────
    {"name": "Winnebago", "type": "subprocess",  "script": "winnebago_county_scraper.py", "args": ["--output", RESULTS_DIR]},
    {"name": "Jo Daviess","type": "subprocess",  "script": "jo_daviess_county_scraper.py","args": ["--output", RESULTS_DIR]},
    {"name": "Marshall",  "type": "subprocess",  "script": "marshall_county_scraper.py",  "args": ["--output", RESULTS_DIR]},
    {"name": "Stark",     "type": "subprocess",  "script": "stark_county_scraper.py",     "args": ["--output", RESULTS_DIR]},
    {"name": "Iroquois",  "type": "subprocess",  "script": "iroquois_county_scraper.py",  "args": ["--output", RESULTS_DIR]},
    {"name": "Cook",      "type": "subprocess",  "script": "cook_county_scraper.py",      "args": ["--output", RESULTS_DIR]},
    {"name": "Rock Island","type": "subprocess", "script": "rock_island_county_scraper.py","args": ["--output", RESULTS_DIR]},
]

# Clarity counties that need election_id + web_id set in config.json before running
CLARITY_COUNTIES_NEEDING_IDS = ["Will", "McHenry", "Kankakee"]


# ── Logging ───────────────────────────────────────────────────────────────────

class Logger:
    """Writes to both console and log file simultaneously."""

    def __init__(self, log_path: str):
        self.log_path = log_path
        # Open log file in append mode so previous runs are preserved
        self.log_file = open(log_path, "a", buffering=1)
        self._write(f"\n{'='*70}")
        self._write(f"ELECTION NIGHT SESSION STARTED: {datetime.now():%Y-%m-%d %H:%M:%S}")
        self._write(f"{'='*70}\n")

    def _write(self, msg: str):
        print(msg)
        self.log_file.write(msg + "\n")

    def info(self, msg: str):
        self._write(f"[{datetime.now():%H:%M:%S}] {msg}")

    def success(self, msg: str):
        self._write(f"[{datetime.now():%H:%M:%S}] ✅ {msg}")

    def warn(self, msg: str):
        self._write(f"[{datetime.now():%H:%M:%S}] ⚠️  {msg}")

    def error(self, msg: str):
        self._write(f"[{datetime.now():%H:%M:%S}] ❌ {msg}")

    def section(self, title: str):
        self._write(f"\n{'─'*70}")
        self._write(f"  {title}")
        self._write(f"{'─'*70}")

    def close(self):
        self._write(f"\n{'='*70}")
        self._write(f"SESSION ENDED: {datetime.now():%Y-%m-%d %H:%M:%S}")
        self._write(f"{'='*70}\n")
        self.log_file.close()


# ── Pre-flight checks ─────────────────────────────────────────────────────────

def load_config() -> dict:
    if not Path(CONFIG_FILE).exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def preflight_check(log: Logger) -> bool:
    """
    Verify that everything is ready before starting.
    Returns True if OK to proceed, False if there are blocking issues.
    """
    log.section("PRE-FLIGHT CHECKS")
    config = load_config()
    counties_cfg = config.get("counties", {})
    ok = True

    # 1. Results directory
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    log.success(f"Results directory ready: {RESULTS_DIR}")

    # 2. Check Clarity IDs are updated
    log.info("Checking Clarity election IDs...")
    missing_ids = []
    for county in CLARITY_COUNTIES_NEEDING_IDS:
        cfg = counties_cfg.get(county, {})
        eid = str(cfg.get("election_id", ""))
        wid = str(cfg.get("web_id", ""))
        if "UPDATE_ON_ELECTION_DAY" in eid or "UPDATE_ON_ELECTION_DAY" in wid or not eid or not wid:
            missing_ids.append(county)

    if missing_ids:
        log.warn(f"Clarity IDs not yet set for: {', '.join(missing_ids)}")
        log.warn("  These counties will be SKIPPED until you update config.json")
        log.warn("  See ELECTION_DAY_SETUP.md for instructions")
    else:
        log.success("All Clarity election IDs configured")

    # 3. Check La Salle PDF doc_id
    lasalle_cfg = counties_cfg.get("La Salle", {})
    doc_id = str(lasalle_cfg.get("doc_id", lasalle_cfg.get("election_doc_id", "")))
    if not doc_id or "UPDATE_ON_ELECTION_DAY" in doc_id:
        log.warn("La Salle County PDF doc_id not set — La Salle will be SKIPPED")
        log.warn("  Update config.json: set 'doc_id' under 'La Salle'")
    else:
        log.success(f"La Salle PDF doc_id: {doc_id}")

    # 4. Check git is available and repo is set up
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True
        )
        remote = result.stdout.strip()
        log.success(f"Git remote: {remote}")
    except subprocess.CalledProcessError:
        log.warn("Git remote not configured — results will NOT be pushed to GitHub")
        log.warn("  Run: git remote add origin https://github.com/mekcoleman/il-election-results.git")
    except FileNotFoundError:
        log.error("Git not installed — results will NOT be pushed to GitHub")

    # 5. Check required scraper files exist
    log.info("Checking scraper files...")
    required_scripts = [
        "clarity_scraper.py", "pollresults_scraper.py", "integra_scraper.py",
        "kane_county_scraper.py", "dupage_county_scraper.py",
        "la_salle_county_scraper.py", "aggregate_results.py",
    ]
    missing_scripts = [s for s in required_scripts if not Path(s).exists()]
    if missing_scripts:
        log.error(f"Missing scraper files: {', '.join(missing_scripts)}")
        ok = False
    else:
        log.success("All scraper files present")

    # Summary
    if ok:
        log.info("\nPre-flight complete. Starting scrape loop...")
    else:
        log.error("\nPre-flight failed. Fix the errors above before running.")

    return ok


# ── Individual scraper runners ────────────────────────────────────────────────

def run_clarity(county_key: str, log: Logger) -> bool:
    """Run Clarity scraper for one county. Returns True on success."""
    try:
        from clarity_scraper import scrape_clarity_county
        result = scrape_clarity_county(county_key, CONFIG_FILE, RESULTS_DIR)
        if result:
            log.success(f"{county_key}: {len(result)} contests")
            return True
        else:
            log.warn(f"{county_key}: scraper returned no results (IDs may not be live yet)")
            return False
    except Exception as e:
        log.error(f"{county_key}: {e}")
        return False


def run_pollresults(county_key: str, log: Logger) -> bool:
    """Run pollresults scraper for one county. Returns True on success."""
    try:
        from pollresults_scraper import scrape_pollresults_county
        result = scrape_pollresults_county(county_key, CONFIG_FILE, RESULTS_DIR)
        if result:
            log.success(f"{county_key}: {len(result)} contests")
            return True
        else:
            log.warn(f"{county_key}: no results returned")
            return False
    except Exception as e:
        log.error(f"{county_key}: {e}")
        return False


def run_integra(log: Logger) -> bool:
    """Run Integra scraper for all Integra counties (DeKalb + Kendall). Returns True on success."""
    try:
        from integra_scraper import scrape_all_integra_counties
        scrape_all_integra_counties(RESULTS_DIR)
        log.success("DeKalb + Kendall: Integra scrape complete")
        return True
    except Exception as e:
        log.error(f"Integra (DeKalb/Kendall): {e}")
        return False


def run_subprocess(scraper: dict, log: Logger) -> bool:
    """
    Run a custom scraper as a subprocess.
    Returns True on success (exit code 0).
    """
    script = scraper["script"]
    args = scraper.get("args", [])
    name = scraper["name"]

    if not Path(script).exists():
        log.warn(f"{name}: {script} not found — skipping")
        return False

    cmd = [sys.executable, script] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120      # 2 minute timeout per scraper
        )
        if result.returncode == 0:
            log.success(f"{name}: complete")
            return True
        else:
            log.error(f"{name}: exited with code {result.returncode}")
            if result.stderr:
                # Log just the last 3 lines of stderr to keep output clean
                for line in result.stderr.strip().splitlines()[-3:]:
                    log.error(f"  {line}")
            return False
    except subprocess.TimeoutExpired:
        log.error(f"{name}: timed out after 120 seconds")
        return False
    except Exception as e:
        log.error(f"{name}: {e}")
        return False


def run_lasalle(log: Logger) -> bool:
    """Run La Salle County PDF scraper. Returns True on success."""
    config = load_config()
    lasalle_cfg = config.get("counties", {}).get("La Salle", {})
    doc_id = str(lasalle_cfg.get("doc_id", lasalle_cfg.get("election_doc_id", "")))

    if not doc_id or "UPDATE_ON_ELECTION_DAY" in doc_id:
        log.warn("La Salle: doc_id not set in config.json — skipping")
        return False

    try:
        from la_salle_county_scraper import scrape
        url = f"https://lasallecountyil.gov/DocumentCenter/View/{doc_id}/Election-Summary-Report"
        scrape(url, RESULTS_DIR)
        log.success("La Salle: PDF scraped successfully")
        return True
    except SystemExit:
        # la_salle_county_scraper calls sys.exit(1) on network errors
        log.error("La Salle: could not download PDF (check URL or internet connection)")
        return False
    except Exception as e:
        log.error(f"La Salle: {e}")
        return False


# ── Aggregator + push ─────────────────────────────────────────────────────────

def run_aggregator(push: bool, log: Logger) -> bool:
    """Run the aggregator and optionally push to GitHub. Returns True on success."""
    try:
        from aggregate_results import MultiCountyAggregator, git_push
        import json as _json

        log.info("Aggregating county results...")
        agg = MultiCountyAggregator(results_dir=RESULTS_DIR)
        results = agg.aggregate()

        with open(OUTPUT_FILE, "w") as f:
            _json.dump(results, f, indent=2)

        n = results.get("num_counties", 0)
        log.success(f"Aggregation complete: {n} counties → {OUTPUT_FILE}")

        if push:
            log.info("Pushing to GitHub...")
            success = git_push(
                output_file=OUTPUT_FILE,
                results_dir=RESULTS_DIR,
            )
            if success:
                log.success(f"Pushed! Widgets update in ~30s at {GITHUB_PAGES}")
            else:
                log.error("Push failed — see errors above")
            return success
        return True

    except Exception as e:
        log.error(f"Aggregator error: {e}")
        log.error(traceback.format_exc())
        return False


# ── Main scrape cycle ─────────────────────────────────────────────────────────

def run_one_cycle(push: bool, log: Logger) -> dict:
    """
    Run all scrapers once, then aggregate and push.
    Returns a summary dict: {county: "ok"|"skipped"|"error"}
    """
    summary = {}
    log.section(f"SCRAPE CYCLE — {datetime.now():%I:%M %p}")

    for scraper in SCRAPERS:
        name = scraper["name"]
        stype = scraper["type"]
        log.info(f"Scraping {name}...")

        try:
            if stype == "clarity":
                ok = run_clarity(scraper["county_key"], log)
            elif stype == "pollresults":
                ok = run_pollresults(scraper["county_key"], log)
            elif stype == "integra":
                ok = run_integra(log)
            elif stype == "subprocess":
                ok = run_subprocess(scraper, log)
            elif stype == "lasalle":
                ok = run_lasalle(log)
            else:
                log.warn(f"{name}: unknown scraper type '{stype}' — skipping")
                ok = False

            summary[name] = "ok" if ok else "error"

        except KeyboardInterrupt:
            raise  # Let Ctrl+C propagate cleanly
        except Exception as e:
            log.error(f"{name}: unexpected error — {e}")
            summary[name] = "error"

    # Aggregate and push regardless of individual scraper failures
    # (partial results are better than no results)
    log.section("AGGREGATING + PUSHING")
    agg_ok = run_aggregator(push=push, log=log)
    summary["_aggregator"] = "ok" if agg_ok else "error"

    # Print cycle summary
    log.section("CYCLE SUMMARY")
    ok_count = sum(1 for v in summary.values() if v == "ok")
    err_count = sum(1 for v in summary.values() if v == "error")
    for county, status in summary.items():
        if county.startswith("_"):
            continue
        icon = "✅" if status == "ok" else "❌"
        log.info(f"  {icon} {county}")
    log.info(f"\n  {ok_count} succeeded · {err_count} failed")

    return summary


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Election Night Conductor — Illinois Primary March 17, 2026",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Normal election night usage
  python run_election_night.py

  # Run every 5 minutes instead of 10
  python run_election_night.py --interval 5

  # Test run: scrape once, don't push
  python run_election_night.py --once --no-push

  # Skip pre-flight checks (faster restart if already verified)
  python run_election_night.py --skip-preflight
        """
    )
    parser.add_argument(
        "--interval", type=int, default=INTERVAL_MIN,
        help=f"Minutes between scrape cycles (default: {INTERVAL_MIN})"
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Run one cycle and exit (don't loop)"
    )
    parser.add_argument(
        "--no-push", action="store_true",
        help="Scrape and aggregate but don't push to GitHub"
    )
    parser.add_argument(
        "--skip-preflight", action="store_true",
        help="Skip the pre-flight config check"
    )
    args = parser.parse_args()

    push = not args.no_push
    log = Logger(LOG_FILE)

    # Handle Ctrl+C gracefully
    def on_interrupt(sig, frame):
        print()
        log.info("Interrupted by user (Ctrl+C). Shutting down cleanly...")
        log.close()
        print()
        print("Election night session ended.")
        print(f"Full log saved to: {LOG_FILE}")
        sys.exit(0)

    signal.signal(signal.SIGINT, on_interrupt)

    # Banner
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║        ILLINOIS PRIMARY ELECTION — MARCH 17, 2026           ║")
    print("║                   Election Night Conductor                   ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print(f"  Results directory : {RESULTS_DIR}")
    print(f"  Output file       : {OUTPUT_FILE}")
    print(f"  Scrape interval   : every {args.interval} minutes")
    print(f"  Push to GitHub    : {'YES → ' + GITHUB_PAGES if push else 'NO (--no-push)'}")
    print(f"  Log file          : {LOG_FILE}")
    print()
    print("  Press Ctrl+C at any time to stop.")
    print()

    # Pre-flight
    if not args.skip_preflight:
        if not preflight_check(log):
            log.close()
            sys.exit(1)

    # Scrape loop
    cycle = 1
    while True:
        log.info(f"Starting cycle #{cycle}")
        run_one_cycle(push=push, log=log)

        if args.once:
            log.info("--once flag set, exiting after first cycle.")
            break

        # Wait for next cycle, showing a countdown
        next_run = datetime.now().timestamp() + args.interval * 60
        log.info(f"Next cycle in {args.interval} minutes "
                 f"(~{datetime.fromtimestamp(next_run):%I:%M %p}). "
                 "Press Ctrl+C to stop.")

        # Sleep in small increments so Ctrl+C is responsive
        sleep_remaining = args.interval * 60
        while sleep_remaining > 0:
            time.sleep(min(5, sleep_remaining))
            sleep_remaining -= 5

        cycle += 1

    log.close()


if __name__ == "__main__":
    main()
