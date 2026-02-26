# Integra Election Reporting Console Scraper Setup

This scraper handles **3 Illinois counties** that use the Integra Election Reporting Console platform.

## Covered Counties

1. **DeKalb County** - http://dekalb.il.electionconsole.com
2. **Kendall County** - http://kendall.il.electionconsole.com  
3. **Henry County** - http://henry.il.electionconsole.com

## Platform Overview

**Vendor:** Integra Business Services  
**Technology:** Plain text results format  
**Complexity:** ⭐ Low (simplest scraper)

The Integra platform provides election results in a plain text format at `/electiontext.php`, which makes it very straightforward to scrape - no JavaScript rendering or complex APIs needed.

## Installation

### Dependencies

The Integra scraper only requires standard Python libraries:
- `requests` - for HTTP requests
- `json`, `re`, `sys`, `datetime` - all part of Python standard library

Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

### Scrape All Integra Counties

Run without arguments to scrape all 3 counties:

```bash
python integra_scraper.py
```

This will create:
- `dekalb_results.json`
- `kendall_results.json`
- `henry_results.json`

### Scrape Single County

Pass county name as argument (case-insensitive):

```bash
python integra_scraper.py DeKalb
python integra_scraper.py kendall
python integra_scraper.py HENRY
```

## Output Format

Each JSON file contains:

```json
{
  "county": "DeKalb County",
  "scraped_at": "2026-03-17T20:15:00",
  "summary": {
    "precincts_counted": 65,
    "registered_voters": 63988,
    "ballots_cast": 9390,
    "turnout_percent": 15
  },
  "contests": [
    {
      "name": "MAYOR CITY OF DEKALB",
      "party": "Non-Partisan",
      "seats": 1,
      "candidates": [
        {
          "name": "Cohen Barnes",
          "party": "NON",
          "votes": 2410,
          "percent": 62.18
        },
        {
          "name": "Carolyn Morris",
          "party": "NON",
          "votes": 1466,
          "percent": 37.82
        }
      ]
    }
  ]
}
```

## Text Format Parsing

The scraper parses the plain text format which looks like:

```
SUMMARY REPORT		DEKALB COUNTY
RUN DATE: 02/10/26	2021 CONSOLIDATED
RUN TIME: 15:17		APRIL 6, 2021

PRECINCTS COUNTED (OF 65) . . . . . . . . . . . . 65  	100
REGISTERED VOTERS - TOTAL . . . . . . . . . . . . 63988
BALLOTS CAST - TOTAL. . . . . . . . . . . . . . . 9390

MAYOR CITY OF DEKALB
VOTE FOR NO MORE THAN 1
Cohen Barnes (NON). . . . . . . . . . . . . . . . 2410	62.18
Carolyn Morris (NON). . . . . . . . . . . . . . . 1466	37.82
```

The parser:
1. Extracts summary statistics from header
2. Identifies contests (all-caps lines)
3. Captures "VOTE FOR NO MORE THAN X" for seats
4. Parses candidate lines with dots separator
5. Detects party from contest name for primary categorization

## Party Detection

The scraper detects primary party affiliation from contest names:

- **Democratic**: Contains "DEMOCRATIC" or "DEM "
- **Republican**: Contains "REPUBLICAN" or "REP "  
- **Non-Partisan**: All other contests

Each candidate also has their own party affiliation (shown in parentheses).

## Advantages of Integra Platform

1. **Simplest format** - Plain text, no JavaScript
2. **Fast scraping** - ~1-2 seconds per county
3. **Reliable** - No dynamic loading or timeouts
4. **Complete data** - All contests in single page
5. **No special tools** - Just HTTP requests

## Election Day Workflow

### Pre-Election Setup
1. Verify all 3 county URLs are accessible
2. Test scraper with each county
3. Confirm output format matches expectations

### Election Night (March 17, 2026)

Monitor results starting around **7:30 PM CST** (polls close at 7:00 PM):

```bash
# Run every 5-10 minutes
while true; do
  python integra_scraper.py
  sleep 300  # 5 minutes
done
```

Or scrape specific county more frequently:
```bash
# Every 2 minutes for DeKalb
while true; do
  python integra_scraper.py DeKalb
  sleep 120
done
```

### Monitoring
- Check `*_results.json` files for updates
- Compare `scraped_at` timestamps
- Monitor `ballots_cast` and `precincts_counted`

## Troubleshooting

### Connection Errors

**Problem:** `Failed to resolve` or `Connection refused`

**Solutions:**
- Check internet connection
- Verify county URL is correct
- Confirm website is accessible in browser
- Results may not be available yet (check county clerk site)

### Empty Results

**Problem:** File created but no contests

**Solutions:**
- Election results may not be posted yet
- Check `summary` section for data
- Visit county URL in browser to verify
- Some elections may have no data for certain counties

### Parse Errors

**Problem:** Incorrect data or missing contests

**Solutions:**
- Check if text format changed
- Review raw text at `/electiontext.php`
- Contest names may vary by election
- Contact county clerk for format questions

## Performance

- **Scraping speed**: ~2 seconds per county
- **All 3 counties**: ~6 seconds total
- **Network**: Minimal bandwidth (text only)
- **Resources**: Very lightweight

## Comparison to Other Platforms

| Platform | Counties | Complexity | Speed | Reliability |
|----------|----------|------------|-------|-------------|
| **Integra** | 3 | ⭐ Low | 2s | ⭐⭐⭐⭐⭐ |
| pollresults.net | 12 | ⭐⭐⭐ High | 5-10s | ⭐⭐⭐⭐ |
| Clarity | 5 | ⭐⭐ Medium | 2-3s | ⭐⭐⭐⭐⭐ |

**Winner:** Integra is the easiest platform to work with!

## Notes

- Integra is used by smaller to medium counties
- Same company provides multiple election software products
- Platform has been stable for many years
- Text format has remained consistent across elections
- Other Illinois counties may also use this platform

## Support

If you encounter issues:

1. Check county clerk websites for alternative results pages
2. Verify election date and time (results may not be available)
3. Test URLs manually in browser
4. Review error messages for specific issues

County Contacts:
- **DeKalb County Clerk**: (815) 895-7147
- **Kendall County Clerk**: (630) 553-4104
- **Henry County Clerk**: (309) 937-3575
