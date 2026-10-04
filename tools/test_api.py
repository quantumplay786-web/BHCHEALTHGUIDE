#!/usr/bin/env python3
"""Checks that your CodeCraft keys work from THIS computer (or from GitHub). Costs about 30 tokens per key.
Never prints your key. Run it on GitHub with Actions > "Test API connection" > Run workflow."""
import os, sys
import requests

BASE = (os.environ.get("API_BASE") or "https://codecraftapi.com/v1").strip().rstrip("/")
MODEL = (os.environ.get("API_MODEL") or "").strip()
KEYS = [k.strip() for k in (os.environ.get("API_KEY", ""), os.environ.get("API_KEY_2", "")) if k and k.strip()]
if not KEYS or not MODEL:
    sys.exit("Set the API_KEY secret and the API_MODEL variable first.")

def kind(status, body):
    b = (body or "")[:1500].lower()
    if status in (403, 429, 503) and ("just a moment" in b or "cloudflare" in b or "<html" in b[:200]):
        return "BLOCKED BY FIREWALL (Cloudflare page, not an API answer)"
    if status in (401, 403):
        return "key rejected"
    if status == 402:
        return "out of tokens / payment needed"
    if status == 404:
        return "wrong address or model name"
    if status == 200:
        return "OK"
    return "unexpected"

ok_any = False
for n, key in enumerate(KEYS, 1):
    print(f"\n=== key {n} ===")
    try:
        r = requests.get(f"{BASE}/models", headers={"Authorization": f"Bearer {key}"}, timeout=40)
        print(f"list models with plain requests : HTTP {r.status_code} -> {kind(r.status_code, r.text)}")
    except Exception as ex:
        print("list models with plain requests : network error:", ex)
    try:
        import openai
        c = openai.OpenAI(api_key=key, base_url=BASE, timeout=90, max_retries=0)
        try:
            raw = c.chat.completions.with_raw_response.create(model=MODEL, max_tokens=20, messages=[{"role": "user", "content": "Say OK"}])
            body = raw.http_response.text
            print(f"tiny chat with openai package   : HTTP {raw.status_code} -> {kind(raw.status_code, body)}")
            ok_any = ok_any or raw.status_code == 200
        except openai.APIStatusError as ex:
            t = getattr(ex.response, "text", "") or str(ex)
            print(f"tiny chat with openai package   : HTTP {ex.status_code} -> {kind(ex.status_code, t)}")
            print("   first 120 characters of answer:", t[:120].replace("\n", " "))
    except ImportError:
        print("openai package not installed (pip install openai)")
    except Exception as ex:
        print("tiny chat with openai package   : error:", str(ex)[:200])

print("\nRESULT:", "at least one key works from here." if ok_any else "no key worked from here. See the lines above.")
sys.exit(0 if ok_any else 1)
