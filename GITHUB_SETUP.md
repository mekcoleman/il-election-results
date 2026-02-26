# GitHub Auto-Push Setup Guide

This guide gets your scrapers automatically pushing results to GitHub Pages
so your election widgets update live on election night — no manual steps needed.

**Time to complete: ~20 minutes**

---

## Step 1: Create a GitHub Account

If you don't have one: https://github.com/signup

---

## Step 2: Create a New Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `il-election-results` (or whatever you prefer)
   - **Visibility:** Public ✅ (required for free GitHub Pages)
   - **Add a README:** ✅ check this box
3. Click **Create repository**

---

## Step 3: Install Git on Your Laptop

**Mac:**
```bash
# Check if you already have it
git --version

# If not installed, this will prompt you to install it
xcode-select --install
```

**Windows:**
Download and install from: https://git-scm.com/download/win
(Use all the default settings during install)

---

## Step 4: Clone the Repo to Your Laptop

Open Terminal (Mac) or Git Bash (Windows) and run:

```bash
# Replace YOUR-USERNAME with your GitHub username
git clone https://github.com/YOUR-USERNAME/il-election-results.git

# Move into the folder
cd il-election-results
```

---

## Step 5: Move Your Project Files In

Copy your scraper project into the cloned folder:
```
il-election-results/
├── aggregate_results.py       ← your updated aggregator
├── county_results/            ← scrapers write JSON here
├── statewide_results.json     ← aggregator writes this
├── widgets/                   ← HTML widgets go here (built later)
├── GITHUB_SETUP.md
└── README.md
```

---

## Step 6: Set Up GitHub Authentication

GitHub requires a Personal Access Token (PAT) instead of a password.

1. Go to: https://github.com/settings/tokens/new
2. Fill in:
   - **Note:** `election-scraper`
   - **Expiration:** `90 days` (covers March 17 with buffer)
   - **Scopes:** Check **`repo`** (top-level checkbox)
3. Click **Generate token**
4. **Copy the token immediately** — you won't see it again

**Save the token to your git credentials so you're never prompted:**

Mac:
```bash
git config --global credential.helper osxkeychain
```

Windows:
```bash
git config --global credential.helper manager
```

Then do one manual push (you'll be prompted for username + token once):
```bash
git add .
git commit -m "Initial setup"
git push -u origin main
```
- Username: your GitHub username
- Password: paste your Personal Access Token

After this, git will remember your credentials automatically.

---

## Step 7: Enable GitHub Pages

1. Go to your repo on GitHub
2. Click **Settings** → **Pages** (left sidebar)
3. Under **Source**, select:
   - Branch: `main`
   - Folder: `/ (root)`
4. Click **Save**

GitHub will show you your site URL:
```
https://YOUR-USERNAME.github.io/il-election-results/
```

Your JSON files will be accessible at URLs like:
```
https://YOUR-USERNAME.github.io/il-election-results/statewide_results.json
https://YOUR-USERNAME.github.io/il-election-results/county_results/will_results.json
```

> **Note:** GitHub Pages can take 5–10 minutes to activate the first time.
> After that, updates appear within ~30 seconds of each push.

---

## Step 8: Run With Auto-Push on Election Night

From now on, run your aggregator with the `--push` flag:

```bash
python aggregate_results.py --results-dir ./county_results --push
```

That's it. Every time it runs, it will:
1. Aggregate all county results into `statewide_results.json`
2. Commit the changes with a timestamp
3. Push to GitHub automatically
4. Your widgets will fetch fresh data within ~30 seconds

---

## Step 9: Set It to Run Automatically (Optional)

Instead of running the aggregator manually every few minutes, you can
schedule it to run automatically.

**Mac — using cron:**
```bash
# Open cron editor
crontab -e

# Add this line to run every 5 minutes (adjust path to your project)
*/5 * * * * cd /path/to/il-election-results && python aggregate_results.py --results-dir ./county_results --push >> ./logs/aggregator.log 2>&1
```

**Windows — using Task Scheduler:**
1. Search for "Task Scheduler" in the Start menu
2. Click "Create Basic Task"
3. Set trigger: Daily, repeat every 5 minutes
4. Set action: Start a program
   - Program: `python`
   - Arguments: `aggregate_results.py --results-dir ./county_results --push`
   - Start in: `C:\path\to\il-election-results`

---

## Troubleshooting

**"Not inside a git repository"**
```bash
# Make sure you're in the right folder
cd /path/to/il-election-results
git status
```

**"Git push failed" / authentication error**
```bash
# Re-enter your credentials
git config --global credential.helper store
git push
# Enter username and token when prompted
```

**GitHub Pages not updating**
- Changes take up to 30 seconds after a push
- Make sure GitHub Pages is enabled (Step 7)
- Check your repo's Actions tab for any errors

**Widgets showing old data**
- Check that `statewide_results.json` was actually updated
- Hard-refresh the page (Ctrl+Shift+R / Cmd+Shift+R)
- Make sure the widget URL matches your GitHub Pages URL

---

## Election Night Checklist

- [ ] Laptop plugged in (don't let it sleep!)
- [ ] Internet connection stable
- [ ] Run a test push before polls close: `python aggregate_results.py --results-dir ./county_results --push`
- [ ] Verify JSON appears at your GitHub Pages URL
- [ ] Verify widgets are loading data from correct URL
- [ ] Keep Terminal/Git Bash window open all night
