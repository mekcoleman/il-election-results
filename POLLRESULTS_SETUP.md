# pollresults.net Scraper Setup Guide

## Overview

The pollresults.net scraper covers **12 Illinois counties** with a single unified scraper:
- Whiteside, Lee, Ogle, Carroll, Putnam
- Vermilion, Tazewell, Stephenson, Boone
- Bureau, Livingston, Ford, Mercer

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - For HTTP requests
- `selenium` - For JavaScript-rendered content
- `beautifulsoup4` - For HTML parsing
- `webdriver-manager` - For automatic ChromeDriver management

### 2. Install Chrome/Chromium

The scraper uses Selenium with Chrome in headless mode.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver
```

**macOS:**
```bash
brew install --cask google-chrome
```

**Windows:**
Download and install Chrome from https://www.google.com/chrome/

### 3. Verify ChromeDriver

```bash
python -c "from selenium import webdriver; webdriver.Chrome()"
```

If this runs without error, you're ready!

## Usage

### Scrape All 12 Counties

```bash
python pollresults_scraper.py
```

This will:
1. Loop through all 12 pollresults.net counties
2. Attempt JSON API access first (fastest)
3. Fall back to Selenium scraping if needed
4. Save results to `{county}_results.json`

### Scrape Specific County

```bash
python pollresults_scraper.py Whiteside
python pollresults_scraper.py Tazewell
python pollresults_scraper.py Livingston
```

### Python API

```python
from pollresults_scraper import scrape_pollresults_county, scrape_all_pollresults_counties

# Scrape one county
results = scrape_pollresults_county("Whiteside")

# Scrape all pollresults counties
all_results = scrape_all_pollresults_counties()
```

## How It Works

### Two-Stage Scraping Strategy

1. **JSON API Detection (Fast)**
   - Tries common JSON endpoint patterns
   - If successful, parses structured data directly
   - Much faster and more reliable

2. **Selenium Fallback (Robust)**
   - Uses headless Chrome to render JavaScript
   - Waits for Angular app to load
   - Extracts data from rendered HTML
   - More robust but slower

### Party Detection

The scraper automatically detects party affiliation from contest names:
- "Democratic Primary" → Democratic
- "Republican Primary" → Republican  
- Other contests → Non-Partisan

## Output Format

Results saved to `{county}_results.json`:

```json
{
  "county": "Whiteside",
  "scrape_time": "2026-03-17T20:15:30",
  "election_type": "Primary",
  "total_contests": 47,
  "contests_by_party": {
    "Democratic": [...],
    "Republican": [...],
    "Non-Partisan": [...]
  },
  "summary": {
    "democratic_contests": 15,
    "republican_contests": 18,
    "non_partisan_contests": 14
  }
}
```

## Troubleshooting

### Selenium Not Working

**Error:** `WebDriverException: 'chromedriver' executable needs to be in PATH`

**Fix:** Install ChromeDriver:
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# Or use webdriver-manager (already in requirements.txt)
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

### Page Load Timeout

**Error:** `TimeoutException: Message: timeout`

**Fix:** The wait time might need adjustment for slow connections. Edit `pollresults_scraper.py`:

```python
# Change this line (around line 100):
WebDriverWait(self.driver, 20).until(...)

# To a longer timeout:
WebDriverWait(self.driver, 60).until(...)
```

### No Results Found

**Issue:** Scraper completes but finds no contests

**Debugging:**
1. Check if the website structure changed
2. Run with visible browser (remove headless mode):
   ```python
   # Comment out this line in init_selenium():
   # options.add_argument('--headless')
   ```
3. Take a screenshot for debugging:
   ```python
   self.driver.save_screenshot('debug.png')
   ```

## Platform Notes

### pollresults.net Characteristics

- **Vendor:** Liberty Systems / CSE Software
- **Technology:** AngularJS-based single-page application
- **Data Loading:** JavaScript renders results dynamically
- **URL Pattern:** `https://il-{county}.pollresults.net/`
- **Common Issue:** No static HTML, requires JavaScript execution

### Why Selenium?

Unlike Clarity Elections which has a clean JSON API, pollresults.net uses an Angular app that:
1. Loads election data via AJAX after page load
2. Renders HTML with Angular templates
3. Does not expose a documented public API

Selenium allows us to:
- Wait for JavaScript to execute
- Wait for Angular to render
- Extract data from the fully-rendered page

## Performance

### Speed Comparison

- **JSON API (if available):** ~1-2 seconds per county
- **Selenium scraping:** ~5-10 seconds per county
- **All 12 counties:** ~1-2 minutes total

### Optimization Tips

1. **Run in parallel** (if scraping many counties):
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=4) as executor:
       results = executor.map(scrape_pollresults_county, county_list)
   ```

2. **Reuse WebDriver** (not currently implemented):
   - Keep one driver instance across counties
   - Saves ~2-3 seconds per county

3. **Check for JSON API first:**
   - The scraper already does this
   - Much faster if available

## Election Day Checklist

✅ Verify all URLs in config.json are correct
✅ Test scraper on one county first
✅ Check that Chrome/ChromeDriver is installed
✅ Run full scrape: `python pollresults_scraper.py`
✅ Verify JSON output files are created
✅ Check that party detection is working correctly

## Need Help?

If the scraper isn't working:
1. Check website is accessible: `curl https://il-whiteside.pollresults.net/`
2. Verify Chrome: `which chromium-browser` or `which google-chrome`
3. Test Selenium: `python -c "from selenium import webdriver; print('OK')"`
4. Enable debug mode (remove `--headless` option)
5. Check for website changes (inspect page source)
