# DuPage County Election Results Scraper Setup

This scraper handles election results from **DuPage County**, Illinois' 2nd largest county.

## County Overview

**DuPage County Statistics:**
- Population: ~930,000 residents
- Voters: ~600,000+ registered voters
- Ranking: 2nd largest Illinois county (after Cook)
- Location: Western Chicago suburbs
- Major cities: Naperville, Aurora (part), Wheaton, Downers Grove, Elmhurst

**Electoral Significance:** DuPage is a critical swing county in Illinois. Historically Republican-leaning but trending Democratic in recent elections. Results here often indicate statewide trends.

## Platform Overview

**Vendor:** Scytl  
**Technology:** JSON API endpoints  
**Complexity:** ⭐⭐ Medium

Scytl is a major international election technology vendor. Their platform provides structured JSON data that can be accessed directly through API endpoints.

## Installation

### Dependencies

Standard requirements only:

```bash
pip install requests
```

No special libraries needed - just `requests` for HTTP and Python's built-in `json` module.

## Critical Election Day Setup

**⚠️ REQUIRED:** You must find the election ID on election day!

### How to Find the Election ID

#### Step 1: Visit DuPage Results Site

Go to: https://www.dupageresults.gov/IL/DuPage

#### Step 2: Find the 2026 Primary

Look for **"March 17, 2026 Primary"** or **"2026 General Primary"** in the elections list.

#### Step 3: Click to View Results

When you click the election, the URL will change to something like:

```
https://www.dupageresults.gov/IL/DuPage/123456/web.345678/
```

#### Step 4: Extract the Election ID

The election ID is the first number after `/DuPage/`

In the example above, the election ID is: **123456**

(Ignore the second number - that's the web ID, not needed for JSON endpoints)

### Updating the Scraper

You have two options:

**Option 1:** Pass ID as command-line argument (recommended)

```bash
python dupage_county_scraper.py --id 123456
```

**Option 2:** Hard-code in the scraper

Edit `dupage_county_scraper.py` and change:

```python
self.election_id = election_id or 'UPDATE_ON_ELECTION_DAY'
```

to:

```python
self.election_id = election_id or '123456'  # ← Your election ID
```

## Usage

### Basic Scraping

With election ID as argument:

```bash
python dupage_county_scraper.py --id 123456
```

This will:
1. Fetch summary results from Scytl JSON endpoint
2. Parse all contests and candidates
3. Save to `dupage_results.json`

### List Available Elections

Try to list elections (may or may not work depending on Scytl configuration):

```bash
python dupage_county_scraper.py --list
```

If successful, will show:
```
Available elections:
  ID: 123456
  Name: March 17, 2026 Primary
  Date: 2026-03-17
```

### Specify Output Directory

```bash
python dupage_county_scraper.py --id 123456 --output /path/to/results/
```

## Output Format

```json
{
  "county": "DuPage County",
  "scraped_at": "2026-03-17T20:15:00",
  "source": "Scytl summary JSON",
  "election_id": "123456",
  "summary": {
    "precincts_reporting": 451,
    "total_precincts": 451,
    "ballots_cast": 125432,
    "registered_voters": 601234
  },
  "contests": [
    {
      "name": "DEM President of the United States",
      "party": "Democratic",
      "candidates": [
        {
          "name": "JOSEPH R. BIDEN",
          "votes": 45678,
          "percent": 65.2
        },
        {
          "name": "UNCOMMITTED",
          "votes": 24322,
          "percent": 34.8
        }
      ]
    }
  ]
}
```

## Scytl JSON API Structure

The scraper accesses these Scytl endpoints:

### Summary Results
```
https://www.dupageresults.gov/IL/DuPage/[ELECTION_ID]/json/en/summary.json
```

Contains:
- All contests with candidates and vote totals
- Precinct reporting statistics
- Turnout information

### Election Settings (optional)
```
https://www.dupageresults.gov/IL/DuPage/[ELECTION_ID]/json/en/electionsettings.json
```

Contains:
- Election metadata
- Contest configuration
- Reporting unit details

### Field Name Variations

Scytl uses abbreviated JSON to reduce file size. The scraper handles these variations:

| Data | Possible Keys |
|------|---------------|
| Contest Name | `C`, `Contest`, `ContestName`, `Name` |
| Candidates | `CH`, `Candidates`, `Choices` |
| Candidate Name | `N`, `Candidate`, `Name`, `Choice` |
| Votes | `V`, `Votes`, `VoteCount` |
| Percentage | `P`, `Percent`, `Percentage` |

## Party Detection

DuPage typically prefixes contest names with party:

- **"DEM President..."** → Democratic
- **"REP President..."** → Republican
- All others → Non-Partisan

## Election Day Workflow

### Pre-Election Testing (Recommended)

Test with a historical election:

1. Visit https://www.dupageresults.gov/IL/DuPage
2. Select a past election (e.g., 2024 General, 2024 Primary)
3. Extract that election ID from URL
4. Run scraper to verify it works:

```bash
python dupage_county_scraper.py --id [HISTORICAL_ID]
```

This confirms:
- JSON endpoints are accessible
- Parsing logic works correctly
- Output format is as expected

### Election Night (March 17, 2026)

**Timeline:**
- 7:00 PM - Polls close
- 7:30-8:00 PM - First results typically posted
- Throughout night - Results updated as precincts report

**Monitoring Strategy:**

```bash
# Run every 10-15 minutes with latest election ID
while true; do
  python dupage_county_scraper.py --id 123456
  echo "Updated at $(date)"
  sleep 600  # 10 minutes
done
```

**What to Watch:**
- `precincts_reporting` vs `total_precincts`
- `ballots_cast` - should increase over time
- New contests appearing as they're reported

### Real-Time Updates

Scytl typically updates their JSON files every 5-10 minutes on election night. The summary.json file is regenerated with each update, so you can simply re-fetch to get latest results.

## Troubleshooting

### "Election ID not configured" Error

**Problem:** Scraper can't find results

**Solution:**
- Make sure you're using the correct election ID
- Visit the URL manually to verify: `/IL/DuPage/[YOUR_ID]/json/en/summary.json`
- Check that results are actually posted (may not be available until polls close)

### 404 Not Found

**Problem:** JSON endpoint returns 404

**Solutions:**
- Election ID is wrong - double-check the URL
- Results not yet posted - too early on election night
- Path structure may have changed - verify URL in browser
- Try different endpoint format if structure changed

### Empty Contests Array

**Problem:** Summary JSON loads but no contests parsed

**Solutions:**
- Scytl may have changed their JSON field names
- Check raw JSON in browser to see actual structure
- May need to adjust `_parse_scytl_contest()` method for new field names
- Some elections have results in different JSON structure

### Connection Timeout

**Problem:** Request times out

**Solutions:**
- Server may be overloaded on election night
- Increase timeout: modify `requests.get(url, timeout=60)`
- Try again - usually temporary
- Check your internet connection

## Performance

- **Scraping speed**: ~2-3 seconds per request
- **Network**: Lightweight (JSON is compact)
- **Resources**: Minimal (just JSON parsing)
- **Rate limits**: Unknown, but respectful 10-minute intervals recommended

## Comparison to Other Counties

| County | Platform | Complexity | Reliability | Speed |
|--------|----------|------------|-------------|-------|
| **DuPage** | Scytl API | ⭐⭐ Medium | ⭐⭐⭐⭐⭐ | 2-3s |
| Cook Clerk | Excel/ZIP | ⭐⭐⭐ High | ⭐⭐⭐⭐⭐ | 10-30s |
| Will | Clarity API | ⭐⭐ Medium | ⭐⭐⭐⭐⭐ | 2-3s |

DuPage's Scytl platform is **very reliable** because:
- Direct JSON access (no scraping/parsing HTML)
- Consistent API structure
- Professional vendor with stable platform
- Well-documented (in other implementations)

## Important Notes

### Election ID Changes

**Critical:** The election ID is different for EVERY election!

- 2024 General has one ID
- 2024 Primary has a different ID  
- 2026 Primary will have yet another ID

You MUST update the ID for each new election!

### Multiple Elections Same Day

If there are multiple elections on March 17, 2026 (e.g., Primary + Special Election), each will have its own ID. Make sure you're scraping the right one!

### Data Freshness

JSON files are typically cached for 5-10 minutes on Scytl's CDN. Even if you request every minute, you may not see updates more frequently than that.

### Official vs Unofficial

Results on election night are **unofficial**. Official results are certified weeks later after absentee/provisional ballot processing.

## Advanced Usage

### Custom Parsing

If you need to extract additional data from the JSON:

```python
# Access raw Scytl data
scraper = DuPageCountyScraper('123456')
response = requests.get(scraper.summary_url)
raw_data = response.json()

# Extract custom fields
# ... your custom parsing here ...
```

### Detailed Results

Scytl may have additional endpoints for precinct-level detail:

```
/IL/DuPage/[ID]/json/en/precinct/[PRECINCT_ID].json
```

These aren't implemented in the basic scraper but could be added if needed.

## Support Contacts

**DuPage County Clerk's Office**
- Website: dupagecounty.gov/elections
- Phone: (630) 407-5600
- Email: elections@dupagecounty.gov

**For technical issues:**
- Check if results are posted at all (may just be too early)
- Verify election ID is correct
- Try accessing JSON URL manually in browser

## Next Steps

1. **Test with historical data** - Run scraper on past election
2. **Monitor for election ID** - Check site on March 17, 2026
3. **Update and run** - Use new ID to scrape live results
4. **Combine with other counties** - Aggregate multi-county races
