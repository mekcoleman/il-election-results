# Woodford County Scraper Setup - Custom Web Platform

This guide covers scraping election results for **Woodford County** using their custom web-based system.

## County Overview

**Woodford County Statistics:**
- Population: ~38,000 residents
- Voters: ~25,000 registered voters
- County seat: Eureka
- Major towns: Eureka, El Paso, Metamora, Roanoke
- Location: Central Illinois, east of Peoria

**Electoral Significance:** Mix of suburban (Peoria metro spillover) and rural agricultural areas. Home to Eureka College, Ronald Reagan's alma mater. Typically Republican-leaning. Part of central Illinois voting bloc. While mid-sized, represents important Peoria metropolitan area growth.

## Platform Overview

**System:** Custom web-based election results system  
**Website:** woodfordcountyelections.com  
**Output Format:** HTML pages or downloadable documents (PDF/Excel)  
**Technology:** Custom platform  
**Complexity:** ⭐⭐ Medium (format unknown until election day)  
**Coverage:** All of Woodford County

### Why This Platform is Flexible

Woodford's custom system could post results in several formats:
- HTML results pages with tables
- PDF documents (like Fulton, La Salle, Rock Island)
- Excel spreadsheets (like Champaign)
- Text-based reports (like McLean)

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

Navigate to: https://woodfordcountyelections.com

#### Step 2: Locate Results

Look for links like:
- "Election Results"
- "2026 Primary Election Results"
- "Current Election Results"
- "March 17, 2026 Results"

#### Step 3: Copy the URL

Right-click the results link and select **"Copy link address"**

Possible URL formats:
```
https://woodfordcountyelections.com/results/2026-primary.html
https://woodfordcountyelections.com/results.php?election=2026-primary
https://woodfordcountyelections.com/wp-content/uploads/2026/03/results.pdf
https://woodfordcountyelections.com/files/primary-2026.xlsx
```

#### Step 4: Run the Scraper

```bash
python woodford_county_scraper.py --url "YOUR_COPIED_URL"
```

### With PDF URL

If results are posted as PDF:

```bash
python woodford_county_scraper.py --url "https://woodfordcountyelections.com/wp-content/uploads/2026/03/results.pdf"
```

### With HTML URL

If results are posted as HTML page:

```bash
python woodford_county_scraper.py --url "https://woodfordcountyelections.com/results/2026-primary.html"
```

### Without URL (Shows Instructions)

```bash
python woodford_county_scraper.py
```

This displays helpful setup instructions.

## Testing with Historical Data

### Why Test Before Election Day

Testing with 2024 or earlier data:
- Verifies your Python environment is set up correctly
- Ensures dependencies are installed
- Shows you what format Woodford uses
- Lets you understand the output structure
- Reduces stress on election night!

### How to Test

1. **Visit the website:**
   https://woodfordcountyelections.com

2. **Find 2024 Primary results:**
   - Look for "Past Election Results" or "Archive"
   - Find "2024 Primary Election" (March 19, 2024)
   - Or try "2022 General Election" (November 8, 2022)

3. **Copy the historical results URL**

4. **Run the scraper:**
   ```bash
   python woodford_county_scraper.py \
     --url "HISTORICAL_URL" \
     --date 2024-03-19
   ```

5. **Verify output:**
   - Check `woodford_results.json`
   - Verify contests are parsed correctly
   - Confirm vote totals match the source

If historical data scrapes successfully, you're ready for 2026!

## Output Format

```json
{
  "county": "Woodford",
  "election_date": "2026-03-17",
  "source": "Woodford County Elections Website",
  "url": "https://woodfordcountyelections.com/results/...",
  "scraped_at": "2026-03-17T20:30:00",
  "metadata": {
    "registered_voters": 25000,
    "ballots_cast": 5200,
    "precincts_reporting": 18,
    "total_precincts": 18,
    "turnout_percent": 20.8
  },
  "contests": [
    {
      "name": "PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY",
      "party": "Republican",
      "candidates": [
        {
          "name": "DONALD J. TRUMP",
          "votes": 3245,
          "percent": 87.2
        },
        {
          "name": "NIKKI HALEY",
          "votes": 476,
          "percent": 12.8
        }
      ]
    },
    {
      "name": "PRESIDENT OF THE UNITED STATES - DEMOCRATIC PARTY",
      "party": "Democratic",
      "candidates": [
        {
          "name": "JOE BIDEN",
          "votes": 1124,
          "percent": 91.4
        },
        {
          "name": "DEAN PHILLIPS",
          "votes": 106,
          "percent": 8.6
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
- Similar to Fulton, La Salle, Rock Island counties

### HTML Detection

If URL doesn't end with `.pdf`:
- Fetches HTML page
- Parses with BeautifulSoup
- Extracts data from tables or structured content
- Similar to Kane County

### Fallback

If neither format works well:
- Manual extraction may be needed
- Document provides clear structure for adaptation
- Contact maintainer for format updates

## Party Detection

The scraper detects party from contest names:

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

The scraper handles both primary and general election formats.

## Troubleshooting

### URL Not Found / 404 Error

**Problem:** Can't access the URL

**Solutions:**
- Verify URL is correct (copy from browser address bar)
- Check if results are actually posted yet
- Try visiting URL in browser first
- Results may post later in evening than expected
- Check for typos in URL

### Empty Results

**Problem:** Scraper runs but returns no contests

**Solutions:**
- Check if page has loaded fully
- Verify data is text (not scanned image)
- Format may differ from expectations
- Run with `--url` to see actual page structure
- May need format adjustment

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
- May need custom parsing logic for this format

### Wrong Vote Totals

**Problem:** Numbers don't match source

**Solutions:**
- Verify you're comparing correct columns
- Check for comma/formatting issues
- Some sites show "total votes" vs "votes for winner"
- Percentages may use different rounding

### Party Assignment Wrong

**Problem:** Contests assigned incorrect party

**Solutions:**
- Check contest name for party indicators
- Verify name includes "REPUBLICAN" or "DEMOCRATIC"
- Non-partisan races won't have party
- Can manually adjust in post-processing if needed

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
   - https://woodfordcountyelections.com
   - Save to election night monitoring list

4. **Have scraper ready:**
   - Know where script is located
   - Have terminal/command prompt ready
   - Know output destination

### Election Night - Timeline

**7:00 PM** - Polls close

**7:30-9:00 PM** - First results typically posted
- Small counties like Woodford usually post within 2 hours
- Check website periodically
- Look for "Unofficial Results" link

**Throughout evening** - Results updated
- Woodford may update same page with new totals
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
# 1. Refresh woodfordcountyelections.com
# 2. Check for new results link
# 3. Copy URL when available
# 4. Run scraper:

python woodford_county_scraper.py --url "RESULTS_URL"

# Save each version if tracking updates:
python woodford_county_scraper.py --url "URL" --output results_8pm.json
python woodford_county_scraper.py --url "URL" --output results_9pm.json
```

### Best Practices

- Start monitoring around 7:30 PM
- Be patient - small county may take time to upload
- Save URL when you find it for repeated scraping
- Don't overload their server - 15-minute intervals minimum
- Keep previous versions if tracking changes

## Format Comparison

### Woodford vs Other Custom Counties

| County | Format | Complexity | Known Features |
|--------|--------|------------|----------------|
| **Woodford** | **Custom (TBD)** | **⭐⭐ Medium** | **Flexible scraper** |
| Kane | Custom HTML | ⭐ Easy | Table-based |
| Fulton | Cumulative PDF | ⭐⭐ Medium | Vote method detail |
| La Salle | Summary PDF | ⭐⭐ Medium | Clean sections |
| Rock Island | GEMS PDF | ⭐ Easy | Cleanest format |
| McLean | Text docs | ⭐⭐ Medium | Manual URLs |
| Champaign | Excel | ⭐⭐ Medium | Single file |
| Peoria | ElectionStats | ⭐⭐⭐ High | Database access |

**Woodford advantage:** Flexible scraper handles multiple formats!

### Why Format is Unknown

Unlike larger counties with established platforms:
- Small counties often change systems
- May use different formats for different elections
- Platform may be simple CMS (WordPress, etc.)
- Results format determined by clerk's preference

The flexible scraper handles this uncertainty!

## Possible Format Scenarios

Based on patterns from similar Illinois counties:

### Scenario A: PDF Document (Most Likely)

Similar to Fulton, La Salle, Rock Island:
- Clean structured PDF
- Contests with candidates and votes
- Summary statistics in header
- **Scraper ready:** Full PDF parsing included

### Scenario B: HTML Table (Likely)

Similar to Kane County:
- Results page with HTML tables
- One table per contest
- Candidate names and vote totals in rows
- **Scraper ready:** Table parsing included

### Scenario C: Excel Spreadsheet (Possible)

Similar to Champaign County:
- Downloadable .xlsx file
- Multiple sheets by party
- Structured columns
- **Adaptation needed:** Can extend scraper for Excel

### Scenario D: Text Report (Possible)

Similar to McLean County:
- Plain text or PDF with text structure
- Contests separated by headers
- Candidate lines with votes
- **Scraper ready:** Text parsing included

## Advanced: Format Adaptation

If the format doesn't match expectations, here's how to adapt:

### For Excel Files

Add openpyxl dependency:
```bash
pip install openpyxl
```

Modify scraper to handle .xlsx:
```python
if url.endswith('.xlsx'):
    return self._scrape_excel()
```

### For JavaScript-Rendered Pages

If data loads via JavaScript:
```bash
pip install selenium
```

Use browser automation to capture rendered content.

### For API-Based Results

If site uses JSON API:
```python
response = requests.get(api_url)
data = response.json()
# Parse JSON structure
```

The scraper framework makes these adaptations straightforward!

## County-Specific Notes

### Geographic Context

Woodford County location matters:
- **East of Peoria County** - metropolitan influence
- **Peoria MSA** - part of larger economic area
- **Interstate 74 corridor** - transportation hub
- **Mix of suburban and rural** - diverse electorate

### Major Population Centers

**Eureka** (county seat, ~5,500 residents):
- Home to Eureka College
- Historic downtown
- Largest town in county

**El Paso** (~2,800 residents):
- Agricultural center
- Interstate 39 access

**Metamora** (~3,900 residents):
- Growing suburban community
- Bedroom community for Peoria workers

**Roanoke** (~2,000 residents):
- Small town character
- Agricultural economy

### Electoral Patterns

- **Turnout:** Typically 20-30% for primaries, 50-65% for generals
- **Party lean:** Solidly Republican in recent elections
- **Key issues:** Agriculture, education, local taxes
- **Bellwether status:** Mirrors central Illinois rural trends

### Precinct Structure

Approximately 18-20 precincts:
- Mix of city precincts (Eureka, El Paso, Metamora, Roanoke)
- Township precincts (rural areas)
- Smaller townships may combine precincts

Full precinct list available on county website.

## Why This County Matters

Despite being mid-sized (~25K voters), Woodford matters because:
1. **Peoria metro** - Part of significant central IL metro area
2. **Growth pattern** - Represents suburban expansion trends
3. **Geographic coverage** - Completes Peoria area coverage
4. **Historical significance** - Reagan's Eureka College connection
5. **Comprehensive project** - One of final 5 counties

In combination with neighboring Peoria County (already complete), provides full coverage of Peoria metropolitan area.

## Historical Context

Woodford County election administration:
- County Clerk is sole election authority
- No separate city election boards
- Website appears to be relatively recent
- Format has likely been consistent for recent elections
- Small office may use simple solutions

Testing with 2024 or 2022 data shows historical format!

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

Woodford integrates with your 38-county project:
- Standard JSON output format
- Consistent party detection
- Compatible with aggregation system
- Ready for statewide rollup

### Adjacent Counties

Woodford completes regional coverage:
- **Peoria County** (west) - ✅ Complete (ElectionStats scraper)
- **McLean County** (east) - ✅ Complete (dual authority scraper)
- **Tazewell County** (south) - ✅ Complete (pollresults.net scraper)

With Woodford complete, entire Peoria metro area has coverage!

## Summary - Quick Reference

**✅ To scrape Woodford County:**

1. Visit: https://woodfordcountyelections.com
2. Find: "2026 Primary Election Results" link
3. Copy results URL (HTML page or PDF link)
4. Run: `python woodford_county_scraper.py --url [URL]`
5. Get: Clean JSON with all contests, candidates, votes

**📊 What you get:**
- All contests with candidates, votes, percentages
- Party detection from contest names
- Summary statistics (turnout, precincts, registered voters)
- Flexible format support (PDF, HTML, tables)
- Metadata extraction

**💡 Why it's good:**
- Flexible scraper handles multiple formats
- No guesswork - just provide URL on election day
- Clear instructions for finding results
- Easy testing with historical data
- Robust error handling

**📍 County importance:**
- ~25K voters in central Illinois
- Part of Peoria metropolitan area
- Mix of suburban and rural
- Completes Peoria area coverage
- One of final 5 counties in project!

**🎯 Election day strategy:**
- Start monitoring at 7:30 PM
- Check website every 15-30 minutes
- Copy URL when results appear
- Run scraper with URL
- Repeat periodically for updates

Woodford County's flexible scraper is ready for whatever format they use!
