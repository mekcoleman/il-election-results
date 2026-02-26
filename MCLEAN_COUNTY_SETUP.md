# McLean County Scraper Setup - DUAL AUTHORITY SYSTEM

This guide covers scraping election results for **McLean County**, which has **TWO separate election authorities**.

## 🚨 CRITICAL: Dual Authority System

**McLean County is like Cook County - two completely separate election authorities!**

| Authority | Jurisdiction | Voters | Platform | Scraper |
|-----------|--------------|--------|----------|---------|
| **McLean County Clerk** | County except Bloomington | ~65K | Text/PDF docs | mclean_county_scraper.py |
| **Bloomington Election Commission** | City of Bloomington only | ~55K | Clarity Elections | clarity_scraper.py |
| **TOTAL** | **All of McLean County** | **~120K** | **Both** | **Need BOTH scrapers** |

**For complete McLean County results, you MUST run BOTH scrapers and combine results!**

## County Overview

**McLean County Statistics:**
- Population: ~170,000 residents
- Voters: ~120,000 registered voters
- Major cities: Bloomington, Normal
- Home to: Illinois State University (Normal)

**Electoral Significance:** College town with mix of university voters, insurance industry (State Farm HQ), and surrounding agricultural communities. Typically Democratic due to Bloomington-Normal.

## Why Two Authorities?

Bloomington is one of only a few Illinois cities with its own election commission:
- Established by state statute
- Independent from county clerk
- Handles ALL elections within Bloomington city limits
- County Clerk handles rest of county (including Normal!)

**Similar setup to:**
- Cook County (Chicago Board + County Clerk)
- Other large Illinois cities with separate commissions

## Platform Overview - Part 1: McLean County Clerk

**System:** Custom text/PDF document system  
**Technology:** Plain text files posted to website  
**Complexity:** ⭐⭐ Medium  
**Coverage:** County EXCEPT Bloomington (~65K voters)

### McLean County Clerk Documents

Multiple document types available:
- **Summary results** - County totals (recommended for scraping)
- **Precinct results** - Detailed by precinct
- **Abstract of canvass** - Official certified results
- **Results with group details** - Breakdown by early/mail/election day

## Platform Overview - Part 2: Bloomington

**System:** Clarity Elections  
**Technology:** Clarity ENR JSON API  
**Complexity:** ⭐⭐ Medium (but we already have scraper!)  
**Coverage:** City of Bloomington only (~55K voters)

**Good news:** We already have a Clarity scraper! Just need Bloomington's election ID.

## Installation

### Dependencies

```bash
# For McLean County Clerk
pip install requests beautifulsoup4

# For Bloomington (Clarity)
# Already covered by existing clarity_scraper.py requirements
```

## Complete McLean County Scraping - Two-Part Process

### PART 1: McLean County Clerk

**What it covers:** Normal + unincorporated McLean County (~65K voters)

**Steps:**

1. Visit: https://www.mcleancountyil.gov/231/Past-McLean-County-Election-Results

2. Find "2026 Primary summary results" (or similar)

3. Right-click → Copy link address

4. Run McLean County scraper:
   ```bash
   python mclean_county_scraper.py --url "https://www.mcleancountyil.gov/DocumentCenter/View/XXXXX/2026-Primary-summary-results"
   ```

5. Output: `mclean_county_clerk_results.json`

### PART 2: Bloomington Election Commission

**What it covers:** City of Bloomington only (~55K voters)

**Steps:**

1. Visit: https://results.enr.clarityelections.com/IL/Bloomington/

2. Find 2026 Primary election, note election ID from URL
   - Example URL: `/IL/Bloomington/123456/` → ID is 123456

3. Run Clarity scraper:
   ```bash
   python clarity_scraper.py --county Bloomington --election-id 123456
   ```

4. Output: `bloomington_results.json` (or clarity output format)

### PART 3: Combining Results

For complete McLean County totals:

```python
# Pseudo-code for combining
mclean_clerk_data = load('mclean_county_clerk_results.json')
bloomington_data = load('bloomington_results.json')

for race in countywide_races:
    total_votes = clerk_votes + bloomington_votes
```

**Important:** Not all races appear in both jurisdictions!
- **Countywide races** (President, U.S. Rep, State offices): Need both combined
- **Local races** (City Council, Township): Only in one jurisdiction

## McLean County Clerk Document Format

### Text File Structure

McLean posts results as plain text files with format:

```
DEMOCRATIC PRIMARY

PRESIDENT OF THE UNITED STATES
Joe Biden ........................ 8,452   85.2%
Dean Phillips ....................   983    9.9%
Marianne Williamson ..............   485    4.9%

U.S. REPRESENTATIVE DISTRICT 13
Nikki Budzinski .................. 9,234  100.0%

REPUBLICAN PRIMARY

PRESIDENT OF THE UNITED STATES
Donald J. Trump .................. 5,873   78.3%
Nikki Haley .....................  1,628   21.7%
```

The scraper parses this format to extract:
- Contest names
- Candidate names
- Vote totals
- Percentages

### Party Detection

Party determined by section headers:
- "DEMOCRATIC PRIMARY" section
- "REPUBLICAN PRIMARY" section
- "NONPARTISAN" section

## Usage - McLean County Clerk Only

### With Document URL

```bash
python mclean_county_scraper.py --url "https://www.mcleancountyil.gov/DocumentCenter/View/27481/..."
```

### Without URL (Shows Instructions)

```bash
python mclean_county_scraper.py
```

## Output Format - County Clerk

```json
{
  "authority": "McLean County Clerk",
  "jurisdiction": "McLean County (except Bloomington)",
  "election_date": "2026-03-17",
  "source": "McLean County Clerk Document",
  "note": "This covers McLean County EXCEPT City of Bloomington. Bloomington has separate results via Clarity Elections.",
  "contests": [
    {
      "name": "PRESIDENT OF THE UNITED STATES",
      "party": "Democratic",
      "candidates": [
        {
          "name": "Joe Biden",
          "votes": 8452,
          "percent": 85.2
        }
      ]
    }
  ]
}
```

## Troubleshooting

### "Results incomplete - missing Bloomington"

**This is expected!** McLean County Clerk scraper only covers part of the county.

**Solution:** Also run Bloomington scraper (clarity_scraper.py)

### Document URL 404

**Problem:** URL doesn't exist

**Solutions:**
- Results may not be posted yet
- Verify URL by visiting in browser
- Check https://www.mcleancountyil.gov/231/Past-McLean-County-Election-Results

### Empty Contests

**Problem:** Document loaded but no contests parsed

**Solutions:**
- Text format may have changed
- Check document manually to see structure
- May need to adjust parsing logic

### Bloomington Election ID Not Found

**Problem:** Can't find Bloomington Clarity election ID

**Solutions:**
- Visit https://results.enr.clarityelections.com/IL/Bloomington/
- Look for 2026 Primary in the list
- Election ID is in the URL path
- Results may not be posted yet if early on election night

### Wrong Totals When Combined

**Problem:** Combined totals seem off

**Solutions:**
- Make sure you're not double-counting
- Some races only appear in one jurisdiction
- Verify both scrapers ran successfully
- Check that you're combining the right contests

## Election Day Workflow

### Pre-Election Setup

1. **Test McLean County Clerk scraper** with 2024 data
2. **Test Bloomington Clarity scraper** with 2024 election ID
3. **Bookmark both result pages**
4. **Prepare combining script** if needed

### Election Night - Timeline

**7:00 PM** - Polls close

**7:30-8:30 PM** - First results typically posted (both authorities)

**Throughout night** - Results updated periodically

**Midnight** - Most results complete (both authorities)

### Monitoring Strategy

Since you need both authorities, monitor both:

```bash
# Terminal 1: McLean County Clerk
while true; do
  python mclean_county_scraper.py --url $CLERK_URL
  echo "Clerk updated at $(date)"
  sleep 900
done

# Terminal 2: Bloomington
while true; do
  python clarity_scraper.py --county Bloomington --election-id $BLOOM_ID
  echo "Bloomington updated at $(date)"
  sleep 900
done
```

Or use a combined script to run both.

## Comparison: McLean vs Cook County

Both are dual-authority counties:

| Aspect | McLean County | Cook County |
|--------|---------------|-------------|
| **Authorities** | 2 (Clerk + Bloomington) | 2 (Clerk + Chicago Board) |
| **Split** | ~65K / ~55K voters | ~2.4M / ~1.5M voters |
| **Platforms** | Text + Clarity | Excel + PDF |
| **Complexity** | ⭐⭐⭐ Medium-High | ⭐⭐⭐⭐ High |
| **Scrapers needed** | 2 (custom + Clarity) | 2 (both custom) |

McLean is simpler because Bloomington uses Clarity (existing scraper!).

## Why This System Exists

**Historical reasons:**
- Bloomington established election commission decades ago
- State statute allows certain cities to have own commissions
- Provides local control over city elections
- Common in Illinois' larger cities

**Practical impact:**
- Separate budgets and staff
- Different voting equipment/systems
- Separate result reporting
- But coordinated for state/federal races

## Advanced: Automated Combining

If you need automated combination:

```python
import json

def combine_mclean_results(clerk_file, bloomington_file):
    """Combine McLean County Clerk and Bloomington results"""
    
    with open(clerk_file) as f:
        clerk_data = json.load(f)
    
    with open(bloomington_file) as f:
        bloom_data = json.load(f)
    
    combined = {
        'county': 'McLean',
        'election_date': clerk_data['election_date'],
        'authorities': [
            {'name': 'McLean County Clerk', 'jurisdiction': 'County except Bloomington'},
            {'name': 'Bloomington Election Commission', 'jurisdiction': 'City of Bloomington'}
        ],
        'contests': []
    }
    
    # Combine contests by name
    contest_map = {}
    
    # Add clerk contests
    for contest in clerk_data.get('contests', []):
        contest_map[contest['name']] = {
            'name': contest['name'],
            'party': contest['party'],
            'candidates': {}
        }
        for cand in contest['candidates']:
            contest_map[contest['name']]['candidates'][cand['name']] = {
                'name': cand['name'],
                'clerk_votes': cand['votes'],
                'bloom_votes': 0,
                'total_votes': cand['votes']
            }
    
    # Add/merge Bloomington contests
    for contest in bloom_data.get('contests', []):
        if contest['name'] not in contest_map:
            # Bloomington-only contest
            contest_map[contest['name']] = {
                'name': contest['name'],
                'party': contest['party'],
                'candidates': {}
            }
        
        for cand in contest['candidates']:
            if cand['name'] in contest_map[contest['name']]['candidates']:
                # Add Bloomington votes to existing
                contest_map[contest['name']]['candidates'][cand['name']]['bloom_votes'] = cand['votes']
                contest_map[contest['name']]['candidates'][cand['name']]['total_votes'] += cand['votes']
            else:
                # Bloomington-only candidate
                contest_map[contest['name']]['candidates'][cand['name']] = {
                    'name': cand['name'],
                    'clerk_votes': 0,
                    'bloom_votes': cand['votes'],
                    'total_votes': cand['votes']
                }
    
    # Convert to list format
    for contest in contest_map.values():
        combined['contests'].append({
            'name': contest['name'],
            'party': contest['party'],
            'candidates': list(contest['candidates'].values())
        })
    
    return combined
```

## Support Contacts

### McLean County Clerk
- Website: mcleancountyil.gov
- Elections page: /231/Past-McLean-County-Election-Results
- Phone: Check website

### Bloomington Election Commission
- Website: results.enr.clarityelections.com/IL/Bloomington/
- Platform: Clarity Elections
- Phone: Check City of Bloomington website

## Summary - Quick Reference

**✅ To scrape complete McLean County:**

1. **McLean County Clerk portion:**
   - Find summary results URL at mcleancountyil.gov
   - Run: `python mclean_county_scraper.py --url [URL]`
   - Gets: ~65K voters (county except Bloomington)

2. **Bloomington portion:**
   - Find election ID at results.enr.clarityelections.com/IL/Bloomington/
   - Run: `python clarity_scraper.py --county Bloomington --election-id [ID]`
   - Gets: ~55K voters (City of Bloomington only)

3. **Combine:** Add vote totals from both for countywide races

**⚠️ Don't forget Step 2!** Without Bloomington, you're missing ~45% of McLean County voters!

McLean County requires extra work due to dual authority, but coverage is worth it - this is a significant bellwether county with ~120K voters!
