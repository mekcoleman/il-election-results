# Champaign County Clerk Scraper Setup

This scraper handles election results from the **Champaign County Clerk** via their document download system.

## County Overview

**Champaign County Statistics:**
- Population: ~210,000 residents
- Voters: ~130,000 registered voters
- Location: East-central Illinois (Champaign-Urbana metro)
- Major cities: Champaign, Urbana, Savoy

**Electoral Significance:** Home to University of Illinois. Mix of college-age voters, faculty/staff, and surrounding rural communities. Often considered a bellwether for downstate Illinois. Typically Democratic due to university influence.

## Platform Overview

**System:** Custom web system with document downloads  
**Technology:** Excel/PDF files posted to website  
**Complexity:** ⭐⭐ Medium

Champaign County Clerk posts election results as downloadable documents on their website. Multiple document types available:
- County Summary (Excel) - Recommended for scraping
- Precinct Results (Excel/PDF) - Detailed by precinct
- Canvass Report (PDF) - Official certified results
- Write-in Tally (PDF/Excel) - Write-in vote details

## Installation

### Dependencies

```bash
pip install requests openpyxl
```

**openpyxl** required for Excel file parsing.

## Critical Setup Note

**⚠️ Document URL Required**

Unlike Kane County (predictable URLs) or Clarity (election ID), Champaign posts documents with custom filenames that change per election.

### What You Need

The direct URL to the "County Summary" Excel file for March 17, 2026 Primary.

Example URL format:
```
https://champaigncountyclerk.com/sites/champaigncountyclerk.com/files/documents/2026-03-17-primary-county-summary/county-summary.xlsx
```

The exact path varies by election.

## Finding the Document URL

### Election Day Steps

1. **Visit**: https://champaigncountyclerk.com/elections/i-want-run-office/historical-election-data

2. **Find the election**: Look for "2026-03-17 - General Primary Election"

3. **Locate document links**: Under that date, you'll see:
   - Precinct Results
   - **County Summary** ← Click this one
   - Canvass Report
   - Write In Tally
   - Referenda

4. **Get the URL**: Right-click "County Summary" → Copy link address

5. **Run scraper**:
   ```bash
   python champaign_county_scraper.py --url [PASTE_URL]
   ```

### Pre-Election Testing

Test with 2024 Primary data:

1. Find "2024-03-19 - General Primary Election"
2. Click "County Summary"
3. Use that URL to test scraper
4. Verify output looks correct

## Usage

### With Document URL (Recommended)

```bash
python champaign_county_scraper.py --url "https://champaigncountyclerk.com/sites/.../county-summary.xlsx"
```

### Without URL (Shows Instructions)

```bash
python champaign_county_scraper.py
```

### Custom Output Directory

```bash
python champaign_county_scraper.py --url [URL] --output /path/to/results/
```

## Output Format

```json
{
  "authority": "Champaign County Clerk",
  "jurisdiction": "Champaign",
  "election_date": "2026-03-17",
  "scraped_at": "2026-03-17T20:30:00",
  "source": "County Summary Excel",
  "excel_url": "https://champaigncountyclerk.com/.../county-summary.xlsx",
  "summary": {},
  "contests": [
    {
      "name": "President of the United States",
      "party": "Democratic",
      "candidates": [
        {
          "name": "Candidate A",
          "votes": 15420,
          "percent": 58.3
        },
        {
          "name": "Candidate B",
          "votes": 11028,
          "percent": 41.7
        }
      ]
    }
  ]
}
```

## Excel File Structure

Champaign's County Summary Excel files typically have:

### Sheet Structure

Multiple sheets, usually one per ballot type:
- "DEM" or "Democratic Primary" sheet
- "REP" or "Republican Primary" sheet
- "NON" or "Non-Partisan" sheet (if applicable)

### Contest Format

Each sheet contains contests in a table format:

```
Contest Name
Candidate Name    Votes    Percent
Candidate Name    Votes    Percent
Total            Total     100%

Next Contest Name
...
```

The scraper parses this structure to extract:
- Contest names
- Candidate names
- Vote totals
- Party affiliation (from sheet name or contest name)

## Party Detection

Party determined by:

1. **Sheet name**: "DEM" → Democratic, "REP" → Republican
2. **Contest name**: "(DEM)" or "(REP)" suffixes
3. **Default**: Non-Partisan for local races

Very reliable since Champaign separates by ballot type.

## Troubleshooting

### "openpyxl not installed" Error

**Problem:** Excel parsing library missing

**Solution:**
```bash
pip install openpyxl
```

### Document URL 404 Error

**Problem:** URL doesn't exist or is incorrect

**Solutions:**
- Verify URL by visiting in browser
- Results may not be posted yet (too early on election night)
- URL path may have changed - check website manually
- Make sure you copied the entire URL

### Empty Contests Array

**Problem:** Excel file loaded but no contests parsed

**Solutions:**
- Excel format may differ from expected structure
- Check file manually in Excel to see format
- May need to adjust parsing logic in `_parse_sheet_contests()`
- Try with 2024 data first to verify parser works

### Wrong Party Assignments

**Problem:** Contests have incorrect party

**Solutions:**
- Check sheet names in Excel file
- Party detection relies on sheet names like "DEM" or "REP"
- If Champaign changed naming, update `_detect_party_from_sheet()`

### Site Blocking (403 Error)

**Problem:** Website blocks automated access

**Solutions:**
- This typically only affects the main website, not direct file downloads
- Always use the direct file URL, not the page URL
- If direct download is blocked, download manually and point scraper to local file

## Performance

- **Download speed**: 2-5 seconds (Excel files are ~100KB-1MB)
- **Parse speed**: 1-2 seconds
- **Total time**: ~5-10 seconds
- **Rate limits**: No known limits

Very fast since it's just one file download!

## Comparison to Other Counties

| County | Platform | ID/URL Method | Complexity | Prep Work |
|--------|----------|---------------|------------|-----------|
| **Champaign** | Excel docs | Document URL | ⭐⭐ | Find URL |
| Peoria | ElectionStats | Contest IDs | ⭐⭐⭐ | Collect IDs |
| Kane | Custom HTML | Date-based | ⭐ Easy | None |
| Chicago Board | PDF | PDF URL | ⭐⭐⭐ | Find URL |

**Champaign's sweet spot:**
- ✅ Just need one URL (easier than Peoria's many IDs)
- ✅ Excel files are structured and reliable
- ✅ Fast to download and parse
- ⚠️ URL must be found manually (not automated)

## Election Day Workflow

### Day Before Election

Optional - test with historical data to confirm scraper works:

```bash
# Find 2024 Primary County Summary URL
python champaign_county_scraper.py --url "https://champaigncountyclerk.com/sites/.../2024-county-summary.xlsx"
```

### Election Night

**Timeline:**
- 7:00 PM - Polls close
- 8:00-9:00 PM - First results typically posted
- Throughout night - Documents updated
- Final - Usually by midnight

**Monitoring Strategy:**

1. Find the County Summary URL (once results are posted)
2. Run scraper every 15-30 minutes
3. Champaign updates the same file with new data

```bash
# Save URL to variable
URL="https://champaigncountyclerk.com/sites/.../county-summary.xlsx"

# Monitor loop
while true; do
  python champaign_county_scraper.py --url "$URL"
  echo "Updated at $(date)"
  sleep 900  # 15 minutes
done
```

### What to Watch

- Vote totals increasing
- New contests appearing
- Precinct reporting percentages (if available)

## Document Types Explained

Champaign provides multiple document types. Here's what each contains:

### County Summary (Recommended)

**What it is:** County-wide vote totals for all contests  
**Format:** Excel (.xlsx)  
**Best for:** Quick scraping of overall results  
**Use when:** You need countywide totals fast

### Precinct Results

**What it is:** Detailed results broken down by precinct  
**Format:** Excel or PDF  
**Best for:** Detailed analysis, maps, targeting  
**Use when:** You need geographic breakdown

### Canvass Report

**What it is:** Official certified results  
**Format:** PDF  
**Best for:** Official final numbers  
**Use when:** Election is certified (weeks after election day)

### Write-in Tally

**What it is:** Detailed write-in vote counts  
**Format:** PDF or Excel  
**Best for:** Write-in candidate analysis  
**Use when:** Write-ins are significant

**For election night scraping, use County Summary!**

## Advanced: Alternative Approaches

### Option 1: Manual Download + Local Parse

If the website is slow or blocking:

1. Manually download County Summary Excel file
2. Save as `county-summary.xlsx` locally
3. Modify scraper to read local file instead of URL

### Option 2: Monitor Document Center

Champaign may post to a document center:
- Check /sites/champaigncountyclerk.com/files/documents/
- Look for recent uploads
- May find file before it's linked from main page

### Option 3: Use Precinct Results

If County Summary isn't available:
- Download Precinct Results Excel
- Modify scraper to parse precinct-level data
- Sum across all precincts for county totals

## Support Contacts

**Champaign County Clerk**
- Website: champaigncountyclerk.com
- Email: elections@champaigncountyclerkil.gov
- Phone: Check website for current number
- Office: Brookens Administrative Center, Urbana, IL

**For technical issues:**
- Documents are usually very reliable
- If URL doesn't work, try visiting page in browser
- Contact county clerk if documents aren't posted on time
- Excel format has been consistent for years

## Why This Approach Works

Despite needing to find the document URL manually, Champaign's system is actually quite good:

✅ **One file, all results** - County Summary has everything  
✅ **Structured data** - Excel format is reliable  
✅ **Fast downloads** - Small files load quickly  
✅ **Consistent format** - Structure hasn't changed in years  
✅ **Multiple formats** - Excel AND PDF available  

Main limitation is just finding the URL, which takes ~30 seconds on election night.

## Testing Checklist

Before election day:

- [ ] openpyxl installed
- [ ] Scraper runs without errors
- [ ] Tested with 2024 Primary County Summary
- [ ] Output JSON looks correct
- [ ] Know where to find document links on election night

Day of election:

- [ ] Historical data page URL bookmarked
- [ ] Ready to find County Summary link
- [ ] Monitoring script prepared
- [ ] Output directory set up

## Next Steps

1. **Install openpyxl** - `pip install openpyxl`
2. **Test with 2024 data** - Find 2024 Primary County Summary and test parse
3. **Bookmark the page** - Save historical data page for quick access
4. **Election night** - Find County Summary URL and run scraper
5. **Monitor** - Re-run every 15-30 minutes as results update

## Summary

**Champaign County scraper is simple and effective:**

- ✅ Pro: Single file download = all results
- ✅ Pro: Excel format is structured and reliable
- ✅ Pro: Fast and efficient
- ⚠️ Con: Document URL must be found manually
- ⚠️ Con: Not fully automated like some counties

**Recommended approach:** Spend 30 seconds on election night finding the County Summary URL, then scraping is automatic and fast.

Champaign strikes a good balance between ease of use and data quality!
