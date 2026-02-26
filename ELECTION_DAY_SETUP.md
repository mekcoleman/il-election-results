# Election Day Setup Guide

## Quick Start - Election Day Morning

### Step 1: Find the Live Results URL
On election day (March 17, 2026), visit your county's website and find the live results link. 

For **Will County**, it will likely be at:
- https://www.willcountyclerk.gov/elections/
- Look for "Live Election Results" or "Real-Time Results"

### Step 2: Extract URL Components
The Clarity Elections URL will look like:
```
https://results.enr.clarityelections.com/IL/Will/123535/357754/Web02/en/summary.html
```

Extract these parts:
- **base_url**: `https://results.enr.clarityelections.com/IL/Will`
- **election_id**: `123535` (the first number after county name)
- **web_id**: `357754` (the second number)

### Step 3: Update config.json
Open `config.json` and update the Will County section:

```json
"Will": {
  "platform": "clarity",
  "base_url": "https://results.enr.clarityelections.com/IL/Will",
  "election_id": "123535",  ← UPDATE THIS
  "web_id": "357754",        ← UPDATE THIS
  "status": "configured"
}
```

### Step 4: Test the Scraper
Run a quick test:
```bash
python will_county_scraper.py
```

You should see output like:
```
Scraping Will County election results...
Election: March 17, 2026 Illinois Primary
Found 47 contests
Saved 47 contests to will_county_results.json
  - Democratic: 15
  - Republican: 18
  - Non-Partisan: 14
```

### Step 5: Check the Results
Open `will_county_results.json` to verify the data looks correct.

Results are automatically organized by party:
- **Democratic** - Democratic primary races
- **Republican** - Republican primary races  
- **Non-Partisan** - Referenda, local races, judicial races

---

## Finding URLs for Other Counties

For each county in your list, on election day:

1. **Search**: `[County Name] Illinois election results 2026`
2. **Look for**: Official county clerk/board of elections website
3. **Identify platform**: 
   - If URL contains `clarityelections.com` → Clarity Elections (use same scraper structure)
   - If different → Note the platform type, we'll build a scraper for it

4. **Update config.json** with the URLs

---

## Primary Election Data Structure

The scraper automatically categorizes races by party type:

### Democratic Contests
- Identified by: "Democratic" in race name, or all candidates marked DEM
- Examples: "US Representative District 14 - Democratic", "Governor - Democratic Primary"

### Republican Contests  
- Identified by: "Republican" in race name, or all candidates marked REP
- Examples: "US Senator - Republican", "State Representative - Republican Primary"

### Non-Partisan Contests
- Everything else: referenda, judicial races, some local offices
- Examples: "Referendum Question 1", "Circuit Court Judge", "School Board"

---

## Troubleshooting

**Problem**: Script says "URLs not yet configured"
- **Solution**: Update `election_id` and `web_id` in config.json

**Problem**: Can't find the election results URL
- **Solution**: Results might not be live yet. County websites usually post them by 7pm on election day

**Problem**: Getting 404 errors
- **Solution**: Double-check the election_id and web_id numbers. They change for each election.

**Problem**: Party categorization looks wrong
- **Solution**: Check the `detect_contest_party()` function in the scraper. May need to adjust logic.

---

## Next Steps After Will County Works

Once Will County is working:
1. Identify which other counties use Clarity Elections (they'll be easiest to add)
2. Find URLs for 5-10 additional counties
3. Update config.json with their details
4. Run multi-county scraper
5. Set up automated polling every 15 minutes
