# HBC Health Guide — Complete Setup Guide

## YOUR LIVE WEBSITE URL
https://quantumplay786-web.github.io/BHCHEALTHGUIDE-/

---

## STEP 1 — Upload ALL Files to GitHub

Go to: github.com/quantumplay786-web/BHCHEALTHGUIDE-

Upload these files to the ROOT of your repo:
- components.js
- generate_articles.py
- fix_index.py
- generate_sitemap.py
- favicon.svg
- manifest.json
- robots.txt
- about.html
- contact.html
- privacy.html
- terms.html
- disclaimer.html

Upload to .github/workflows/ folder:
- daily-articles.yml

---

## STEP 2 — Check API Secrets

Go to: Settings → Secrets and variables → Actions

Make sure BOTH exist with EXACT names:
  GEMINI_KEY     ← from aistudio.google.com
  UNSPLASH_KEY   ← from unsplash.com/developers

If unsplash is rate-limited, the script uses a fallback image automatically.

---

## STEP 3 — Enable GitHub Pages

Settings → Pages → Branch: main → Save

Your site goes live at:
https://quantumplay786-web.github.io/BHCHEALTHGUIDE-/

---

## STEP 4 — Run the Workflow NOW

Actions → Generate Daily Articles → Run workflow → Run workflow

Wait 3-4 minutes. It will:
1. Generate 22 new disease articles with real content
2. Fix all existing pages (remove ads, fix links, fix images)
3. Update sitemap.xml with all pages
4. Push everything live automatically

---

## STEP 5 — Submit to Google Search Console

1. Go to: search.google.com/search-console
2. Click "Add property"
3. Enter: https://quantumplay786-web.github.io/BHCHEALTHGUIDE-/
4. Verify ownership (HTML file method is easiest)
5. Go to Sitemaps → Add sitemap
6. Enter: sitemap.xml
7. Click Submit

Google will start indexing your pages within 1-2 weeks.
Traffic grows slowly over 2-3 months as Google indexes more pages.

---

## HOW TO GET A FREE CUSTOM DOMAIN

### Option A — Free .tk domain (freenom.com)
1. Go to freenom.com
2. Search "hbchealthguide" → choose .tk, .ml, or .ga
3. Register free for 12 months
4. In Freenom DNS settings, add:
   Type: CNAME  |  Name: www  |  Value: quantumplay786-web.github.io
5. In GitHub repo: Settings → Pages → Custom domain → type your domain
6. Check "Enforce HTTPS" → Save
7. Wait 24 hours

### Option B — Paid domain (recommended, ~$10/year)
Buy from namecheap.com or godaddy.com
Then follow same DNS steps above.

---

## MONETAG ADS — When Approved

When Monetag approves your site:
1. Open components.js in your GitHub repo
2. Find the buildAds() function at the bottom
3. Paste your Monetag code inside it
4. Every page on your site instantly shows ads

Current Monetag ad types available for new sites:
- Push Notifications (paste script in buildAds)
- In-Page Push (paste script in buildAds)
- Vignette ads (paste script in buildAds)
- Banner/Display ads (available after traffic grows)

---

## HOW NEW ARTICLES BECOME PAGES

Every HTML file = its own URL automatically on GitHub Pages.
When the script runs at 6 AM daily:

Diseases/disease-malaria.html → 
  yoursite.github.io/BHCHEALTHGUIDE-/Diseases/disease-malaria.html

No database. No server. Just files. Instant.

---

## LOGO PROMPT FOR AI IMAGE GENERATORS

Use this prompt on Adobe Firefly, Midjourney, or DALL-E:

"Professional medical logo for HBC Health Guide.
A clean modern healthcare emblem featuring a bold blue cross (+) symbol 
integrated with a subtle DNA helix or heartbeat ECG line.
The letters HBC in strong sans-serif typography.
Below it the text HEALTH GUIDE in smaller spaced uppercase letters.
Color palette: primary #1a8fd1 (medical blue), white, with subtle green accent.
Style: flat vector, minimal, professional, suitable for a health information website.
Background: white. No gradients. No shadows. Clean lines only."

---

## DAILY AUTOMATION SCHEDULE

Every day at 6:00 AM UTC the system:
1. Picks 22 random diseases from the topic list
2. Writes full medical articles via Gemini AI
3. Fetches real photos from Unsplash
4. Fixes all HTML pages (links, images, AI phrases)
5. Updates sitemap.xml
6. Pushes everything to GitHub
7. Site updates live within 60 seconds

---

## FILE STRUCTURE

BHCHEALTHGUIDE-/
├── index.html            ← Homepage
├── style.css             ← All styles
├── components.js         ← Nav, footer, ads (edit this for changes)
├── generate_articles.py  ← Daily article generator
├── fix_index.py          ← Auto-fixes all HTML pages
├── generate_sitemap.py   ← Sitemap generator
├── favicon.svg           ← Logo/favicon
├── manifest.json         ← PWA manifest
├── robots.txt            ← SEO robots file
├── sitemap.xml           ← Auto-generated daily
├── about.html
├── contact.html
├── privacy.html
├── terms.html
├── disclaimer.html
├── .github/
│   └── workflows/
│       └── daily-articles.yml ← Automation
├── Categories/
│   ├── category-viruses.html
│   ├── category-bacteria.html
│   ├── category-chronic.html
│   ├── category-mental.html
│   ├── category-skin.html
│   ├── category-children.html
│   ├── category-neuro.html
│   └── category-psychology.html
└── Diseases/
    └── disease-*.html  ← Grows by 22 pages every day
