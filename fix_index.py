import re, os

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
    "viruses":    "https://images.unsplash.com/photo-1584118624012-df056829fbd0?w=600&q=80",
    "bacteria":   "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?w=600&q=80",
    "chronic":    "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=600&q=80",
    "mental":     "https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=600&q=80",
    "skin":       "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=600&q=80",
    "children":   "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80",
    "neuro":      "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=600&q=80",
    "psychology": "https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=600&q=80",
}

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
    (r'\bFurthermore,\b', 'Also,'),
    (r'\bMoreover,\b', 'Also,'),
    (r'\bAdditionally,\b', 'Also,'),
    (r'\bUtilize\b', 'Use'),
    (r'\butilize\b', 'use'),
    (r'\bcrucial\b', 'important'),
    (r'\bCrucial\b', 'Important'),
    (r'\boptimal\b', 'best'),
    (r'\bOptimal\b', 'Best'),
]

MONETAG = '<meta name="monetag" content="b3195f88c823e794e73ceaf7aa86b93d">'

def add_monetag(html):
    if 'monetag' not in html:
        html = html.replace('</head>', f'{MONETAG}\n</head>')
    return html

def remove_ads(html):
    html = re.sub(
        r'<div[^>]*class="[^"]*ad-slot[^"]*"[^>]*>.*?</div>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    return html

def fix_broken_artifacts(html):
    # Remove onerror attributes completely
    html = re.sub(r'\s*onerror\s*=\s*["\'][^"\']*["\']', '', html, flags=re.DOTALL)
    # Remove leftover '" > text visible on page
    html = re.sub(r"""['"]{1,2}\s*>(?!\s*<)""", '', html)
    html = re.sub(r"""^\s*['"]{1,2}>\s*$""", '', html, flags=re.MULTILINE)
    # Remove "Upload: filename.jpg" text
    html = re.sub(r'Upload:\s*[\w/\-\.]+\.(?:jpg|jpeg|png|gif|webp)', '', html, flags=re.IGNORECASE)
    return html

def clean_ai(html):
    for pattern, replacement in AI_FIXES:
        html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)
    return html

def inject_components(html, script):
    # Remove ALL nav elements completely
    html = re.sub(r'<nav\b[^>]*>.*?</nav>', '', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*class="nav-drawer"[^>]*>.*?</div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*id="drawer"[^>]*>.*?</div>', '', html, flags=re.DOTALL)

    # Remove ALL footer elements
    html = re.sub(r'<footer\b[^>]*>.*?</footer>', '', html, flags=re.DOTALL)

    # Remove old scripts that conflict
    html = re.sub(r'<script>\s*const hbg.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script>\s*hbg\b.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script>\s*document\.querySelectorAll.*?</script>', '', html, flags=re.DOTALL)

    # Add nav placeholder right after <body> if not there
    if 'nav-placeholder' not in html:
        html = html.replace('<body>', '<body>\n<div id="nav-placeholder"></div>')

    # Add footer placeholder before </body> if not there
    if 'footer-placeholder' not in html:
        html = html.replace('</body>', '<div id="footer-placeholder"></div>\n</body>')

    # Add components.js before </body>
    if 'components.js' not in html:
        html = html.replace('</body>', f'<script src="{script}"></script>\n</body>')

    return html

def fix_topics_grid(html):
    # Find the topics grid and ensure all 8 categories are present
    # Add neuro and psychology if missing
    neuro_card = '''<a href="Categories/category-neuro.html" class="topic-card tc-blue">
        <div class="topic-icon">
          <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
            <path d="M26 11C20 11 13 16 13 23C13 27 15 30 18 32V42H34V32C37 30 39 27 39 23C39 16 32 11 26 11Z" stroke="#1a8fd1" stroke-width="2.5" stroke-linejoin="round"/>
            <line x1="26" y1="11" x2="26" y2="42" stroke="#1a8fd1" stroke-width="2" stroke-dasharray="3 2.5"/>
          </svg>
        </div>
        <span class="topic-name">Neurological</span>
      </a>'''

    psychology_card = '''<a href="Categories/category-psychology.html" class="topic-card tc-purple">
        <div class="topic-icon">
          <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
            <circle cx="26" cy="20" r="10" stroke="#7c3aed" stroke-width="2.5"/>
            <path d="M18 42C18 36 21 33 26 33C31 33 34 36 34 42" stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="topic-name">Psychology</span>
      </a>'''

    if 'category-neuro.html' not in html:
        html = html.replace('</div>\n</section>\n\n<!-- AD',
                           neuro_card + '\n' + psychology_card + '\n</div>\n</section>\n\n<!-- AD')
    return html


def add_latest_articles_section(html):
    if 'latest-articles' in html:
        return html

    latest_section = '''
<!-- LATEST ARTICLES -->
<section style="background:#f8fafc;padding:52px 0" id="latest-articles">
  <div class="container">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px">
      <h2 class="sec-title" style="margin-bottom:0">Latest Health Articles</h2>
      <a href="Categories/category-viruses.html" style="font-size:13px;font-weight:700;color:#1a8fd1;text-decoration:none">View All →</a>
    </div>
    <div id="latest-articles-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">
      <div style="background:#fff;border-radius:14px;border:1.5px solid #dde8f0;overflow:hidden">
        <img src="https://images.unsplash.com/photo-1584118624012-df056829fbd0?w=400&q=80" style="width:100%;height:160px;object-fit:cover" alt="Article">
        <div style="padding:16px">
          <span style="display:inline-block;padding:3px 10px;background:#e3f4fd;color:#1a8fd1;border-radius:20px;font-size:11px;font-weight:700;margin-bottom:8px">Viral Disease</span>
          <h3 style="font-size:15px;font-weight:700;color:#1a232e;margin-bottom:6px;line-height:1.4">COVID-19 Vaccine Updates and What You Need to Know</h3>
          <a href="Diseases/disease-covid19.html" style="font-size:13px;font-weight:700;color:#1a8fd1;text-decoration:none">Read More →</a>
        </div>
      </div>
      <div style="background:#fff;border-radius:14px;border:1.5px solid #dde8f0;overflow:hidden">
        <img src="https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?w=400&q=80" style="width:100%;height:160px;object-fit:cover" alt="Article">
        <div style="padding:16px">
          <span style="display:inline-block;padding:3px 10px;background:#e8f5e9;color:#2e7d32;border-radius:20px;font-size:11px;font-weight:700;margin-bottom:8px">Prevention</span>
          <h3 style="font-size:15px;font-weight:700;color:#1a232e;margin-bottom:6px;line-height:1.4">How to Protect Yourself During Flu Season</h3>
          <a href="Diseases/disease-flu.html" style="font-size:13px;font-weight:700;color:#1a8fd1;text-decoration:none">Read More →</a>
        </div>
      </div>
      <div style="background:#fff;border-radius:14px;border:1.5px solid #dde8f0;overflow:hidden">
        <img src="https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=400&q=80" style="width:100%;height:160px;object-fit:cover" alt="Article">
        <div style="padding:16px">
          <span style="display:inline-block;padding:3px 10px;background:#e8f5e9;color:#2e7d32;border-radius:20px;font-size:11px;font-weight:700;margin-bottom:8px">Mental Health</span>
          <h3 style="font-size:15px;font-weight:700;color:#1a232e;margin-bottom:6px;line-height:1.4">Understanding Depression: Signs, Causes and Recovery</h3>
          <a href="Diseases/disease-depression.html" style="font-size:13px;font-weight:700;color:#1a8fd1;text-decoration:none">Read More →</a>
        </div>
      </div>
    </div>
  </div>
</section>'''

    # Insert before the footer placeholder
    html = html.replace('<div id="footer-placeholder">',
                       latest_section + '\n<div id="footer-placeholder">')
    return html


# ── FIX index.html ───────────────────────────────
def fix_index():
    path = 'index.html'
    if not os.path.exists(path):
        print("index.html not found")
        return
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    orig = html

    html = fix_broken_artifacts(html)
    html = remove_ads(html)

    # Hero image — replace placeholder div AND any existing img
    html = re.sub(
        r'<div class="hero-img-ph"[^>]*>.*?</div>',
        f'<img src="{HERO_IMAGE}" alt="Trusted Health Guides" style="width:100%;height:370px;object-fit:cover;object-position:top center">',
        html, flags=re.DOTALL
    )
    html = re.sub(
        r'<img[^>]*(?:hero-doctors|hero)[^>]*>',
        f'<img src="{HERO_IMAGE}" alt="Trusted Health Guides" style="width:100%;height:370px;object-fit:cover;object-position:top center">',
        html, flags=re.IGNORECASE
    )
    # Remove leftover text like "Upload: images/hero-doctors.jpg"
    html = re.sub(r'Upload:\s*images/hero-doctors\.jpg', '', html)

    # Article images
    count = [0]
    def art_img(m):
        img = ARTICLE_IMAGES[count[0] % len(ARTICLE_IMAGES)]
        count[0] += 1
        return f'<img src="{img}" alt="Health Article" style="width:100%;height:180px;object-fit:cover">'

    html = re.sub(r'<img[^>]*src="images/article-[^"]*"[^>]*>', art_img, html, flags=re.IGNORECASE)
    html = re.sub(r'<div class="art-img-ph"[^>]*>.*?</div>', art_img, html, flags=re.DOTALL)
    # Remove any leftover Upload text
    html = re.sub(r'Upload:\s*article-[a-z\-]+\.jpg', '', html)

    # Fix internal links — index is at root
    html = re.sub(r'href="disease-', 'href="Diseases/disease-', html)
    html = re.sub(r'href="category-', 'href="Categories/category-', html)
    # Prevent double fix
    html = html.replace('href="Diseases/Diseases/', 'href="Diseases/')
    html = html.replace('href="Categories/Categories/', 'href="Categories/')

    # Fix title
    html = re.sub(
        r'<title>.*?</title>',
        '<title>HealthGuide | Trusted Health Information and Disease Guides</title>',
        html
    )

    # Add Monetag
    html = add_monetag(html)

    # Inject components
    html = inject_components(html, 'components.js')

    html = fix_topics_grid(html)
    html = add_latest_articles_section(html)

    # AI cleanup
    html = clean_ai(html)

    if html != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print("✅ index.html fixed")
    else:
        print("  index.html — no changes needed")

# ── FIX Categories/*.html ────────────────────────
def fix_categories():
    folder = 'Categories'
    if not os.path.exists(folder):
        print("Categories/ not found")
        return
    for fn in os.listdir(folder):
        if not fn.endswith('.html'):
            continue
        path = os.path.join(folder, fn)
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        orig = html

        html = fix_broken_artifacts(html)
        html = remove_ads(html)

        # Category hero image
        cat = fn.replace('category-', '').replace('.html', '')
        img = CATEGORY_IMAGES.get(cat, ARTICLE_IMAGES[0])
        html = re.sub(
            r'<div class="cat-img-ph"[^>]*>.*?</div>',
            f'<img src="{img}" alt="{cat.title()}" style="width:100%;height:160px;object-fit:cover;border-radius:14px">',
            html, flags=re.DOTALL
        )
        html = re.sub(
            r'<img[^>]*src="images/[^"]*"[^>]*>',
            f'<img src="{img}" alt="{cat.title()}" style="width:100%;height:160px;object-fit:cover;border-radius:14px">',
            html, flags=re.IGNORECASE
        )

        # Fix paths — from inside Categories/ folder
        if 'href="../Diseases/' not in html:
            html = re.sub(r'href="disease-', 'href="../Diseases/disease-', html)
        if 'href="../index' not in html:
            html = re.sub(r'href="index\.html', 'href="../index.html', html)
        if 'href="../style' not in html:
            html = re.sub(r'href="style\.css"', 'href="../style.css"', html)

        # Fix title
        html = re.sub(
            r'<title>.*?</title>',
            f'<title>{cat.replace("-"," ").title()} | HealthGuide</title>',
            html
        )

        # Add Monetag
        html = add_monetag(html)

        # Inject components
        html = inject_components(html, '../components.js')

        # AI cleanup
        html = clean_ai(html)

        if html != orig:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ {fn} fixed")
        else:
            print(f"  {fn} — no changes")

# ── FIX Diseases/*.html ──────────────────────────
def fix_diseases():
    folder = 'Diseases'
    if not os.path.exists(folder):
        print("Diseases/ not found")
        return
    for fn in os.listdir(folder):
        if not fn.endswith('.html'):
            continue
        path = os.path.join(folder, fn)
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        orig = html

        html = fix_broken_artifacts(html)
        html = remove_ads(html)

        # Fix paths — from inside Diseases/ folder
        if 'href="../style' not in html:
            html = re.sub(r'href="style\.css"', 'href="../style.css"', html)
        if 'href="../index' not in html:
            html = re.sub(r'href="index\.html', 'href="../index.html', html)
        if 'href="../Categories/' not in html:
            html = re.sub(r'href="category-', 'href="../Categories/category-', html)
        if 'src="../components' not in html:
            html = re.sub(r'src="components\.js"', 'src="../components.js"', html)

        # Add Monetag
        html = add_monetag(html)

        # Inject components
        html = inject_components(html, '../components.js')

        # AI cleanup
        html = clean_ai(html)

        if html != orig:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ {fn} fixed")
        else:
            print(f"  {fn} — no changes")

# ── RUN ALL ──────────────────────────────────────
if __name__ == '__main__':
    print("\n── Fixing index.html ──")
    fix_index()
    print("\n── Fixing Categories ──")
    fix_categories()
    print("\n── Fixing Diseases ──")
    fix_diseases()
    print("\n🎉 All done!")
