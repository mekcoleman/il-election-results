# Election Results Widget — Future Election To-Do List

A checklist of everything that needs to be updated or verified before each election.
Work through this list top to bottom, ideally 1–2 weeks before election day.

---

## 1. Google Doc Updates

- [ ] Update all race listings with current candidates for each market
- [ ] Update multi-county district lists for all regional superintendent races
  - Confirm which counties are included for each superintendent jurisdiction
  - Verify county lists haven't changed due to redistricting or administrative changes
- [ ] Update judicial races (vacancies change each election)
- [ ] Update referendum questions (these are unique to each election)
- [ ] Verify incumbents — confirm (i) designations are current
- [ ] Remove any candidates who withdrew or were ruled off the ballot

---

## 2. Widget Updates (one per market)

For each of the 11 widgets, update the following:

### Candidate lists (`PENDING_CANDIDATES`)
- [ ] Replace all candidate names with current election's candidates
- [ ] Update incumbent (i) designations
- [ ] Add/remove party blocks as needed (e.g., if a race goes from contested to uncontested)
- [ ] Update referendum Yes/No entries — add any new referendums, remove old ones

### Race definitions (`RACE_DEFINITIONS`)
- [ ] Update race labels to match current contest names
- [ ] Update regex match patterns if contest naming convention changed
- [ ] Add new races (new judgeships, new referendums, new offices)
- [ ] Remove races that are no longer on the ballot
- [ ] Update multi-county notes for races that span counties

### Export text (`exportResults`)
- [ ] Update the opening paragraph for each widget:
  - Change "this week" to "last week" if publishing after election week
  - Confirm county name(s) in the opener are correct
  - Adjust "counties, state and country" vs "communities, schools, townships..." depending on race types
- [ ] Update the export filename (e.g., `dupage_primary_results_march_2026.txt`)

### Header
- [ ] Update the election date in the widget header (currently "March 17, 2026")
- [ ] Update the official results link in the footer for each county

---

## 3. Scraper / Config Updates

- [ ] **Clarity counties** (Will, McHenry, Kankakee, Winnebago) — find live election IDs on election morning
  - Visit each county's Clarity URL, find the current election, extract `election_id` and `web_id`
  - Update `config.json` before 7pm
- [ ] **DuPage** (Scytl) — find and update election ID in `config.json`
- [ ] **La Salle** — find PDF document ID from lasallecountyil.gov on election night, update `config.json`
- [ ] **Marshall** — find results URL from marshallcountyil.gov on election night, pass via `--url` flag
- [ ] **Jo Daviess** — find results URL, pass via `--url` flag
- [ ] **Iroquois** — find results URL, pass via `--url` flag
- [ ] **Stark** — find results PDF URL, pass via `--url` flag
- [ ] Verify all pollresults.net counties are still on the same platform
- [ ] Verify Integra counties (DeKalb, Kendall, Henry) are still on the same platform
- [ ] Check if any counties have switched election platforms since last election

---

## 4. Aggregator Updates

- [ ] Update `2026_races.xlsx` with current congressional, state senate and state house district mappings if redistricting occurred
- [ ] Verify superintendent race county lists in `aggregate_results.py` match the Google Doc
- [ ] Update the election date string in aggregator output (`2026-03-17`)

---

## 5. Conductor Updates (`run_election_night.py`)

- [ ] Verify all scraper filenames in `SCRAPERS` list still match actual filenames
- [ ] Add any new county scrapers built since last election
- [ ] Update `RESULTS_DIR` if directory structure changed
- [ ] Test with `--once --no-push` the morning of the election to catch any failures early

---

## 6. GitHub / Deployment

- [ ] Confirm GitHub Pages is still enabled on `mekcoleman/il-election-results`
- [ ] Confirm `statewide_results.json` is accessible at `https://mekcoleman.github.io/il-election-results/statewide_results.json`
- [ ] Test widget fetch by pushing a sample JSON and confirming the widget goes live
- [ ] Verify all 11 widget files are embedded correctly in the CMS

---

## 7. Election Night

- [ ] Update Clarity election IDs in `config.json` by 6:30pm
- [ ] Update La Salle PDF doc ID in `config.json` as soon as results are posted
- [ ] Note Jo Daviess, Iroquois, Stark and Marshall results URLs as they go live
- [ ] Start conductor at 7pm: `python run_election_night.py`
- [ ] Monitor `election_night.log` for scraper failures
- [ ] Stop conductor when all results are final (typically midnight or next morning)

---

## 8. Post-Election

- [ ] Export text files from all 11 widgets for story use
- [ ] Archive `statewide_results.json` and all county JSONs with election date in filename
- [ ] Note any scraper failures or platform changes for next election
- [ ] Update this to-do list with any new items discovered during this election

---

*Last updated for March 17, 2026 Illinois Primary*
