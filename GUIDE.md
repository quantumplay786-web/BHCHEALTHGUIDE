# BHC Health Guide: complete setup guide

## 1. What is in this folder

```
index.html, diseases.html, search.html, 404.html   built pages
Categories/  Diseases/                             built pages
about, contact, privacy, terms, disclaimer,
copyright, editorial-policy .html                  AdSense pages
data/site.json         YOUR SETTINGS (email, domain, AdSense id)
data/categories.json   22 categories
data/topics.json       369 queued topics
data/articles/*.json   one file per article (the source of every article page)
build.py               builds every page from the data
generate_articles.py   writes new articles with the API
components.js          menu, footer, search, share buttons, logo (base64)
style.css              the design
tools/                 weekly check + search engine ping
.github/workflows/     3 automatic jobs
favicon.ico, favicon-48.png, favicon-96.png, icon-192.png, icon-512.png,
icon-maskable-512.png, apple-touch-icon.png, og-image.png, manifest.json   logo files
```

Never edit the `.html` pages by hand. They are rewritten on every build. Change `data/`, `style.css`, or `build.py` instead.

## 2. Logo, Google icon and app manifest

- **In the site:** your full BHC logo is embedded as base64 inside `components.js` (the `LOGO_B64` line), so it shows in the menu and footer of every page with no extra file to load. No extra name text is added next to it.
- **Google search icon:** Google needs real files, not base64. Every page links to `favicon.ico`, `favicon-48.png` and `icon-192.png`. Google wants a square icon whose size is a multiple of 48 pixels (48, 96, 192), which these are. After you publish, it can take days to weeks to appear in results.
- **Manifest:** `manifest.json` is built automatically: name, description, white background, blue theme colour, normal icons (192 and 512), a separate "maskable" icon so Android shows the logo cleanly in a round or square tile, and shortcuts to Search and All Conditions. Paths are relative, so it works on a `github.io` address and on your own domain.
- **Share image:** `og-image.png` (1200x630) is used when someone shares a link on WhatsApp or Facebook.
- To change the logo later, replace the image files and the base64 line in `components.js`.

## 3. Add your settings (do this first)

Open `data/site.json`:

```json
{
  "name": "BHC Health Guide",
  "base_url": "",
  "email": "umorasocial24@gmail.com",
  "adsense_client": ""
}
```
- `base_url`: leave empty. GitHub fills in your address automatically from the repo name (and from a custom domain once you add one in Settings > Pages). Only fill it in if the address ever looks wrong.
- `email`: already set to umorasocial24@gmail.com (shown on the Contact and Privacy pages).
- `adsense_client`: leave empty until Google approves you.

## 4. Create the new GitHub account and repo

1. Go to github.com/signup. Use a new email, a username like `bhchealthguide`, and verify the email.
2. Settings > Password and authentication > turn on **two-factor login**. Save the recovery codes offline.
3. Click **New repository**. Name it `bhchealthguide.github.io` (your username plus `.github.io`). That gives the address `https://bhchealthguide.github.io` with no subfolder. Choose **Public**.
4. Upload everything inside this folder (Add file > Upload files). **Include the hidden `.github` folder**; a computer is easier for this than a phone. Commit.
5. **Settings > Pages**: Source "Deploy from a branch", Branch `main`, folder `/ (root)`. Tick **Enforce HTTPS**.
6. **Settings > Secrets and variables > Actions**:

| Where | Name | Value |
|---|---|---|
| Secrets | `API_KEY` | first CodeCraft key |
| Secrets | `API_KEY_2` | second CodeCraft key (optional) |
| Secrets | `UNSPLASH_KEY` | optional, free at unsplash.com/developers |
| Variables | `API_BASE` | `https://codecraftapi.com/v1` |
| Variables | `API_MODEL` | `claude-sonnet-5` |
| Variables | `ARTICLES_PER_DAY` | `3` to start, then `5` |
| Variables | `TOKEN_BUDGET` | `800000` (per key, per month) |
| Variables | `MAX_OUTPUT_TOKENS` | `10000` |

7. Nothing to edit in `data/site.json`: the address and email are already handled.
8. **Actions** tab > "Daily articles" > **Run workflow**, count `1`. Do this right after uploading: the first run rebuilds every page with your real web address (canonical links, sitemap). A green tick means it works. A red cross shows the exact reason (wrong key, wrong model name, no tokens).
9. Read the new article and check the token count printed in the log. Tokens per article x articles per day x 30 should stay under about 1.6M (two keys at 800,000).

## 5. The 3 automatic jobs

| Job | When (UTC) | Pakistan time | What it does |
|---|---|---|---|
| Daily articles | every day 05:17 | 10:17 AM | writes articles, rebuilds the site, saves |
| Tell search engines | every day 07:41 | 12:41 PM | sends new pages to Bing, Yandex and others (IndexNow) |
| Weekly site check | Sundays 02:43 | 7:43 AM | checks links and article quality, shows a report |

Expect roughly 5 to 6 hours of runner time a month in total. Public repositories get unlimited free Actions minutes; the 2,000 minute (33 hour) limit applies to private repos. A failed job emails you automatically. The weekly report is in the Actions tab, inside the run, under "Summary".

## 6. How to use the API (methods)

Your service is OpenAI-compatible and also accepts the Anthropic style. Same key, three ways:

1. **GitHub workflow (what this site uses):** `generate_articles.py` sends the request. Nothing to do.
2. **Terminal test:**
```
curl https://codecraftapi.com/v1/chat/completions \
  -H "Authorization: Bearer cc_YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-5","max_tokens":300,"messages":[{"role":"user","content":"Explain asthma in 3 lines"}]}'
```
3. **Anthropic style:** set the variable `API_STYLE` to `anthropic` and `API_BASE` to `https://codecraftapi.com` (no `/v1`). Use only if the normal style gives errors.

Never put a key in `index.html` or any browser JavaScript. Anyone can read it. Keys live only in GitHub Secrets.

## 7. Ideas to use the API to improve this site

1. **Upgrade the 21 original articles.** They average about 250 words. Rewriting them to 1,000+ words is the biggest quality gain. It costs roughly 100,000 tokens in total.
2. **Quality pass:** a second call that checks a finished article for wrong facts, doses or scary wording and fixes it. About 3,000 extra tokens per article, worth it for health content.
3. **Better titles and meta descriptions.** Ask for a click-friendly description per article.
4. **Urdu pages** for your best articles. Your audience in Pakistan searches in Urdu with far less competition.
5. **"People also ask" questions** added as FAQ, which can win Google's expanded results.
6. **Reading level check** so every article stays easy to read.
7. **Smarter related links** chosen by meaning, not only category.

Each is a small new script and workflow. Add them after the daily articles run smoothly.

## 8. Getting to the top of Google (honest steps)

No one can promise first place, and health is Google's strictest topic. These steps give you the best chance:

1. **Get a custom domain** (for example `bhchealthguide.com`, about 10 USD a year). Add it in Settings > Pages > Custom domain. The next build picks it up automatically. Do it early; changing later loses ranking.
2. **Google Search Console** (search.google.com/search-console): add the site, verify it, then **Sitemaps > submit `sitemap.xml`**.
3. **Bing Webmaster Tools**: add the site. Bing also gets the daily pings.
4. In Search Console use **URL Inspection > Request indexing** for the homepage and your 5 to 10 best articles.
5. **Publish steadily**, with at least 50 to 100 good articles before applying to AdSense.
6. **Quality over quantity.** Read a few new articles each week and fix mistakes the same day.
7. **Keep honest labels.** Keep "not reviewed by a doctor". Do not claim expert review unless it is true.
8. Check **pagespeed.web.dev** once after launch.
9. **Be patient.** New sites usually take 3 to 6 months to gain traffic.
10. **Never** buy links, copy other sites, or click your own ads.

## 9. AdSense checklist

- Real email in `data/site.json`; the seven policy pages are already built.
- A custom domain, 50+ good articles, and some visitors.
- After approval put `ca-pub-XXXXXXXXXXXXXXXX` in `adsense_client`. The next build adds the script to every page, creates `ads.txt`, and widens the security policy for Google's ad domains.

## 10. Daily running and safety

- Keys only in Secrets. Revoke a key in CodeCraft if you think it leaked.
- Protect the `main` branch: Settings > Branches > add a rule.
- Keep a copy of this zip on your computer as a backup.
- Delete an article by deleting its file in `data/articles/`; the page, sitemap and search entry disappear on the next build.
- Add topics in `data/topics.json`, categories in `data/categories.json`.
- Preview on a computer: `python build.py`, then open `index.html`.
- Test without the API: `python generate_articles.py --test --count 2`, then delete the two new fake files it creates in `data/articles/` (newest files, with text like "Point number 1 gives one more plain detail") and run `python build.py` again.
