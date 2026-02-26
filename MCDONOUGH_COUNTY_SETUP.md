# McDonough County Scraper Setup - Logonix Platform

This guide covers scraping election results for **McDonough County** using their custom Logonix Corporation web platform.

## County Overview

**McDonough County Statistics:**
- Population: ~30,000 residents
- Voters: ~20,000 registered voters
- County seat: Macomb
- Major institution: Western Illinois University (~8,000 students)
- Location: West-central Illinois

**Electoral Significance:** College town with unique demographics. Western Illinois University brings student population that influences voting patterns. Mix of academic community and rural agricultural areas. Typically competitive due to diverse voter base. One of few Illinois counties with major university presence.

## Platform Overview

**System:** Custom web-based system (Logonix Corporation)  
**Website:** mcdonoughelections.com  
**Output Format:** Unknown until election day (likely HTML, possibly PDF)  
**Technology:** Logonix custom platform  
**Complexity:** ⭐⭐ Medium (vendor platform, format unknown)  
**Coverage:** All of McDonough County

### About Logonix Corporation

Logonix Corporation provides election management software and websites for small jurisdictions. Their systems typically feature:
- Web-based results display
- HTML pages with tabular data
- Sometimes PDF exports
- Clean, structured output

Similar vendor platforms (Clarity, pollresults.net) have been straightforward to scrape.

## Installation

### Dependencies

```bash
pip install requests beautifulsoup4 pdfplumber
```

## Usage

### Finding the Results URL

**CRITICAL:** You must provide the direct URL to results on election day.

#### Step-by-Step

1. **Visit:** https://www.mcdonoughelections.com
2. **Look for:** "Election Results", "View Results", "2026 Primary Results"
3. **Copy URL:** Right-click link → "Copy link address"
4. **Run:** `python mcdonough_county_scraper.py --url "YOUR_URL"`

Possible URL formats:
```
https://www.mcdonoughelections.com/results/2026-primary.html
https://www.mcdonoughelections.com/results.php?election=2026-primary
https://www.mcdonoughelections.com/files/2026-primary.pdf
```

### Examples

```bash
# With HTML results page
python mcdonough_county_scraper.py --url "https://www.mcdonoughelections.com/results/2026-primary.html"

# With PDF document
python mcdonough_county_scraper.py --url "https://www.mcdonoughelections.com/files/2026-primary.pdf"

# Test with 2024 data
python mcdonough_county_scraper.py --url "2024_URL" --date 2024-03-19

# Without URL (shows instructions)
python mcdonough_county_scraper.py
```

## Testing with Historical Data

**Strongly recommended** before election day:

1. Visit mcdonoughelections.com
2. Find 2024 Primary or 2022 General results
3. Copy URL
4. Run: `python mcdonough_county_scraper.py --url "URL" --date 2024-03-19`
5. Verify output in `mcdonough_results.json`

This validates the scraper works with McDonough's actual format!

## Output Format

```json
{
  "county": "McDonough",
  "election_date": "2026-03-17",
  "source": "McDonough County Elections Website",
  "url": "https://www.mcdonoughelections.com/...",
  "scraped_at": "2026-03-17T20:30:00",
  "metadata": {
    "registered_voters": 20000,
    "ballots_cast": 5200,
    "precincts_reporting": 28,
    "total_precincts": 28,
    "turnout_percent": 26.0
  },
  "contests": [
    {
      "name": "PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY",
      "party": "Republican",
      "candidates": [
        {"name": "DONALD J. TRUMP", "votes": 2245, "percent": 82.1},
        {"name": "NIKKI HALEY", "votes": 489, "percent": 17.9}
      ]
    }
  ]
}
```

## Format Detection

The scraper automatically handles:
- **HTML pages:** Parses tables, divs, structured content
- **PDF documents:** Extracts text and parses contests
- **Text reports:** Handles plain text formats

## College Town Considerations

### Student Precincts

Western Illinois University has dedicated precincts:
- Campus precincts typically numbered separately
- May show as "WIU Precinct" or similar
- Student turnout varies greatly by election type
- Presidential primaries see higher student participation

### Macomb City vs Rural

- **Macomb city:** ~15,000 residents, includes WIU
- **Rural townships:** Agricultural communities
- Results may show distinct voting patterns
- Scraper captures all precincts

## Election Day Workflow

### Timeline

**7:00 PM** - Polls close

**7:30-9:00 PM** - First results posted
- Logonix platforms typically post quickly
- Check website starting 7:30 PM
- Look for "Unofficial Results"

**Throughout evening** - Updates posted
- Results updated as precincts report
- Refresh page or check for new documents

**Next day - 2 weeks** - Official results

### Monitoring Strategy

```bash
# Check website every 15 minutes
# When results appear:
python mcdonough_county_scraper.py --url "RESULTS_URL"

# Save timestamped versions:
python mcdonough_county_scraper.py --url "URL" --output results_8pm.json
python mcdonough_county_scraper.py --url "URL" --output results_9pm.json
```

## Troubleshooting

### Common Issues

**URL Not Found:** Verify URL, check if results posted yet

**Empty Results:** Format may differ from expected, check actual page structure

**PDF Fails:** Ensure pdfplumber installed: `pip install pdfplumber`

**Wrong Totals:** Verify comparing correct columns, check for formatting

**Party Wrong:** Check contest name, may be non-partisan race

## Why This County Matters

Despite being small (~20K voters), McDonough is significant:
1. **College town** - Unique demographic (WIU students)
2. **Competitive races** - Academic/rural mix creates interesting patterns
3. **West-central Illinois** - Represents this region
4. **Largest remaining** - Of the final 3 counties
5. **Student vote** - Demonstrates impact of university populations

## County Context

### Western Illinois University

- Enrollment: ~8,000 students
- Founded: 1899
- Campus in Macomb
- Affects voter registration and turnout
- Student precincts important for complete picture

### Geography

- **Macomb:** County seat, university town
- **Rural townships:** Agricultural areas
- **Location:** West-central Illinois, near Iowa border
- **Economy:** Education, agriculture, services

### Electoral Patterns

- **Primary turnout:** 20-30% typically
- **General turnout:** 55-70%
- **Party lean:** Competitive due to student population
- **Key factors:** Student turnout, rural/urban split

### Precinct Structure

Approximately 28-30 precincts:
- Macomb city precincts (including WIU campus)
- Rural township precincts
- Some townships combine for efficiency

## Integration with Project

### Regional Coverage

McDonough completes west-central Illinois:
- **Fulton County** (west) - ✅ Complete
- **Warren County** (north) - ✅ Complete (GBS platform)
- **Knox County** (north) - ✅ Complete (dual authority)
- **McDonough County** (center) - Custom scraper ← YOU ARE HERE

### Standard Output

- Compatible JSON format
- Consistent party detection
- Ready for multi-county aggregation
- Matches other 34 counties

## Summary - Quick Reference

**✅ To scrape McDonough County:**

1. Visit: www.mcdonoughelections.com
2. Find: 2026 Primary results link
3. Copy URL
4. Run: `python mcdonough_county_scraper.py --url [URL]`
5. Get: Clean JSON output

**📊 Key features:**
- Flexible format support (HTML, PDF, text)
- Multiple parsing strategies for HTML
- Handles Logonix platform variations
- College town precinct support
- Comprehensive error handling

**🎓 College town notes:**
- Watch for WIU/campus precincts
- Student turnout affects totals
- Macomb vs rural patterns
- Presidential primaries see higher student participation

**📍 County importance:**
- ~20K voters in west-central Illinois
- Western Illinois University influence
- Largest of 3 remaining counties
- Completes west-central coverage

**🎯 Election day:**
- Start checking at 7:30 PM
- Logonix platforms usually post quickly
- Look for "Unofficial Results"
- Run scraper when URL available

McDonough County's flexible scraper handles the Logonix platform!
