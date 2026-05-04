"""
fix_index.py
Automatically fixes index.html, all Category pages, and all Disease pages.
Run this after generate_articles.py in the GitHub Actions workflow.
"""

import re
import os

# ── CONFIG ───────────────────────────────────────
HERO_IMAGE = "https://images.unsplash.com/photo-1638202993928-7267aad84c31?w=900&q=80"

ARTICLE_IMAGES = [
    "https://images.unsplash.com/photo-1584118624012-df056829fbd0?w=600&q=80",
    "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?w=600&q=80",
    "https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=600&q=80",
    "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=600&q=80",
    "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=600&q=80",
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80",
]

CATEGORY_IMAGES = {
    "viruses":    "https://images.unsplash.com/photo-1584118624012-df056829fbd0?w=700&q=80",
    "bacteria":   "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?w=700&q=80",
    "chronic":    "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=700&q=80",
    "mental":     "https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=700&q=80",
    "skin":       "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=700&q=80",
    "children":   "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=700&q=80",
    "neuro":      "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=700&q=80",
    "psychology": "https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=700&q=80",
}

MONETAG_TAG = '<meta name="monetag" content="b3195f88c823e794e73ceaf7aa86b93d">'

AI_FIXES = [
    (r'\bexpert-reviewed\b', 'reviewed by experts'),
    (r'\bevidence-based\b', 'proven'),
    (r'\bwell-known\b', 'widely recognized'),
    (r'\blong-term\b', 'long term'),
    (r'\bshort-term\b', 'short term'),
    (r'\bhigh-risk\b', 'high risk'),
    (r'\blife-threatening\b', 'serious and potentially fatal'),
    (r'\bover-the-counter\b', 'over the counter'),
    (r'\bup-to-date\b', 'current'),
    (r'\bwell-being\b', 'wellbeing'),
    (r'\bself-care\b', 'self care'),
    (r'\s*—\s*', ', '),
    (r'\s*–\s*', ', '),
    (r'\bFurthermore,?\b', 'Also,'),
    (r'\bMoreover,?\b', 'Also,'),
    (r'\bAdditionally,?\b', 'Also,'),
    (r'\bNevertheless,?\b', 'Still,'),
    (r'\bConsequently,?\b', 'As a result,'),
    (r'\bUtilize\b', 'Use'),
    (r'\butilize\b', 'use'),
    (r'\bCrucial\b', 'Important'),
    (r'\bcrucial\b', 'important'),
    (r'\bOptimal\b', 'Best'),
    (r'\boptimal\b', 'best'),
    (r'\bIn conclusion,?\b', 'Overall,'),
    (r'\bIt is worth noting that\b', 'Note that'),
    (r'HealthGuide\s*[—–|]\s*', 'HBC Health Guide | '),
]

FAVICON_SVG = '''<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">'''


# ── SHARED HELPERS ────────────────────────────────

def remove_ads(html):
    """Remove all ad slot placeholder divs."""
    return re.sub(
        r'<div[^>]*class="[^"]*ad-slot[^"]*"[^>]*>.*?</div>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )


def fix_broken_artifacts(html):
    """Remove onerror attributes and visible '" > artifacts."""
    html = re.sub(r'''\s*onerror\s*=\s*["'][^"']*["']''', '', html, flags=re.DOTALL)
    html = re.sub(r"""['"]{1,2}\s*>(?!\s*<(?!br|p|div|span|li|ul|ol|img|a))""", '', html)
    html = re.sub(r"""^\s*['"]{1,2}>\s*$""", '', html, flags=re.MULTILINE)
    html = re.sub(r'Upload:\s*[\w/\-\.]+\.(?:jpg|jpeg|png|gif|webp)', '', html, flags=re.IGNORECASE)
    return html


def clean_ai(html):
    """Remove AI writing patterns."""
    for pattern, replacement in AI_FIXES:
        html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)
    return html


def add_monetag(html):
    """Add Monetag verification meta tag."""
    if 'monetag' not in html:
        html = html.replace('</head>', f'{MONETAG_TAG}\n</head>')
    return html


def add_favicon(html, pre=''):
    """Add favicon link tag."""
    tag = f'<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">'
    if 'favicon' not in html:
        html = html.replace('</head>', f'{tag}\n</head>')
    return html


def inject_components(html, script):
    """
    Replace old nav/footer with component placeholders.
    Prevents double nav/footer from showing.
    """
    # Remove ALL existing nav elements
    html = re.sub(r'<nav\b[^>]*>.*?</nav>', '', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*class="nav-drawer"[^>]*>.*?</div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*id="drawer"[^>]*>.*?</div>', '', html, flags=re.DOTALL)

    # Remove ALL existing footer elements
    html = re.sub(r'<footer\b[^>]*>.*?</footer>', '', html, flags=re.DOTALL)

    # Remove old inline scripts that conflict
    html = re.sub(r'<script>\s*const hbg.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script>\s*hbg\b.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script>\s*document\.querySelectorAll\(.*?</script>', '', html, flags=re.DOTALL)

    # Add nav placeholder right after <body>
    if 'nav-placeholder' not in html:
        html = html.replace('<body>', '<body>\n<div id="nav-placeholder"></div>')

    # Add share + footer placeholder before </body>
    if 'share-placeholder' not in html:
        html = html.replace('</body>', '<div id="share-placeholder"></div>\n</body>')
    if 'footer-placeholder' not in html:
        html = html.replace('</body>', '<div id="footer-placeholder"></div>\n</body>')

    # Add components.js script before </body>
    if 'components.js' not in html:
        html = html.replace('</body>', f'<script src="{script}"></script>\n</body>')

    return html


# ── FIX index.html ────────────────────────────────

def fix_index():
    path = 'index.html'
    if not os.path.exists(path):
        print(f"  Skipping: {path} not found")
        return

    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    original = html

    html = fix_broken_artifacts(html)
    html = remove_ads(html)

    # Fix hero image
    html = re.sub(
        r'<div[^>]*class="hero-img-ph"[^>]*>.*?</div>',
        f'<img src="{HERO_IMAGE}" alt="Trusted Health Guides" style="width:100%;height:370px;object-fit:cover;object-position:top center">',
        html, flags=re.DOTALL
    )
    html = re.sub(
        r'<img[^>]*(?:hero-doctors|hero)[^>]*>',
        f'<img src="{HERO_IMAGE}" alt="Trusted Health Guides" style="width:100%;height:370px;object-fit:cover;object-position:top center">',
        html, flags=re.IGNORECASE
    )
    html = re.sub(r'Upload:\s*images/hero-doctors\.jpg', '', html)

    # Fix article images
    count = [0]
    def art_img(m):
        img = ARTICLE_IMAGES[count[0] % len(ARTICLE_IMAGES)]
        count[0] += 1
        return f'<img src="{img}" alt="Health Article" style="width:100%;height:180px;object-fit:cover">'

    html = re.sub(r'<img[^>]*src="images/article-[^"]*"[^>]*>', art_img, html, flags=re.IGNORECASE)
    html = re.sub(r'<div[^>]*class="art-img-ph"[^>]*>.*?</div>', art_img, html, flags=re.DOTALL)

    # Fix internal links (index is at root level)
    html = re.sub(r'href="disease-', 'href="Diseases/disease-', html)
    html = re.sub(r'href="category-', 'href="Categories/category-', html)
    # Prevent double-fixing
    html = html.replace('href="Diseases/Diseases/', 'href="Diseases/')
    html = html.replace('href="Categories/Categories/', 'href="Categories/')

    # Fix page title
    html = re.sub(
        r'<title>.*?</title>',
        '<title>HBC Health Guide | Trusted Health Information and Disease Guides</title>',
        html
    )

    # Fix eyebrow text
    html = re.sub(r'Expert-Reviewed Health Information', 'Reviewed by Health Experts', html, flags=re.IGNORECASE)

    html = add_monetag(html)
    html = add_favicon(html, pre='')
    html = inject_components(html, 'components.js')
    html = clean_ai(html)

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  Fixed: index.html")
    else:
        print(f"  No changes: index.html")


# ── FIX Categories/*.html ─────────────────────────

def fix_categories():
    folder = 'Categories'
    if not os.path.exists(folder):
        print(f"  Skipping: {folder}/ not found")
        return

    for fn in sorted(os.listdir(folder)):
        if not fn.endswith('.html'):
            continue
        path = os.path.join(folder, fn)
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        original = html

        html = fix_broken_artifacts(html)
        html = remove_ads(html)

        # Fix category hero image
        cat = fn.replace('category-', '').replace('.html', '')
        img = CATEGORY_IMAGES.get(cat, ARTICLE_IMAGES[0])
        html = re.sub(
            r'<div[^>]*class="cat-img-ph"[^>]*>.*?</div>',
            f'<img src="{img}" alt="{cat.title()}" style="width:100%;height:160px;object-fit:cover;border-radius:14px">',
            html, flags=re.DOTALL
        )
        html = re.sub(
            r'<img[^>]*src="images/[^"]*"[^>]*>',
            f'<img src="{img}" alt="{cat.title()}" style="width:100%;height:160px;object-fit:cover;border-radius:14px">',
            html, flags=re.IGNORECASE
        )

        # Fix paths (inside Categories/ folder, so needs ../ prefix)
        if 'href="../Diseases/' not in html:
            html = re.sub(r'href="disease-', 'href="../Diseases/disease-', html)
        if 'href="../index' not in html:
            html = re.sub(r'href="index\.html', 'href="../index.html', html)
        if 'href="../style' not in html:
            html = re.sub(r'href="style\.css"', 'href="../style.css"', html)

        # Fix title
        html = re.sub(
            r'<title>.*?</title>',
            f'<title>{cat.replace("-", " ").title()} | HBC Health Guide</title>',
            html
        )

        html = add_monetag(html)
        html = add_favicon(html, pre='../')
        html = inject_components(html, '../components.js')
        html = clean_ai(html)

        if html != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  Fixed: {fn}")
        else:
            print(f"  No changes: {fn}")


# ── FIX Diseases/*.html ───────────────────────────

def fix_diseases():
    folder = 'Diseases'
    if not os.path.exists(folder):
        print(f"  Skipping: {folder}/ not found")
        return

    for fn in sorted(os.listdir(folder)):
        if not fn.endswith('.html'):
            continue
        path = os.path.join(folder, fn)
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        original = html

        html = fix_broken_artifacts(html)
        html = remove_ads(html)

        # Fix paths (inside Diseases/ folder, so needs ../ prefix)
        if 'href="../style' not in html:
            html = re.sub(r'href="style\.css"', 'href="../style.css"', html)
        if 'href="../index' not in html:
            html = re.sub(r'href="index\.html', 'href="../index.html', html)
        if 'href="../Categories/' not in html:
            html = re.sub(r'href="category-', 'href="../Categories/category-', html)
        if 'src="../components' not in html:
            html = re.sub(r'src="components\.js"', 'src="../components.js"', html)

        html = add_monetag(html)
        html = add_favicon(html, pre='../')
        html = inject_components(html, '../components.js')
        html = clean_ai(html)

        if html != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  Fixed: {fn}")


# ── MAIN ──────────────────────────────────────────

if __name__ == '__main__':
    print("\n── Fixing index.html ──────────────────────")
    fix_index()

    print("\n── Fixing Categories/*.html ───────────────")
    fix_categories()

    print("\n── Fixing Diseases/*.html ─────────────────")
    fix_diseases()

    print("\n✅ All files fixed!")
