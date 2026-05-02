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
    (r'\bexpert-reviewed\b','reviewed by experts'),
    (r'\bevidence-based\b','proven'),
    (r'\bwell-known\b','widely recognized'),
    (r'\blong-term\b','long term'),
    (r'\bshort-term\b','short term'),
    (r'\bhigh-risk\b','high risk'),
    (r'\blife-threatening\b','serious and potentially fatal'),
    (r'\bover-the-counter\b','over the counter'),
    (r'\bup-to-date\b','current'),
    (r'\bwell-being\b','wellbeing'),
    (r'\bself-care\b','self care'),
    (r'\s*—\s*',', '),
    (r'\s*–\s*',', '),
    (r'\bFurthermore,\b','Also,'),
    (r'\bMoreover,\b','Also,'),
    (r'\bAdditionally,\b','Also,'),
    (r'\bUtilize\b','Use'),
    (r'\butilize\b','use'),
    (r'\bcrucial\b','important'),
    (r'\boptimal\b','best'),
]

def remove_ads(html):
    return re.sub(r'<div[^>]*class="[^"]*ad-slot[^"]*"[^>]*>.*?</div>','',html,flags=re.DOTALL|re.IGNORECASE)

def clean_ai(html):
    for p,r in AI_FIXES:
        html = re.sub(p,r,html,flags=re.IGNORECASE)
    return html

def inject_components(html, script):
    html = re.sub(r'<nav\b[^>]*>.*?</nav>','<div id="nav-placeholder"></div>',html,flags=re.DOTALL)
    html = re.sub(r'<div class="nav-drawer"[^>]*>.*?</div>','',html,flags=re.DOTALL)
    html = re.sub(r'<footer\b[^>]*>.*?</footer>','<div id="footer-placeholder"></div>',html,flags=re.DOTALL)
    html = re.sub(r'<script>\s*const hbg.*?</script>','',html,flags=re.DOTALL)
    html = re.sub(r'<script>\s*document\.querySelectorAll.*?</script>','',html,flags=re.DOTALL)
    if 'components.js' not in html:
        html = html.replace('</body>',f'<script src="{script}"></script>\n</body>')
    return html

def safe_replace(html, old, new):
    # Prevent double replacing
    if new in html:
        return html
    return html.replace(old, new)

# ── index.html ──────────────────────────────────
def fix_index():
    if not os.path.exists('index.html'):
        return
    with open('index.html','r',encoding='utf-8') as f:
        html = f.read()
    orig = html

    html = remove_ads(html)

    # Hero image
    html = re.sub(r'<img[^>]*hero-doctors[^>]*>',
        f'<img src="{HERO_IMAGE}" alt="Trusted Health Guides" style="width:100%;height:370px;object-fit:cover;object-position:top center">',
        html, flags=re.IGNORECASE)
    html = re.sub(r'<div class="hero-img-ph"[^>]*>.*?</div>',
        f'<img src="{HERO_IMAGE}" alt="Trusted Health Guides" style="width:100%;height:370px;object-fit:cover;object-position:top center">',
        html, flags=re.DOTALL)

    # Article images
    count = [0]
    def art_img(m):
        img = ARTICLE_IMAGES[count[0] % len(ARTICLE_IMAGES)]
        count[0] += 1
        return f'<img src="{img}" alt="Health Article" style="width:100%;height:180px;object-fit:cover">'
    html = re.sub(r'<img[^>]*src="images/article-[^"]*"[^>]*>',art_img,html,flags=re.IGNORECASE)
    html = re.sub(r'<div class="art-img-ph"[^>]*>.*?</div>',art_img,html,flags=re.DOTALL)

    # Fix links
    html = re.sub(r'href="disease-','href="Diseases/disease-',html)
    html = re.sub(r'href="category-','href="Categories/category-',html)
    html = html.replace('href="Diseases/Diseases/','href="Diseases/')
    html = html.replace('href="Categories/Categories/','href="Categories/')

    # Title
    html = re.sub(r'<title>.*?</title>',
        '<title>HealthGuide | Trusted Health Information and Disease Guides</title>',html)

    html = inject_components(html,'components.js')
    html = clean_ai(html)

    if html != orig:
        with open('index.html','w',encoding='utf-8') as f:
            f.write(html)
        print("✅ index.html fixed")

# ── Categories/*.html ────────────────────────────
def fix_categories():
    folder = 'Categories'
    if not os.path.exists(folder):
        return
    for fn in os.listdir(folder):
        if not fn.endswith('.html'):
            continue
        path = os.path.join(folder,fn)
        with open(path,'r',encoding='utf-8') as f:
            html = f.read()
        orig = html

        html = remove_ads(html)

        cat = fn.replace('category-','').replace('.html','')
        img = CATEGORY_IMAGES.get(cat, ARTICLE_IMAGES[0])
        html = re.sub(r'<div class="cat-img-ph"[^>]*>.*?</div>',
            f'<img src="{img}" alt="{cat.title()}" style="width:100%;height:160px;object-fit:cover;border-radius:14px">',
            html,flags=re.DOTALL)
        html = re.sub(r'<img[^>]*src="images/[^"]*"[^>]*>',
            f'<img src="{img}" alt="{cat.title()}" style="width:100%;height:160px;object-fit:cover;border-radius:14px">',
            html,flags=re.IGNORECASE)

        # Fix links — from Categories/ folder
        html = re.sub(r'href="disease-','href="../Diseases/disease-',html)
        html = re.sub(r'href="index\.html','href="../index.html',html)
        html = re.sub(r'href="style\.css"','href="../style.css"',html)
        # Prevent double fixing
        html = html.replace('href="../Diseases/../Diseases/','href="../Diseases/')
        html = html.replace('href="../index.html"/../','href="../')
        html = html.replace('href="../style.css"/../','href="../')

        html = re.sub(r'<title>.*?</title>',
            f'<title>{cat.replace("-"," ").title()} | HealthGuide</title>',html)

        html = inject_components(html,'../components.js')
        html = clean_ai(html)

        if html != orig:
            with open(path,'w',encoding='utf-8') as f:
                f.write(html)
            print(f"✅ {fn} fixed")

# ── Diseases/*.html ──────────────────────────────
def fix_diseases():
    folder = 'Diseases'
    if not os.path.exists(folder):
        return
    for fn in os.listdir(folder):
        if not fn.endswith('.html'):
            continue
        path = os.path.join(folder,fn)
        with open(path,'r',encoding='utf-8') as f:
            html = f.read()
        orig = html

        html = remove_ads(html)

        # Fix paths — from Diseases/ folder
        html = re.sub(r'href="style\.css"','href="../style.css"',html)
        html = re.sub(r'href="index\.html','href="../index.html',html)
        html = re.sub(r'href="category-','href="../Categories/category-',html)
        html = re.sub(r'src="components\.js"','src="../components.js"',html)
        # Prevent double fixing
        html = html.replace('href="../Categories/../Categories/','href="../Categories/')

        html = inject_components(html,'../components.js')
        html = clean_ai(html)

        if html != orig:
            with open(path,'w',encoding='utf-8') as f:
                f.write(html)
            print(f"✅ {fn} fixed")

if __name__ == '__main__':
    print("── Fixing index.html ──")
    fix_index()
    print("── Fixing Categories ──")
    fix_categories()
    print("── Fixing Diseases ──")
    fix_diseases()
    print("\n🎉 All done!")
