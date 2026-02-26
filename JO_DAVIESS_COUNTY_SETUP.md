# Jo Daviess County Scraper Setup - Custom PHP Platform

This guide covers scraping election results for **Jo Daviess County** - one of the FINAL 2 counties!

## County Overview

**Jo Daviess County Statistics:**
- Population: ~22,000 residents
- Voters: ~15,000 registered voters
- County seat: Galena (historic tourism town)
- Location: Northwest corner of Illinois
- Borders: Wisconsin (north), Iowa (west), Mississippi River

**Historical Significance:** Home to Galena - historic 19th century river town and home of Ulysses S. Grant. Tourism-based economy with historic downtown. Beautiful bluffs and river valley. One of Illinois's most scenic counties. **This is one of the final 2 counties in the 38-county project!**

## Platform Overview

**System:** Custom PHP-based web system  
**Website:** jodaviesscountyil.gov  
**Results URL:** /departments/elections/election_results.php  
**Output Format:** HTML or PDF (unknown until election day)  
**Complexity:** ⭐⭐ Medium  
**Coverage:** All of Jo Daviess County

## Installation

```bash
pip install requests beautifulsoup4 pdfplumber
```

## Usage

### Finding Results

**Primary URL:**
```
https://jodaviesscountyil.gov/departments/elections/election_results.php
```

**Steps:**
1. Visit the URL above (or navigate from homepage)
2. Results may be displayed on page OR linked as document
3. Copy URL from address bar OR right-click document link
4. Run: `python jo_daviess_county_scraper.py --url "URL"`

### Examples

```bash
# With PHP results page
python jo_daviess_county_scraper.py --url "https://jodaviesscountyil.gov/departments/elections/election_results.php"

# With PDF document
python jo_daviess_county_scraper.py --url "https://jodaviesscountyil.gov/files/2026-primary.pdf"

# Test with 2024 data
python jo_daviess_county_scraper.py --url "URL" --date 2024-03-19

# Without URL (shows instructions)
python jo_daviess_county_scraper.py
```

## Testing with Historical Data

**RECOMMENDED before election day:**

1. Visit: jodaviesscountyil.gov/departments/elections/election_results.php
2. Find 2024 Primary or 2022 General results
3. Copy URL
4. Test: `python jo_daviess_county_scraper.py --url "URL" --date 2024-03-19`
5. Verify output looks correct

## Output Format

```json
{
  "county": "Jo Daviess",
  "election_date": "2026-03-17",
  "source": "Jo Daviess County Elections Website",
  "url": "...",
  "scraped_at": "2026-03-17T20:30:00",
  "metadata": {
    "registered_voters": 15000,
    "ballots_cast": 3800,
    "precincts_reporting": 22,
    "total_precincts": 22,
    "turnout_percent": 25.3
  },
  "contests": [
    {
      "name": "PRESIDENT - REPUBLICAN PARTY",
      "party": "Republican",
      "candidates": [
        {"name": "DONALD J. TRUMP", "votes": 2245, "percent": 84.2},
        {"name": "NIKKI HALEY", "votes": 421, "percent": 15.8}
      ]
    }
  ]
}
```

## Election Day Workflow

### Timeline

**7:00 PM** - Polls close

**7:30-9:00 PM** - First results likely posted
- Small county, quick tabulation
- Check election_results.php page
- Look for new documents or page updates

**Throughout evening** - Updates as precincts report

**Next day - 2 weeks** - Official canvassed results

### Monitoring

```bash
# Check every 15-30 minutes starting at 7:30 PM
# When results appear, run scraper:
python jo_daviess_county_scraper.py --url "RESULTS_URL"
```

## Troubleshooting

**URL Not Found:** Verify URL, check if results posted yet

**Empty Results:** Page structure may differ, check actual HTML

**PDF Fails:** Ensure pdfplumber installed

**Wrong Totals:** Verify comparing correct columns

## Why This County Matters

Despite being one of the smallest (~15K voters):
1. **Historic Galena** - Tourism town, Grant's home
2. **Geographic completion** - Northwest corner of Illinois
3. **Mississippi River** - Scenic bluffs and river valley
4. **Project milestone** - **Second-to-last county!**
5. **Full coverage** - With this + Stark = 100% complete!

## Galena Context

**Historic Tourism Town:**
- 85% of buildings on National Register
- Ulysses S. Grant lived here 1860-1861
- Major tourism destination (2+ million visitors/year)
- Mississippi River location
- Population: ~3,100 (largest in county)

**Electoral Impact:**
- Mix of retirees and tourism workers
- Some commuters to Dubuque, IA
- Rural townships outside Galena
- Typically Republican-leaning

## County Geography

**Precincts (~22):**
- Galena city precincts
- Elizabeth, Hanover (small towns)
- Rural township precincts
- Some may be combined

**Terrain:**
- Mississippi River bluffs
- Hilly, scenic (unlike flat Illinois)
- Agricultural valleys
- Historic river towns

## Integration with Project

### Regional Coverage

Jo Daviess completes northwest Illinois:
- **Stephenson County** (east) - ✅ Complete (pollresults.net)
- **Carroll County** (southeast) - ✅ Complete (pollresults.net)
- **Jo Daviess County** (northwest corner) - Custom scraper ← YOU ARE HERE

### Final Mile

**Project Status:**
- 36 of 38 counties complete before Jo Daviess
- Jo Daviess = **37 of 38**
- Only **Stark County** remains!
- This scraper brings project to **97% complete!**

## Summary - Quick Reference

**✅ To scrape Jo Daviess County:**

1. Visit: jodaviesscountyil.gov/departments/elections/election_results.php
2. Find: 2026 Primary results (on page or as link)
3. Copy URL
4. Run: `python jo_daviess_county_scraper.py --url [URL]`
5. Get: Clean JSON output

**🏛️ Historic Context:**
- Galena = Ulysses S. Grant's home
- 19th century river town
- Tourism economy
- Northwest corner of Illinois

**📍 County importance:**
- ~15K voters (0.25% of Illinois)
- Completes northwest region
- Historic significance
- **Second-to-last county = 97% complete!**

**🎯 Project milestone:**
- This + Stark = 100% coverage
- 38 of 38 counties complete
- Ready for March 2026 primary
- **Nearly there!**

Jo Daviess County brings the project to 97% completion - only Stark County remains!
