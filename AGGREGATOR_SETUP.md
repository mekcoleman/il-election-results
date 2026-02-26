# Multi-County Election Results Aggregator

Combines election results from all 38 Illinois counties into unified statewide results.

## Overview

The aggregator handles three types of races:

1. **Statewide Races** - Appear in all/most counties (President, US Senator, etc.)
2. **Multi-County Districts** - Span multiple counties (Congress, State Senate, State House)
3. **County-Specific** - Local races unique to each county

## Installation

```bash
# Required for Excel race mappings
pip install openpyxl
```

## Usage

### Basic Aggregation

```bash
# Aggregate all county results
python aggregate_results.py --results-dir ./county_results
```

This will:
1. Load all JSON files from `./county_results/`
2. Aggregate statewide races across all counties
3. Combine multi-county races using the race mappings
4. Output unified results to `statewide_results.json`

### Specify Output File

```bash
python aggregate_results.py \
  --results-dir ./county_results \
  --output primary_2026_statewide.json
```

### Custom Race Mappings

```bash
python aggregate_results.py \
  --results-dir ./county_results \
  --races custom_races.xlsx
```

## Input Format

### County Results Files

The aggregator expects JSON files named by county (e.g., `cook_results.json`, `dupage_results.json`) with this structure:

```json
{
  "county": "Cook",
  "election_date": "2026-03-17",
  "contests": [
    {
      "name": "PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY",
      "party": "Republican",
      "candidates": [
        {"name": "DONALD J. TRUMP", "votes": 245389, "percent": 85.3},
        {"name": "NIKKI HALEY", "votes": 42301, "percent": 14.7}
      ]
    }
  ]
}
```

### Race Mappings File

Excel file (`2026_races.xlsx`) with columns:
- **County**: County name
- **Congress**: Congressional district numbers
- **State Senate**: State Senate district numbers
- **State House**: State House district numbers

Example:
```
County      | Congress | State Senate | State House
Cook        | 1-11     | 1-20,22-30   | 1-40,43-45
DuPage      | 6,11     | 21,41,42     | 41,42,81-84
Will        | 11,14    | 21,38,43     | 42,75,76,85,86
```

## Output Format

### Statewide Results

```json
{
  "aggregated_at": "2026-03-17T21:30:00",
  "num_counties": 38,
  "counties_included": ["Cook", "DuPage", "Will", ...],
  
  "statewide_races": {
    "PRESIDENT - REPUBLICAN PARTY": {
      "name": "PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY",
      "party": "Republican",
      "counties": ["Cook", "DuPage", "Will", ...],
      "num_counties": 38,
      "total_votes": 1245389,
      "candidates": [
        {
          "name": "DONALD J. TRUMP",
          "votes": 1058581,
          "percent": 85.0,
          "counties": ["Cook", "DuPage", ...]
        }
      ]
    }
  },
  
  "multi_county_races": {
    "congress": {
      "District 1": {
        "name": "U.S. REPRESENTATIVE DISTRICT 1 - DEMOCRATIC PARTY",
        "party": "Democratic",
        "counties": ["Cook"],
        "num_counties": 1,
        "total_votes": 45389,
        "candidates": [...]
      }
    },
    "state_senate": {
      "District 21": {
        "name": "STATE SENATOR DISTRICT 21 - REPUBLICAN PARTY",
        "party": "Republican",
        "counties": ["DuPage", "Will"],
        "num_counties": 2,
        "total_votes": 85432,
        "candidates": [...]
      }
    }
  },
  
  "county_results": {
    "Cook": { ... },
    "DuPage": { ... }
  }
}
```

## Election Day Workflow

### 1. Collect County Results

Run all 38 county scrapers:

```bash
# Platform scrapers (23 counties)
python clarity_scraper.py --output ./county_results/
python pollresults_scraper.py --output ./county_results/
python integra_scraper.py --output ./county_results/
python gbs_scraper.py --output ./county_results/

# Custom scrapers (15 counties)
python cook_county_clerk_scraper.py --output ./county_results/cook_results.json
python chicago_board_scraper.py --output ./county_results/chicago_results.json
python dupage_county_scraper.py --output ./county_results/dupage_results.json
# ... etc for all 15 custom counties
```

### 2. Aggregate Results

```bash
python aggregate_results.py \
  --results-dir ./county_results \
  --output primary_2026_statewide.json
```

### 3. Verify Output

```bash
# Check aggregated results
cat primary_2026_statewide.json | jq '.num_counties'
# Should show: 38

# Check statewide races
cat primary_2026_statewide.json | jq '.statewide_races | keys'

# Check Congressional districts
cat primary_2026_statewide.json | jq '.multi_county_races.congress | keys'
```

## How It Works

### Statewide Race Detection

The aggregator identifies statewide races by:
1. Normalizing contest names across counties
2. Finding contests that appear in 5+ counties
3. Merging votes from all counties

Example: "PRESIDENT - REPUBLICAN PARTY" appearing in all 38 counties gets aggregated.

### Multi-County Race Aggregation

For races spanning multiple counties:
1. Load race mappings from Excel (which counties are in which district)
2. Find matching contests in each relevant county
3. Sum votes across all counties in the district
4. Calculate district-wide percentages

Example: Congressional District 11 (Cook, DuPage, Will, Lake counties)

### Candidate Name Matching

The aggregator normalizes candidate names by:
- Removing party indicators: `"TRUMP (REP)"` → `"TRUMP"`
- Removing extra whitespace
- Converting to uppercase
- Matching variations: `"Donald J. Trump"` and `"TRUMP, DONALD J."` both match

### Vote Aggregation

For each candidate:
- Sum votes from all relevant counties
- Track which counties contributed votes
- Calculate statewide/district-wide percentage

## Features

### Intelligent Contest Matching

```python
# These all match as the same contest:
"PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY"
"President - Republican Party"
"PRESIDENT (Republican)"
```

### Multi-County Tracking

```json
{
  "candidates": [
    {
      "name": "DONALD J. TRUMP",
      "votes": 1058581,
      "percent": 85.0,
      "counties": ["Cook", "DuPage", "Will", ...]  // Which counties contributed
    }
  ]
}
```

### Complete Audit Trail

- All county-level results included
- Which counties contributed to each race
- Total votes per race
- Percentages recalculated at district/state level

## Troubleshooting

### No results aggregated

**Problem:** Aggregator runs but finds no races

**Solution:**
- Check `--results-dir` path is correct
- Verify JSON files exist in directory
- Ensure JSON files have `contests` array
- Check for `error` fields in county files

### Missing districts

**Problem:** Some Congressional/Senate/House districts not appearing

**Solution:**
- Verify race mappings file exists and is readable
- Check county names match between mappings and result files
- Ensure contest names include district numbers
- Look for pattern matching issues in contest names

### Duplicate candidates

**Problem:** Same candidate appears multiple times

**Solution:**
- Check candidate name formatting across counties
- Look for different party indicators
- Verify name normalization logic
- May need manual deduplication for write-in candidates

### Wrong vote totals

**Problem:** Aggregated totals don't match expected values

**Solution:**
- Verify all relevant counties are included
- Check for duplicate county files
- Ensure county results aren't partial/preliminary
- Look for missing counties in race mappings

## Advanced Usage

### Filter by Party

Modify the aggregator to focus on specific primaries:

```python
# Only aggregate Republican primary races
if contest.get('party') == 'Republican':
    # ... aggregate logic
```

### Export Formats

Convert aggregated results to other formats:

```bash
# CSV export
cat statewide_results.json | jq -r '.statewide_races[] | [.name, .total_votes] | @csv'

# Excel export (requires additional libraries)
python export_to_excel.py statewide_results.json results.xlsx
```

### Comparison with Previous Years

Compare 2026 results with historical data:

```bash
# Load 2024 and 2026 results
python compare_elections.py \
  --current statewide_2026.json \
  --previous statewide_2024.json \
  --output comparison.json
```

## Integration

### With Web Dashboard

```python
# Load aggregated results in web app
with open('statewide_results.json', 'r') as f:
    results = json.load(f)

# Display statewide races
for race_name, race_data in results['statewide_races'].items():
    print(f"{race_name}: {race_data['total_votes']} votes")
    for candidate in race_data['candidates']:
        print(f"  {candidate['name']}: {candidate['votes']} ({candidate['percent']}%)")
```

### With Database

```python
# Import to PostgreSQL/SQLite
import psycopg2

conn = psycopg2.connect(...)
cursor = conn.cursor()

# Insert aggregated results
for race in results['statewide_races'].values():
    cursor.execute("""
        INSERT INTO races (name, party, total_votes)
        VALUES (%s, %s, %s)
    """, (race['name'], race['party'], race['total_votes']))
```

## Summary

The multi-county aggregator:
- ✅ Combines results from all 38 counties
- ✅ Handles statewide races automatically
- ✅ Uses race mappings for multi-county districts
- ✅ Tracks vote contributions by county
- ✅ Calculates statewide/district percentages
- ✅ Provides complete audit trail
- ✅ Ready for March 17, 2026!

**Complete Illinois election results in one unified JSON file!**
