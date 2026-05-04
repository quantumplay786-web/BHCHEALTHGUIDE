"""
generate_sitemap.py
Auto-generates sitemap.xml with all HTML pages.
Run this after generate_articles.py and fix_index.py.
"""

import os
from datetime import date

# UPDATE THIS to your actual GitHub Pages URL
BASE_URL = "https://quantumplay786-web.github.io/BHCHEALTHGUIDE-"
TODAY = date.today().isoformat()


def main():
    urls = []

    for root, dirs, files in os.walk('.'):
        # Skip hidden folders and Python cache
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.github', 'node_modules']]

        for filename in files:
            if not filename.endswith('.html'):
                continue

            rel = os.path.join(root, filename)
            rel = rel.replace('.\\', '').replace('./', '').replace('\\', '/')

            # Assign priority and change frequency
            if rel == 'index.html':
                priority = '1.0'
                freq = 'daily'
            elif rel.startswith('Categories/'):
                priority = '0.8'
                freq = 'weekly'
            elif rel.startswith('Diseases/'):
                priority = '0.7'
                freq = 'weekly'
            else:
                priority = '0.5'
                freq = 'monthly'

            full_url = f"{BASE_URL}/{rel}"
            urls.append((full_url, priority, freq))

    # Sort for cleanliness
    urls.sort(key=lambda x: x[0])

    # Build XML
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for url, priority, freq in urls:
        lines.append(f'''  <url>
    <loc>{url}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>''')

    lines.append('</urlset>')

    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Sitemap generated: {len(urls)} URLs → sitemap.xml")


if __name__ == '__main__':
    main()
