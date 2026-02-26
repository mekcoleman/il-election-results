# Cook County Clerk Election Results Scraper Setup

This scraper handles election results from the **Cook County Clerk** for **Suburban Cook County**.

## ⚠️ CRITICAL: Dual Authority Jurisdiction

**Cook County has TWO separate election authorities:**

1. **Cook County Clerk** (this scraper)
   - Coverage: ALL of Cook County EXCEPT Chicago
   - Includes: All suburban Cook County municipalities and townships
   - Website: cookcountyclerkil.gov
   - ~2.4 million voters

2. **Chicago Board of Election Commissioners** (separate scraper needed)
   - Coverage: ONLY City of Chicago
   - Website: chicagoelections.gov  
   - ~1.5 million voters

**You need BOTH scrapers for complete Cook County results!**

## Coverage

This scraper covers **Suburban Cook County**, which includes all Cook County voters outside Chicago city limits, such as:
- Evanston, Skokie, Oak Park, Cicero, Schaumburg
- Palatine, Arlington Heights, Des Plaines, Orland Park
- Tinley Park, Berwyn, Oak Lawn, Mount Prospect
- And 100+ other suburban municipalities

## Platform Overview

**Vendor:** Custom Cook County system  
**Technology:** Excel/ZIP downloads + Web interface  
**Complexity:** ⭐⭐⭐ High (dual format handling)

Cook County Clerk provides results in two formats:

1. **Excel/ZIP Downloads** (Recommended) - Most reliable
   - Precinct-level canvasses as Excel spreadsheets
   - Available at: `/elections/results-and-election-data/election-data/precinct-canvasses`
   - Posted within hours of polls closing

2. **Web Interface** (Fallback) - May have access restrictions
   - Interactive results site: `resultsMMYY.cookcountyclerkil.gov`
   - May block automated scraping
   - Good for manual checking

## Installation

### Dependencies

```bash
pip install -r requirements.txt
```

Additional required package for Excel parsing:

```bash
pip install openpyxl
```

Updated `requirements.txt` should include:
```
requests>=2.31.0
beautifulsoup4>=4.12.0
openpyxl>=3.1.0
```

## Recommended Approach: Excel/ZIP Download

This is the **most reliable method** for election night.

### Step-by-Step Process

#### 1. On Election Night (March 17, 2026)

After polls close (~7:00 PM CST), results are typically posted within 1-2 hours.

#### 2. Download the ZIP File

Visit: https://www.cookcountyclerkil.gov/elections/results-and-election-data/election-data/precinct-canvasses

Look for: **"March 17, 2026 Primary Election"** or similar

Click to download the ZIP file (will be named something like `2026_Primary_Results.zip`)

#### 3. Run the Scraper

```bash
python cook_county_scraper.py --zip /path/to/2026_Primary_Results.zip
```

For example:
```bash
python cook_county_scraper.py --zip ~/Downloads/2026_Primary_Results.zip
```

#### 4. Results Saved

Output will be saved to `cook_clerk_results.json`

### What Gets Extracted

From the Excel spreadsheets, the scraper extracts:

- Contest names (with party detection)
- Candidate names
- Vote counts by candidate
- Percentages
- Sheet organization (by contest category)

## Alternative Approach: Web Interface

Use this if Excel files aren't yet available, but be prepared for access issues.

### Finding the Results URL

On election day, the results will be at a URL like:

```
results[MMYY].cookcountyclerkil.gov
```

For March 2026, this would be:
```
results0326.cookcountyclerkil.gov
```

### Running the Web Scraper

```bash
python cook_county_scraper.py --code 0326
```

**Note:** The web interface may:
- Block automated requests (403 errors)
- Require CAPTCHA verification
- Have rate limiting
- Change format between elections

**Excel download is strongly recommended!**

## Output Format

```json
{
  "authority": "Cook County Clerk",
  "coverage": "Suburban Cook County (excluding Chicago)",
  "source": "Excel ZIP download",
  "scraped_at": "2026-03-17T21:30:00",
  "contests": [
    {
      "name": "DEM PRESIDENT OF THE UNITED STATES",
      "party": "Democratic",
      "sheet": "Presidential",
      "candidates": [
        {
          "name": "JOSEPH R. BIDEN",
          "votes": 234567,
          "percent": 65.4
        },
        {
          "name": "UNCOMMITTED",
          "votes": 124123,
          "percent": 34.6
        }
      ]
    },
    {
      "name": "REP PRESIDENT OF THE UNITED STATES",
      "party": "Republican",
      "sheet": "Presidential",
      "candidates": [
        {
          "name": "DONALD J. TRUMP",
          "votes": 198765,
          "percent": 72.3
        }
      ]
    }
  ]
}
```

## Excel File Structure

Cook County's Excel files typically contain:

### Sheet Organization
- One sheet per contest category (Presidential, Congressional, etc.)
- Or one sheet per type (Federal, State, County, Local)

### Row Format
```
Contest Name (header row)
Candidate 1    12,345    45.2%
Candidate 2    15,678    54.8%
TOTAL          28,023    100.0%
```

### Variations
- Some elections have multiple tables per sheet
- Headers may be in different rows
- Vote totals may be split by township/precinct

The scraper handles common variations but may need adjustment for specific elections.

## Election Day Workflow

### Pre-Election Setup

1. **Test with historical data**
   ```bash
   # Download a past election ZIP from precinct-canvasses page
   python cook_county_scraper.py --zip historical_election.zip
   ```

2. **Verify Excel parsing works** - Check output JSON structure

3. **Update requirements**
   ```bash
   pip install openpyxl
   ```

### Election Night (March 17, 2026)

**Timeline:**
- 7:00 PM - Polls close
- 8:00-9:00 PM - First results typically posted
- Throughout night - Results updated as precincts report

**Monitoring Strategy:**

```bash
# Check for new ZIP files every 15-30 minutes
# Manual process:
# 1. Visit precinct-canvasses page
# 2. Check for "March 17, 2026" ZIP file
# 3. Download when available
# 4. Run scraper
# 5. Check for updated versions later in evening
```

**Automated checking (advanced):**

```bash
#!/bin/bash
while true; do
  echo "Checking for results updates..."
  # You would manually check and download
  # Then run:
  # python cook_county_scraper.py --zip latest.zip
  sleep 1800  # 30 minutes
done
```

### Post-Election

Official results are canvassed and certified approximately 2-3 weeks after the election.

## Troubleshooting

### Excel Parsing Errors

**Problem:** `Error parsing ZIP file` or `No Excel files found`

**Solutions:**
- Verify ZIP file downloaded completely
- Check file isn't corrupted (try opening in Excel manually)
- Make sure openpyxl is installed: `pip install openpyxl`
- ZIP may contain PDFs instead of Excel - check contents

### Missing Contests

**Problem:** Some contests not appearing in output

**Solutions:**
- Excel format may vary - check actual spreadsheet structure
- Contest headers might not be detected - adjust `_is_contest_header()` logic
- Some contests may be in separate files in the ZIP
- Process all Excel files in ZIP manually if needed

### Web Interface Blocked

**Problem:** 403 Forbidden or CAPTCHA when trying web scraping

**Solutions:**
- **Use Excel download instead** (recommended)
- Wait and try again later (rate limiting may reset)
- Access from different IP address
- Check manually in browser - results may not be posted yet

### Duplicate Data Issues

**Problem:** Getting data from both Cook Clerk and Chicago - which is correct?

**Reminder:**
- Cook County Clerk = Suburban Cook ONLY
- Chicago Board = Chicago city ONLY  
- These should NEVER overlap
- If you need all of Cook County, combine both scrapers

## Performance

- **Excel parsing**: ~10-30 seconds (depending on file size)
- **Web scraping**: ~5-10 seconds (if not blocked)
- **File size**: Excel ZIPs typically 5-20 MB
- **Memory**: Moderate (loading Excel into memory)

## Comparison to Other Counties

| County | Platform | Complexity | Reliability | Speed |
|--------|----------|------------|-------------|-------|
| **Cook** | Custom Excel | ⭐⭐⭐ High | ⭐⭐⭐⭐⭐ | 10-30s |
| Will | Clarity API | ⭐⭐ Medium | ⭐⭐⭐⭐⭐ | 2-3s |
| DuPage | Scytl | ⭐⭐⭐ High | ⭐⭐⭐⭐ | Variable |

Cook County's Excel approach is actually **more reliable** than many web-based systems because:
- Files don't change format mid-election
- No JavaScript rendering needed
- No rate limiting on downloads
- Data is complete and official

## Important Notes

### Dual Authority Reminder

To get **complete Cook County results**, you must:

1. Run this scraper (Cook County Clerk - Suburban)
2. Run Chicago scraper (Chicago Board - City only)
3. Combine results appropriately

**Do NOT assume Cook County Clerk = All of Cook County!**

### Data Timing

- **Unofficial results**: Posted election night (what this scraper gets)
- **Official results**: Certified 2-3 weeks later
- Results may be updated multiple times election night as precincts report

### Precinct-Level Data

The Excel files contain precinct-level detail. This scraper aggregates to contest totals, but you could modify it to preserve precinct breakdowns if needed.

### Historical Data

The precinct-canvasses page has ZIP files going back many years. Great for:
- Testing the scraper
- Understanding Excel format variations
- Historical analysis

## Support Contacts

**Cook County Clerk's Office**
- Website: cookcountyclerkil.gov
- Phone: (312) 603-0906
- Email: See website for department contacts

**Technical Questions**
- For election results questions: Contact Clerk's office
- For data format questions: Check post-election reports on website

## Next Steps

1. Install openpyxl: `pip install openpyxl`
2. Test with historical election ZIP
3. On election day: Download ZIP, run scraper
4. Combine with Chicago results for complete Cook County data

## Chicago Board Scraper

For City of Chicago results, you'll need a separate scraper for:

**Chicago Board of Election Commissioners**
- Website: chicagoelections.gov
- Coverage: City of Chicago only
- Platform: Different custom system
- Separate scraper needed (not included here)
