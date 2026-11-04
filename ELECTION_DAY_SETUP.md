# Election Day Setup Guide
## November 2026 General Election

---

## The Core Problem: web_ids Change Every Election

Clarity Elections assigns a new **web_id** for every election. The old web_id stops receiving updates — so if you use a stale web_id, your scraper will pull old or partial results even though the live site shows full results.

**This is the #1 thing to fix before going live on election night.**

---

## Step 0: Two to Three Weeks Out — Check Every County Results Site

County websites get redesigned or moved between elections, and a scraper pointed at a dead address fails quietly. It keeps publishing old or empty results. In April 2026, Jo Daviess relaunched its site and every saved link returned a 404. Nov. 3, 2026 also turned up stale addresses for DuPage, Winnebago and Chicago.

- [ ] **Check for a redesign or move.** Open each county's results page and confirm the URL in its scraper or `config.json` still loads. Watch for sites relaunched on a new platform (e.g. CivicEngage), new PDF document IDs, and pages that now link to a vendor (Clarity, Scytl, Platinum, pollresults.net).
- [ ] **Confirm the platform.** pollresults.net hosts only Bond, Boone, Bureau, Carroll, Christian, Clark, Coles, DeWitt, Douglas, Edgar, Ford, Lee, Livingston, Logan, Macon, Mason, Moultrie, Ogle, Piatt, Putnam, Shelby, Stephenson, Tazewell, Vermilion and Whiteside. Any other `il-<county>.pollresults.net` address redirects to /Error/NotFound and returns nothing.
- [ ] **Platinum counties (DeKalb, Henry):** compare the category links on the results page with `CATEGORIES` in `dekalb_county_scraper.py`. Henry reuses the DeKalb parser, so test both after any change.
- [ ] **No hard-coded data versions.** Every Clarity/Scytl scraper (including DuPage and Winnebago) must read `current_ver.txt` on each run.
- [ ] **Per-election PDF addresses:** La Salle (`config.json` → `doc_id`, from the county's Election Results page) and Jo Daviess (`PDF_URL` in `jo_daviess_county_scraper.py`, from `jodaviesscountyil.gov/1380/Election-Results`).
- [ ] **Every needed county is in `run_all_scrapers.sh`.** DuPage, La Salle and Jo Daviess weren't running automatically on Nov. 3, 2026.
- [ ] **Test run, then check freshness.** List `scraped_at` and total votes for every file in `county_results/`. Anything stale, or empty on a site that has test data, needs fixing before election night.

Details for each of these are in `CLAUDE.md` ("Election Night Widget Ops — Lessons Learned", #11–#15).

---

## Step 1: Find the Current web_id for Each Clarity County

Do this for **Will, McHenry, Kankakee, and DuPage** on election night.

1. Open the county's results page in Chrome
2. Open DevTools → Network tab (Cmd+Option+I → Network)
3. Refresh the page
4. Filter for `.json` in the search box
5. Look for a URL like:
   ```
   https://results.enr.clarityelections.com/IL/Will/126051/369273/json/en/summary.json
   ```
6. The **6-digit number after the election_id** is the web_id — in this example, `369273`

The election_id (first number) usually stays the same within an election cycle. The web_id changes as Clarity publishes updates.

**Lesson from March 2026:** McHenry's config had web_id `369018` but the live site was using `369273`. The scraper was pulling 457 votes for a candidate when the correct total was 1,234.

---

## Step 2: Update config.json

Use this command to update all Clarity web_ids at once — don't try to edit the file manually (saves don't always stick):

```bash
python3 -c "
import json
with open('config.json') as f:
    d = json.load(f)
d['counties']['Will']['web_id']     = 'REPLACE'
d['counties']['McHenry']['web_id']  = 'REPLACE'
d['counties']['Kankakee']['web_id'] = 'REPLACE'
d['counties']['DuPage']['web_id']   = 'REPLACE'
with open('config.json', 'w') as f:
    json.dump(d, f, indent=2)
print('Saved.')
for c in ['Will','McHenry','Kankakee','DuPage']:
    print(c, d['counties'][c]['web_id'])
"
```

Replace each `'REPLACE'` with the web_id you found in Step 1.

Also update election_ids if they changed (same Network tab process — it's the first number in the URL path).

---

## Step 3: Update Cook County Clerk URL

Cook County Clerk uses a different results server for each election. The server name encodes the election date:
- November 2024: `results1124.cookcountyclerkil.gov`
- March 2026: `results326.cookcountyclerkil.gov`
- **November 2026: will likely be `results1126.cookcountyclerkil.gov`**

Check by visiting `https://results1126.cookcountyclerkil.gov` on election night. If it's live, update lines 43-44 in `cook_county_scraper.py`:

```python
LIVE_EXCEL_URL = 'https://results1126.cookcountyclerkil.gov/Home/SummaryExport'
LIVE_RESULTS_SITE = 'https://results1126.cookcountyclerkil.gov/'
```

---

## Step 4: Verify config saved correctly

```bash
python3 -c "
import json
with open('config.json') as f:
    d = json.load(f)
for county in ['Will', 'McHenry', 'Kankakee', 'DuPage']:
    cfg = d['counties'][county]
    print(f'{county}: election_id={cfg[\"election_id\"]} web_id={cfg[\"web_id\"]}')
"
```

---

## Step 5: Set your GitHub token

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Verify:
```bash
echo $GITHUB_TOKEN
```

---

## Step 6: Test run before polls close

Run once without pushing to catch any scraper failures:

```bash
python3 run_election_night.py --once --no-push
```

Look for counties showing `0 contests` — those need their web_ids fixed. Any county logging `0 contests` with a Clarity platform is a stale web_id.

---

## Step 7: Start the loop at 7pm

```bash
python3 run_election_night.py
```

This runs every 10 minutes automatically. Results push to GitHub Pages after each cycle. Press Ctrl+C to stop.

---

## Troubleshooting

**County shows 0 contests**
- For Clarity counties: stale web_id. Find the current one via DevTools Network tab.
- For pollresults.net counties: URL may have changed. Check `https://il-[county].pollresults.net`.
- For Kendall: URL is `https://results.co.kendall.il.us/` — check it's still live.

**Candidate vote totals look wrong (too low)**
- Almost always a stale web_id. The old web_id returns partial results.
- Cross-check against the county's official results page.

**Superintendent races incomplete**
- Each county must be scraped and its results present in `county_results/` before the aggregator can include it.
- Check `statewide_results.json` → `multi_county_races` → `regional_superintendents` → `[race_id]` → `counties_missing` to see what's still needed.

**push_to_github.py fails**
- Check `GITHUB_TOKEN` is set: `echo $GITHUB_TOKEN`
- Token may have expired — generate a new one at https://github.com/settings/tokens/new (scope: `repo`)

**GBS Vote scraper (Grundy) can't find election**
- Visit `https://results.gbsvote.com`, click Grundy County, find the November 2026 election link
- Note the `e_id` from the URL
- Run: `python3 gbs_scraper.py --county Grundy --election-id [e_id] --output ./county_results`

---

## Pre-Election Pipeline Validation

**Run this before polls close** to catch naming-format gaps in the aggregator before they become election-night holes.

```bash
cd /path/to/il_election_scraper
python3 validate_aggregator.py --statewide
```

This script checks every Congressional, State Senate, and State House district in `2026_races.xlsx` against the actual contest names in every `county_results/*.json` file, then cross-references the live `statewide_results.json` to show which districts are missing.

**When to run it:**
1. After all county JSON files are in place but before the first scraper loop goes live (day before election)
2. Any time you add a new county scraper — a new naming format may require a pattern fix in `aggregate_results.py`

**How to fix a gap:** If the validator flags a district, check the county JSON file for the actual contest name, then add a matching pattern to `_aggregate_state_senate()` or `_aggregate_state_house()` in `aggregate_results.py`. The `_district_re()` function now generates both numeric (`38th`) and alphabetic (`thirty-eighth`) ordinals, so most formats should match automatically.

**Note:** Gaps for Cook County, Champaign, McLean, and downstate counties outside Shaw's market are expected — those naming formats differ and the districts don't appear in Shaw's widgets anyway. Only worry about gaps in your market's counties.

---

## Cross-County Race Verification Checklist

After aggregating, verify these totals match official sources:

| Race | Counties | Check against |
|---|---|---|
| KCC — Kane Superintendent | Kane, McHenry, DeKalb, DuPage, Cook | Kane County official results |
| MHN/KCN — Grundy/Kendall Superintendent | Grundy, Kendall, Will, Kane | Grundy County official results |
| JHN — Will Superintendent | Will, Kendall, Kankakee | Will County official results |
| NWH — McHenry Superintendent | McHenry, Boone, Kane | McHenry County official results |

**Quick check command:**
```bash
python3 -c "
import json
with open('statewide_results.json') as f:
    d = json.load(f)
supts = d['multi_county_races']['regional_superintendents']
for race_id, race in supts.items():
    status = 'COMPLETE' if race.get('complete') else f'PARTIAL ({len(race.get(\"counties_found\",[]))}/{len(race.get(\"counties_needed\",[]))})'
    print(f'{race_id}: {status}')
    for c in (race.get('candidates') or []):
        print(f'  {c[\"name\"]}: {c[\"votes\"]}')
"
```

---

## Lessons Learned — March 2026 Primary

### County Results Files

**Some counties delete results after certification and replace the page with a canvas image or static graphic.** The GBS Vote scraper for Grundy hit this after results were finalized — the scraper returned nothing and the widget showed no data. The fix is to create a static `grundy_results.json` by hand with the final certified results and push it as the permanent file. Do this for any county whose results page goes dark post-election.

**File naming:** County result files are named `{county}_results.json` (e.g. `grundy_results.json`, `will_results.json`). The push script maps these to `county_{slug}.json` on GitHub Pages via `FILENAME_SLUG_MAP` in `push_to_github.py`. Any new county file needs an entry in that map or it won't be pushed.

**The aggregator reads from `county_results/` directly** — it does not read from GitHub Pages. So putting a hand-built file in `county_results/` is all you need before running the aggregator.

---

### Aggregator — Cross-County Race Matching

**Each county names superintendent races differently.** The aggregator's `match` regex for each superintendent race must cover all county naming variants or counties will be silently dropped. After March 2026, the confirmed naming variants for `mhn_grundy_kendall` are:

| County | Contest name in results file |
|---|---|
| Grundy | `REGIONAL SUPERINTENDENT OF SCHOOLS FOR GRUNDY AND KENDALL COUNTIES` |
| Kendall | `ESR-GRUNDY KENDALL EGK` |
| Will | `FOR REGIONAL SUPERINTENDENT OF SCHOOLS  (GRUNDY AND KENDALL COUNTIES)` |
| Kane | `GRUNDY & KENDALL COUNTIES FOR REGIONAL SUPERINTENDENT OF SCHOOLS - REP` |

The fix applied in `aggregate_results.py`:
```python
"match": re.compile(r"ESR-GRUNDY KENDALL|grundy.{0,10}kendall.{0,50}superintendent|superintendent.{0,50}grundy.{0,10}kendall", re.I),
```

**Check all superintendent race matches before election night** by running the aggregator dry and inspecting `counties_found` / `counties_missing` for each race. The quick check command is in the section above.

**State Senate / State House district naming varies by county.** Some counties (Grundy, Jo Daviess) use fully spelled-out ordinals in contest names (`STATE SENATOR - THIRTY-EIGHTH LEGISLATIVE DISTRICT`); others use numeric ordinals (`STATE SENATE 38TH DISTRICT`); DuPage uses `FOR STATE SENATOR FORTY-FIRST LEGISLATIVE DISTRICT`. The `_district_re()` function in `aggregate_results.py` was updated in November 2026 to generate both numeric and alphabetic ordinals (e.g. `(?:38(?:rd)?|thirty-eighth)`) so all formats match. If a district is missing from `statewide_results.json`, run `validate_aggregator.py` to find the unmatched contest name, then add a pattern to `_aggregate_state_senate()` or `_aggregate_state_house()`. The two patterns most likely to be missing are `state senate.*{d_re}` (Grundy/Bureau short format) and `general assembly.*{d_re}` (DuPage house format).

**Candidate bleed-between-races:** Will County's results file includes superintendent contests for every district in the county, including ones that don't belong to Will (e.g. Grundy/Kendall). If the aggregator match regex is too broad (e.g. just `regional superintendent`), a candidate from an unrelated district bleeds into the wrong race. Make sure every superintendent race has a specific match pattern that only catches that district's naming variants.

**Aggregated candidates originally had no `party` field.** The aggregator's `_merge_contests` function originally stored candidates without a `party` field, causing all superintendent and appellate candidates to fall through to Non-Partisan in the widget. This was fixed in March 2026 — `_merge_contests` now stamps `party` on each candidate using the contest's bucket party (`bucket_party` passed through `appearances`), with a fallback that strips `(DEM)`/`(REP)` name suffixes. If you ever see aggregated candidates showing as Non-Partisan, check that `_merge_contests` is receiving `bucket_party` in the appearances list.

**Will County includes ALL superintendent districts in its results file**, not just its own. This causes candidate bleed — e.g. Theresa Rouse (Will superintendent) appearing in the Grundy/Kendall race because the match regex was too broad. Two defenses: (1) use specific match patterns per race, and (2) ensure `_merge_contests` uses `bucket_party` from the contest's party bucket.

**Quote variants cause candidate name merging failures.** Different counties format the same name with different quote characters — e.g. `MARGARET 'PEGGY' O'CONNELL` (curly apostrophe) vs `MARGARET "PEGGY" O'CONNELL (DEM)` (straight quotes). The `_normalize_candidate_name` function must strip all quote variants before comparing, or the same candidate appears twice with split vote totals. This fix was applied to `aggregate_results.py` in March 2026.

**The 3rd Appellate District race requires a dedicated `_aggregate_appellate` method.** It is not a superintendent race and is not wired up by default. The method was added in March 2026 and writes to `multi_county_races.third_appellate` in `statewide_results.json`. The relevant counties are DuPage, Will, Bureau, Grundy, Iroquois, Kankakee, and La Salle. The match pattern is `appellate court.*third|third.*judicial.*district|3rd appellate`. If this key is missing, the widget falls back to pending candidates with empty bars. Check with:
```bash
python3 -c "
import json
with open('statewide_results.json') as f:
    d = json.load(f)
app = d['multi_county_races'].get('third_appellate')
print('third_appellate:', 'FOUND' if app else 'MISSING')
if app:
    print('Counties found:', app.get('counties_found'))
    for c in app.get('candidates', []):
        print(f'  {c["name"]}: {c["votes"]} party={c.get("party","MISSING")}')
"
```

**Verify party fields on all aggregated candidates before pushing:**
```bash
python3 -c "
import json
with open('statewide_results.json') as f:
    d = json.load(f)
mc = d.get('multi_county_races', {})
for race_id, race in mc.get('regional_superintendents', {}).items():
    for c in race.get('candidates', []):
        if not c.get('party'):
            print(f'MISSING PARTY: {race_id} — {c["name"]}')
for key in ['third_appellate']:
    for c in mc.get(key, {}).get('candidates', []):
        if not c.get('party'):
            print(f'MISSING PARTY: {key} — {c["name"]}')
print('Party check complete')
"
```

---

### Widget Issues

**The `aggregate_results.py --no-push` flag does not exist.** To do a dry run without pushing, simply omit `--push`:
```bash
python3 aggregate_results.py --results-dir ./county_results
```

**Three scraper output shapes exist.** `normalizeContests()` in the widgets handles all three, but inject functions (`injectSuptRace`, `injectMultiCountyRace`, `injectCrossCountyRefs`) must also handle all three or they crash silently:
- `{ by_party: { Democratic: { contests: [] } } }` — Will scraper
- `{ contests_by_party: { Democratic: { contests: [] } } }` — Clarity / pollresults
- `{ contests: [ {name, party, candidates} ] }` — DuPage / Kane / Integra

The updated inject functions using the shared `injectIntoData()` helper handle all three shapes. Use those — do not revert to shape-specific branching.

**Multi-seat winner bolding:** The original `renderCandidateRow` only bolded the single candidate with the most votes, even in "Vote for 3" races. The fix passes `seats` through `renderPartyBlock` → `renderCandidateRow` and ranks candidates by vote total, bolding the top N. Make sure `race.seats` is set correctly in `RACE_DEFINITIONS` for every multi-seat race.

**Apostrophes in candidate names break JavaScript.** Names like `O'Brien` and `O'Connell` inside single-quoted JS strings cause a `SyntaxError` that silently kills the entire script — the widget shows a permanent loading spinner with no error message visible unless you check the browser console. The fix is to use double-quoted strings for any name containing an apostrophe:
```javascript
// WRONG — breaks JS
{ name: 'Erin O'Brien', votes: 0 }

// CORRECT
{ name: "Erin O'Brien", votes: 0 }
```

**Always check the browser console first when a widget is stuck loading.** The page's ad network produces hundreds of lines of noise — look for `Uncaught SyntaxError` at the very top of the console output, which will name the unexpected identifier (e.g. `Brien`, `Connell`). That identifies the broken name instantly.

**`renderPending()` runs but can be immediately overwritten.** The boot sequence calls `renderPending()` then immediately calls `refresh()`. If `refresh()` fails (e.g. 404 on the JSON file), the original code left the spinner up rather than restoring pending candidates. The null result path in `refresh()` should always call `renderSections()` to show pending candidates:
```javascript
if (!result) {
  badge.textContent = 'Results Pending';
  badge.className   = 'badge';
  const sections = buildSections({ Democratic: [], Republican: [], 'Non-Partisan': [] });
  root.innerHTML = renderSections(sections);
  return;
}
```

---

### Building New Market Widgets

When creating a widget for a new market by copying an existing one, audit these items in order:

1. `MARKET`, `COUNTY`, `COUNTY_SLUG`, `SUPT_RACE_ID` config constants
2. `RACE_DEFINITIONS` — all sections, races, match regexes, and `seats` values
3. `PENDING_CANDIDATES` — all candidate names; switch any name containing an apostrophe to a double-quoted string
4. `CROSS_COUNTY_REF_IDS` — add any cross-county referendum IDs relevant to this market
5. `injectSuptRace` label string — must match the contest name the widget will render
6. Export preamble text and filenames
7. Footer official results link
8. Fetch source — confirm whether this market reads from `statewide_results.json` (county data inside `county_results[COUNTY]`) or split files (`county_{slug}.json` + `statewide_meta.json`)

**County contest names for judicial races vary as much as superintendent races.** Will County's naming for the March 2026 primary:

| Race | Will County contest name |
|---|---|
| 3rd Appellate | `FOR JUDGE OF THE APPELLATE COURT THIRD JUDICIAL DISTRICT (To fill the vacancy of the Hon. Mary W. McDade)` |
| 12th Circuit 1st Subcircuit | `FOR JUDGE OF THE CIRCUIT COURT 12TH JUDICIAL CIRCUIT 1ST SUBCIRCUIT (To fill the vacancy of the Hon. David M. Carlson)` |
| 12th Circuit 3rd Subcircuit | `FOR JUDGE OF THE CIRCUIT COURT 12TH JUDICIAL CIRCUIT 3RD SUBCIRCUIT (To fill the vacancy of the Hon. John C. Anderson)` |
| 12th Circuit 5th Subcircuit | `FOR JUDGE OF THE CIRCUIT COURT 12TH JUDICIAL CIRCUIT 5TH SUBCIRCUIT (To fill the vacancy of the Hon. Barbara N. Petrungaro)` |

The widget regexes that match these are `appellate court.*third|third.*judicial.*district` and `12th.*1st sub|12th.*carlson` etc. These vacancy names will change each election — update the regexes if judges change.

**Scraped candidate names often differ from ballot filings** in middle initials, hyphenation, and spacing. Always verify `PENDING_CANDIDATES` names against the actual scraped output after the first results come in and update to match. March 2026 examples from Will County:

| Filed name | Scraped name |
|---|---|
| `Katie Deanne Schottman` | `KATIE DEANE-SCHLOTTMAN` |
| `Stephen Balich` | `STEPHEN J. BALICH` |
| `James Richmond` | `JAMES M. RICHMOND` |
| `David Oxley` | `DAVID G. OXLEY` |
| `Mark V. Reavis` | `MARK V. REVIS` |
| `Jim Reilly` | `JAMES 'JIM' REILLY` |
| `John Paul Ivec` | `JOHNPAUL IVEC` |
| `Jacqueline L. Traynere` | `JACQUELINE L TRAYNERE` |
| `Pawel J. Tyrala` | `PAWEL J TYRALA` |

Run a syntax check before publishing. A quick way to catch apostrophe issues:
```bash
python3 -c "
import re
with open('your_widget.html') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if re.search(r\"name: '[^']*[a-z]'[A-Za-z]\", line):
        print(f'Line {i}: {line.strip()[:100]}')
print('Done')
"
```
