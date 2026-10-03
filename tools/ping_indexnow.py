#!/usr/bin/env python3
"""Tell Bing, Yandex and other IndexNow search engines about pages changed in the last 2 days.
(Google does not use IndexNow. For Google, submit sitemap.xml once in Search Console.)"""
import json, os, re, sys, urllib.request
from datetime import date, timedelta
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
site = json.load(open("data/site.json"))
sm = open("sitemap.xml", encoding="utf-8").read()
first = re.search(r"<loc>(.*?)/index\.html</loc>", sm)
key = site.get("indexnow_key")
base = (site.get("base_url") or "").rstrip("/") or (first.group(1) if first else "")
if not key or not base:
    sys.exit("indexnow_key missing in data/site.json, or the sitemap has no address")
recent = {(date.today() - timedelta(days=i)).isoformat() for i in range(2)}
urls = []
for loc, last in re.findall(r"<loc>(.*?)</loc><lastmod>(.*?)</lastmod>", sm):
    if last in recent:
        urls.append(loc)
urls = urls[:500]
if not urls:
    print("No new or updated pages to send.")
    sys.exit(0)
host = urlparse(base).netloc
body = json.dumps({"host": host, "key": key, "keyLocation": f"{base}/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow accepted {len(urls)} URLs (HTTP {r.status}).")
except urllib.error.HTTPError as e:
    # 200/202 = ok. 403/422 usually mean the key file is not live yet; harmless, it retries tomorrow.
    print(f"IndexNow answered HTTP {e.code}: {e.read()[:200]!r}")
    sys.exit(0 if e.code in (202, 403, 422, 429) else 1)
