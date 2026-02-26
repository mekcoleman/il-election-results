# Fulton County Scraper Setup - Cumulative Results Report

This guide covers scraping election results for **Fulton County** using their Cumulative Results Report PDF format.

## County Overview

**Fulton County Statistics:**
- Population: ~35,000 residents
- Voters: ~25,000 registered voters
- Major city: Canton (county seat)
- Other towns: Lewistown, Farmington
- Location: West-central Illinois

**Electoral Significance:** Small rural county with agricultural economy. Canton is historic small industrial city. Typically Republican, part of rural downstate voting patterns. While small, represents the many rural counties that collectively form significant portion of Illinois electorate.

## Platform Overview

**System:** Custom PDF - Cumulative Results Report  
**Output Format:** Structured PDF with detailed breakdowns  
**Technology:** Tabular format with vote method details  
**Complexity:** ⭐⭐ Medium  
**Coverage:** All of Fulton County

### Why This Format is Good

Fulton's Cumulative Results Report is **very well-structured**:
- Clean tabular layout
- Vote breakdown by method (Election Day, Early, Mail)
- Party clearly indicated in contest names
- Summary statistics in header
- Consistent formatting across elections

Similar to La Salle's Election Summary Report but with more detail on voting methods!

## Installation

### Dependencies

```bash
pip install requests pdfplumber
```

The scraper uses:
- `requests` - Download PDF files
- `pdfplumber` - Extract text from PDFs

## Cumulative Results Report Format

### Overall Structure

```
Cumulative Results Report
ELECTION DAY
Run Time 12:18 PM
Run Date 04/02/2024
Fulton County, IL
Fulton 2024 General Primary Election
3/19/2024
Page 1
Official Results

Registered Voters 3336 of 24200 = 13.79%
Precincts Reporting 44 of 44 = 100.00%

FOR PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY - (Vote for one)
Precincts
Counted Total Percent
44 44 100.00%
Voters
Ballots Registered Percent
1,989 24,200 8.22%

Choice Party Election Day Early-Grace Vote By Mail Total
DONALD J. TRUMP 1,487 87.11% 91 87.50% 106 67.09% 1,684 85.53%
NIKKI HALEY 147 8.61% 11 10.58% 39 24.68% 197 10.01%
RON DeSANTIS 43 2.52% 2 1.92% 8 5.06% 53 2.69%
Cast Votes: 1,707 100.00% 104 100.00% 158 100.00% 1,969 100.00%
Undervotes: 15 3 1 19
Overvotes: 0 0 1 1
```

### Key Format Features

1. **Header Section:** Title, date/time, election name, official status
2. **Summary Line:** Registered voters, ballots cast, turnout percentage, precincts reporting
3. **Contest Headers:** "FOR [CONTEST NAME] - [PARTY] - (Vote for X)"
4. **Contest Metadata:** Precincts counted, voters/ballots statistics
5. **Vote Method Columns:** Election Day, Early-Grace, Vote By Mail, Total
6. **Candidate Lines:** Name followed by votes and percentages for each method
7. **Cast Votes Line:** Total votes cast in contest (marks end of candidates)
8. **Undervotes/Overvotes:** Additional statistics

### Party Notation

Party indicated in contest name:
- `FOR ... - REPUBLICAN PARTY - (Vote for one)` - Republican primary contest
- `FOR ... - DEMOCRATIC PARTY - (Vote for one)` - Democratic primary contest
- No party suffix for non-partisan races (judges, local offices)

For primary elections, contests are separated by party, with Republican contests typically appearing first, followed by Democratic contests.

### Vote Method Breakdown

Fulton provides detailed breakdown by voting method:
- **Election Day** - Votes cast at polls on election day
- **Early-Grace** - Early voting and grace period voting combined
- **Vote By Mail** - Mail-in/absentee ballots
- **Total** - Sum of all methods

Each method shows both raw vote count and percentage within that method.

## Usage

### With PDF URL

```bash
python fulton_county_scraper.py --url "https://fultoncountyilelections.gov/wp-content/uploads/2024/04/2024-Official-Primary-Results.pdf"
```

### Without URL (Shows Instructions)

```bash
python fulton_county_scraper.py
```

## Finding the PDF URL

### Step-by-Step

1. **Visit the Election Results page:**
   https://fultoncountyilelections.gov/election-results/

2. **Find the 2026 Primary results:**
   - Page shows results organized by year (2025, 2024, 2023, etc.)
   - Look for "2026 Primary Election OFFICIAL Results"
   - May also see "Unofficial Results" early in evening

3. **Copy the link:**
   - Right-click the PDF link
   - Select "Copy link address"

4. **Run the scraper:**
   ```bash
   python fulton_county_scraper.py --url "[PASTED_URL]"
   ```

### URL Format

Fulton PDFs are hosted on WordPress site:
```
https://fultoncountyilelections.gov/wp-content/uploads/YYYY/MM/filename.pdf
```

Example:
```
https://fultoncountyilelections.gov/wp-content/uploads/2024/04/2024-Official-Primary-Results.pdf
```

### Official vs Unofficial Results

Fulton typically posts:
1. **Unofficial Results** - Posted election night, may be updated
2. **Official Results** - Posted after canvass (typically 2 weeks later)

For election night monitoring, use Unofficial. For final certified data, wait for Official.

## Testing with 2024 Data

### Using Historical Data

Test your setup with the 2024 Primary:

1. Visit: https://fultoncountyilelections.gov/election-results/
2. Find "2024 Primary Election OFFICIAL Results"
3. Copy URL
4. Run:
   ```bash
   python fulton_county_scraper.py \
     --url "https://fultoncountyilelections.gov/wp-content/uploads/2024/04/2024-Official-Primary-Results.pdf" \
     --date 2024-03-19
   ```

This verifies the scraper works before election day!

### What to Expect from 2024 Test

The 2024 Primary had:
- 3,336 ballots cast out of 24,200 registered (13.79% turnout)
- 44 precincts reporting
- Separate Republican and Democratic contests
- Presidential primary (Trump vs Haley on GOP; Biden on Dem)
- Congressional races
- County offices

If your test scraper successfully extracts these contests with correct vote totals, you're ready for 2026!

## Output Format

```json
{
  "county": "Fulton",
  "election_date": "2026-03-17",
  "source": "Fulton County Cumulative Results Report PDF",
  "pdf_url": "https://fultoncountyilelections.gov/wp-content/uploads/2026/03/...",
  "scraped_at": "2026-03-17T20:30:00",
  "metadata": {
    "registered_voters": 24200,
    "ballots_cast": 3336,
    "precincts_reporting": 44,
    "total_precincts": 44
  },
  "contests": [
    {
      "name": "FOR PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY",
      "party": "Republican",
      "vote_for": 1,
      "candidates": [
        {
          "name": "DONALD J. TRUMP",
          "votes": 1684,
          "percent": 85.53
        },
        {
          "name": "NIKKI HALEY",
          "votes": 197,
          "percent": 10.01
        }
      ]
    }
  ]
}
```

## Parsing Details

### Contest Detection

Contest headers are identified by:
- Starting with "FOR "
- Containing " - " (party separator) or "(Vote for" notation
- Being longer than typical candidate names

Example: `FOR PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY - (Vote for one)`

### Party Detection

Party is extracted from contest name:
1. Check for " - REPUBLICAN PARTY" or " - DEMOCRATIC PARTY" suffix
2. Check for "REPUBLICAN" or "DEMOCRATIC" anywhere in name
3. Default to "Non-Partisan" if no party indicators

### Vote-For Number

Extracted from parenthetical notation:
- `(Vote for one)` → 1
- `(Vote for not more than three)` → 3
- `(Vote for two)` → 2

### Candidate Parsing

Candidate lines are parsed by:
1. Identifying lines between contest header and "Cast Votes:" line
2. Working backwards from end of line to find total votes and percentage
3. Everything before the numbers is the candidate name
4. Skipping "No Candidate" entries (they didn't receive votes)

### Multi-Candidate Races

Format handles multi-seat races clearly:
```
FOR MEMBERS OF THE COUNTY BOARD DISTRICT 1 - REPUBLICAN PARTY - (Vote for three)
...
MICHAEL EUGENE SHERBEYN 299 100.00% 15 100.00% 35 100.00% 349 100.00%
```

The scraper extracts `vote_for: 3` from the header.

### Vote Method Detail

While the PDF shows breakdown by voting method (Election Day, Early, Mail), the scraper focuses on **Total** column for simplicity. The vote method breakdown is available in the PDF for manual analysis if needed, but the JSON output contains only the final totals.

This keeps the output clean and consistent with other county scrapers that don't have this level of detail.

## Troubleshooting

### PDF Download Fails

**Problem:** Can't download PDF

**Solutions:**
- Verify URL is correct (copy from browser address bar)
- Check if PDF exists (visit URL in browser first)
- Results may not be posted yet if early in evening
- Try without VPN if using one

### Empty Contests

**Problem:** PDF loaded but no contests parsed

**Solutions:**
- Check if PDF is text-based (not scanned image)
- Verify contest headers start with "FOR "
- Format may have changed slightly
- Compare to 2024 sample to see differences

### Missing Candidates

**Problem:** Some candidates not showing in output

**Solutions:**
- Check original PDF - is data there?
- Candidate line format may be unusual
- "No Candidate" entries are intentionally skipped
- Write-in candidates may have different formatting

### Wrong Vote Totals

**Problem:** Vote counts don't match PDF

**Solutions:**
- Scraper uses Total column (rightmost numbers)
- Check you're comparing totals, not Election Day only
- Verify PDF isn't corrupted
- Re-download PDF and try again

### Party Assignment Issues

**Problem:** Contests assigned wrong party

**Solutions:**
- Party comes from contest name
- Check if " - REPUBLICAN PARTY" or " - DEMOCRATIC PARTY" is in name
- Non-partisan races won't have party suffix
- Scraper defaults to "Non-Partisan" if ambiguous

### Percentage Discrepancies

**Problem:** Calculated percentages differ from PDF

**Solutions:**
- PDF may use different rounding
- Scraper uses 2 decimal places
- Both should be very close (within 0.1%)
- Small differences due to rounding are normal

## Election Day Workflow

### Pre-Election Setup

1. **Test with 2024 data** to verify scraper works
2. **Bookmark results page** for quick access
3. **Note URL pattern** for quick identification
4. **Have scraper ready** in your election night setup

### Election Night - Timeline

**7:00 PM** - Polls close

**7:30-8:30 PM** - First results typically posted
- Fulton usually posts within 90 minutes of poll closing
- Check the election results page
- Look for "Unofficial Results"

**Throughout night** - Results updated
- Fulton may update PDF with new vote counts
- Same URL typically, just replace file
- Or may post entirely new PDF

**Next day - 2 weeks** - Official results
- Final canvassed results posted
- "Official Results" designation
- Includes all provisional ballots

### Monitoring Strategy

```bash
# Option 1: Manual checking
# Visit page every 15-30 minutes
# When you see new PDF, copy URL and run scraper

# Option 2: Automated (if URL pattern is predictable)
FULTON_URL="https://fultoncountyilelections.gov/wp-content/uploads/2026/03/2026-Primary-Unofficial-Results.pdf"

while true; do
  python fulton_county_scraper.py --url $FULTON_URL
  echo "Updated at $(date)"
  sleep 900  # 15 minutes
done
```

### Best Practices

- Check page first to see if results are posted
- PDF filename may not be predictable in advance
- Start checking around 8:00 PM
- Be patient - small county, may take time to tabulate
- Save each version if tracking updates

## Format Comparison

### Fulton vs La Salle vs Rock Island

| County | Format | Vote Detail | Complexity |
|--------|--------|-------------|------------|
| **Fulton** | **Cumulative Report** | **By method** | **⭐⭐ Medium** |
| La Salle | Summary Report | Totals only | ⭐⭐ Medium |
| Rock Island | GEMS | Totals only | ⭐ Easy |

**Key differences:**
- **Fulton** provides vote breakdown by method (Election Day, Early, Mail)
- **La Salle** similar structure but only total votes
- **Rock Island** cleanest format with dots for alignment

All three are well-structured and reliable - Fulton just has extra detail!

### Similar Counties

Fulton's format is most similar to:
- La Salle (nearly identical structure)
- Smaller rural counties with custom PDF systems
- Counties using tabular reporting formats

Different from:
- GEMS counties (Rock Island) - different header style
- Excel counties (Champaign, Cook) - different file format
- Database counties (Peoria) - requires ID collection

## Primary vs General Format

### Primary Elections

For primaries, Fulton separates by party:
```
FOR PRESIDENT OF THE UNITED STATES - REPUBLICAN PARTY - (Vote for one)
[Republican candidates]

FOR PRESIDENT OF THE UNITED STATES - DEMOCRATIC PARTY - (Vote for one)
[Democratic candidates]
```

Party is explicitly in the contest name.

### General Elections

For generals, contests show all parties:
```
FOR PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES - (Vote for one)
DONALD J. TRUMP (REP)
KAMALA D. HARRIS (DEM)
[Other candidates]
```

Party notation `(REP)` or `(DEM)` appears after candidate names.

The scraper handles both formats automatically.

## Advanced: Vote Method Analysis

While the scraper outputs only total votes for simplicity, the PDF contains rich data about voting methods:

```
DONALD J. TRUMP 1,487 87.11% 91 87.50% 106 67.09% 1,684 85.53%
                ^Election Day  ^Early      ^Mail      ^Total
```

This data is valuable for:
- Understanding voting patterns
- Detecting anomalies
- Analyzing early vs election day turnout
- Mail ballot usage patterns

If you need this detail, you could extend the scraper to capture vote method breakdown. The parsing logic would need to extract all four number pairs instead of just the total.

## Historical Context

Fulton County has used this Cumulative Results Report format for several years:
- Consistent since at least 2016
- WordPress-based website updated around 2022
- Format stable across elections
- Only minor tweaks to header information

Same parser should work across multiple election years with minimal adjustments!

## County-Specific Notes

### Small County Considerations

At ~25,000 voters, Fulton is:
- One of the smaller counties in your 38-county list
- Results typically complete faster (fewer precincts to tabulate)
- Less complex local races
- Easier to manually verify if needed

### Canton Dominance

Canton (county seat) comprises about 40% of county population:
- Results from Canton precincts disproportionately important
- Watch Canton precincts for early indication
- City of Canton has separate precincts (Canton 1-16 in 2024)

### Precinct Count

44 precincts in 2024:
- Mix of city precincts (Canton, Lewistown, Farmington)
- Township precincts (rural areas)
- Some townships have multiple precincts
- Full list available in PDF

## Why This County Matters

Despite being small (~25K voters), Fulton matters because:
1. **Representative** - Typical of many rural Illinois counties
2. **Clean data** - Well-organized reporting
3. **Bellwether** - Often mirrors statewide rural trends
4. **Complete coverage** - Getting these small counties shows thoroughness

In aggregate, counties like Fulton represent significant portions of downstate Illinois vote.

## Summary - Quick Reference

**✅ To scrape Fulton County:**

1. Visit: https://fultoncountyilelections.gov/election-results/
2. Find: "2026 Primary Election OFFICIAL Results" PDF
3. Copy PDF URL
4. Run: `python fulton_county_scraper.py --url [URL]`
5. Get: Clean JSON with all contests, candidates, votes

**📊 What you get:**
- All contests with candidates, votes, percentages
- Party from contest names (- REPUBLICAN PARTY, - DEMOCRATIC PARTY)
- Summary statistics (turnout, precincts, registered voters)
- Proper handling of multi-candidate races
- Cleaned candidate names (no "No Candidate" entries)

**💡 Why it's good:**
- Clean, structured PDF format
- Consistent formatting makes parsing reliable
- Vote method breakdown available (though not in JSON output)
- Small county = fast results
- Good representative of rural Illinois counties

**📍 County importance:**
- ~25K voters in west-central Illinois
- Canton + rural townships
- Typical Republican rural county
- Part of comprehensive Illinois coverage

Fulton County provides excellent structured data - one of the better small-county PDF formats in Illinois!
