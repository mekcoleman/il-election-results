# Kane County Election Results Scraper Setup

This scraper handles election results from **Kane County**, Illinois' 3rd largest county.

## County Overview

**Kane County Statistics:**
- Population: ~550,000 residents
- Voters: ~350,000+ registered voters
- Ranking: 3rd largest Illinois county
- Location: Western Chicago suburbs and exurbs
- Major cities: Aurora (shared with DuPage), Elgin, St. Charles, Geneva, Batavia, Carpentersville

**Electoral Significance:** Kane is a critical collar county. Historically swing county that has trended Democratic in recent elections. Mix of suburban and rural areas. Home to fast-growing Hispanic communities, particularly in Aurora and Elgin.

## Platform Overview

**Vendor:** Custom Kane County system  
**Technology:** Date-based HTML with clean table structure  
**Complexity:** ⭐ Easy

Kane County maintains one of the **cleanest and most reliable** election results websites in Illinois. Simple HTML structure, consistent formatting, predictable URLs.

## Installation

### Dependencies

Standard requirements only:

```bash
pip install requests beautifulsoup4
```

No special libraries needed - just `requests` for HTTP and `BeautifulSoup` for HTML parsing.

## URL Structure

Kane County uses a beautifully simple date-based URL pattern:

### Pattern

```
https://electionresults.kanecountyil.gov/YYYY-MM-DD/Contests/
```

### Examples

```
# 2026 Primary (March 17, 2026)
https://electionresults.kanecountyil.gov/2026-03-17/Contests/

# 2024 Primary (March 19, 2024)
https://electionresults.kanecountyil.gov/2024-03-19/Contests/

# 2024 General (November 5, 2024)
https://electionresults.kanecountyil.gov/2024-11-05/Contests/
```

### Available Endpoints

Each election date has two main endpoints:

1. **Contest Totals**: `/YYYY-MM-DD/Contests/`
   - Summary results by contest
   - County-wide totals
   - Precinct reporting statistics

2. **Precinct Results**: `/YYYY-MM-DD/Precincts/`
   - Results by individual precinct
   - More detailed breakdown
   - Not used by this scraper (contest totals are sufficient)

## Usage

### Basic Scraping

For the 2026 Primary:

```bash
python kane_county_scraper.py
```

This uses the default date of `2026-03-17` (March 17, 2026 Primary).

### Custom Date

For a different election:

```bash
python kane_county_scraper.py --date 2024-03-19
```

### Specify Output Directory

```bash
python kane_county_scraper.py --output /path/to/results/
```

### Combined Options

```bash
python kane_county_scraper.py --date 2026-03-17 --output ./results/
```

## Output Format

```json
{
  "county": "Kane County",
  "election_date": "2026-03-17",
  "scraped_at": "2026-03-17T20:15:00",
  "source": "Kane County custom platform",
  "summary": {
    "registered_voters": 350234,
    "ballots_cast": 52891,
    "turnout_percent": 15.09
  },
  "contests": [
    {
      "name": "FOR PRESIDENT OF THE UNITED STATES - REP",
      "party": "Republican",
      "precincts_reporting": 292,
      "total_precincts": 292,
      "candidates": [
        {
          "name": "DONALD J. TRUMP",
          "votes": 17786,
          "percent": 77.56
        },
        {
          "name": "NIKKI HALEY",
          "votes": 3946,
          "percent": 17.21
        }
      ]
    },
    {
      "name": "FOR PRESIDENT OF THE UNITED STATES - DEM",
      "party": "Democratic",
      "precincts_reporting": 292,
      "total_precincts": 292,
      "candidates": [
        {
          "name": "JOSEPH R BIDEN JR",
          "votes": 21127,
          "percent": 94.22
        }
      ]
    }
  ]
}
```

## HTML Structure

Kane County's HTML is exceptionally clean:

### Page Structure

```html
<h1>2024 General Primary Results - Official Contest Results</h1>
<p>Current as of Wednesday, April 3, 2024 07:49 AM</p>

<p>Registered Voters: <strong>309543</strong></p>
<p>Ballots Cast: <strong>47334</strong></p>
<p>Turnout: <strong>15.29%</strong></p>

<h2>FOR PRESIDENT OF THE UNITED STATES - REP</h2>
<p>Registered Voters: <strong>309543</strong></p>
<p>Ballots Cast: <strong>23396</strong></p>
<p>Turnout: <strong>7.56%</strong></p>
<p><strong>292</strong> of <strong>292</strong> Precincts Reporting</p>

<table>
  <tr>
    <td>DONALD J. TRUMP</td>
    <td>17786</td>
    <td>77.56%</td>
  </tr>
  <tr>
    <td>NIKKI HALEY</td>
    <td>3946</td>
    <td>17.21%</td>
  </tr>
</table>

<h2>FOR PRESIDENT OF THE UNITED STATES - DEM</h2>
<!-- ... next contest ... -->
```

### Key Features

- **Consistent structure**: Every contest follows the same format
- **Clean tables**: Simple 3-column tables (name, votes, percent)
- **Clear headings**: H2 elements for contest names
- **Separated stats**: Paragraphs with summary statistics
- **No JavaScript**: Pure HTML, no dynamic loading

## Party Detection

Kane County includes party suffix in contest names:

| Suffix | Party |
|--------|-------|
| ` - REP` | Republican |
| ` - DEM` | Democratic |
| ` - NP` | Non-Partisan |

Examples:
- "FOR PRESIDENT OF THE UNITED STATES **- REP**" → Republican
- "FOR PRESIDENT OF THE UNITED STATES **- DEM**" → Democratic
- "(VILL OF PINGREE GROVE) LEVY A NON-HOME RULE MUNICIPAL SALES TAX **- NP**" → Non-Partisan

## Election Day Workflow

### Pre-Election Testing

Test with the 2024 Primary to verify everything works:

```bash
python kane_county_scraper.py --date 2024-03-19
```

This will:
1. Fetch real historical data
2. Verify parsing logic works
3. Confirm output format is correct
4. Show you what to expect on election night

### Election Night (March 17, 2026)

**Timeline:**
- 7:00 PM - Polls close
- 7:30-8:00 PM - First results typically posted
- Throughout night - Results updated as precincts report

**Monitoring Strategy:**

```bash
# Run every 10-15 minutes
while true; do
  python kane_county_scraper.py
  echo "Updated at $(date)"
  sleep 600  # 10 minutes
done
```

**What to Watch:**
- `precincts_reporting` vs `total_precincts` for each contest
- `ballots_cast` - should increase over time
- Overall `turnout_percent`

### Real-Time Updates

Kane County updates their website regularly on election night:
- Initial results: Within 30-60 minutes of polls closing
- Updates: Every 15-30 minutes as precincts report
- Final unofficial: Usually complete by midnight

The HTML is regenerated with each update, so simply re-scraping will get latest results.

## Troubleshooting

### 404 Not Found

**Problem:** URL returns 404

**Solutions:**
- Verify election date format (must be YYYY-MM-DD)
- Check that results are actually posted
- Visit https://electionresults.kanecountyil.gov/ to see available elections
- Results may not be posted until after polls close

### No Contests Found

**Problem:** Scraper runs but finds no contests

**Solutions:**
- Check if page structure has changed
- View HTML source in browser to verify format
- May be too early - results not yet posted
- Try with historical date (2024-03-19) to test parsing

### Empty Candidate Lists

**Problem:** Contests are found but no candidates

**Solutions:**
- HTML table structure may have changed
- Check if tables are nested differently
- May need to adjust `_parse_contest()` method
- Verify with browser that candidates are visible on page

### Wrong Party Detection

**Problem:** Contests assigned to wrong party

**Solutions:**
- Check if suffix format changed (" - REP", " - DEM", " - NP")
- May need to update `detect_party()` method
- Kane historically has been very consistent with this format

## Performance

- **Scraping speed**: ~3-5 seconds total
- **Network**: Single HTTP request, lightweight HTML
- **Resources**: Minimal memory usage
- **Rate limits**: No known limits, but be respectful (10-minute intervals recommended)

## Comparison to Other Counties

| County | Platform | Complexity | Reliability | Speed |
|--------|----------|------------|-------------|-------|
| **Kane** | Custom HTML | ⭐ Easy | ⭐⭐⭐⭐⭐ | 3-5s |
| DuPage | Scytl JSON | ⭐⭐ Medium | ⭐⭐⭐⭐⭐ | 2-3s |
| Cook Clerk | Excel/ZIP | ⭐⭐⭐ High | ⭐⭐⭐⭐⭐ | 10-30s |
| Will | Clarity API | ⭐⭐ Medium | ⭐⭐⭐⭐⭐ | 2-3s |

Kane County is **the easiest county to scrape** because:
- No authentication needed
- No special IDs to find
- Simple, consistent HTML structure
- Predictable date-based URLs
- No JavaScript/dynamic loading
- Historically very stable format

## Important Notes

### Date Format Matters

**Critical:** The date MUST be in YYYY-MM-DD format with leading zeros:

✅ Correct: `2026-03-17`  
❌ Wrong: `2026-3-17` (no leading zero)  
❌ Wrong: `03-17-2026` (wrong order)  
❌ Wrong: `2026/03/17` (wrong separator)

### Results Availability

Results are posted on Kane County's website:
- **Unofficial results**: Night of election (starting ~7:30 PM)
- **Updated results**: Throughout counting period
- **Final unofficial**: Usually by midnight
- **Official certified**: ~30 days after election

This scraper accesses **unofficial results** only.

### Historical Data

Kane County maintains excellent historical archives going back to 2012. All elections use the same URL structure and HTML format. Great for testing and historical analysis!

### Primary vs General Elections

The scraper works identically for both:
- **Primary**: `/2026-03-17/Contests/`
- **General**: `/2026-11-03/Contests/`

Just change the date parameter.

## Advanced Usage

### Filtering by Party

If you only want Democratic or Republican contests:

```python
from kane_county_scraper import KaneCountyScraper

scraper = KaneCountyScraper('2026-03-17')
results = scraper.scrape_contests()

# Filter to only Democratic contests
dem_contests = [c for c in results['contests'] if c['party'] == 'Democratic']

# Filter to only Republican contests
rep_contests = [c for c in results['contests'] if c['party'] == 'Republican']
```

### Getting Specific Contests

```python
# Find presidential primary results
for contest in results['contests']:
    if 'PRESIDENT' in contest['name']:
        print(f"{contest['name']}:")
        for candidate in contest['candidates']:
            print(f"  {candidate['name']}: {candidate['votes']:,} ({candidate['percent']:.1f}%)")
```

### Monitoring Precinct Reporting

```python
# Track how many precincts have reported
for contest in results['contests']:
    reporting = contest.get('precincts_reporting', 0)
    total = contest.get('total_precincts', 0)
    if total > 0:
        pct = (reporting / total) * 100
        print(f"{contest['name']}: {reporting}/{total} precincts ({pct:.1f}%)")
```

## Support Contacts

**Kane County Clerk's Office**
- Website: clerk2.kanecountyil.gov
- Phone: (630) 232-5950
- Email: CountyClerk@KaneCountyIL.gov

**For technical issues:**
- Check if results page is accessible in browser
- Verify date format is correct (YYYY-MM-DD)
- Try historical date to test if scraper is working
- Most issues are timing-related (results not yet posted)

## Next Steps

1. **Test with historical data** - Run scraper on 2024-03-19
2. **Verify date format** - Make sure using YYYY-MM-DD
3. **Monitor on election night** - Results typically posted by 7:30-8:00 PM
4. **Combine with other counties** - Aggregate results for statewide races

## Why Kane County is Great for Scraping

Kane County deserves recognition for maintaining an **exemplary election results website**:

✅ **Simple URLs** - Easy to construct, no guessing  
✅ **Clean HTML** - Semantic, well-structured  
✅ **Consistent format** - Same structure across all elections  
✅ **No JavaScript** - Pure HTML, works with simple HTTP requests  
✅ **Historical archives** - Data back to 2012, same format  
✅ **Fast updates** - Regular updates on election night  
✅ **Mobile-friendly** - Responsive design  
✅ **Accessible** - No barriers to data access  

This is a model for how election results should be published online. If all counties did this, election data would be trivially easy to aggregate!
