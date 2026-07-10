# U.S. Visa Wait Times — Global Dashboard
https://dtm-repo.github.io/visa-wait-dash/

A live dashboard showing U.S. visa interview wait times worldwide, pulled automatically from the [State Department's Global Visa Wait Times page](https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html).

**Primary focus:** F/M/J student and exchange visas.

## What's in this repo

| File | Purpose |
|------|---------|
| `index.html` | The dashboard (served by GitHub Pages) |
| `data.json` | Visa wait time data (auto-updated monthly) |
| `scraper.py` | Fetches and parses the State Dept page |
| `.github/workflows/update-data.yml` | Runs the scraper on the 8th of every month |

## How auto-updating works

GitHub Actions runs `scraper.py` on the **8th of every month** (State Dept updates in the first week of each month). The scraper fetches the live page, parses the table, and commits an updated `data.json` to the repo. GitHub Pages then serves the updated data automatically.

You can also trigger an update manually:
1. Go to your repo on GitHub
2. Click the **Actions** tab
3. Click **Update Visa Wait Times Data**
4. Click **Run workflow** → **Run workflow**

## One-time setup checklist

- [ ] Create a new GitHub repo (public)
- [ ] Upload all files (drag & drop onto GitHub)
- [ ] Go to Settings → Pages → Source: **Deploy from a branch** → Branch: `main` → folder: `/ (root)` → Save
- [ ] Your URL will be: `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`

## Data notes

- Source updates monthly; the scraper runs on the 8th to catch it.
- `0.25` = "< 0.5 Month" on the source page.
- N/A = no appointment data available for that post.
