# Iroquois County Scraper Setup - Custom Web Platform

This guide covers scraping election results for **Iroquois County** using their custom web-based system.

## County Overview

**Iroquois County Statistics:**
- Population: ~27,000 residents
- Voters: ~20,000 registered voters
- County seat: Watseka
- Major towns: Watseka, Gilman, Onarga, Milford
- Location: East-central Illinois, Indiana border

**Electoral Significance:** Rural agricultural county bordering Indiana. Part of eastern Illinois voting bloc. Typically Republican-leaning. Small but completes coverage of east-central Illinois region. Represents rural/agricultural voting patterns common in eastern Illinois.

## Platform Overview

**System:** Custom web-based election results system  
**Website:** iroquoiscountyil.gov/elections  
**Output Format:** Unknown until election day (PDF, HTML, or text)  
**Technology:** Custom platform  
**Complexity:** ⭐⭐ Medium (format unknown until accessed)  
**Coverage:** All of Iroquois County

### Why This Platform is Flexible

Iroquois County's custom system could post results in several formats:
- PDF documents (like Fulton, La Salle, Rock Island, Woodford)
- HTML results pages with tables (like Kane)
- Text-based reports
- Excel spreadsheets

The scraper is designed to handle multiple formats!

## Installation

### Dependencies

```bash
pip install requests beautifulsoup4 pdfplumber
```

The scraper uses:
- `requests` - Download web pages and files
- `beautifulsoup4` - Parse HTML content
- `pdfplumber` - Extract text from PDFs (optional but recommended)

## Usage

### Finding the Results URL

**CRITICAL:** You must provide the direct URL to the results on election day.

#### Step 1: Visit the Website

Navigate to: https://iroquoiscountyil.gov/elections

#### Step 2: Locate Results

Look for links like:
- "Election Results"
- "2026 Primary Election Results"
- "March 17, 2026 Results"
- "Current Election"

#### Step 3: Copy the URL

Right-click the results link and select **"Copy link address"**

Possible URL formats:
```
https://iroquoiscountyil.gov/elections/results/2026-primary.html
https://iroquoiscountyil.gov/elections/results/2026-primary.pdf
https://iroquoiscountyil.gov/wp-content/uploads/2026/03/results.pdf
https://iroquoiscountyil.gov/elections/results.php?id=2026-primary
```

#### Step 4: Run the Scraper

```bash
python iroquois_county_scraper.py --url "YOUR_COPIED_URL"
```

### With PDF URL

If results are posted as PDF:

```bash
python iroquois_county_scraper.py --url "https://iroquoiscountyil.gov/elections/results/2026-primary.pdf"
```

### With HTML URL

If results are posted as HTML page:

```bash
python iroquois_county_scraper.py --url "https://iroquoiscountyil.gov/elections/results/2026-primary.html"
```

### Without URL (Shows Instructions)

```bash
python iroquois_county_scraper.py
```

This displays helpful setup instructions.

## Testing with Historical Data

### Why Test Before Election Day

Testing with 2024 or earlier data:
- Verifies your Python environment is set up correctly
- Ensures dependencies are installed
- Shows you what format Iroquois uses
- Lets you understand the output structure
- Reduces stress on election night!

### How to Test

1. **Visit the website:**
   https://iroquoiscountyil.gov/elections

2. **Find historical results:**
   - Look for "Past Election Results" or "Archive"
   - Find "2024 Primary Election" (March 19, 2024)
   - Or try "2022 General Election" (November 8, 2022)

3. **Copy the historical results URL**

4. **Run the scraper:**
   ```bash
   python iroquois_county_scraper.py \
     --url "HISTORICAL_URL" \
     --date 2024-03-19
   ```

5. **Verify output:**
   - Check `iroquois_results.json`
   - Verify contests are parsed correctly
   - Confirm vote totals match the source

If historical data scrapes successfully, you're ready for 2026!

## Output Format

```json
{
  "county": "Iroquois",
  "election_date": "2026-03-17",
  "source": "Iroquois County Elections Website",
  "url": "https://iroquoiscountyil.gov/elections/...",
  "scraped_at": "2026-03-17T20:30:00",
  "metadata": {
    "registered_voters": 20000,
    "ballots_cast": 4500,
    "precincts_reporting": 25,
    "total_precincts": 25,
    "turnout_percent": 22.5
  },
  "contests": [
    {
      "name": "PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY",
      "party": "Republican",
      "candidates": [
        {
          "name": "DONALD J. TRUMP",
          "votes": 2845,
          "percent": 88.2
        },
        {
          "name": "NIKKI HALEY",
          "votes": 381,
          "percent": 11.8
        }
      ]
    }
  ]
}
```

## Format Detection

The scraper automatically detects the format:

### PDF Detection

If URL ends with `.pdf`:
- Downloads PDF file
- Extracts text with pdfplumber
- Parses contests and candidates from text
- Similar to Woodford, Fulton, La Salle, Rock Island

### HTML Detection

If URL doesn't end with `.pdf`:
- Fetches HTML page
- Parses with BeautifulSoup
- Extracts data from tables or structured content
- Similar to Kane County

## Party Detection

The scraper detects party from contest names and candidate names:

### Primary Elections

Contests typically include party in name:
```
"PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY"  → Republican
"PRESIDENT OF THE UNITED STATES - DEMOCRATIC PARTY"  → Democratic
"COUNTY BOARD MEMBER"                                 → Non-Partisan
```

Party indicators recognized:
- `REPUBLICAN`, `- REP`, `(REP)`
- `DEMOCRATIC`, `DEMOCRAT`, `- DEM`, `(DEM)`
- No indicator = Non-Partisan

### General Elections

Candidates typically show party:
```
"DONALD J. TRUMP (REP)"  → Republican candidate
"KAMALA D. HARRIS (DEM)" → Democratic candidate
```

## Troubleshooting

### URL Not Found / 404 Error

**Problem:** Can't access the URL

**Solutions:**
- Verify URL is correct (copy from browser address bar)
- Check if results are actually posted yet
- Try visiting URL in browser first
- Results may post later than expected
- Check for typos in URL

### Empty Results

**Problem:** Scraper runs but returns no contests

**Solutions:**
- Check if page has loaded fully
- Verify data is text (not scanned image)
- Format may differ from expectations
- May need format-specific adjustments

### PDF Parsing Fails

**Problem:** PDF won't parse or extracts gibberish

**Solutions:**
- Ensure pdfplumber is installed: `pip install pdfplumber`
- Check if PDF is text-based (not scanned image)
- Try opening PDF manually to verify it's valid
- Re-download PDF in case of corruption

### HTML Parsing Issues

**Problem:** HTML page loads but data extraction fails

**Solutions:**
- Page structure may use different layout
- Check if results are in JavaScript (not static HTML)
- Try viewing page source to understand structure
- May need custom parsing logic

### Wrong Vote Totals

**Problem:** Numbers don't match source

**Solutions:**
- Verify you're comparing correct columns
- Check for comma/formatting issues
- Some sites show different totals
- Percentages may use different rounding

### Party Assignment Wrong

**Problem:** Contests assigned incorrect party

**Solutions:**
- Check contest name for party indicators
- Verify candidate names include party
- Non-partisan races won't have party
- Can manually adjust in post-processing

## Election Day Workflow

### Pre-Election Setup

1. **Install dependencies:**
   ```bash
   pip install requests beautifulsoup4 pdfplumber
   ```

2. **Test with historical data:**
   - Find 2024 results on website
   - Test scraper with historical URL
   - Verify output format

3. **Bookmark the website:**
   - https://iroquoiscountyil.gov/elections
   - Save to election night monitoring list

4. **Have scraper ready:**
   - Know where script is located
   - Have terminal/command prompt ready
   - Know output destination

### Election Night - Timeline

**7:00 PM** - Polls close

**7:30-9:00 PM** - First results typically posted
- Small counties like Iroquois usually post within 2 hours
- Check website periodically
- Look for "Unofficial Results" link

**Throughout evening** - Results updated
- County may update same page with new totals
- Or post entirely new document
- Check every 15-30 minutes

**Next day - 2 weeks** - Official results
- Canvassed results posted
- "Official Results" designation
- Final certified totals

### Monitoring Strategy

```bash
# Manual monitoring recommended
# Since format is unknown, automated polling could fail

# Every 15-30 minutes:
# 1. Refresh iroquoiscountyil.gov/elections
# 2. Check for new results link
# 3. Copy URL when available
# 4. Run scraper:

python iroquois_county_scraper.py --url "RESULTS_URL"

# Save each version if tracking updates:
python iroquois_county_scraper.py --url "URL" --output results_8pm.json
python iroquois_county_scraper.py --url "URL" --output results_9pm.json
```

### Best Practices

- Start monitoring around 7:30 PM
- Be patient - small county may take time to upload
- Save URL when you find it for repeated scraping
- Don't overload their server - 15-minute intervals minimum
- Keep previous versions if tracking changes

## Format Comparison

### Iroquois vs Other Custom Counties

| County | Format | Complexity | Known Features |
|--------|--------|------------|----------------|
| **Iroquois** | **Unknown (TBD)** | **⭐⭐ Medium** | **Flexible scraper** |
| Woodford | Summary Report text | ⭐⭐ Medium | Dot-aligned, tested |
| Kane | Custom HTML | ⭐ Easy | Table-based |
| Fulton | Cumulative PDF | ⭐⭐ Medium | Vote method detail |
| La Salle | Summary PDF | ⭐⭐ Medium | Clean sections |
| Rock Island | GEMS PDF | ⭐ Easy | Cleanest format |

**Iroquois advantage:** Flexible scraper handles multiple formats!

### Why Format is Unknown

Unlike larger counties with established platforms:
- Small counties often change systems
- May use different formats for different elections
- Platform may be simple CMS
- Results format determined by clerk's preference

The flexible scraper handles this uncertainty!

## Possible Format Scenarios

Based on patterns from similar Illinois counties:

### Scenario A: PDF Document (Likely)

Similar to Woodford, Fulton, La Salle, Rock Island:
- Structured PDF
- Contests with candidates and votes
- Summary statistics in header
- **Scraper ready:** Full PDF parsing included

### Scenario B: HTML Table (Likely)

Similar to Kane County:
- Results page with HTML tables
- One table per contest
- Candidate names and vote totals
- **Scraper ready:** Table parsing included

### Scenario C: Text Report (Possible)

Similar to Woodford/McLean:
- Plain text structure
- Contests separated by headers
- Candidate lines with votes
- **Scraper ready:** Text parsing included

### Scenario D: Excel Spreadsheet (Less Likely)

Similar to Champaign County:
- Downloadable .xlsx file
- Multiple sheets by party
- **Adaptation possible:** Can extend scraper

## County-Specific Notes

### Geographic Context

Iroquois County location matters:
- **Eastern Illinois border** - Indiana state line
- **Agricultural economy** - Corn and soybean production
- **Rural character** - Small towns, farming communities
- **Transportation** - US Route 24, Illinois Route 1

### Major Population Centers

**Watseka** (county seat, ~5,000 residents):
- Largest town in county
- County government center
- Historic courthouse square

**Gilman** (~1,800 residents):
- Railroad town
- Agricultural center

**Onarga** (~1,300 residents):
- Small town character
- Rural community

**Milford** (~1,200 residents):
- Eastern county location
- Near Indiana border

### Electoral Patterns

- **Turnout:** Typically 20-30% for primaries, 55-65% for generals
- **Party lean:** Solidly Republican in recent elections
- **Key issues:** Agriculture, local taxes, rural development
- **Bellwether status:** Reflects eastern Illinois rural trends

### Precinct Structure

Approximately 25-30 precincts:
- Mix of town precincts (Watseka, Gilman, Onarga, Milford)
- Township precincts (rural areas)
- Some townships may combine precincts

Full precinct list available on county website.

## Why This County Matters

Despite being small (~20K voters), Iroquois matters because:
1. **Eastern Illinois coverage** - Completes border region
2. **Rural representation** - Typical of agricultural counties
3. **Geographic diversity** - Adds eastern Illinois to dataset
4. **Comprehensive project** - One of final 4 counties

Completes coverage of east-central Illinois when combined with Champaign, Ford, Vermilion counties.

## Historical Context

Iroquois County election administration:
- County Clerk is sole election authority
- No separate city election boards
- Website appears relatively simple
- Format has likely been consistent
- Small office may use simple solutions

Testing with historical data reveals format!

## Primary vs General Format

### Primary Elections

For primaries, expect:
- Separate sections or contests by party
- "REPUBLICAN PARTY" and "DEMOCRATIC PARTY" in contest names
- Party-specific ballot races

Example:
```
PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY
[Republican candidates]

PRESIDENT OF THE UNITED STATES - DEMOCRATIC PARTY
[Democratic candidates]
```

### General Elections

For generals, expect:
- Single contest with all party candidates
- Party indicators after candidate names
- More local non-partisan races

Example:
```
PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES
DONALD J. TRUMP (REP)
KAMALA D. HARRIS (DEM)
```

The scraper handles both!

## Integration with Project

### Within Multi-County System

Iroquois integrates with your 38-county project:
- Standard JSON output format
- Consistent party detection
- Compatible with aggregation system
- Ready for statewide rollup

### Adjacent Counties

Iroquois completes regional coverage:
- **Ford County** (north) - ✅ Complete (pollresults.net)
- **Vermilion County** (east) - ✅ Complete (pollresults.net)
- **Livingston County** (west) - ✅ Complete (pollresults.net)
- **Kankakee County** (south) - ✅ Complete (Clarity Elections)

With Iroquois complete, entire east-central Illinois region has full coverage!

## Summary - Quick Reference

**✅ To scrape Iroquois County:**

1. Visit: https://iroquoiscountyil.gov/elections
2. Find: "2026 Primary Election Results" link
3. Copy results URL (HTML page or PDF/document link)
4. Run: `python iroquois_county_scraper.py --url [URL]`
5. Get: Clean JSON with all contests, candidates, votes

**📊 What you get:**
- All contests with candidates, votes, percentages
- Party detection from contest/candidate names
- Summary statistics (turnout, precincts, registered voters)
- Flexible format support (PDF, HTML, text)
- Metadata extraction

**💡 Why it's good:**
- Flexible scraper handles multiple formats
- No guesswork - just provide URL on election day
- Clear instructions for finding results
- Easy testing with historical data
- Robust error handling

**📍 County importance:**
- ~20K voters in east-central Illinois
- Rural agricultural county on Indiana border
- Completes eastern Illinois coverage
- One of final 4 counties in project!

**🎯 Election day strategy:**
- Start monitoring at 7:30 PM
- Check website every 15-30 minutes
- Copy URL when results appear
- Run scraper with URL
- Repeat periodically for updates

Iroquois County's flexible scraper is ready for whatever format they use!
