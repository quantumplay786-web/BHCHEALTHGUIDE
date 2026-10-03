#!/usr/bin/env python3
"""Weekly health check + report for the site. No tokens used, no API calls.
Exit code 1 (red run, GitHub emails you) if something is actually broken."""
import glob, json, os, re, sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
errors, warnings = [], []
site = json.load(open("data/site.json"))
cats = json.load(open("data/categories.json"))

# 1. broken internal links / images
pages = [f for f in glob.glob("**/*.html", recursive=True) if not f.startswith("templates/")]
checked = 0
for f in pages:
    html = open(f, encoding="utf-8").read()
    base = os.path.dirname(f)
    for m in re.finditer(r'(?:href|src)="([^"#?]+)', html):
        u = m.group(1)
        if u.startswith(("http", "mailto:", "data:", "//", "javascript")) or re.search(r"[\'+{$]", u):
            continue            # external links and links built by JavaScript
        checked += 1
        if not os.path.exists(os.path.normpath(os.path.join(base, unquote(u)))):
            errors.append(f"broken link in {f}: {u}")

# 2. malformed tags (the old fix_index.py bug) and leftover junk
for f in pages:
    html = open(f, encoding="utf-8").read()
    if re.search(r'<[a-zA-Z][^<>]*="[^"<>]*<', html):
        errors.append(f"malformed HTML tag in {f}")
    for bad in ("Upload:", "yourdomain.com", "undefined", "NaN"):
        if bad in html:
            warnings.append(f"{f} contains '{bad}'")

# 3. article quality
arts = glob.glob("data/articles/*.json")
thin = []
words_total = 0
for f in arts:
    a = json.load(open(f, encoding="utf-8"))
    text = " ".join([a.get("subtitle", "")] + [sec.get("intro", "") + " " + " ".join(sec.get("items", [])) +
                    " ".join(q["q"] + " " + q["a"] for q in sec.get("faq", [])) for sec in a["sections"]])
    n = len(text.split())
    words_total += n
    if a.get("origin") != "original" and n < 700:
        thin.append(f"{os.path.basename(f)} ({n} words)")
    if len(a["sections"]) < 4:
        errors.append(f"{f}: fewer than 4 sections")
if thin:
    errors.append("short articles: " + ", ".join(thin))

# 4. sitemap sanity
sm = open("sitemap.xml", encoding="utf-8").read() if os.path.exists("sitemap.xml") else ""
if sm.count("<loc>") < len(arts):
    errors.append("sitemap.xml has fewer URLs than articles; run build.py")
if not site.get("email") and not site.get("contact_form_url"):
    warnings.append("data/site.json has no email: AdSense needs a way to contact you")

# 5. report
usage = json.load(open("data/usage.json")) if os.path.exists("data/usage.json") else {}
empty = [c["h1"] for s, c in cats.items() if not glob.glob(f"data/articles/*.json") or
         not any(json.load(open(f)).get("category") == s for f in arts)]
topics = json.load(open("data/topics.json"))
done = {os.path.basename(f)[:-5] for f in arts}
left = len([t for t in topics if t["slug"] not in done])

lines = ["# Weekly site report", "",
         f"- Articles published: **{len(arts)}** (average {words_total // max(len(arts), 1)} words; the 21 original articles are short, new ones are longer)",
         f"- Topics still queued: **{left}** (about {left // max(int(site.get('articles_per_day', 5)), 1)} days at the current pace)",
         f"- Pages checked: {len(pages)}, links checked: {checked}",
         f"- Categories still empty: {len(empty)}"]
for month in sorted(usage)[-2:]:
    u = usage[month]
    keys = ", ".join(f"key {int(k) + 1}: {v:,}" for k, v in sorted(u.get("keys", {}).items()))
    lines.append(f"- Tokens {month}: **{u.get('tokens', 0):,}** ({keys or 'no per-key data'}), articles written: {u.get('articles', 0)}")
if warnings:
    lines += ["", "## Warnings"] + [f"- {w}" for w in warnings[:25]]
if errors:
    lines += ["", "## Problems"] + [f"- {e}" for e in errors[:50]]
else:
    lines += ["", "No problems found."]
report = "\n".join(lines)
print(report)
if os.environ.get("GITHUB_STEP_SUMMARY"):
    open(os.environ["GITHUB_STEP_SUMMARY"], "a").write(report + "\n")
sys.exit(1 if errors else 0)
