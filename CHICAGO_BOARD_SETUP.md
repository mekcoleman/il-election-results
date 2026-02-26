# Chicago Board of Election Commissioners Scraper Setup

This scraper handles election results from the **Chicago Board of Election Commissioners** - the authority for **City of Chicago elections only**.

## 🚨 CRITICAL JURISDICTION NOTE

**Chicago Board handles ONLY the City of Chicago (Chicago proper).**

**Cook County Clerk handles Suburban Cook County (everywhere else in Cook County).**

These are TWO COMPLETELY SEPARATE election authorities with different systems!

| Authority | Jurisdiction | Voters | Platform |
|-----------|--------------|--------|----------|
| **Chicago Board** | City of Chicago | ~1.5M | PDF (Azure) |
| **Cook County Clerk** | Suburban Cook | ~2.4M | Excel/ZIP |

**For complete Cook County coverage, you need BOTH scrapers!**

## County Overview

**Chicago Board Statistics:**
- Population: City of Chicago (~2.7M residents)
- Voters: ~1.5M registered voters (as of 2024)
- Precincts: ~1,290 precincts
- Ranking: Single largest election authority in Illinois

**Electoral Significance:** Chicago drives Democratic margins in Illinois. Critical for understanding statewide races. Home to major policy referendums and diverse electorate.

## Platform Overview

**Vendor:** Custom Azure-hosted PDF system  
**Technology:** PDF documents with parseable text  
**Complexity:** ⭐⭐⭐ Medium-High

Chicago Board publishes official results as PDF files hosted on Microsoft Azure Government Cloud storage (`cboeresults.blob.core.usgovcloudapi.net`).

## Installation

### Dependencies

```bash
pip install requests pdfplumber
```

**pdfplumber** is required for PDF text extraction.

## Critical Setup Notes

### PDF URLs Change Per Election

Unlike Kane County's predictable date-based URLs, Chicago Board's PDF URLs are **not standardized**. You must find the actual URL for each election.

### Where Results Are Published

1. **Official results page**: https://chicagoelections.gov/elections/results
2. **Azure blob storage**: https://cboeresults.blob.core.usgovcloudapi.net/results/

Results appear as:
- "Summary Report (2 Column).pdf" - Most common format
- "Summary Report.pdf" - Alternative format
- May have different names per election

## Usage

### Method 1: Auto-Find PDF (Tries Common Names)

```bash
python chicago_board_scraper.py
```

This tries common PDF filenames automatically. May or may not work depending on what Chicago Board named the file.

### Method 2: Specific PDF URL (Recommended)

```bash
python chicago_board_scraper.py --url "https://cboeresults.blob.core.usgovcloudapi.net/results/Summary%20Report.pdf"
```

This is more reliable - you provide the exact PDF URL.

### Finding the PDF URL (Election Day)

**Step 1:** Visit https://chicagoelections.gov/elections/results

**Step 2:** Find "March 17, 2026 Primary" in the elections list

**Step 3:** Look for PDF download link (usually labeled "2026 Primary - DEM", "2026 Primary - REP", or "Summary Report")

**Step 4:** Right-click the PDF link → "Copy link address"

**Step 5:** Use that URL:

```bash
python chicago_board_scraper.py --url "[PASTE_URL_HERE]"
```

## Output Format

```json
{
  "authority": "Chicago Board of Election Commissioners",
  "jurisdiction": "Chicago (City)",
  "election_date": "2026-03-17",
  "scraped_at": "2026-03-17T20:30:00",
  "source": "Chicago Board PDF",
  "pdf_url": "https://cboeresults.blob.core.usgovcloudapi.net/results/Summary%20Report.pdf",
  "summary": {
    "registered_voters": 1498873,
    "total_votes_cast": 1018359,
    "precincts_reporting": 1291,
    "total_precincts": 1291
  },
  "contests": [
    {
      "name": "President & Vice President, U.S.",
      "party": "Democratic",
      "precincts_reporting": 1291,
      "total_precincts": 1291,
      "candidates": [
        {
          "name": "Kamala D. Harris & Tim Walz",
          "votes": 775699,
          "percent": 78.25
        },
        {
          "name": "Donald J. Trump & JD Vance",
          "votes": 203817,
          "percent": 20.56
        }
      ]
    }
  ]
}
```

## PDF Structure

Chicago Board PDFs have a consistent, clean text format:

```
CITY OF CHICAGO
November 5, 2024
Summary Report - Unofficial Results

Registered Voters    Turnout
Total Registration and Turnout 1,498,873 1,018,359
( 1291 of 1291 precincts reported )

President & Vice President, U.S.
( 1291 of 1291 precincts reported )
DEM - Kamala D. Harris & Tim Walz 775,699 78.25%
REP - Donald J. Trump & JD Vance 203,817 20.56%
Total 991,292

U.S. Representative, 1st District
( 230 of 230 precincts reported )
DEM - Jonathan L. Jackson 134,776 91.73%
REP - Marcus Lewis 12,158 8.27%
Total 146,934
```

### Format Features

- Contest name on one line
- Precinct reporting in parentheses
- Party prefix: "DEM -", "REP -", "NON -", "LIB -", "GRN -", "IND -"
- Candidate name, votes, percentage on one line
- "Total" line marks end of contest

## Party Detection

Chicago Board uses clear party prefixes:

| Prefix | Party |
|--------|-------|
| `DEM -` | Democratic |
| `REP -` | Republican |
| `NON -` | Non-Partisan |
| `LIB -` | Libertarian |
| `GRN -` | Green |
| `IND -` | Independent |

Very reliable - easier than most platforms!

## Election Day Workflow

### Pre-Election Testing

Test with historical data:

1. Visit https://chicagoelections.gov/elections/results
2. Find "2024 General Election" or "2024 Primary"
3. Download the PDF
4. Test the scraper:

```bash
python chicago_board_scraper.py --url "https://cboeresults.blob.core.usgovcloudapi.net/results/Summary%20Report%20(2%20Column).pdf"
```

This confirms the PDF parser works correctly.

### Election Night (March 17, 2026)

**Timeline:**
- 7:00 PM - Polls close
- 7:30-8:00 PM - First results typically posted
- Throughout night - Results updated
- Final unofficial - Usually complete by 11 PM-midnight

**Monitoring Strategy:**

```bash
# Once you have the PDF URL, run every 15 minutes
URL="https://cboeresults.blob.core.usgovcloudapi.net/results/Summary%20Report.pdf"

while true; do
  python chicago_board_scraper.py --url "$URL"
  echo "Updated at $(date)"
  sleep 900  # 15 minutes
done
```

**What to Watch:**
- `precincts_reporting` vs `total_precincts`
- `total_votes_cast` should increase
- New contests may appear as they're reported

### Real-Time Updates

Chicago Board typically updates the PDF every 15-30 minutes on election night. The PDF is regenerated with updated numbers.

## Troubleshooting

### "pdfplumber not installed" Error

**Problem:** PDF parsing library missing

**Solution:**
```bash
pip install pdfplumber
```

### "PDF not found" Error

**Problem:** Auto-find couldn't locate PDF

**Solutions:**
- Use `--url` parameter with exact PDF URL
- Visit chicagoelections.gov/elections/results manually
- Check that results have been posted (may be too early)
- PDF filename may be different than expected

### Empty Contests Array

**Problem:** PDF loads but no contests parsed

**Solutions:**
- PDF format may have changed slightly
- Check if PDF is actually the summary report (not proclamation)
- Try viewing PDF manually to see structure
- May need to adjust parsing logic for new format

### 404 Error on PDF URL

**Problem:** URL returns 404

**Solutions:**
- Election ID or filename is wrong
- Results not yet posted
- URL structure may have changed
- Check chicagoelections.gov for correct link

### Party Detection Issues

**Problem:** All contests show "Unknown" party

**Solution:**
- Check if Chicago Board changed their prefix format
- PDF may be missing party prefixes (rare)
- May need to update `detect_party()` logic

## Performance

- **Scraping speed**: ~5-10 seconds (includes PDF download)
- **Network**: PDF files are ~200KB-1MB
- **Resources**: Moderate (PDF parsing uses some memory)
- **Rate limits**: No known limits, but respectful 15-minute intervals recommended

## Comparison to Other Authorities

| Authority | Platform | Complexity | Reliability | Speed |
|-----------|----------|------------|-------------|-------|
| **Chicago Board** | PDF/Azure | ⭐⭐⭐ Med-High | ⭐⭐⭐⭐ | 5-10s |
| Cook County Clerk | Excel/ZIP | ⭐⭐⭐ High | ⭐⭐⭐⭐⭐ | 10-30s |
| Kane | HTML Tables | ⭐ Easy | ⭐⭐⭐⭐⭐ | 3-5s |
| DuPage | Scytl JSON | ⭐⭐ Medium | ⭐⭐⭐⭐⭐ | 2-3s |

Chicago Board's PDF system is **moderately complex** but **very reliable**:
- Official documents, always published
- Clean, consistent text format
- Azure storage is fast and reliable
- Party prefixes make parsing easier

Main challenge is finding the PDF URL (not automated).

## Important Notes

### Separate from Cook County Clerk

This cannot be emphasized enough: **Chicago Board ≠ Cook County Clerk**

- Chicago Board: City of Chicago only (~1.5M voters)
- Cook County Clerk: All of Cook County EXCEPT Chicago (~2.4M voters)

For complete Cook County coverage, run BOTH scrapers and combine results.

### PDF vs Web Interface

Chicago Board's website (chicagoelections.gov) has a web interface for results, but it:
- May block automated requests (403 errors)
- Format varies by election
- Less reliable for scraping

**PDFs are the recommended approach** - they're official, complete, and consistently formatted.

### Multiple PDFs

Chicago Board may publish separate PDFs for:
- Democratic Primary
- Republican Primary
- Non-Partisan contests
- Summary (all parties combined)

The **Summary Report** is usually what you want - it has everything in one file.

### Unofficial vs Official

Results on election night are **unofficial**. Official results are certified weeks later after all absentee/provisional ballots are processed.

## Advanced Usage

### Scraping Multiple PDFs

If there are separate PDFs for different parties:

```bash
# Democratic Primary
python chicago_board_scraper.py --url "https://...Dem.pdf" --output ./results/dem/

# Republican Primary
python chicago_board_scraper.py --url "https://...Rep.pdf" --output ./results/rep/

# Combine later if needed
```

### Custom PDF Processing

If you need to extract additional data:

```python
from chicago_board_scraper import ChicagoBoardScraper
import pdfplumber

scraper = ChicagoBoardScraper('2026-03-17')

# Download PDF
response = requests.get(pdf_url)
pdf_file = io.BytesIO(response.content)

# Custom extraction
with pdfplumber.open(pdf_file) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        # Your custom parsing here
```

### Combining with Cook County Clerk

To get complete Cook County results:

```python
# Scrape both authorities
chicago_results = chicago_board_scraper.scrape_summary_report()
suburban_results = cook_county_clerk_scraper.scrape_excel()

# Combine for statewide races
combined = {
    'county': 'Cook County (Complete)',
    'authorities': [
        {'name': 'Chicago Board', 'voters': chicago_results['summary']['registered_voters']},
        {'name': 'Cook County Clerk', 'voters': suburban_results['summary']['registered_voters']}
    ],
    'contests': merge_contests(chicago_results['contests'], suburban_results['contests'])
}
```

## Support Contacts

**Chicago Board of Election Commissioners**
- Website: chicagoelections.gov
- Address: 69 West Washington Street, Suites 600/800, Chicago, IL 60602
- Phone: (312) 269-7900
- Email: info@chicagoelections.gov

**For technical issues:**
- Check chicagoelections.gov/elections/results for PDF availability
- Verify PDF URL is correct (right-click → copy link)
- PDF format changes are rare but possible
- Most issues are timing-related (results not yet posted)

## Next Steps

1. **Install pdfplumber** - `pip install pdfplumber`
2. **Test with historical data** - Download a 2024 PDF and test parsing
3. **Find 2026 PDF URL** - On election night, get the correct URL
4. **Monitor and scrape** - Run every 15 minutes during counting
5. **Combine with Cook County Clerk** - For complete Cook County coverage

## Why PDFs?

You might wonder why Chicago Board uses PDFs instead of structured data APIs. Here's why PDFs actually work well:

✅ **Official documents** - These ARE the official results  
✅ **Consistent format** - Text layout is very stable  
✅ **Human-readable** - Easy to verify/debug  
✅ **Fast publishing** - PDFs are quick to generate  
✅ **Reliable** - Azure storage is rock-solid  
✅ **Accessible** - Anyone can view without special tools  

The main downside is PDF URLs aren't predictable, but once you have the URL, scraping is straightforward.

## Cook County Complete Coverage Checklist

To fully cover Cook County elections:

- [ ] **Chicago Board scraper** - City of Chicago (~1.5M voters) ← This scraper
- [ ] **Cook County Clerk scraper** - Suburban Cook (~2.4M voters) ← Separate scraper
- [ ] Combine results for statewide/countywide races
- [ ] Handle jurisdiction boundaries correctly
- [ ] Note which contests appear in both vs. one jurisdiction

**Combined: ~3.9M voters = 65% of Illinois!**
