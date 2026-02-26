# Peoria County Election Commission Scraper Setup

This scraper handles election results from the **Peoria County Election Commission** via their ElectionStats database.

## County Overview

**Peoria County Statistics:**
- Population: ~180,000 residents
- Voters: ~130,000 registered voters
- Location: Central Illinois (Peoria metro area)
- Ranking: 7th largest county in Illinois by population

**Electoral Significance:** Peoria County is considered a classic downstate bellwether. Its voting patterns often mirror statewide results. Home to Caterpillar Inc. and a mix of urban (City of Peoria), suburban, and rural voters.

## Platform Overview

**System:** ElectionStats (Custom database)  
**Vendor:** Custom-built by Peoria County  
**Technology:** Web-based searchable database  
**Complexity:** ⭐⭐⭐ Medium-High

Peoria County developed ElectionStats as an "every election at your fingertips" searchable database covering elections from 2006-present.

## Key Features

✅ **Comprehensive historical data** - Elections back to 2006  
✅ **Searchable interface** - Filter by year, office, district, candidate  
✅ **Individual contest pages** - Detailed results per race  
✅ **CSV downloads** - Structured data export per contest  
⚠️ **No bulk API** - Must access contests individually  
⚠️ **Requires contest IDs** - IDs must be found via web interface  

## Installation

### Dependencies

```bash
pip install requests beautifulsoup4
```

## Critical Setup Challenge

**⚠️ Contest IDs Required**

Unlike platforms like Kane County (date-based URLs) or Clarity (election ID), Peoria's ElectionStats requires **individual contest IDs** to scrape efficiently.

### What are Contest IDs?

Each election contest (President, Governor, State Rep, etc.) has a unique numeric ID:

- Example URL: `https://electionarchive.peoriaelections.gov/eng/contests/view/5432`
- Contest ID: `5432`

### Why This Matters

- You can't programmatically generate URLs for all contests
- Must browse the web interface to find contest IDs
- Each major race needs its ID noted separately
- No single "summary" endpoint

This makes **election day preparation** more manual than other counties.

## Election Day Strategy

### Pre-Election: Build Contest ID List

**Do this 1-2 days before election (when contests are finalized):**

1. Visit https://electionarchive.peoriaelections.gov
2. Use the search interface:
   - Date: "2026 Mar 17 - Primary"
   - Office: Browse major offices (President, U.S. Rep, Governor, etc.)
3. For each major contest, click through and note the contest ID from URL
4. Build a list like:

```
President - Democratic: 6789
President - Republican: 6790
U.S. Representative 17th - Democratic: 6791
U.S. Representative 17th - Republican: 6792
Governor - Democratic: 6793
Governor - Republican: 6794
... (continue for all major races)
```

### Election Night: Scrape with IDs

Once you have the contest IDs:

```bash
python peoria_county_scraper.py --ids 6789,6790,6791,6792,6793,6794,...
```

This will fetch all specified contests and combine into one JSON file.

## Usage

### Method 1: With Contest IDs (Recommended)

```bash
# Scrape specific contests by ID
python peoria_county_scraper.py --ids 5432,5433,5434,5435,5436

# With custom output directory
python peoria_county_scraper.py --ids 5432,5433,5434 --output /path/to/results/
```

### Method 2: Without IDs (Shows Instructions)

```bash
# This will show you instructions for finding IDs
python peoria_county_scraper.py
```

## Output Format

```json
{
  "authority": "Peoria County Election Commission",
  "jurisdiction": "Peoria",
  "election_date": "2026-03-17",
  "scraped_at": "2026-03-17T20:30:00",
  "source": "ElectionStats Database",
  "summary": {},
  "contests": [
    {
      "id": 5432,
      "name": "President of the United States",
      "party": "Democratic",
      "election_type": "Democratic Primary",
      "candidates": [
        {
          "name": "Candidate A",
          "votes": 12345,
          "percent": 55.5
        },
        {
          "name": "Candidate B",
          "votes": 9876,
          "percent": 44.5
        }
      ]
    }
  ]
}
```

## Finding Contest IDs

### Web Interface Navigation

1. **Go to**: https://electionarchive.peoriaelections.gov/eng/

2. **Search for your election:**
   - Select Date dropdown → "2026 Mar 17 - Primary"
   - OR use Years filter → 2026

3. **Browse contests:**
   - Use Office dropdown to filter (President, U.S. House, State Senator, etc.)
   - Click on each contest name

4. **Extract ID from URL:**
   - URL format: `/eng/contests/view/XXXXX`
   - XXXXX is the contest ID you need

5. **Repeat for all major races:**
   - Presidential Primary (both Dem and Rep if both on ballot)
   - U.S. Representative (your district)
   - State Senator
   - State Representative
   - County offices
   - Judicial races
   - Referendums

### Example Contest ID Collection

Here's what a complete ID list might look like for 2026 Primary:

```
# Federal Races
President - DEM: 6789
President - REP: 6790
U.S. Rep 17th - DEM: 6791
U.S. Rep 17th - REP: 6792

# State Races
Governor - DEM: 6793
Governor - REP: 6794
Lt. Governor - DEM: 6795
Lt. Governor - REP: 6796
Attorney General - DEM: 6797
Attorney General - REP: 6798

# State Legislature
State Senator 46th - DEM: 6799
State Senator 46th - REP: 6800
State Rep 91st - DEM: 6801
State Rep 91st - REP: 6802
State Rep 92nd - DEM: 6803
State Rep 92nd - REP: 6804

# County Races
County Board - District X: 6805
... etc.
```

Save this as `peoria_contest_ids.txt` for easy reference.

## Technical Details

### How the Scraper Works

1. **Takes contest IDs as input**
2. **For each ID**, tries two methods:
   - **CSV download** (preferred): `/eng/contests/download/ID/show_granularity_dt_id:7/.csv`
   - **HTML parsing** (fallback): `/eng/contests/view/ID`
3. **Extracts** candidate names and vote totals
4. **Calculates** percentages
5. **Determines party** from election type in title
6. **Combines** all contests into unified JSON

### CSV Format

ElectionStats provides CSV downloads with this structure:

```csv
Precinct,Candidate1,Candidate2,Total Votes Cast,Undervotes,Registered Voters
Precinct 1,150,200,350,25,500
Precinct 2,180,210,390,30,550
Totals,330,410,740,55,1050
```

The scraper sums the "Totals" row for county-wide results.

### HTML Parsing

If CSV isn't available, the scraper parses the HTML contest page:
- Extracts title: "2024 Mar 19 :: Republican Primary :: Office :: District"
- Finds candidate names from links
- Extracts votes from results table
- Looks for "Totals" row for county-wide numbers

## Party Detection

ElectionStats includes party in the election type:

| Election Type | Party |
|---------------|-------|
| "Democratic Primary" | Democratic |
| "Republican Primary" | Republican |
| "Consolidated General" | Non-Partisan |

Very reliable since it's in the contest title!

## Troubleshooting

### "Contest ID not found" or 404

**Problem:** Contest ID doesn't exist or hasn't been published yet

**Solutions:**
- Verify ID by visiting URL manually: `https://electionarchive.peoriaelections.gov/eng/contests/view/XXXXX`
- Results may not be posted yet (too early on election night)
- ID may have changed - check web interface again

### Empty Candidates Array

**Problem:** Contest exists but no results parsed

**Solutions:**
- Contest may have no candidates (unopposed or vacant)
- CSV download may have failed
- HTML parsing may need adjustment for this contest type
- Check contest page manually to see format

### Missing Some Contests

**Problem:** Some races aren't in your results

**Solutions:**
- Those contest IDs weren't included in your list
- Go back to web interface and find missing IDs
- Add them to your ID list and re-run scraper

### Wrong Party Assignments

**Problem:** Party detection incorrect

**Solutions:**
- Check election type in contest title
- Party should be in format "Election Type :: Office"
- If Peoria changed format, may need to update `detect_party()` logic

## Performance

- **Speed per contest**: 1-3 seconds (CSV) or 3-5 seconds (HTML)
- **10 contests**: ~30 seconds total
- **50 contests**: ~2-3 minutes total
- **Rate limits**: No known limits, but be respectful

Peoria's server is fast and reliable. The main limitation is the manual ID collection step.

## Comparison to Other Counties

| County | Platform | ID Method | Complexity | Automation |
|--------|----------|-----------|------------|------------|
| **Peoria** | ElectionStats | Contest IDs | ⭐⭐⭐ | Manual IDs |
| Kane | Custom HTML | Date-based | ⭐ Easy | Fully auto |
| DuPage | Scytl | Election ID | ⭐⭐ | Semi-auto |
| Chicago Board | PDF | PDF URL | ⭐⭐⭐ | Manual URL |

**Peoria's challenge:** Contest IDs must be collected manually before scraping.

**Peoria's strengths:**
- Very reliable once IDs are known
- Clean, consistent data format
- Historical data back to 2006
- CSV downloads are structured and accurate

## Election Day Workflow

### Day Before Election

1. Visit ElectionStats database
2. Browse 2026 Primary contests
3. Collect all relevant contest IDs
4. Create ID list file: `peoria_2026_primary_ids.txt`

### Election Night

```bash
# Read IDs from your list and scrape
IDS="6789,6790,6791,6792,6793,6794,6795,6796"

python peoria_county_scraper.py --ids $IDS

# Or from file
IDS=$(cat peoria_2026_primary_ids.txt | tr '\n' ',')
python peoria_county_scraper.py --ids $IDS
```

### Monitoring Updates

ElectionStats is typically updated periodically on election night. To monitor:

```bash
while true; do
  python peoria_county_scraper.py --ids $IDS
  echo "Updated at $(date)"
  sleep 900  # 15 minutes
done
```

## Alternative: Manual Browsing

If automated scraping isn't working, you can always:

1. Browse to https://electionarchive.peoriaelections.gov
2. Search for 2026 Primary
3. Click through each race
4. Manually record results
5. Use CSV downloads for easy import to Excel

The ElectionStats interface is actually quite good for manual use!

## Advanced: Bulk ID Discovery

**For programmers:** You could theoretically enumerate contest IDs:

```python
# Check a range of IDs
for contest_id in range(6500, 7000):
    url = f"https://electionarchive.peoriaelections.gov/eng/contests/view/{contest_id}"
    # Check if returns 200
    # Extract title to see if it's 2026 Primary
    # Add to list if match
```

However, this is slow and Peoria might not appreciate it. Better to use their search interface as intended.

## Support Contacts

**Peoria County Election Commission**
- Website: peoriaelections.gov
- Database: electionarchive.peoriaelections.gov
- Address: 4422 Brandywine Drive, Suite 1, Peoria, IL 61614
- Phone: (309) 324-2300
- Email: electioncommission@peoriaelections.gov

**For technical issues:**
- ElectionStats is well-maintained
- Contact election commission if database is down
- Contest IDs are stable once assigned
- CSV downloads are very reliable

## Why ElectionStats is Actually Great

Despite the manual ID collection requirement, Peoria's system has many advantages:

✅ **Searchable historical data** - Years of elections easily accessible  
✅ **Clean data format** - CSV downloads are structured perfectly  
✅ **Transparent** - Every contest is individually viewable  
✅ **Reliable** - System has been stable for years  
✅ **Well-documented** - Interface is intuitive  

Many counties have worse systems! Peoria just requires a bit more prep work.

## Next Steps

1. **Install dependencies** - `pip install requests beautifulsoup4`
2. **Test with 2024 data** - Use 2024 Primary contest IDs to verify scraper works
3. **Day before 2026 election** - Browse interface and collect contest IDs
4. **Election night** - Run scraper with your ID list
5. **Monitor** - Re-run periodically as results update

## Historical Testing

Test your scraper with 2024 Primary data:

1. Visit https://electionarchive.peoriaelections.gov
2. Select "2024 Mar 19 - Primary"
3. Find contest IDs for major races
4. Run: `python peoria_county_scraper.py --ids [2024_IDs]`
5. Verify output looks correct

This confirms the scraper works before election day!

## Summary

**Peoria County scraper requires manual contest ID collection but is very reliable once IDs are known.**

- ✅ Pro: Clean, structured data via CSV downloads
- ✅ Pro: Historical database is excellent resource
- ✅ Pro: Stable, reliable platform
- ⚠️ Con: Contest IDs must be found manually
- ⚠️ Con: Requires prep work day before election

**Recommended approach:** Spend 30-60 minutes the day before the election collecting contest IDs. Then scraping on election night is straightforward and reliable.
