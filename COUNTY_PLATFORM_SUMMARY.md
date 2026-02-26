# County Platform Research Summary

## Clarity Elections Counties ✅ (Can use existing scraper)

These counties use the Clarity Elections platform and can be added easily:

1. **Will County** - https://results.enr.clarityelections.com/IL/Will
   - Status: Scraper built and ready
   - URL Pattern: results.enr.clarityelections.com

2. **McHenry County** - https://mchenry-il.connect4.clarityelections.com
   - Status: Ready to add
   - URL Pattern: connect4.clarityelections.com subdomain

3. **Lake County** - https://results.enr.clarityelections.com/IL/Lake
   - Status: Ready to add
   - URL Pattern: results.enr.clarityelections.com

4. **Kankakee County** - https://results.enr.clarityelections.com/IL/Kankakee
   - Status: Ready to add
   - URL Pattern: results.enr.clarityelections.com

5. **Winnebago County ⚠️ DUAL AUTHORITY - BOTH CLARITY**
   - **County Clerk** (county except Rockford): https://results.enr.clarityelections.com/WRC/Winnebago
   - **Rockford Board of Elections** (City of Rockford): https://results.enr.clarityelections.com/WRC/Rockford
   - Status: Ready to add - both use existing Clarity scraper
   - URL Pattern: results.enr.clarityelections.com (uses WRC instead of IL)
   - Note: TWO separate election authorities, but BOTH use Clarity. Need to scrape both URLs for complete county results.

---

## Other Platforms ⚠️ (Need custom scrapers)

### Cook County
- Platform: Custom PDF-based system
- URL: https://www.cookcountyclerkil.gov/elections/results
- Status: Needs custom scraper
- Note: Largest county in IL, but uses PDFs not structured data

### DuPage County
- Platform: Scytl
- URL: https://www.dupageresults.gov/IL/DuPage
- Status: Needs custom scraper
- Note: Uses Scytl platform (similar to Clarity but different API)

### Kane County
- Platform: Custom Kane County system
- URL: https://electionresults.kanecountyil.gov
- Status: Needs custom scraper
- Note: Custom-built system

### DeKalb, Kendall, and Henry Counties
- Platform: Integra Election Reporting Console  
- URLs:
  - DeKalb: http://dekalb.il.electionconsole.com
  - Kendall: http://kendall.il.electionconsole.com (also has https://results.co.kendall.il.us)
  - Henry: https://platinumelectionresults.com/reports/summary/76
- Status: Needs custom scraper (same scraper should work for all 3)
- Note: All appear on platinumelectionresults.com

### Peoria County
- Platform: Custom PDF/ArcGIS system
- URL: https://www.peoriaelections.gov/165/Election-Results
- Status: Needs custom scraper
- Note: Uses PDF documents and ArcGIS dashboards, has ElectionStats database

### McLean County ⚠️ DUAL AUTHORITY
- **County Clerk** (Normal + Rural): Custom text/PDF system
  - URL: https://www.mcleancountyil.gov/231/Past-McLean-County-Election-Results
  - Status: Needs custom scraper
- **Bloomington Election Commission** (City of Bloomington only): Clarity Elections
  - URL: https://results.enr.clarityelections.com/IL/Bloomington/
  - Status: Can use existing Clarity scraper
- Note: Unusual split jurisdiction - TWO separate election authorities in one county

### pollresults.net Counties (12 COUNTIES - ONE SCRAPER!)
- Platform: pollresults.net (Liberty Systems/CSE Software)
- URLs:
  - Whiteside: https://il-whiteside.pollresults.net
  - Lee: https://il-lee.pollresults.net
  - Ogle: https://il-ogle.pollresults.net
  - Carroll: https://il-carroll.pollresults.net
  - Putnam: https://il-putnam.pollresults.net
  - Vermilion: https://il-vermilion.pollresults.net (BOTH county clerk AND Danville Election Commission use this)
  - Tazewell: https://il-tazewell.pollresults.net
  - Stephenson: https://il-stephenson.pollresults.net
  - Boone: https://il-boone.pollresults.net
  - Bureau: https://il-bureau.pollresults.net
  - Livingston: https://il-livingston.pollresults.net
  - Ford: https://il-ford.pollresults.net
  - Mercer: https://il-mercer.pollresults.net
- Status: Needs custom scraper (but same scraper works for all 12)
- Note: Vermilion has dual authority (Danville Election Commission for city) but both use same pollresults.net URL

### Knox County Clerk, Grundy County, and Warren County
- Platform: GBS (Governmental Business Systems)
- URLs:
  - Knox County Clerk: https://results.gbsvote.com (county except Galesburg)
  - Grundy County: https://results.gbsvote.com
  - Warren County: https://results.gbsvote.com
- Status: Needs custom scraper (same scraper should work for all 3)
- Note: Knox also has Galesburg BEC with different platform (see Knox County dual authority section above)

### La Salle County
- Platform: Custom PDF system
- URL: https://www.lasallecountyil.gov/251/Election-Results
- Status: Needs custom scraper
- Note: Posts election results as PDF documents

### Jo Daviess County
- Platform: Custom web system
- URL: https://jodaviesscountyil.gov/departments/elections/election_results.php
- Status: Needs custom scraper
- Note: Custom web-based results reporting

### Woodford County
- Platform: Custom web system
- URL: https://woodfordcountyelections.com
- Status: Needs custom scraper
- Note: Custom web-based election results interface

### Stark County
- Platform: Custom PDF system
- URL: https://www.starkco.illinois.gov/elections/election-results
- Status: Needs custom scraper
- Note: Posts election results as PDF documents

### Iroquois County
- Platform: Custom web system
- URL: https://iroquoiscountyil.gov/elections
- Status: Needs custom scraper
- Note: Custom web-based results reporting

### Fulton County
- Platform: Custom PDF system
- URL: https://fultoncountyilelections.gov/election-results/
- Status: Needs custom scraper
- Note: Posts election results as PDF documents

### McDonough County
- Platform: Custom web system (Logonix)
- URL: https://www.mcdonoughelections.com
- Status: Needs custom scraper
- Note: Custom web-based election results system by Logonix Corporation

### Knox County ⚠️ DUAL AUTHORITY - MIXED PLATFORMS
- **Knox County Clerk** (county except Galesburg): GBS (Governmental Business Systems)
  - URL: https://results.gbsvote.com
  - Status: Needs custom scraper
- **Galesburg Board of Elections** (City of Galesburg only): Custom web/document center
  - URL: https://www.ci.galesburg.il.us (posts to document center)
  - Status: Needs custom scraper
- Note: Two separate platforms require two different scrapers

### Champaign County
- Platform: Custom web/document center
- URL: https://champaigncountyclerk.com/elections
- Status: Needs custom scraper
- Note: County Clerk is sole authority, posts results as PDFs/spreadsheets

### Rock Island County
- Platform: GEMS (Global Election Management System)
- URL: https://www.rockislandcountyil.gov/588/Current-Election-Results
- Status: Needs custom scraper
- Note: County Clerk posts results as PDFs and text files using GEMS

---

## Counties Still To Research (33 remaining)

**High Priority** (larger population):
- [ ] Winnebago
- [ ] Peoria
- [ ] McLean
- [ ] Champaign
- [ ] Sangamon (if needed for statewide races)

**Medium Priority**:
- [ ] Kendall, Ford, Iroquois, Livingston, Vermilion
- [ ] Boone, DeKalb, Bureau, La Salle, Putnam, Grundy
- [ ] Henry, Jo Daviess, Lee, Ogle, Stark, Stephenson
- [ ] Tazewell, Woodford, Carroll, Fulton, Knox
- [ ] McDonough, Mercer, Rock Island, Warren, Whiteside

---

## Next Steps

### Immediate (This Week):
1. **Research 5-10 more counties** to find additional Clarity Elections counties
2. **Test multi-county scraper** with the 4 Clarity counties we have

### Before Election Day:
1. **Build Clarity multi-county scraper** that handles all 4+ Clarity counties
2. **Decide on Cook/DuPage/Kane**: 
   - Option A: Skip them (focus on counties with easy access)
   - Option B: Build custom scrapers (more work but more complete data)
3. **Set up automated polling** every 15 minutes

### Election Day:
1. **Update all election_id and web_id values** in config.json
2. **Test scraper** with live data
3. **Monitor and fix** any issues

---

## Recommendation

**Focus on Clarity Elections counties first.** You have 4 confirmed counties using Clarity, and there are likely 5-10 more in your list. This gives you solid coverage without needing to build multiple custom scrapers.

Cook/DuPage/Kane represent large populations, but they'll require significant additional work. Decide if the extra coverage is worth the development time.
