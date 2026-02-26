# La Salle County Scraper Setup - Election Summary Report

This guide covers scraping election results for **La Salle County** using their Election Summary Report PDF format.

## County Overview

**La Salle County Statistics:**
- Population: ~110,000 residents
- Voters: ~80,000 registered voters
- Major cities: Ottawa (county seat), Peru, Streator, LaSalle
- Location: North-central Illinois

**Electoral Significance:** Mix of small industrial cities (Ottawa, Peru) and rural areas. Historically Republican, agricultural economy mixed with manufacturing. Key county for understanding downstate voting patterns.

## Platform Overview

**System:** Custom PDF - Election Summary Report  
**Output Format:** Structured PDF with clean formatting  
**Technology:** Similar to GEMS but distinct format  
**Complexity:** ⭐⭐ Medium  
**Coverage:** All of La Salle County

### Why This Format is Good

La Salle's Election Summary Report is **clean and well-structured**:
- Consistent layout across all contests
- Clear separation of contests
- Vote counts and percentages aligned
- Party affiliations clearly marked
- Summary statistics in header

Not quite as clean as Rock Island's GEMS, but still very parseable!

## Installation

### Dependencies

```bash
pip install requests pdfplumber
```

## Election Summary Report Format

### Overall Structure

```
Election Summary Report
 GENERAL PRIMARY ELECTION
TUESDAY, MARCH 17, 2026
LaSALLE COUNTY, ILLINOIS
March 17, 2026 Primary Election
OFFICIAL RESULTS

Date: 03/31/2026
Time: 4:41:06 PM CST
Page 1/6

Registered Voters 73,745 - Total Ballots 35,072 : 47.56%
120 of 120 Precincts Reporting 100.00%

PRESIDENT OF THE UNITED STATES - DEMOCRATIC
Number of Precincts 120
Precincts Reporting 120
Vote For 1
Joe Biden (DEM) 15,234 85.67%
Dean Phillips (DEM) 2,545 14.33%
Total Votes 17,779
100.00%

PRESIDENT OF THE UNITED STATES - REPUBLICAN
Number of Precincts 120
Precincts Reporting 120
Vote For 1
Donald J. Trump (REP) 12,873 78.45%
Nikki Haley (REP) 3,536 21.55%
Total Votes 16,409
100.00%
```

### Key Format Features

1. **Header:** Election title, date, official status
2. **Metadata:** Date/time generated, page numbers
3. **Summary Line:** Registered voters, ballots cast, turnout, precincts
4. **Contest Headers:** Contest name (ALL CAPS)
5. **Contest Metadata:** Number of precincts, vote-for number
6. **Candidate Lines:** Name (PARTY) votes percent%
7. **Total Votes:** Sum at end of each contest

### Party Notation

Parties shown in parentheses after candidate names:
- `(REP)` - Republican
- `(DEM)` - Democratic
- `(IND)` - Independent
- `No Candidate (REP)` - No candidate filed

Primary elections typically separate contests by party in contest name:
- "PRESIDENT OF THE UNITED STATES - DEMOCRATIC"
- "PRESIDENT OF THE UNITED STATES - REPUBLICAN"

## Usage

### With PDF URL

```bash
python la_salle_county_scraper.py --url "https://www.lasallecountyil.gov/DocumentCenter/View/XXXXX/..."
```

### Without URL (Shows Instructions)

```bash
python la_salle_county_scraper.py
```

## Finding the PDF URL

### Step-by-Step

1. **Visit the Election Results page:**
   https://www.lasallecountyil.gov/251/Election-Results

2. **Find the 2026 Primary results:**
   - Look for "2026 General Primary Election Results"
   - May be labeled "Official" vs "Unofficial"
   - May have separate PDFs with/without write-ins

3. **Copy the link:**
   - Right-click the PDF link
   - Select "Copy link address"

4. **Run the scraper:**
   ```bash
   python la_salle_county_scraper.py --url "[PASTED_URL]"
   ```

### URL Format

La Salle PDFs use DocumentCenter URLs:
```
https://www.lasallecountyil.gov/DocumentCenter/View/[ID]/[FILENAME]
```

Example:
```
https://www.lasallecountyil.gov/DocumentCenter/View/4216/2024-General-Election-Results
```

### Multiple PDF Versions

La Salle often posts two versions:
1. **Official without write-ins** - Cleaner, recommended for scraping
2. **Official with write-ins** - Includes write-in votes

Use the "without write-ins" version unless you specifically need write-in data.

## Testing with 2024 Data

Test with the 2024 General Election:

1. Visit: https://www.lasallecountyil.gov/251/Election-Results
2. Find "Official 2024 General Election Results without write in votes (PDF)"
3. Copy URL (should be DocumentCenter/View/4216 or similar)
4. Run:
   ```bash
   python la_salle_county_scraper.py --url [URL] --date 2024-11-05
   ```

This verifies the scraper works before election day!

## Output Format

```json
{
  "county": "La Salle",
  "election_date": "2026-03-17",
  "source": "La Salle County Election Summary Report PDF",
  "metadata": {
    "registered_voters": 73745,
    "ballots_cast": 35072,
    "turnout_percent": 47.56,
    "precincts_reporting": 120,
    "total_precincts": 120
  },
  "contests": [
    {
      "name": "PRESIDENT OF THE UNITED STATES - DEMOCRATIC",
      "party": "Democratic",
      "vote_for": 1,
      "candidates": [
        {
          "name": "Joe Biden",
          "votes": 15234,
          "percent": 85.67,
          "party": "Democratic"
        }
      ]
    }
  ]
}
```

## Parsing Details

### Contest Detection

Contest headers are:
- ALL CAPS text
- Longer than 10 characters
- Not starting with "NUMBER OF" or "VOTE FOR" or "TOTAL VOTES"
- Not just a party abbreviation like "(REP)"

### Candidate Parsing

Candidate lines are parsed by:
1. Working backwards from end of line
2. Finding percent (XX.XX%)
3. Finding votes (before percent)
4. Remaining text is candidate name + party

Party notation `(PARTY)` is extracted and removed from name.

### Multi-Candidate Races

Format handles multi-seat races:
```
COUNTY BOARD 3RD DISTRICT MEMBER
...
Vote For 3
Candidate A (REP) 1,234 25.4%
Candidate B (DEM) 1,190 24.5%
Candidate C (REP) 1,156 23.8%
...
```

The scraper extracts `vote_for: 3` from metadata.

### No Candidate Filed

Lines like "No Candidate (REP)" are skipped - the scraper only includes actual candidates who received votes.

## Troubleshooting

### PDF Download Fails

**Problem:** Can't download PDF

**Solutions:**
- Verify URL is correct (copy from browser)
- Check if PDF exists (visit URL in browser first)
- Results may not be posted yet

### Empty Contests

**Problem:** PDF loaded but no contests parsed

**Solutions:**
- Check if PDF is text-based (not scanned image)
- Verify contest headers are ALL CAPS
- Format may have changed (compare to 2024 sample)

### Missing Candidates

**Problem:** Some candidates not showing

**Solutions:**
- Check original PDF - is data there?
- Candidate line format may be unusual
- "No Candidate" entries are intentionally skipped

### Wrong Percentages

**Problem:** Percentages don't match PDF

**Solutions:**
- PDF may use different rounding
- Scraper uses 2 decimal places
- Should be close (within 0.1%)

## Election Day Workflow

### Pre-Election Setup

1. **Test with 2024 data** to verify scraper works
2. **Bookmark results page**
3. **Note URL pattern** for quick access

### Election Night - Timeline

**7:00 PM** - Polls close

**8:00-9:00 PM** - First results typically posted
- La Salle usually posts results within an hour
- PDF appears on Election Results page

**Throughout night** - Results updated
- La Salle replaces PDFs with updated versions
- Check for "Unofficial" vs "Official" status
- URL may stay same or change

**Next day** - Official results
- Final official PDF posted
- Includes all provisional ballots

### Monitoring Strategy

```bash
# Check for new PDF every 15 minutes
while true; do
  python la_salle_county_scraper.py --url $LASALLE_URL
  echo "Updated at $(date)"
  sleep 900  # 15 minutes
done
```

Or manually refresh the results page and re-run when you see updates.

## Format Comparison

### La Salle vs Rock Island vs Others

| County | Format | Layout | Complexity |
|--------|--------|--------|------------|
| **La Salle** | **Summary Report** | **Structured sections** | **⭐⭐ Medium** |
| Rock Island | GEMS PDF | Dots + alignment | ⭐ Easy |
| McLean | Text files | Line-based | ⭐⭐ Medium |
| Champaign | Excel | Spreadsheet | ⭐⭐ Medium |
| Peoria | ElectionStats | Database | ⭐⭐⭐ Medium-High |

La Salle's format is clean and well-designed, though requires slightly more parsing logic than Rock Island's GEMS format.

## Primary vs General Format

### Primary Elections

For primaries, La Salle typically includes party in contest name:
```
PRESIDENT OF THE UNITED STATES - DEMOCRATIC
PRESIDENT OF THE UNITED STATES - REPUBLICAN
```

The scraper detects party from contest names and candidate notations.

### General Elections

For generals, contests are non-partisan or include both parties:
```
PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES
(Donald J. Trump (JD Vance (REP) ...
(Kamala D. Harris (Tim Walz (DEM) ...
```

Party comes from candidate notation `(REP)` or `(DEM)`.

## Advanced: Write-In Votes

La Salle posts separate PDFs for write-in results. If needed:

1. Find "Official with Write-In Votes" PDF
2. Run scraper on that version
3. Write-in candidates shown like regular candidates

Most users won't need write-in data for main results.

## Historical Context

La Salle has used this Election Summary Report format for several years:
- Consistent across elections
- Only minor formatting tweaks over time
- Good for building historical databases

Same parser should work across multiple election years!

## Summary - Quick Reference

**✅ To scrape La Salle County:**

1. Visit: https://www.lasallecountyil.gov/251/Election-Results
2. Find: "2026 General Primary Election Results" PDF
3. Copy PDF URL
4. Run: `python la_salle_county_scraper.py --url [URL]`
5. Get: Clean JSON with all contests, candidates, votes

**📊 What you get:**
- All contests with candidates, votes, percentages
- Party affiliations from candidate notation
- Summary statistics (turnout, precincts, etc.)
- Proper handling of multi-candidate races

**💡 Why it's good:**
- Clean, structured PDF format
- Consistent layout makes parsing reliable
- Summary statistics included
- Party information clearly marked

**📍 County importance:**
- ~80K voters in north-central Illinois
- Mix of small industrial cities and rural areas
- Historically Republican, downstate bellwether
- Part of understanding Illinois rural vote

La Salle County provides excellent structured data - one of the better PDF formats in Illinois!
