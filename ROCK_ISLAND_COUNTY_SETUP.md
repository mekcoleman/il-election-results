# Rock Island County Scraper Setup - GEMS System

This guide covers scraping election results for **Rock Island County** using their GEMS (Global Election Management System) output.

## County Overview

**Rock Island County Statistics:**
- Population: ~145,000 residents
- Voters: ~100,000 registered voters
- Major cities: Rock Island, Moline, East Moline
- Part of: Quad Cities metro (Illinois side)

**Electoral Significance:** Part of the Quad Cities area (with Iowa), historically Democratic but competitive. Industrial heritage (John Deere headquarters in Moline), working-class voters, union presence.

## Platform Overview

**System:** GEMS (Global Election Management System)  
**Output Format:** PDF files with clean text formatting  
**Technology:** Structured text with consistent formatting  
**Complexity:** ⭐ Easy (one of the cleanest formats!)  
**Coverage:** All of Rock Island County

### Why GEMS is Great

GEMS produces **extremely clean, structured output**:
- Consistent formatting across all contests
- Clear separation between candidates and vote counts
- Dots/spaces align columns perfectly
- Party affiliations clearly marked
- Summary statistics included

This is one of the **easiest Illinois county formats** to parse!

## Installation

### Dependencies

```bash
pip install requests pdfplumber
```

The scraper uses:
- `requests` - Download PDF files
- `pdfplumber` - Extract text from PDFs

## GEMS Format Structure

### Overall Layout

```
SUMMARY REPORT        ROCK ISLAND COUNTY, ILLINOIS     OFFICIAL RESULTS
RUN DATE:04/15/25     2025 CONSOLIDATED ELECTION
RUN TIME:01:52 PM     APRIL 1, 2025

                                                       VOTES PERCENT

           PRECINCTS COUNTED (OF 120).  .  .  .  .       120  100.00
           REGISTERED VOTERS - TOTAL .  .  .  .  .    88,039
           BALLOTS CAST - TOTAL.  .  .  .  .  .  .    19,679
           VOTER TURNOUT - TOTAL  .  .  .  .  .  .             22.35

          PRESIDENT OF THE UNITED STATES
          (VOTE FOR)  1
           Joe Biden (DEM).  .  .  .  .  .  .  .  .     8,452   85.2%
           Dean Phillips (DEM) .  .  .  .  .  .  .       983    9.9%

          U.S. REPRESENTATIVE DISTRICT 17
          (VOTE FOR)  1
           Eric Sorensen (DEM) .  .  .  .  .  .  .     9,234  100.0%
```

### Key Features

1. **Header Section:** Summary statistics (precincts, turnout, voters)
2. **Contest Headers:** Contest name in ALL CAPS
3. **Vote-For Line:** `(VOTE FOR) N` indicates how many to elect
4. **Candidate Lines:** Name, party (in parentheses), dots, votes, percent
5. **Spacing:** Consistent alignment using dots and spaces

### Party Notation

Party affiliations shown in parentheses:
- `(DEM)` - Democratic
- `(REP)` - Republican
- `(IND)` or `(INC)` - Independent
- `(CON)` - Conservative (local party)
- `(CIT)` - Citizens (local party)
- `(PEO)` - People (local party)
- `(PRO)` - Progressive (local party)

For primary elections, results are often grouped by party section.

## Usage

### With PDF URL

```bash
python rock_island_county_scraper.py --url "https://www.rockislandcountyil.gov/DocumentCenter/View/XXXXX/..."
```

### Without URL (Shows Instructions)

```bash
python rock_island_county_scraper.py
```

## Finding the PDF URL

### Step-by-Step

1. **Visit the Previous Election Results page:**
   https://www.rockislandcountyil.gov/272/Previous-Election-Results

2. **Find the 2026 Primary election:**
   - Look for "General Primary Election - March 17, 2026 (PDF)"
   - Should be near the top of the page

3. **Copy the link:**
   - Right-click the PDF link
   - Select "Copy link address"

4. **Run the scraper:**
   ```bash
   python rock_island_county_scraper.py --url "[PASTED_URL]"
   ```

### URL Format

Rock Island PDFs use DocumentCenter URLs:
```
https://www.rockislandcountyil.gov/DocumentCenter/View/[ID]/[FILENAME]
```

Example:
```
https://www.rockislandcountyil.gov/DocumentCenter/View/1775/General-Primary-Election---March-19-2024-PDF
```

## Testing with 2024 Data

### Using Historical Data

Test your setup with the 2024 Primary:

1. Visit: https://www.rockislandcountyil.gov/272/Previous-Election-Results
2. Find "General Primary Election - March 19, 2024 (PDF)"
3. Copy URL
4. Run:
   ```bash
   python rock_island_county_scraper.py --url [URL] --date 2024-03-19
   ```

This lets you verify the scraper works before election day!

## Output Format

```json
{
  "county": "Rock Island",
  "election_date": "2026-03-17",
  "source": "Rock Island County GEMS PDF",
  "metadata": {
    "precincts_counted": 120,
    "registered_voters": 88039,
    "ballots_cast": 19679,
    "turnout_percent": 22.35
  },
  "contests": [
    {
      "name": "PRESIDENT OF THE UNITED STATES",
      "party": "Democratic",
      "vote_for": 1,
      "candidates": [
        {
          "name": "Joe Biden",
          "votes": 8452,
          "percent": 85.2,
          "party": "Democratic"
        }
      ]
    }
  ]
}
```

## Parsing Details

### What the Scraper Does

1. **Downloads PDF** from provided URL
2. **Extracts text** using pdfplumber
3. **Parses header** for summary statistics
4. **Identifies contests** by ALL CAPS headers + "(VOTE FOR)" line
5. **Extracts candidates** by parsing indented lines with dots
6. **Detects parties** from parenthetical abbreviations and section headers
7. **Calculates percentages** if missing

### Party Detection

The scraper uses multiple methods to determine party:

1. **Candidate party notation:** `(DEM)`, `(REP)`, etc.
2. **Contest name:** "DEMOCRATIC PRIMARY", "REPUBLICAN PRIMARY"
3. **Section headers:** Text between contests indicating party
4. **Default:** Non-Partisan for local races

### Multi-Candidate Races

GEMS handles multi-seat races clearly:
```
COUNTY BOARD DISTRICT 3
(VOTE FOR) 3
 Candidate A (DEM).  .  .  .  .  .  .  .     1,234   25.4%
 Candidate B (DEM).  .  .  .  .  .  .  .     1,190   24.5%
 Candidate C (REP).  .  .  .  .  .  .  .     1,156   23.8%
 Candidate D (REP).  .  .  .  .  .  .  .     1,278   26.3%
```

The scraper extracts `vote_for: 3` from the header.

## Troubleshooting

### PDF Download Fails

**Problem:** Can't download PDF

**Solutions:**
- Check URL is correct (copy from browser address bar)
- Verify PDF exists (visit URL in browser first)
- Results may not be posted yet if early in evening

### Empty Contests List

**Problem:** PDF loaded but no contests found

**Solutions:**
- PDF may be malformed or scanned image (not text)
- Check PDF manually - is text selectable?
- GEMS format may have changed (unlikely - very stable)

### Missing Candidates

**Problem:** Some candidates not showing

**Solutions:**
- Check original PDF to verify data exists
- Candidate line formatting may be unusual
- Write-in candidates sometimes formatted differently

### Wrong Party Detection

**Problem:** Party assigned incorrectly

**Solutions:**
- Check if party notation exists in PDF
- Some contests may be non-partisan
- Scraper defaults to Non-Partisan for ambiguous cases

### Percentages Don't Match

**Problem:** Calculated percentages differ from PDF

**Solutions:**
- PDF percentages may be rounded differently
- Scraper uses 2 decimal places
- Both should be close (within 0.1%)

## Election Day Workflow

### Pre-Election Setup

1. **Test with 2024 data** to verify scraper works
2. **Bookmark results page** for quick access
3. **Have URL format ready** to quickly find new PDF

### Election Night - Timeline

**7:00 PM** - Polls close

**7:30-8:30 PM** - First results typically posted
- Rock Island usually posts results fairly quickly
- PDF appears on Previous Election Results page

**Throughout night** - Results updated
- GEMS PDFs are typically replaced with updated versions
- Same URL, newer timestamp in PDF

**11:00 PM - Midnight** - Most results complete

### Monitoring Strategy

```bash
# Check for new PDF every 15 minutes
while true; do
  python rock_island_county_scraper.py --url $ROCK_ISLAND_URL
  echo "Updated at $(date)"
  sleep 900  # 15 minutes
done
```

Or manually check the results page and re-run when you see updates.

## Advanced: Party Breakdown

### Primary Election Format

For primary elections, GEMS typically groups by party:

```
DEMOCRATIC PRIMARY

PRESIDENT OF THE UNITED STATES
(VOTE FOR) 1
 Joe Biden (DEM) . . . . . . . .   8,452  85.2%

U.S. REPRESENTATIVE DISTRICT 17
(VOTE FOR) 1
 Eric Sorensen (DEM) . . . . . .   9,234 100.0%

REPUBLICAN PRIMARY

PRESIDENT OF THE UNITED STATES
(VOTE FOR) 1
 Donald J. Trump (REP) . . . . .   5,873  78.3%
 Nikki Haley (REP) . . . . . . .   1,628  21.7%
```

The scraper detects these section headers and applies party to subsequent contests.

### Non-Partisan Section

Some contests (judges, local offices) appear in a non-partisan section:

```
NONPARTISAN

CIRCUIT COURT JUDGE
(VOTE FOR) 1
 Incumbent Judge . . . . . . . .  12,345  100.0%
```

## Comparison: Rock Island vs Other Counties

| County | Format | Complexity | Party Notation |
|--------|--------|------------|----------------|
| **Rock Island** | **GEMS PDF** | **⭐ Easy** | **In parentheses** |
| McLean | Text docs | ⭐⭐ Medium | Section headers |
| Champaign | Excel | ⭐⭐ Medium | Sheet names |
| Peoria | ElectionStats | ⭐⭐⭐ Medium-High | Contest titles |

Rock Island is one of the easiest to parse - clean, consistent format!

## Why GEMS is Excellent

**Advantages:**
1. **Consistent formatting** - Same structure every election
2. **Clear alignment** - Dots make parsing reliable
3. **Complete data** - Votes, percentages, party all included
4. **Machine-readable** - Text-based PDF, not scanned image
5. **Summary stats** - Turnout and precinct info in header
6. **Multi-seat support** - `(VOTE FOR) N` clearly marked

**Only minor challenge:**
- Need to find PDF URL (not auto-generated)
- But format is so clean that parsing is trivial

## Historical Context

Rock Island has used GEMS for many years:
- Very stable format across elections
- County clerk maintains consistency
- Excellent for building historical databases

If you're scraping multiple years, the same parser works for all!

## Summary - Quick Reference

**✅ To scrape Rock Island County:**

1. Visit: https://www.rockislandcountyil.gov/272/Previous-Election-Results
2. Find: "General Primary Election - March 17, 2026 (PDF)"
3. Copy PDF URL
4. Run: `python rock_island_county_scraper.py --url [URL]`
5. Get: Clean JSON with all contests, candidates, votes, parties

**📊 What you get:**
- All contests with candidate names, votes, percentages
- Party affiliations clearly marked
- Summary statistics (turnout, precincts, etc.)
- Properly parsed multi-candidate races

**⚡ Why it's easy:**
- GEMS format is extremely clean and consistent
- Text-based PDF (not scanned image)
- Structured layout makes parsing reliable
- One of the simplest Illinois county formats!

Rock Island County is ~100K voters in the Quad Cities - an important bellwether for western Illinois!
