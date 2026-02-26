#!/usr/bin/env python3
"""
Multi-County Election Results Aggregator

Aggregates election results from all 38 Illinois counties into unified statewide results.
Handles multi-county races (Congress, State Senate, State House) by combining votes
across all relevant counties.

Usage:
    # Aggregate all counties
    python aggregate_results.py --results-dir ./county_results
    
    # Aggregate specific election date
    python aggregate_results.py --results-dir ./county_results --date 2026-03-17
    
    # Output to specific file
    python aggregate_results.py --results-dir ./county_results --output statewide_results.json
"""

import json
import os
import re
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime
import openpyxl


class MultiCountyAggregator:
    """Aggregates election results from multiple Illinois counties."""
    
    def __init__(self, results_dir: str, races_file: str = None):
        """
        Initialize aggregator.
        
        Args:
            results_dir: Directory containing county JSON result files
            races_file: Path to Excel file with multi-county race mappings
        """
        self.results_dir = Path(results_dir)
        self.races_file = races_file or "/mnt/project/2026_races.xlsx"
        
        # Load multi-county race mappings
        self.race_mappings = self._load_race_mappings()
        
    def _load_race_mappings(self) -> Dict:
        """Load multi-county race mappings from Excel file."""
        if not os.path.exists(self.races_file):
            print(f"Warning: Race mappings file not found: {self.races_file}")
            return {}
        
        try:
            wb = openpyxl.load_workbook(self.races_file, data_only=True)
            ws = wb.active
            
            mappings = {
                'congress': {},
                'state_senate': {},
                'state_house': {},
                'judicial': {}
            }
            
            # Read data (skip header row)
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row[0]:  # Skip empty rows
                    continue
                
                county = str(row[0]).strip()
                
                # Congress districts (column 2)
                if row[1]:
                    districts = self._parse_districts(str(row[1]))
                    for district in districts:
                        if district not in mappings['congress']:
                            mappings['congress'][district] = []
                        mappings['congress'][district].append(county)
                
                # State Senate (column 3)
                if row[2]:
                    districts = self._parse_districts(str(row[2]))
                    for district in districts:
                        if district not in mappings['state_senate']:
                            mappings['state_senate'][district] = []
                        mappings['state_senate'][district].append(county)
                
                # State House (column 4)
                if row[3]:
                    districts = self._parse_districts(str(row[3]))
                    for district in districts:
                        if district not in mappings['state_house']:
                            mappings['state_house'][district] = []
                        mappings['state_house'][district].append(county)
            
            return mappings
            
        except Exception as e:
            print(f"Warning: Could not load race mappings: {e}")
            return {}
    
    def _parse_districts(self, district_str: str) -> List[int]:
        """Parse district numbers from various formats."""
        districts = []
        
        # Remove spaces and convert to string
        district_str = str(district_str).replace(' ', '')
        
        # Handle comma-separated values
        parts = district_str.split(',')
        
        for part in parts:
            # Handle ranges (e.g., "1-20")
            if '-' in part:
                try:
                    start, end = part.split('-')
                    start_num = int(float(start))
                    end_num = int(float(end))
                    districts.extend(range(start_num, end_num + 1))
                except:
                    pass
            else:
                # Single number
                try:
                    # Handle floats like "15.0"
                    num = int(float(part))
                    districts.append(num)
                except:
                    pass
        
        return sorted(set(districts))
    
    def aggregate(self) -> Dict:
        """
        Aggregate results from all county files.
        
        Returns:
            Dictionary containing aggregated statewide results
        """
        print("=" * 80)
        print("MULTI-COUNTY ELECTION RESULTS AGGREGATOR")
        print("=" * 80)
        print()
        
        # Load all county results
        county_results = self._load_county_results()
        
        if not county_results:
            return {
                "error": "No county results found",
                "results_dir": str(self.results_dir)
            }
        
        print(f"✓ Loaded results from {len(county_results)} counties")
        print()
        
        # Aggregate by race type
        print("Aggregating results...")
        aggregated = {
            "aggregated_at": datetime.now().isoformat(),
            "num_counties": len(county_results),
            "counties_included": list(county_results.keys()),
            "statewide_races": self._aggregate_statewide_races(county_results),
            "multi_county_races": {
                "congress": self._aggregate_congress(county_results),
                "state_senate": self._aggregate_state_senate(county_results),
                "state_house": self._aggregate_state_house(county_results)
            },
            "county_results": county_results
        }
        
        print("✓ Aggregation complete!")
        print()
        
        return aggregated
    
    def _load_county_results(self) -> Dict:
        """Load all county JSON result files."""
        county_results = {}
        
        # Look for JSON files in results directory
        if not self.results_dir.exists():
            print(f"Error: Results directory not found: {self.results_dir}")
            return {}
        
        print(f"Scanning: {self.results_dir}")
        
        for file_path in self.results_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Extract county name
                county_name = data.get('county', file_path.stem)
                
                # Skip error files
                if 'error' in data:
                    print(f"  ⚠ Skipping {county_name}: {data['error']}")
                    continue
                
                county_results[county_name] = data
                print(f"  ✓ {county_name}: {len(data.get('contests', []))} contests")
                
            except Exception as e:
                print(f"  ✗ Error loading {file_path.name}: {e}")
        
        return county_results
    
    def _aggregate_statewide_races(self, county_results: Dict) -> Dict:
        """Aggregate races that appear in all/most counties (e.g., President)."""
        statewide = {}
        
        # Collect all contests that appear in multiple counties
        contest_appearances = defaultdict(list)
        
        for county_name, data in county_results.items():
            for contest in data.get('contests', []):
                contest_key = self._normalize_contest_name(contest['name'])
                contest_appearances[contest_key].append({
                    'county': county_name,
                    'contest': contest
                })
        
        # Aggregate contests that appear in multiple counties
        for contest_key, appearances in contest_appearances.items():
            if len(appearances) >= 5:  # At least 5 counties = likely statewide
                aggregated_contest = self._merge_contests(appearances)
                statewide[contest_key] = aggregated_contest
        
        return statewide
    
    def _aggregate_congress(self, county_results: Dict) -> Dict:
        """Aggregate Congressional district races."""
        congress = {}
        
        if not self.race_mappings.get('congress'):
            return {}
        
        for district, counties in self.race_mappings['congress'].items():
            district_key = f"District {district}"
            contest_data = self._aggregate_multi_county_race(
                county_results,
                counties,
                race_patterns=[
                    f"CONGRESS.*{district}",
                    f"CONGRESSIONAL DISTRICT {district}",
                    f"U.S. REPRESENTATIVE.*{district}"
                ]
            )
            
            if contest_data:
                congress[district_key] = contest_data
        
        return congress
    
    def _aggregate_state_senate(self, county_results: Dict) -> Dict:
        """Aggregate State Senate district races."""
        senate = {}
        
        if not self.race_mappings.get('state_senate'):
            return {}
        
        for district, counties in self.race_mappings['state_senate'].items():
            district_key = f"District {district}"
            contest_data = self._aggregate_multi_county_race(
                county_results,
                counties,
                race_patterns=[
                    f"STATE SENATE.*{district}",
                    f"SENATOR.*{district}",
                    f"SENATE DISTRICT {district}"
                ]
            )
            
            if contest_data:
                senate[district_key] = contest_data
        
        return senate
    
    def _aggregate_state_house(self, county_results: Dict) -> Dict:
        """Aggregate State House district races."""
        house = {}
        
        if not self.race_mappings.get('state_house'):
            return {}
        
        for district, counties in self.race_mappings['state_house'].items():
            district_key = f"District {district}"
            contest_data = self._aggregate_multi_county_race(
                county_results,
                counties,
                race_patterns=[
                    f"STATE REPRESENTATIVE.*{district}",
                    f"REPRESENTATIVE.*{district}",
                    f"HOUSE DISTRICT {district}",
                    f"STATE HOUSE.*{district}"
                ]
            )
            
            if contest_data:
                house[district_key] = contest_data
        
        return house
    
    def _aggregate_multi_county_race(
        self,
        county_results: Dict,
        counties: List[str],
        race_patterns: List[str]
    ) -> Dict:
        """Aggregate a race across multiple counties."""
        appearances = []
        
        for county in counties:
            if county not in county_results:
                continue
            
            for contest in county_results[county].get('contests', []):
                contest_name = contest['name'].upper()
                
                # Check if this contest matches any pattern
                for pattern in race_patterns:
                    if re.search(pattern, contest_name, re.IGNORECASE):
                        appearances.append({
                            'county': county,
                            'contest': contest
                        })
                        break
        
        if not appearances:
            return None
        
        return self._merge_contests(appearances)
    
    def _merge_contests(self, appearances: List[Dict]) -> Dict:
        """Merge multiple instances of the same contest."""
        # Use first appearance for base info
        merged = {
            "name": appearances[0]['contest']['name'],
            "party": appearances[0]['contest'].get('party', 'Non-Partisan'),
            "counties": [a['county'] for a in appearances],
            "num_counties": len(appearances),
            "candidates": {}
        }
        
        # Aggregate candidate votes
        for appearance in appearances:
            for candidate in appearance['contest'].get('candidates', []):
                name = self._normalize_candidate_name(candidate['name'])
                
                if name not in merged['candidates']:
                    merged['candidates'][name] = {
                        "name": candidate['name'],
                        "votes": 0,
                        "counties": []
                    }
                
                merged['candidates'][name]['votes'] += candidate.get('votes', 0)
                merged['candidates'][name]['counties'].append(appearance['county'])
        
        # Calculate percentages
        total_votes = sum(c['votes'] for c in merged['candidates'].values())
        if total_votes > 0:
            for candidate in merged['candidates'].values():
                candidate['percent'] = round((candidate['votes'] / total_votes) * 100, 2)
        
        # Convert to list and sort by votes
        merged['candidates'] = sorted(
            merged['candidates'].values(),
            key=lambda x: x['votes'],
            reverse=True
        )
        
        merged['total_votes'] = total_votes
        
        return merged
    
    def _normalize_contest_name(self, name: str) -> str:
        """Normalize contest name for matching."""
        # Remove extra whitespace and standardize
        normalized = ' '.join(name.upper().split())
        
        # Remove common variations
        normalized = normalized.replace('PRESIDENT OF THE UNITED STATES', 'PRESIDENT')
        normalized = normalized.replace('U.S. SENATOR', 'SENATOR')
        normalized = normalized.replace('U.S. REPRESENTATIVE', 'REPRESENTATIVE')
        
        return normalized
    
    def _normalize_candidate_name(self, name: str) -> str:
        """Normalize candidate name for matching."""
        # Remove party indicators
        name = re.sub(r'\s*\([A-Z]+\)\s*', '', name)
        
        # Remove extra whitespace
        name = ' '.join(name.upper().split())
        
        return name


def git_push(output_file: str, results_dir: str, repo_dir: str = None) -> bool:
    """
    Auto-commit and push results to GitHub so widgets update automatically.
    
    Args:
        output_file: Path to the aggregated statewide JSON file
        results_dir: Directory containing county JSON files
        repo_dir: Root of the git repo (auto-detected if not specified)
    
    Returns:
        True if push succeeded, False otherwise
    """
    print()
    print("=" * 80)
    print("PUSHING TO GITHUB")
    print("=" * 80)

    # Auto-detect repo root if not specified
    if repo_dir is None:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=True
            )
            repo_dir = result.stdout.strip()
        except subprocess.CalledProcessError:
            print("❌ Not inside a git repository. Run 'git init' first.")
            print("   See GITHUB_SETUP.md for instructions.")
            return False

    def run(cmd, cwd=repo_dir):
        """Run a shell command and return (success, output)."""
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

    # Check if there's anything to commit
    ok, stdout, _ = run(["git", "status", "--porcelain"])
    if not stdout:
        print("✓ No changes to push (results unchanged since last push)")
        return True

    # Stage the output file and county results directory
    files_to_add = [output_file, results_dir]
    for f in files_to_add:
        ok, _, err = run(["git", "add", f])
        if not ok:
            print(f"⚠ Could not stage {f}: {err}")

    # Commit with a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Results update: {timestamp}"
    ok, _, err = run(["git", "commit", "-m", commit_msg])
    if not ok:
        if "nothing to commit" in err:
            print("✓ No changes to push (results unchanged since last push)")
            return True
        print(f"❌ Git commit failed: {err}")
        return False

    # Push to GitHub
    print(f"  Pushing to GitHub... ", end="", flush=True)
    ok, _, err = run(["git", "push"])
    if not ok:
        print("FAILED")
        print(f"❌ Git push failed: {err}")
        print()
        print("Common fixes:")
        print("  • Make sure you've run 'git push -u origin main' at least once manually")
        print("  • Check your internet connection")
        print("  • See GITHUB_SETUP.md for full setup instructions")
        return False

    print("done!")
    print(f"✓ Results pushed to GitHub at {timestamp}")
    print("  GitHub Pages will update within ~30 seconds")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Aggregate election results from all 38 Illinois counties',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Aggregate and auto-push to GitHub (recommended on election night)
  %(prog)s --results-dir ./county_results --push

  # Aggregate only, no push (for testing)
  %(prog)s --results-dir ./county_results

  # Specify output file
  %(prog)s --results-dir ./county_results --output statewide_2026.json --push

  # With race mappings file
  %(prog)s --results-dir ./county_results --races 2026_races.xlsx --push
        """
    )

    parser.add_argument(
        '--results-dir',
        required=True,
        help='Directory containing county JSON result files'
    )

    parser.add_argument(
        '--races',
        help='Excel file with multi-county race mappings (default: /mnt/project/2026_races.xlsx)'
    )

    parser.add_argument(
        '--output',
        default='statewide_results.json',
        help='Output JSON file (default: statewide_results.json)'
    )

    parser.add_argument(
        '--push',
        action='store_true',
        help='Auto-commit and push results to GitHub after aggregation'
    )

    parser.add_argument(
        '--repo-dir',
        default=None,
        help='Path to git repo root (auto-detected if not specified)'
    )

    args = parser.parse_args()

    # Create aggregator
    aggregator = MultiCountyAggregator(
        results_dir=args.results_dir,
        races_file=args.races
    )

    # Aggregate results
    results = aggregator.aggregate()

    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    if "error" in results:
        print(f"❌ Error: {results['error']}")
    else:
        print(f"✓ Counties aggregated: {results['num_counties']}")
        print(f"✓ Statewide races: {len(results['statewide_races'])}")
        print(f"✓ Congressional districts: {len(results['multi_county_races']['congress'])}")
        print(f"✓ State Senate districts: {len(results['multi_county_races']['state_senate'])}")
        print(f"✓ State House districts: {len(results['multi_county_races']['state_house'])}")
        print()
        print(f"✓ Results saved to: {args.output}")

    print("=" * 80)

    # Auto-push to GitHub if requested
    if args.push:
        success = git_push(
            output_file=args.output,
            results_dir=args.results_dir,
            repo_dir=args.repo_dir
        )
        if not success:
            sys.exit(1)  # Non-zero exit so calling scripts know push failed


if __name__ == "__main__":
    main()
