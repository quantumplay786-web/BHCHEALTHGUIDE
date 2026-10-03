#!/usr/bin/env python3
"""
build.py  -  rebuilds the WHOLE site from data/*.json

  data/site.json         site name, base URL, email, AdSense id (edit this one)
  data/categories.json   category pages + cards on the homepage
  data/articles/*.json   one file per disease article (written by generate_articles.py)
  templates/index.html   homepage skeleton

Nothing here edits HTML with regex. Every page is written fresh from the same
templates, so the design can never drift or get corrupted by a daily run.

Run:  python build.py
"""
import glob
import html
import json
import os
import re
import sys
from datetime import date, datetime
from urllib.parse import quote_plus, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


def load(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


SITE = load("data/site.json", {})
CATS = load("data/categories.json", {})
ICONS = load("data/icons.json", {})
NAME = SITE.get("name", "BHC Health Guide")
def derive_base():
    """Site address. Priority: base_url in data/site.json > custom domain in CNAME > GitHub repo name."""
    b = (SITE.get("base_url") or "").strip().rstrip("/")
    if b:
        return b
    if os.path.exists("CNAME"):
        dom = open("CNAME", encoding="utf-8").read().strip().split()
        if dom:
            return "https://" + dom[0]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" in repo:
        owner, name = repo.split("/", 1)
        owner = owner.lower()
        return f"https://{owner}.github.io" if name.lower() == f"{owner}.github.io" else f"https://{owner}.github.io/{name}"
    return ""


BASE = derive_base()
YEAR = date.today().year

# ---------------------------------------------------------------- images
FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1584118624012-df056829fbd0?w=900&q=80",
    "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?w=900&q=80",
    "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=900&q=80",
    "https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=900&q=80",
    "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=900&q=80",
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=900&q=80",
]


def fallback_image(key, width=900):
    idx = sum(ord(c) for c in key) % len(FALLBACK_IMAGES)
    return FALLBACK_IMAGES[idx].replace("w=900", f"w={width}")


def small(url, width):
    return re.sub(r"([?&])w=\d+", rf"\g<1>w={width}", url) if "unsplash.com" in url else url


# ---------------------------------------------------------------- data
def load_articles():
    arts = {}
    for f in sorted(glob.glob("data/articles/*.json")):
        try:
            a = load(f)
            slug = os.path.basename(f)[:-5]
            a["slug"] = slug
            if a.get("category") not in CATS:
                print(f"  WARNING {slug}: unknown category {a.get('category')!r}, skipped")
                continue
            if not a.get("title") or not a.get("sections"):
                print(f"  WARNING {slug}: missing title/sections, skipped")
                continue
            arts[slug] = a
        except Exception as ex:  # one bad file must never stop the whole build
            print(f"  WARNING {f}: {ex}")
    return arts


ARTS = load_articles()
BY_CAT = {c: sorted([a for a in ARTS.values() if a["category"] == c], key=lambda a: a["title"].lower()) for c in CATS}


def badge_class(text):
    t = (text or "").lower()
    if any(w in t for w in ("mild", "low", "minor")):
        return "badge-green"
    if any(w in t for w in ("serious", "high", "severe", "life", "fatal", "emergency")):
        return "badge-red"
    return "badge-orange"


def short(text, n):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rsplit(" ", 1)[0].rstrip(",;:.") + "..."


def pretty_date(iso):
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%B %d, %Y").replace(" 0", " ")
    except Exception:
        return iso or ""


# ---------------------------------------------------------------- shared head
THEME = SITE.get("theme_color", "#1a8fd1")


def csp():
    """Content-Security-Policy written as a meta tag (GitHub Pages cannot send real headers).
    Stricter without ads; opened up for Google AdSense only when adsense_client is set."""
    ads = bool(SITE.get("adsense_client"))
    pu = urlparse(BASE)
    origin = f"{pu.scheme}://{pu.netloc}" if pu.netloc else ""   # lets the 404 page load files through its <base> tag
    script = "'self' 'unsafe-inline'" + (f" {origin}" if origin else "") + (" https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.google.com https://*.doubleclick.net https://*.googleadservices.com https://*.adtrafficquality.google" if ads else "")
    parts = [
        "default-src 'self'",
        f"script-src {script}",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com" + (f" {origin}" if origin else ""),
        "font-src 'self' https://fonts.gstatic.com data:",
        "img-src 'self' data: https:",
        "connect-src 'self'" + (" https:" if ads else ""),
        "frame-src " + ("https:" if ads else "'none'"),
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self' mailto:",
    ]
    return "; ".join(parts)

def head(title, desc, rel_path, prefix, og_image="", og_type="website", jsonld=None, noindex=False):
    canon = f"{BASE}/{rel_path}" if BASE else ""
    ads = ""
    if SITE.get("adsense_client"):
        ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='
               f'{e(SITE["adsense_client"])}" crossorigin="anonymous"></script>\n')
    og_image = og_image or (f"{BASE}/og-image.png" if BASE else "")
    og = ""
    if og_image:
        og = f'<meta property="og:image" content="{e(og_image)}">\n<meta name="twitter:card" content="summary_large_image">\n'
    ld = ""
    if jsonld:
        for block in jsonld:
            ld += '<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(short(desc, 158))}">
<meta name="robots" content="{robots}">
{f'<link rel="canonical" href="{e(canon)}">' if canon else ''}
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(short(desc, 158))}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{e(NAME)}">
{f'<meta property="og:url" content="{e(canon)}">' if canon else ''}
{og}<link rel="icon" href="{prefix}favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="{prefix}favicon-48.png">
<link rel="icon" type="image/png" sizes="192x192" href="{prefix}icon-192.png">
<link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png">
<link rel="manifest" href="{prefix}manifest.json">
<meta name="theme-color" content="{THEME}">
<meta http-equiv="Content-Security-Policy" content="{csp()}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}style.css">
{ads}{ld}</head>
'''


def tail(prefix, share=False):
    return (('<div id="share-placeholder"></div>\n' if share else "") +
            f'<div id="footer-placeholder"></div>\n\n<script src="{prefix}components.js"></script>\n</body>\n</html>\n')


def breadcrumb(items, prefix):
    parts = []
    for i, (label, href) in enumerate(items):
        if i:
            parts.append('<span class="bc-sep">›</span>')
        parts.append(f'<a href="{href}">{e(label)}</a>' if href else f"<span>{e(label)}</span>")
    return '<div class="breadcrumb">' + "".join(parts) + "</div>"


# ---------------------------------------------------------------- article page
SOURCES = [("WHO", "who.int"), ("CDC", "cdc.gov"), ("NHS", "nhs.uk"), ("MedlinePlus", "medlineplus.gov")]


def section_html(sec):
    sid = sec.get("id", "acc-x")
    icon = ICONS.get(sid) or ICONS.get("acc-sym", "")
    chev = ICONS.get("chev", "")
    body = ""
    if sec.get("intro"):
        body += f"<p>{e(sec['intro'])}</p>"
    if sec.get("items"):
        body += '<ul class="one">' + "".join(f"<li>{e(i)}</li>" for i in sec["items"]) + "</ul>"
    for qa in sec.get("faq", []):
        body += (f'<h4 style="font-size:14px;font-weight:700;color:var(--t);margin:14px 0 4px">{e(qa["q"])}</h4>'
                 f'<p>{e(qa["a"])}</p>')
    op = " open" if sec.get("open") else ""
    return (f'  <div class="acc{op}" id="{e(sid)}"><div class="acc-h" role="button" tabindex="0" onclick="toggleAcc(\'{e(sid)}\')">'
            f'<div class="acc-iw {e(sec.get("color", "blue"))}">{icon}</div><span class="acc-title">{e(sec["title"])}</span>{chev}</div>\n'
            f'  <div class="acc-body">{body}</div></div>\n')


def related_for(a):
    out, seen = [], {a["slug"]}
    for name, slug in a.get("related", []):
        if slug in ARTS and slug not in seen:
            out.append((ARTS[slug]["title"], slug)); seen.add(slug)
    # top up from the same category so the block is never empty
    for other in BY_CAT.get(a["category"], []):
        if len(out) >= 5:
            break
        if other["slug"] not in seen:
            out.append((other["title"], other["slug"])); seen.add(other["slug"])
    return out[:5]


def render_article(a):
    cat = CATS[a["category"]]
    p = "../"
    title = a["title"]
    img = a.get("image") or fallback_image(a["category"] + a["slug"])
    badges = "&nbsp;".join(f'<span class="{e(c)}">{e(t)}</span>' for c, t in a.get("badges", []))
    qbar = "".join(f'<div class="qbar-item"><div class="qb-lbl">{e(l)}</div><div class="qb-val">{e(v)}</div></div>'
                   for l, v in a.get("qbar", []))
    credit = ""
    secs = "".join(section_html(s) for s in a["sections"])

    facts = ""
    fl = a.get("facts", [])
    if fl:
        rows = []
        for i, (l, v) in enumerate(fl):
            st = ' style="border-top:1px solid var(--bd);padding-top:10px"' if i else ""
            rows.append(f'<div{st}><strong>{e(l)}:</strong><br><span style="color:var(--ts)">{e(v)}</span></div>')
        facts = ('<div class="sw"><div class="sw-head">Quick Facts</div><div class="sw-body">'
                 '<div style="display:flex;flex-direction:column;gap:10px;font-size:13px">' + "".join(rows) + "</div></div></div>")

    rel = related_for(a)
    related = ""
    if rel:
        related = (f'<div class="sw"><div class="sw-head">{e(a.get("related_label", "Related Diseases"))}</div><div class="sw-body">' +
                   "".join(f'<a href="disease-{e(s)}.html" class="sw-link"><div class="sw-dot"></div>{e(t)}</a>' for t, s in rel) +
                   "</div></div>")

    action = (f'<div class="sw"><div class="sw-head">Take Action</div><div class="sw-body">'
              f'<a href="../Categories/category-{e(a["category"])}.html" class="btn-p">More {e(cat["h1"])}</a>'
              f'<a href="../disclaimer.html" class="btn-o">Read the Medical Disclaimer</a></div></div>')

    q = quote_plus(title)
    srcs = "".join(
        f'<a href="https://www.google.com/search?q={q}+site%3A{dom}" target="_blank" rel="noopener nofollow" class="sw-link"><div class="sw-dot"></div>{n}: {e(title)}</a>'
        for n, dom in SOURCES)
    learn = f'<div class="sw"><div class="sw-head">Learn More From Trusted Sources</div><div class="sw-body">{srcs}</div></div>'

    about = (f'<div class="sw"><div class="sw-head">About This Guide</div><div class="sw-body">'
             f'<p style="font-size:13px;color:var(--ts);line-height:1.6;margin-bottom:10px">Last updated {e(pretty_date(a.get("updated")))}. '
             f'Information only. Not reviewed by a doctor.</p>'
             f'<a href="../editorial-policy.html" class="sw-link"><div class="sw-dot"></div>How we write our guides</a>'
             f'<a href="../contact.html" class="sw-link"><div class="sw-dot"></div>Report a mistake</a></div></div>')

    promo = a.get("promo_html", "") if SITE.get("show_affiliate_boxes") else ""

    notice = ('<div style="background:#f0f8ff;border:1.5px solid #b3d9f0;border-radius:12px;padding:12px 16px;font-size:13px;'
              'color:var(--tm);line-height:1.6;margin-bottom:16px"><strong>For information only.</strong> This guide is not medical advice. '
              'If you feel unwell, see a qualified health professional. In an emergency, call your local emergency number. '
              '<a href="../disclaimer.html" style="color:#1a8fd1;font-weight:600">Read the full disclaimer</a>.</div>')

    desc = a.get("description") or a.get("subtitle") or title
    url = f"{BASE}/Diseases/disease-{a['slug']}.html"
    ld = [{
        "@context": "https://schema.org", "@type": "Article", "headline": title, "description": short(desc, 200),
        "image": img, "datePublished": a.get("created") or a.get("updated"), "dateModified": a.get("updated"),
        "mainEntityOfPage": url, "author": {"@type": "Organization", "name": NAME},
        "publisher": {"@type": "Organization", "name": NAME},
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/index.html"},
            {"@type": "ListItem", "position": 2, "name": cat["h1"], "item": f"{BASE}/Categories/category-{a['category']}.html"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url}]}]
    faqs = [qa for s in a["sections"] for qa in s.get("faq", [])]
    if faqs:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": qa["q"], "acceptedAnswer": {"@type": "Answer", "text": qa["a"]}} for qa in faqs]})

    page = head(f"{title}: Symptoms, Causes and Treatment | {NAME}", desc, f"Diseases/disease-{a['slug']}.html", p,
                og_image=img, og_type="article", jsonld=ld)
    page += f'''<body>
<div id="nav-placeholder"></div>

<section class="dis-hero"><div class="container">
  {breadcrumb([("Home", "../index.html"), (cat["h1"], f"../Categories/category-{a['category']}.html"), (title, None)], p)}
  <div class="dis-hero-inner">
    <div>
      <div style="margin-bottom:12px">{badges}</div>
      <h1>{e(title)}</h1><p class="dis-sub">{e(a.get("subtitle", ""))}</p>
      <div style="font-size:12px;color:var(--ts);margin:-4px 0 14px">Last updated {e(pretty_date(a.get("updated")))} &middot; Information only, not medical advice</div>
      <div class="qbar">
        {qbar}
      </div>
    </div>
    <div class="dis-hero-img"><img src="{e(img)}" alt="{e(title)}">{credit}</div>
  </div>
</div></section>

<div class="container"><div class="dis-layout">
<div class="dis-main">
{notice}
{secs}</div>
<aside class="dis-side">
  {facts}
  {related}
  {action}
  {about}
  {promo}
</aside>
</div></div>

'''
    page += tail(p, share=True)
    return page


# ---------------------------------------------------------------- category page
COLOR_BY_TC = {"tc-blue": "blue", "tc-green": "green", "tc-purple": "purple", "tc-orange": "orange"}


def render_category(slug):
    c = CATS[slug]
    arts = BY_CAT[slug]
    p = "../"
    img = c.get("image") or fallback_image(slug, 600)
    color = COLOR_BY_TC.get((c.get("topic") or {}).get("tc", ""), "blue")
    subs = ""
    if c.get("subs"):
        cards = "".join(
            f'<a href="#conditions" class="sub-card"><div class="sub-icon {e(s["color"])}">{s["svg"]}</div>'
            f'<div class="sub-name">{e(s["name"])}</div><div class="sub-desc">{e(s["desc"])}</div></a>' for s in c["subs"])
        subs = f'<h2 class="sec-title">Browse by Type</h2>\n  <div class="sub-grid">{cards}</div>\n'
    if arts:
        items = "".join(
            f'<a href="../Diseases/disease-{e(a["slug"])}.html" class="dis-item"><div class="dis-ico {color}">{c["list_svg"]}</div>'
            f'<div class="dis-info"><h4>{e(a["title"])}</h4><p>{e(short(a.get("subtitle", ""), 110))}</p></div>'
            f'<div class="dis-sev"><span class="{e(a["badges"][0][0]) if a.get("badges") else "badge-orange"}">'
            f'{e(a["badges"][0][1]) if a.get("badges") else "Guide"}</span></div><div class="dis-arr">{c["arrow_svg"]}</div></a>'
            for a in arts)
        n = len(arts)
        listing = (f'<div class="dis-list" id="conditions">\n    <div class="dis-list-head">{e(c.get("list_label", "All Conditions"))} '
                   f'<span class="dis-list-count">{n} {"Condition" if n == 1 else "Conditions"}</span></div>\n    {items}\n  </div>')
    else:
        listing = ('<div class="dis-list" id="conditions"><div class="dis-list-head">Guides are on the way</div>'
                   '<div style="padding:22px;font-size:14px;color:var(--ts);line-height:1.7">We are adding new guides to this '
                   'section every day. Please check back soon, or <a href="../diseases.html" style="color:#1a8fd1;font-weight:700">browse all conditions</a>.</div></div>')
    desc = c["blurb"]
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": c["h1"], "description": short(desc, 200),
           "url": f"{BASE}/Categories/category-{slug}.html"}]
    page = head(f"{c['h1']}: Conditions, Symptoms and Guides | {NAME}", desc, f"Categories/category-{slug}.html", p,
                og_image=img, jsonld=ld, noindex=not arts)
    page += f'''<body>
<div id="nav-placeholder"></div>

<section class="cat-hero"><div class="container">
  {breadcrumb([("Home", "../index.html"), (c["h1"], None)], p)}
  <div class="cat-hero-inner">
    <div><h1>{e(c["h1"])}</h1><p>{e(c["blurb"])}</p></div>
    <div class="cat-hero-img"><img src="{e(img)}" alt="{e(c["h1"])}" style="width:100%;height:160px;object-fit:cover;border-radius:14px"></div>
  </div>
</div></section>

<div class="container" style="padding-top:36px;padding-bottom:52px">
  {subs}
  {listing}
</div>

'''
    page += tail(p)
    return page


# ---------------------------------------------------------------- all-diseases page
def render_all():
    p = ""
    blocks = ""
    total = 0
    for slug, c in CATS.items():
        arts = BY_CAT[slug]
        if not arts:
            continue
        total += len(arts)
        color = COLOR_BY_TC.get((c.get("topic") or {}).get("tc", ""), "blue")
        items = "".join(
            f'<a href="Diseases/disease-{e(a["slug"])}.html" class="dis-item"><div class="dis-ico {color}">{c["list_svg"]}</div>'
            f'<div class="dis-info"><h4>{e(a["title"])}</h4><p>{e(short(a.get("subtitle", ""), 110))}</p></div>'
            f'<div class="dis-sev"><span class="{e(a["badges"][0][0]) if a.get("badges") else "badge-orange"}">'
            f'{e(a["badges"][0][1]) if a.get("badges") else "Guide"}</span></div><div class="dis-arr">{c["arrow_svg"]}</div></a>'
            for a in arts)
        blocks += (f'<div class="dis-list all-block" style="margin-bottom:22px"><div class="dis-list-head"><a href="Categories/category-{e(slug)}.html" '
                   f'style="color:inherit;text-decoration:none">{e(c["h1"])}</a> <span class="dis-list-count">{len(arts)}</span></div>{items}</div>\n')
    page = head(f"All Conditions A to Z | {NAME}", "Browse every health condition guide on BHC Health Guide, grouped by body system and type.",
                "diseases.html", p)
    page += f'''<body>
<div id="nav-placeholder"></div>

<section class="cat-hero"><div class="container">
  {breadcrumb([("Home", "index.html"), ("All Conditions", None)], p)}
  <div class="cat-hero-inner">
    <div><h1>All Conditions</h1><p>{total} plain-language guides, grouped by body system and type. Use the search box in the menu to find a condition quickly.</p></div>
  </div>
</div></section>

<div class="container" style="padding-top:36px;padding-bottom:52px" id="all-wrap">
{blocks}</div>

<script>
(function () {{
  var q = new URLSearchParams(location.search).get("q");
  if (!q) return;
  q = q.toLowerCase();
  document.querySelectorAll(".dis-item").forEach(function (a) {{
    a.style.display = a.textContent.toLowerCase().indexOf(q) > -1 ? "" : "none";
  }});
  document.querySelectorAll(".all-block").forEach(function (b) {{
    var any = Array.prototype.some.call(b.querySelectorAll(".dis-item"), function (a) {{ return a.style.display !== "none"; }});
    b.style.display = any ? "" : "none";
  }});
}})();
</script>
'''
    page += tail(p)
    return page


# ---------------------------------------------------------------- search page
def render_search():
    chips = '<button class="chip on" data-c="">All</button>' + "".join(
        f'<button class="chip" data-c="{e(slug)}">{e(c["h1"])}</button>' for slug, c in CATS.items() if BY_CAT[slug])
    page = head(f"Search Health Conditions | {NAME}", "Search symptoms, diseases and health topics and find the guide you need.",
                "search.html", "", noindex=True)
    page += f'''<body>
<style>
.s-box{{display:flex;gap:8px;background:#fff;border:1.5px solid #dde8f0;border-radius:12px;padding:6px 6px 6px 16px;align-items:center;max-width:620px}}
.s-box input{{flex:1;min-width:0;border:none;outline:none;font:inherit;font-size:16px;color:#1a232e;padding:10px 0;background:transparent}}
.s-box button{{background:#1a8fd1;color:#fff;border:none;border-radius:9px;padding:11px 20px;font:inherit;font-weight:700;cursor:pointer}}
.chips{{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 6px}}
.chip{{background:#fff;border:1.5px solid #dde8f0;border-radius:99px;padding:7px 14px;font:inherit;font-size:13px;font-weight:600;color:#4a5568;cursor:pointer}}
.chip.on{{background:#1a8fd1;border-color:#1a8fd1;color:#fff}}
.s-meta{{font-size:13px;color:#94a3b8;margin:10px 2px 14px}}
</style>
<div id="nav-placeholder"></div>

<section class="cat-hero"><div class="container">
  {breadcrumb([("Home", "index.html"), ("Search", None)], "")}
  <div class="cat-hero-inner"><div>
    <h1>Search Health Topics</h1>
    <p style="margin-bottom:16px">Type a condition, a symptom, or a topic you care about, for example <em>headache</em>, <em>child fever</em> or <em>blood sugar</em>.</p>
    <div class="s-box"><input id="s-q" type="search" placeholder="Search conditions and symptoms..." aria-label="Search" autocomplete="off"><button id="s-go" type="button">Search</button></div>
  </div></div>
</div></section>

<div class="container" style="padding-top:22px;padding-bottom:52px">
  <div class="chips" id="s-chips">{chips}</div>
  <div class="s-meta" id="s-meta"></div>
  <div class="dis-list" id="s-results"></div>
</div>

<script>
document.addEventListener("DOMContentLoaded", function () {{
  var q = document.getElementById("s-q"), meta = document.getElementById("s-meta"), out = document.getElementById("s-results");
  var cat = "", data = [];
  function esc(x) {{ return String(x).replace(/[&<>"]/g, function (c) {{ return {{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]; }}); }}
  function render() {{
    var terms = bhcTerms(q.value);
    var list = terms.length ? bhcSearch(q.value, data, 60) : data.slice().sort(function (a, b) {{ return a.t.localeCompare(b.t); }}).slice(0, 60);
    if (cat) list = list.filter(function (x) {{ return x.cs === cat; }});
    meta.textContent = terms.length ? (list.length + " result" + (list.length === 1 ? "" : "s") + " for \u201c" + q.value.trim() + "\u201d") : "Showing the first guides. Type to search.";
    if (!list.length) {{ out.innerHTML = '<div style="padding:22px;font-size:14px;color:#94a3b8">No guide found yet. Try a different word, or <a href="diseases.html" style="color:#1a8fd1;font-weight:700">browse all conditions</a>. New guides are added every day.</div>'; return; }}
    out.innerHTML = list.map(function (x) {{
      return '<a href="' + x.u + '" class="dis-item"><div class="dis-info"><h4>' + esc(x.t) + '</h4><p>' + esc(x.c) + ' &middot; ' + esc(x.s) + '</p></div><div class="dis-sev"><span class="' + esc(x.bc) + '">' + esc(x.b) + '</span></div></a>';
    }}).join("");
  }}
  q.value = new URLSearchParams(location.search).get("q") || "";
  fetch("search-index.json").then(function (r) {{ return r.json(); }}).then(function (d) {{ data = d; render(); }}).catch(function () {{ meta.textContent = "Search is not available right now."; }});
  q.addEventListener("input", function () {{ history.replaceState(null, "", q.value ? "?q=" + encodeURIComponent(q.value) : location.pathname); render(); }});
  document.getElementById("s-go").addEventListener("click", render);
  q.addEventListener("keydown", function (ev) {{ if (ev.key === "Enter") render(); }});
  document.getElementById("s-chips").addEventListener("click", function (ev) {{
    var b = ev.target.closest(".chip"); if (!b) return;
    document.querySelectorAll(".chip").forEach(function (c) {{ c.classList.remove("on"); }});
    b.classList.add("on"); cat = b.getAttribute("data-c"); render();
  }});
}});
</script>
'''
    page += tail("")
    return page


# ---------------------------------------------------------------- homepage
def render_index():
    tpl = open("templates/index.html", encoding="utf-8").read()
    cards = ""
    for slug, c in CATS.items():
        t = c.get("topic")
        if not t:
            continue
        cards += (f'      <a href="Categories/category-{e(slug)}.html" class="topic-card {e(t["tc"])}">\n'
                  f'        <div class="topic-icon">{t["svg"]}</div>\n        <span class="topic-name">{e(t["name"])}</span>\n      </a>\n')
    # featured: newest articles first, then the originals
    ranked = sorted(ARTS.values(), key=lambda a: (a.get("created") or a.get("updated") or "", a["slug"]), reverse=True)
    featured = ranked[:6]
    fa = ""
    tag = ["badge-blue", "badge-green", "badge-orange"]
    for i, a in enumerate(featured):
        img = small(a.get("image") or fallback_image(a["category"] + a["slug"]), 600)
        fa += (f'      <a href="Diseases/disease-{e(a["slug"])}.html" class="art-card">\n'
               f'        <img src="{e(img)}" alt="{e(a["title"])}" loading="lazy" style="width:100%;height:180px;object-fit:cover">\n'
               f'        <div class="art-body">\n          <div class="art-tag"><span class="{tag[i % 3]}">{e(CATS[a["category"]]["h1"])}</span></div>\n'
               f'          <h3 class="art-title">{e(a["title"])}</h3>\n          <p class="art-exc">{e(short(a.get("subtitle", ""), 150))}</p>\n'
               f'          <span class="art-more">Read More {ICONS.get("art-arrow", "")}</span>\n        </div>\n      </a>\n')
    desc = ("Plain-language guides to diseases, symptoms, causes, treatment and prevention. "
            "Information only, not medical advice.")
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": f"{BASE}/index.html"},
          {"@context": "https://schema.org", "@type": "Organization", "name": NAME, "url": f"{BASE}/index.html",
           "logo": f"{BASE}/icon-512.png"}]
    h = head(f"{NAME} | Trusted Health Information and Disease Guides", desc, "index.html", "",
             og_image=f"{BASE}/og-image.png", jsonld=ld)
    out = tpl.replace("{{HEAD}}", h).replace("<!--@TOPICS@-->", cards).replace("<!--@ARTICLES@-->", fa)
    return out


# ---------------------------------------------------------------- static pages
def static_page(file, title, desc, intro, blocks, crumb=None, noindex=False):
    body = ""
    for h2, content in blocks:
        body += ('  <div style="background:#fff;border:1.5px solid #dde8f0;border-radius:14px;padding:30px 32px;margin-bottom:20px">\n'
                 + (f'    <h2 style="font-size:20px;font-weight:800;color:#1a232e;margin-bottom:12px">{e(h2)}</h2>\n' if h2 else "")
                 + f'    <div class="prose" style="font-size:14.5px;color:#4a5568;line-height:1.8">{content}</div>\n  </div>\n')
    page = head(f"{title} | {NAME}", desc, file, "", noindex=noindex)
    page += f'''<body>
<div id="nav-placeholder"></div>

<section style="background:linear-gradient(130deg,#d6ebf7,#e8f4fd);padding:56px 0 40px;border-bottom:1.5px solid #dde8f0">
  <div class="container">
    {breadcrumb([("Home", "index.html"), (crumb or title, None)], "")}
    <h1 style="font-size:36px;font-weight:800;color:#1a232e;margin:12px 0 10px">{e(title)}</h1>
    <p style="font-size:16px;color:#4a5568;max-width:640px;line-height:1.7">{intro}</p>
  </div>
</section>

<div class="container" style="padding-top:44px;padding-bottom:64px;max-width:840px">
{body}</div>

'''
    page += tail("")
    return page


def P(*paras):
    return "".join(f'<p style="margin-bottom:12px">{x}</p>' for x in paras)


def UL(items):
    return '<ul style="margin:0 0 12px 20px;list-style:disc">' + "".join(f'<li style="margin-bottom:6px">{x}</li>' for x in items) + "</ul>"


def build_static():
    email = SITE.get("email", "").strip()
    mail = f'<a href="mailto:{e(email)}" style="color:#1a8fd1;font-weight:700">{e(email)}</a>' if email else "the contact details on this page"
    updated = SITE.get("policies_updated", date.today().isoformat())
    pages = {}

    pages["about.html"] = static_page("about.html", "About Us",
        f"Learn about {NAME}, a plain-language health information website.",
        "We make health information clear, honest, and easy to understand.",
        [("Our mission", P(f"{e(NAME)} is an information website. We explain diseases, symptoms, causes, tests, treatments, and prevention in simple words so that you can understand what you read and ask better questions when you speak to a health professional.")),
         ("How our guides are made", P("Every guide follows the same fixed outline and is checked by automated rules for structure and safety. Guides are based on widely published public health knowledge.",
                                    "<strong>Our guides are not reviewed by doctors.</strong> We say this openly because you deserve to know. Read our <a href='editorial-policy.html' style='color:#1a8fd1;font-weight:700'>editorial policy</a> for the full process.")),
         ("What we are not", P("We are not a clinic, a pharmacy, or a diagnosis tool. We cannot tell you what is wrong with you, and we never give medicine doses. If you are worried about your health, please see a qualified health professional.")),
         ("Found a mistake?", P(f"Tell us through our <a href='contact.html' style='color:#1a8fd1;font-weight:700'>contact page</a>. We review every report and correct errors."))])

    contact_lines = []
    if email:
        contact_lines.append(f"<strong>Email:</strong> {mail}")
    if SITE.get("contact_form_url"):
        contact_lines.append(f'<strong>Contact form:</strong> <a href="{e(SITE["contact_form_url"])}" style="color:#1a8fd1;font-weight:700" rel="noopener">Open the form</a>')
    contact_html = P(*contact_lines) if contact_lines else P("<strong>Contact details are being set up.</strong>")
    pages["contact.html"] = static_page("contact.html", "Contact Us",
        f"Contact {NAME} to report an error, ask a question, or send feedback.",
        "We read every message and reply as soon as we can.",
        [("Get in touch", contact_html + P("Please do not send private medical information. We cannot give medical advice, diagnose conditions, or recommend treatment by email.")),
         ("What you can contact us about", UL(["Reporting a factual mistake or an outdated statement in a guide", "Suggesting a condition you would like us to cover",
                                                "Copyright, image, or content removal requests", "Privacy questions and requests", "Advertising or partnership questions"])),
         ("Emergency?", P("<strong>If you think you or someone else is having a medical emergency, call your local emergency number now.</strong> Do not wait for a reply from us."))])

    pages["privacy.html"] = static_page("privacy.html", "Privacy Policy",
        f"How {NAME} collects, uses, and protects information.",
        f"Last updated: {e(pretty_date(updated))}",
        [("Overview", P(f"This policy explains what information {e(NAME)} (&ldquo;we&rdquo;, &ldquo;us&rdquo;) collects when you visit this website and how it is used. We do not ask you to create an account, and we do not sell personal information.")),
         ("Information we collect", UL(["<strong>Log data.</strong> Our website is hosted on GitHub Pages. Like any web host, it may record technical data such as your IP address, browser type, pages visited, and time of visit.",
                                        "<strong>Information you send us.</strong> If you email us, we receive your email address and your message.",
                                        "<strong>Cookies and similar technology.</strong> We do not set our own tracking cookies. Third parties described below may set cookies."])),
         ("Advertising and Google AdSense", P("We may show advertisements provided by Google AdSense or other ad partners now or in the future. Google and its partners use cookies, including the DoubleClick cookie, to serve ads based on your visits to this and other websites.",
                                             "You can opt out of personalised advertising by visiting <a href='https://adssettings.google.com' style='color:#1a8fd1' rel='noopener'>Google Ads Settings</a> or <a href='https://www.aboutads.info' style='color:#1a8fd1' rel='noopener'>aboutads.info</a>. "
                                             "You can read how Google uses data at <a href='https://policies.google.com/technologies/partner-sites' style='color:#1a8fd1' rel='noopener'>policies.google.com/technologies/partner-sites</a>. "
                                             "Where the law requires it (for example in the European Economic Area and the United Kingdom), we will ask for your consent before personalised ads or non-essential cookies are used.")),
         ("Third-party services", UL(["<strong>Google Fonts</strong> loads the typeface used on this site, which means your browser contacts Google servers.",
                                      "<strong>Stock photo hosting</strong> serves many of our photographs, which load from the image provider's servers.",
                                      "<strong>Social sharing links</strong> (WhatsApp, Facebook, X) only send data when you click them."])),
         ("Children's privacy", P("Our website is for a general audience and is not directed at children under 13. We do not knowingly collect personal information from children.")),
         ("Your rights", P(f"Depending on where you live, you may have the right to ask what information we hold about you, to correct it, to delete it, or to object to its use. Contact us at {mail} to make a request.")),
         ("Changes to this policy", P("We may update this policy from time to time. The date at the top shows when it was last changed.")),
         ("Contact", P(f"Questions about this policy? Please visit our <a href='contact.html' style='color:#1a8fd1;font-weight:700'>contact page</a>."))])

    pages["terms.html"] = static_page("terms.html", "Terms of Service",
        f"The terms for using {NAME}.", f"Last updated: {e(pretty_date(updated))}",
        [("Acceptance of terms", P(f"By using {e(NAME)} you agree to these terms. If you do not agree, please do not use the website.")),
         ("Information only", P("All content is general information for education. It is <strong>not medical advice</strong> and does not create a doctor and patient relationship. See our <a href='disclaimer.html' style='color:#1a8fd1;font-weight:700'>medical disclaimer</a>.")),
         ("Acceptable use", UL(["Do not copy our content in bulk, scrape the site, or republish it without permission.", "Do not attempt to damage, overload, or gain unauthorised access to the website.", "Do not use the website to make medical decisions without consulting a qualified professional."])),
         ("Intellectual property", P(f"The text and design of this website are &copy; {YEAR} {e(NAME)}. All rights reserved. See our <a href='copyright.html' style='color:#1a8fd1;font-weight:700'>copyright page</a>.")),
         ("External links", P("We link to outside websites such as the WHO, CDC, and NHS. We do not control those sites and are not responsible for their content.")),
         ("No warranty and limitation of liability", P("The website is provided &ldquo;as is&rdquo;. We try to keep information accurate, but we make no promise that it is complete, current, or free of errors. To the fullest extent allowed by law, we are not liable for any loss or harm that results from using the website.")),
         ("Changes", P("We may change these terms at any time. Continued use means you accept the updated terms."))])

    pages["disclaimer.html"] = static_page("disclaimer.html", "Medical Disclaimer",
        "Important information about how to use the health content on this website.",
        "<strong>This website does not give medical advice. Always speak to a qualified health professional.</strong>",
        [("Not a substitute for professional care", P("Everything on this website is for general information and education only. It cannot diagnose, treat, cure, or prevent any condition, and it is not a substitute for advice from a doctor, nurse, pharmacist, or other qualified health professional.")),
         ("How our content is created", P("Our guides are checked by automated rules. They are <strong>not reviewed by doctors</strong>. Medicine changes quickly, and a guide may be incomplete, simplified, or out of date.")),
         ("Emergencies", P("<strong>If you think you are having a medical emergency, call your local emergency number immediately.</strong> Do not rely on this website in an emergency. Examples include chest pain, trouble breathing, signs of a stroke, severe bleeding, a seizure, or thoughts of harming yourself.")),
         ("No doses or personal treatment plans", P("We do not give medicine doses or tell you which treatment to use. Treatment depends on your age, health, other medicines, and local guidance. Only a professional who knows your situation can decide this.")),
         ("No doctor and patient relationship", P("Using this website or contacting us does not create a doctor and patient relationship.")),
         ("Accuracy", P(f"We work to keep information correct, but we cannot guarantee it. If you find a mistake, please <a href='contact.html' style='color:#1a8fd1;font-weight:700'>tell us</a>. Use of this information is at your own risk.")),
         ("External links and ads", P("Links to other websites and any advertisements are not endorsements. We are not responsible for products, services, or claims made by third parties."))])

    pages["copyright.html"] = static_page("copyright.html", "Copyright and Content Use",
        f"Copyright notice and content-use rules for {NAME}.", "All rights reserved.",
        [("Copyright notice", P(f"&copy; {YEAR} {e(NAME)}. All rights reserved. The text, layout, and design of this website may not be copied, reproduced, or republished without written permission.")),
         ("Sharing and quoting", P("You are welcome to link to any page. You may quote a short excerpt (a sentence or two) if you clearly credit " + e(NAME) + " and link back to the original page. Please do not republish whole articles.")),
         ("Photographs", P("Photographs on this website come from free-to-use stock photo sources and are used under their licences.")),
         ("Copyright complaints", P(f"If you believe content on this website infringes your copyright, please send us a message through the <a href='contact.html' style='color:#1a8fd1;font-weight:700'>contact page</a> with: a description of the work, the exact page address, your contact details, and a statement that you are the owner or authorised to act for the owner. We will review the request promptly and remove content where appropriate."))])

    pages["editorial-policy.html"] = static_page("editorial-policy.html", "Editorial Policy",
        f"How {NAME} researches, writes, checks, and corrects its health guides.",
        "We believe you should know exactly how our guides are made.",
        [("What we publish", P("Plain-language guides about diseases and health conditions: what they are, common symptoms, causes, risk factors, how they are diagnosed, general treatment approaches, prevention, and when to see a doctor.")),
         ("How each guide is made", UL(["A topic is chosen from our list of conditions.", "The guide is prepared using a fixed outline and strict safety rules.",
                                         "Automated checks reject a draft if it is too short, is missing sections, contains medicine doses, or makes promises such as &ldquo;guaranteed cure&rdquo;.",
                                         "The guide is published with a clear note that it is information only and has not been reviewed by a doctor."])),
         ("Review by medical professionals", P("<strong>Our guides are not currently reviewed by doctors.</strong> We do not claim medical review or expert review anywhere on this site. If that changes, we will say so on the pages that were reviewed, and name the reviewer.")),
         ("What we will not do", UL(["Give medicine doses or personal treatment plans", "Promise cures or miracle results", "Promote supplements or products as treatments", "Tell readers to stop or change prescribed treatment"])),
         ("Corrections and updates", P("We fix confirmed errors as quickly as we can and update the &ldquo;last updated&rdquo; date on the page. To report a problem, use the <a href='contact.html' style='color:#1a8fd1;font-weight:700'>contact page</a>.")),
         ("Advertising", P("Advertising, if shown, does not influence what we write. We do not accept payment to change or promote health content."))])
    return pages


# ---------------------------------------------------------------- 404, sitemap, search, misc
def page_404():
    return static_page("404.html", "Page Not Found", "The page you are looking for could not be found.",
                       "Sorry, we could not find that page.",
                       [("", P('Try the <a href="index.html" style="color:#1a8fd1;font-weight:700">home page</a>, '
                               'browse <a href="diseases.html" style="color:#1a8fd1;font-weight:700">all conditions</a>, or use the search box in the menu.'))],
                       noindex=True).replace('<head>', f'<head>\n<base href="{BASE}/">', 1)


def build_sitemap(extra_pages):
    urls = [("index.html", "1.0", "daily", date.today().isoformat()), ("diseases.html", "0.8", "daily", date.today().isoformat())]
    for slug in CATS:
        if BY_CAT[slug]:
            urls.append((f"Categories/category-{slug}.html", "0.8", "weekly", date.today().isoformat()))
    for a in ARTS.values():
        urls.append((f"Diseases/disease-{a['slug']}.html", "0.7", "monthly", a.get("updated") or date.today().isoformat()))
    for pg in extra_pages:
        if pg not in ("404.html", "search.html"):
            urls.append((pg, "0.3", "yearly", date.today().isoformat()))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for rel, pr, fr, lm in urls:
        lines.append(f"  <url><loc>{e(BASE)}/{rel}</loc><lastmod>{lm}</lastmod><changefreq>{fr}</changefreq><priority>{pr}</priority></url>")
    lines.append("</urlset>\n")
    write("sitemap.xml", "\n".join(lines))
    return len(urls)


def build_misc():
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    manifest = {
        "id": "./",
        "name": NAME,
        "short_name": "BHC Health",
        "description": "Plain-language guides to diseases, symptoms, causes, treatment and prevention.",
        "start_url": "./index.html",
        "scope": "./",
        "display": "standalone",
        "orientation": "portrait-primary",
        "background_color": SITE.get("background_color", "#ffffff"),
        "theme_color": THEME,
        "lang": "en",
        "dir": "ltr",
        "categories": ["health", "medical", "education"],
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "shortcuts": [
            {"name": "Search conditions", "short_name": "Search", "url": "./search.html",
             "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}]},
            {"name": "All conditions A to Z", "short_name": "All conditions", "url": "./diseases.html",
             "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}]},
        ],
    }
    write("manifest.json", json.dumps(manifest, indent=2) + "\n")
    idx = []
    for a in sorted(ARTS.values(), key=lambda a: a["title"].lower()):
        kw = " ".join(
            [i for sec in a["sections"] if sec["id"] in ("acc-sym", "acc-cause", "acc-risk", "acc-treat", "acc-prev") for i in sec.get("items", [])]
            + [sec.get("intro", "") for sec in a["sections"][:2]])
        kw = re.sub(r"[^a-z0-9 ]+", " ", kw.lower())
        kw = " ".join(dict.fromkeys(w for w in kw.split() if len(w) > 3))[:900]
        also = next((v for l, v in a.get("facts", []) if "also known" in l.lower()), "")
        badge = a["badges"][0] if a.get("badges") else ["badge-orange", "Guide"]
        idx.append({"t": a["title"], "u": f"Diseases/disease-{a['slug']}.html", "c": CATS[a["category"]]["h1"],
                    "cs": a["category"], "s": short(a.get("subtitle", ""), 120), "a": also.lower()[:80], "k": kw,
                    "b": badge[1], "bc": badge[0]})
    write("search-index.json", json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    if SITE.get("adsense_client"):
        pub = SITE["adsense_client"].replace("ca-", "")
        write("ads.txt", f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")
    key = SITE.get("indexnow_key")
    if key:
        write(f"{key}.txt", key)


def main():
    if not CATS:
        sys.exit("data/categories.json is missing")
    for a in ARTS.values():
        write(f"Diseases/disease-{a['slug']}.html", render_article(a))
    # remove pages whose data file was deleted, so old/test pages never linger
    for f in glob.glob("Diseases/disease-*.html"):
        if os.path.basename(f)[8:-5] not in ARTS:
            os.remove(f)
    for slug in CATS:
        write(f"Categories/category-{slug}.html", render_category(slug))
    write("diseases.html", render_all())
    write("search.html", render_search())
    write("index.html", render_index())
    statics = build_static()
    for fn, content in statics.items():
        write(fn, content)
    write("404.html", page_404())
    n = build_sitemap(list(statics))
    build_misc()
    # tidy up files from the old broken system
    for old in ("sw.js", "fix_index.py", "generate_sitemap.py"):
        if os.path.exists(old):
            os.remove(old)
    empty = [s for s in CATS if not BY_CAT[s]]
    print(f"Built {len(ARTS)} articles, {len(CATS)} categories ({len(empty)} still empty), {n} URLs in sitemap.")
    if not SITE.get("email") and not SITE.get("contact_form_url"):
        print("WARNING: set \"email\" in data/site.json - the Contact page needs a way to reach you (required for AdSense).")
    if not BASE:
        print("NOTE: site address unknown on this computer, so canonical links are empty. GitHub fills it in automatically when it builds.")


if __name__ == "__main__":
    main()
