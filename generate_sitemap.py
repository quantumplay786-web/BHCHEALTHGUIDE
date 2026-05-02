import os
from datetime import date

BASE = "https://quantumplay786-web.github.io/BHCHEALTHGUIDE-"
TODAY = date.today().isoformat()

def main():
    urls = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.git','__pycache__']]
        for file in files:
            if not file.endswith('.html'):
                continue
            rel = os.path.join(root,file).replace('.\\','').replace('./','').replace('\\','/')
            if rel == 'index.html':
                p,f = '1.0','daily'
            elif 'Categories/' in rel:
                p,f = '0.8','weekly'
            elif 'Diseases/' in rel:
                p,f = '0.7','weekly'
            else:
                p,f = '0.5','monthly'
            urls.append((f"{BASE}/{rel}",p,f))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url,p,f in urls:
        lines.append(f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{f}</changefreq>\n    <priority>{p}</priority>\n  </url>')
    lines.append('</urlset>')

    with open('sitemap.xml','w',encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Sitemap done: {len(urls)} URLs")

if __name__ == '__main__':
    main()
