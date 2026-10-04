#!/usr/bin/env python3
"""
generate_articles.py  -  writes NEW article data files (data/articles/<slug>.json).
It never touches HTML. build.py turns the data into pages, so the design is always identical.

Settings come from environment variables (GitHub Secrets / Variables):

  API_KEY            your first key                             (required)
  API_KEY_2          second key, used automatically when the first is used up or rejected (optional)
  API_BASE           e.g. https://codecraftapi.com/v1           (default shown)
  API_MODEL          exact model name from your provider        (required)
  API_STYLE          "openai" (default) or "anthropic"
  ARTICLES_PER_DAY   default 5
  MAX_OUTPUT_TOKENS  default 6000 (cap per article)
  TOKEN_BUDGET       default 900000 tokens per month PER KEY; each key is used until it reaches this
  UNSPLASH_KEY       optional, for a matching photo per article

Test without any API (checks the whole pipeline offline):
  python generate_articles.py --test --count 2

The script EXITS WITH AN ERROR if nothing was generated, so a broken key or
model name shows up as a red failed run in GitHub Actions instead of silently
doing nothing (this is what happened with the old script).
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import date

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

SITE = json.load(open("data/site.json", encoding="utf-8"))
CATS = json.load(open("data/categories.json", encoding="utf-8"))
TOPICS = json.load(open("data/topics.json", encoding="utf-8"))

API_BASE = (os.environ.get("API_BASE") or "https://codecraftapi.com/v1").strip().rstrip("/")
KEYS = [k.strip() for k in (os.environ.get("API_KEY", ""), os.environ.get("API_KEY_2", "")) if k and k.strip()]
DEAD = set()
API_MODEL = (os.environ.get("API_MODEL") or "").strip()
API_STYLE = (os.environ.get("API_STYLE") or "openai").strip().lower()
PER_DAY = int(os.environ.get("ARTICLES_PER_DAY") or SITE.get("articles_per_day", 5))
MAX_OUT = int(os.environ.get("MAX_OUTPUT_TOKENS") or 6000)
BUDGET = int(os.environ.get("TOKEN_BUDGET") or 900000)
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY", "")
TODAY = date.today().isoformat()
MONTH = TODAY[:7]

SENSITIVE = {"mental", "psychology"}
SENSITIVE_WORDS = ("suicid", "self-harm", "eating disorder", "substance use", "addiction", "overdose")

SECTION_PLAN = [  # key in model output, id, title, color, open?, min items
    ("symptoms", "acc-sym", "Symptoms", "blue", True, 6),
    ("causes", "acc-cause", "Causes", "red", True, 4),
    ("risk_factors", "acc-risk", "Risk Factors", "red", False, 4),
    ("diagnosis", "acc-diag", "Diagnosis", "blue", False, 3),
    ("treatment", "acc-treat", "Treatment", "orange", False, 4),
    ("prevention", "acc-prev", "Prevention", "green", False, 4),
    ("complications", "acc-comp", "Possible Complications", "orange", False, 3),
    ("living_with", "acc-living", "Living With and Managing It", "green", False, 3),
    ("when_to_see_doctor", "acc-doctor", "When to See a Doctor", "red", False, 3),
]

# --------------------------------------------------------------------------- prompt
SYSTEM = """You write plain-language health information guides for a public website. You are careful, calm, and accurate.

Hard rules:
- Information only. Never give medicine doses, drug brand names, or personal treatment plans. You may name general treatment types (for example "antibiotics when a bacterial infection is confirmed") without amounts.
- Never promise a cure, never use words like "guaranteed", "miracle", or "100 percent".
- Never tell readers to stop, skip, or change prescribed treatment.
- Do not invent statistics, dates, studies, or names. Only use a number if it is widely published and stable, and round it. If unsure, describe it in words instead.
- Be honest about uncertainty. Say "may", "often", "in some people" where that is accurate.
- Write for a general reader at about a 7th grade level. Short sentences. Plain everyday words. No filler, no hype, no marketing language.
- Do not use markdown, bullet characters, asterisks, hashtags, or emojis inside the text values.
- Do not use em dashes or en dashes.
- Include clear emergency warning signs where they exist.
Return ONLY one valid JSON object. No text before or after it."""

SCHEMA = """{
  "title": "Proper condition name (add the common name in brackets only if helpful)",
  "subtitle": "One plain sentence, max 200 characters, saying what this condition is",
  "description": "Search result description, 120 to 155 characters",
  "severity": "one of: Mild, Manageable, Serious, Life Threatening, Varies",
  "contagious": "one of: Contagious, Non-Contagious",
  "onset": "one of: Sudden, Gradual, Varies",
  "vaccine": "one of: Vaccine Available, No Vaccine",
  "symptoms":   {"intro": "2 to 3 sentences", "items": ["7 to 9 full sentences, each naming a symptom and what it feels or looks like"]},
  "causes":     {"intro": "2 to 3 sentences", "items": ["5 to 7 full sentences"]},
  "risk_factors": {"intro": "1 to 2 sentences", "items": ["5 to 7 full sentences"]},
  "diagnosis":  {"intro": "2 to 3 sentences", "items": ["4 to 6 full sentences about tests and exams doctors use"]},
  "treatment":  {"intro": "2 to 3 sentences", "items": ["5 to 7 full sentences about general treatment approaches, no doses"]},
  "prevention": {"intro": "1 to 2 sentences", "items": ["5 to 7 full sentences"]},
  "complications": {"intro": "1 to 2 sentences", "items": ["4 to 6 full sentences"]},
  "living_with": {"intro": "1 to 2 sentences", "items": ["4 to 6 full sentences on daily management and outlook"]},
  "when_to_see_doctor": {"intro": "1 to 2 sentences", "items": ["4 to 6 full sentences, include emergency warning signs"]},
  "faq": [{"q": "A question real people search for", "a": "A clear answer of 2 to 3 sentences"}],
  "facts": [{"label": "Also known as", "value": "..."}, {"label": "Who is most affected", "value": "..."}, {"label": "Usual outlook", "value": "..."}],
  "related": ["3 to 5 names chosen ONLY from the list given in the request"]
}"""


def build_prompt(topic, related_pool):
    extra = ""
    if topic["category"] in SENSITIVE or any(w in topic["name"].lower() for w in SENSITIVE_WORDS):
        extra = ("\nThis is a sensitive mental health topic. Use calm, non-judgmental language. Never describe methods of self-harm. "
                 "In the 'when_to_see_doctor' section include that anyone with thoughts of harming themselves should contact local "
                 "emergency services or a crisis line in their country right away.")
    return (f"Write a guide about: {topic['name']}\nCategory: {CATS[topic['category']]['h1']}\n"
            f"Aim for about 1000 to 1300 words in total across all fields.{extra}\n\n"
            f"Candidate names for the 'related' field (choose 3 to 5 that make sense): {', '.join(related_pool)}\n\n"
            f"Return JSON in exactly this shape:\n{SCHEMA}")


# --------------------------------------------------------------------------- LLM
class AuthError(Exception):
    pass


class KeyRejected(AuthError):
    """This one key is dead or out of tokens; the other key can still be tried."""


def extract_text(data):
    """Pull the text out of OpenAI-style or Anthropic-style responses (ignores 'thinking' blocks)."""
    if "choices" in data:
        content = data["choices"][0]["message"].get("content")
        if isinstance(content, list):
            return "".join(b.get("text", "") for b in content if b.get("type") in (None, "text"))
        return content or ""
    if "content" in data:
        return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
    return ""


class CloudBlocked(AuthError):
    """The provider's firewall (Cloudflare) answered with a web page instead of the API. This is NOT a key problem."""


def looks_like_firewall(status, body):
    b = (body or "")[:1500].lower()
    return status in (403, 429, 503) and ("just a moment" in b or "cf-chl" in b or "cloudflare" in b or b.lstrip().startswith("<!doctype html") or "<html" in b[:200])


def send(prompt, key):
    """One request. Returns (status_code, response_text). Uses the official openai package when installed
    (it identifies itself as a normal API client), otherwise plain requests."""
    if API_STYLE == "anthropic":
        r = requests.post(f"{API_BASE}/v1/messages",
                          headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                          json={"model": API_MODEL, "max_tokens": MAX_OUT, "system": SYSTEM, "messages": [{"role": "user", "content": prompt}]},
                          timeout=240)
        return r.status_code, r.text
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]
    try:
        import openai
    except ImportError:
        r = requests.post(f"{API_BASE}/chat/completions", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                          json={"model": API_MODEL, "max_tokens": MAX_OUT, "messages": messages}, timeout=240)
        return r.status_code, r.text
    client = openai.OpenAI(api_key=key, base_url=API_BASE, timeout=240, max_retries=0)
    try:
        raw = client.chat.completions.with_raw_response.create(model=API_MODEL, max_tokens=MAX_OUT, messages=messages)
        return raw.status_code, raw.http_response.text
    except openai.APIStatusError as ex:
        return ex.status_code, getattr(ex.response, "text", "") or str(ex)
    except openai.APIConnectionError as ex:
        raise requests.RequestException(str(ex))


def call_llm(prompt, key):
    for attempt in range(4):
        try:
            status, text = send(prompt, key)
        except requests.RequestException as ex:
            print(f"    network error: {ex}")
            time.sleep(5 * (attempt + 1))
            continue
        if looks_like_firewall(status, text):
            raise CloudBlocked(f"HTTP {status}: the provider's firewall (Cloudflare) blocked this request and returned a web page. "
                               "Your key is NOT the problem. Run the 'Test API connection' workflow for details, "
                               "or ask CodeCraft support to allow API traffic from GitHub Actions.")
        if status in (401, 402, 403):
            raise KeyRejected(f"HTTP {status}: key rejected or out of tokens. Response: {text[:200]}")
        if status == 404:
            raise AuthError(f"HTTP 404: wrong API_BASE or model name {API_MODEL!r}. Response: {text[:200]}")
        if status == 400:
            raise AuthError(f"HTTP 400: request rejected (often a wrong model name). Response: {text[:300]}")
        if status in (429, 500, 502, 503, 529):
            wait = 15 * (attempt + 1)
            print(f"    HTTP {status}, waiting {wait}s then retrying")
            time.sleep(wait)
            continue
        if status >= 400:
            raise RuntimeError(f"HTTP {status}: {text[:200]}")
        data = json.loads(text)
        usage = data.get("usage") or {}
        tokens = usage.get("total_tokens") or (usage.get("input_tokens", 0) + usage.get("output_tokens", 0)) or \
            (usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0))
        out = extract_text(data)
        if not tokens:  # provider sent no usage numbers: estimate on the high side so the free limit is never passed
            tokens = int((len(SYSTEM) + len(prompt) + len(out)) / 3 * 1.5)
            print(f"    (no usage data from API, estimated {tokens:,} tokens)")
        return out, int(tokens)
    raise RuntimeError("LLM call failed after several retries")


def mock_llm(prompt):
    """Offline stand-in used only by --test."""
    name = re.search(r"Write a guide about: (.+)", prompt).group(1).strip()
    pool = re.search(r"\(choose 3 to 5 that make sense\): (.+)", prompt).group(1).split(", ")
    filler = f"{name} can affect daily life in different ways, and people often notice changes over several days or weeks."
    block = lambda n: {"intro": f"{filler} This section explains the main points in simple words for readers.",
                       "items": [f"{filler} Point number {i + 1} gives one more plain detail about {name} for the reader." for i in range(n)]}
    d = {"title": name, "subtitle": f"{name} is a health condition that this guide explains in plain words.",
         "description": f"Learn about {name}: common symptoms, causes, tests, treatment options, prevention, and when to see a doctor.",
         "severity": "Manageable", "contagious": "Non-Contagious", "onset": "Varies", "vaccine": "No Vaccine",
         "symptoms": block(8), "causes": block(6), "risk_factors": block(6), "diagnosis": block(5), "treatment": block(6),
         "prevention": block(6), "complications": block(5), "living_with": block(5), "when_to_see_doctor": block(5),
         "faq": [{"q": f"Question {i + 1} about {name}?", "a": f"{filler} This is a short and clear answer for the reader."} for i in range(4)],
         "facts": [{"label": "Also known as", "value": "See the guide"}, {"label": "Who is most affected", "value": "People of any age"},
                   {"label": "Usual outlook", "value": "Depends on the person"}],
         "related": pool[:4]}
    return json.dumps(d), 0


# --------------------------------------------------------------------------- parse + validate
DOSE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:mg|mcg|µg|ml|iu|units?|tablets?|pills?|capsules?)\b", re.I)
BANNED = ("guaranteed", "miracle", "100% cure", "100 percent cure", "as an ai", "language model", "i cannot", "stop taking")
SEV = {"mild", "manageable", "serious", "life threatening", "varies"}


def parse_json(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("no JSON object in reply")
    raw = text[start:end + 1]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return json.loads(re.sub(r",\s*([}\]])", r"\1", raw))


def clean(s):
    s = str(s or "")
    s = s.replace("\u2014", ", ").replace("\u2013", " to " if re.search(r"\d\u2013\d", s) else ", ")
    s = re.sub(r"[*#`_]{1,}", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def walk_text(d):
    for k, v in d.items():
        if isinstance(v, str):
            yield v
        elif isinstance(v, dict):
            yield from walk_text(v)
        elif isinstance(v, list):
            for i in v:
                if isinstance(i, str):
                    yield i
                elif isinstance(i, dict):
                    yield from walk_text(i)


def validate(d):
    problems = []
    for k in ("title", "subtitle", "severity", "contagious", "onset", "vaccine"):
        if not isinstance(d.get(k), str) or not d[k].strip():
            problems.append(f"missing {k}")
    for key, _id, _t, _c, _o, mn in SECTION_PLAN:
        sec = d.get(key)
        if not isinstance(sec, dict) or not isinstance(sec.get("items"), list) or len([i for i in sec["items"] if isinstance(i, str) and i.strip()]) < mn:
            problems.append(f"section {key} too short or missing")
    if not isinstance(d.get("faq"), list) or len(d["faq"]) < 3:
        problems.append("faq needs 3+ questions")
    text = " ".join(walk_text(d))
    words = len(text.split())
    if words < 700:
        problems.append(f"only {words} words (need 700+)")
    low = text.lower()
    for b in BANNED:
        if b in low:
            problems.append(f"banned phrase: {b}")
    m = DOSE.search(text)
    if m:
        problems.append(f"contains a dose-like amount: {m.group(0)}")
    return problems


def to_article(d, topic, related_pool_map, image, credit):
    sev = clean(d["severity"]).title() if clean(d["severity"]).lower() in SEV else "Varies"
    sev_cls = "badge-green" if sev == "Mild" else "badge-red" if sev in ("Serious", "Life Threatening") else "badge-orange"
    contagious = "Contagious" if "non" not in d["contagious"].lower() else "Non-Contagious"
    onset = clean(d["onset"]).title() if clean(d["onset"]).lower() in ("sudden", "gradual", "varies") else "Varies"
    vaccine = "Vaccine Available" if "no" not in d["vaccine"].lower() else "No Vaccine"
    sections = []
    for key, sid, title, color, open_, _mn in SECTION_PLAN:
        s = d[key]
        sections.append({"id": sid, "title": title, "color": color, "open": open_,
                         "intro": clean(s.get("intro", "")), "items": [clean(i) for i in s["items"] if clean(i)]})
    faq = [{"q": clean(x.get("q")), "a": clean(x.get("a"))} for x in d["faq"][:6] if isinstance(x, dict) and clean(x.get("q")) and clean(x.get("a"))]
    sections.append({"id": "acc-faq", "title": "Frequently Asked Questions", "color": "blue", "open": False,
                     "intro": "", "items": [], "faq": faq})
    related = []
    for name in d.get("related", []):
        slug = related_pool_map.get(clean(name).lower())
        if slug and slug != topic["slug"] and [clean(name), slug] not in related:
            related.append([clean(name), slug])
    facts = [[clean(f.get("label")), clean(f.get("value"))] for f in d.get("facts", []) if isinstance(f, dict) and clean(f.get("label")) and clean(f.get("value"))][:4]
    art = {
        "slug": topic["slug"], "category": topic["category"], "title": clean(d["title"]) or topic["name"],
        "subtitle": clean(d["subtitle"]), "description": clean(d.get("description")) or clean(d["subtitle"]),
        "badges": [[sev_cls, sev], ["badge-blue", contagious]],
        "qbar": [["Severity", sev], ["Spread", contagious], ["Onset", onset], ["Vaccine", vaccine]],
        "sections": sections, "facts": facts, "related": related, "related_label": "Related Conditions",
        "image": image, "created": TODAY, "updated": TODAY, "origin": "ai-assisted",
    }
    if credit:
        art["image_credit"] = credit
    return art


# --------------------------------------------------------------------------- images
def unsplash(query):
    if not UNSPLASH_KEY:
        return "", None
    try:
        r = requests.get("https://api.unsplash.com/search/photos",
                         params={"query": query, "per_page": 1, "orientation": "landscape", "content_filter": "high"},
                         headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"}, timeout=15)
        if r.status_code == 200 and r.json().get("results"):
            p = r.json()["results"][0]
            try:  # Unsplash asks API users to register the "download" when a photo is used
                requests.get(p["links"]["download_location"], headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"}, timeout=10)
            except Exception:
                pass
            u = p["urls"]["raw"] + ("&" if "?" in p["urls"]["raw"] else "?") + "w=900&q=80&fit=crop&auto=format"
            user = p["user"]
            return u, {"name": user.get("name", "Unsplash photographer"),
                       "link": user["links"]["html"] + "?utm_source=bhc_health_guide&utm_medium=referral"}
    except Exception as ex:
        print(f"    image lookup failed: {ex}")
    return "", None


# --------------------------------------------------------------------------- usage ledger
def load_usage():
    try:
        return json.load(open("data/usage.json"))
    except Exception:
        return {}


def save_usage(u):
    json.dump(u, open("data/usage.json", "w"), indent=1)


# --------------------------------------------------------------------------- topic picking
def pick_topics(n, only=None):
    have = {f[:-5] for f in os.listdir("data/articles") if f.endswith(".json")}
    pending = [t for t in TOPICS if t["slug"] not in have]
    if only:
        return [t for t in TOPICS if t["slug"] == only]
    counts = {c: 0 for c in CATS}
    for f in have:
        try:
            counts[json.load(open(f"data/articles/{f}.json"))["category"]] += 1
        except Exception:
            pass
    chosen = []
    while len(chosen) < n and pending:
        # always take the next topic from whichever category has the fewest guides (fills every category evenly)
        by_cat = {}
        for t in pending:
            by_cat.setdefault(t["category"], t)
        cat = min(by_cat, key=lambda c: (counts[c], list(CATS).index(c)))
        t = by_cat[cat]
        chosen.append(t)
        pending.remove(t)
        counts[cat] += 1
    return chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="offline run with fake text (no API call)")
    ap.add_argument("--count", type=int, default=PER_DAY)
    ap.add_argument("--topic", help="force one topic slug")
    args = ap.parse_args()

    if not args.test and (not KEYS or not API_MODEL):
        sys.exit("ERROR: set the API_KEY secret and the API_MODEL variable (see GUIDE.md).")
    os.makedirs("data/articles", exist_ok=True)

    usage = load_usage()

    def key_spent(i):
        return usage.get(MONTH, {}).get("keys", {}).get(str(i), 0)

    def pick_key():
        for i in range(len(KEYS)):
            if i not in DEAD and key_spent(i) < BUDGET:
                return i
        return None

    spent = usage.get(MONTH, {}).get("tokens", 0)
    if not args.test and pick_key() is None:
        print(f"Every key has reached its monthly budget of {BUDGET:,} tokens. Nothing generated today.")
        return

    todo = pick_topics(args.count, args.topic)
    if not todo:
        print("All queued topics are done. Add more to data/topics.json.")
        return
    print(f"Generating {len(todo)} article(s) for {TODAY}. Tokens used this month so far: {spent:,}")

    all_names = {t["name"].lower(): t["slug"] for t in TOPICS}
    for f in os.listdir("data/articles"):
        try:
            a = json.load(open(f"data/articles/{f}"))
            all_names[a["title"].lower()] = f[:-5]
        except Exception:
            pass

    made = failed = 0
    for topic in todo:
        if not args.test and pick_key() is None:
            print("Monthly token budget reached on all keys, stopping.")
            break
        print(f"- {topic['name']} ({topic['category']})")
        pool = [t["name"] for t in TOPICS if t["category"] == topic["category"] and t["slug"] != topic["slug"]][:30]
        prompt = build_prompt(topic, pool)
        article = None
        for attempt in range(1, 4):
            try:
                ki = None if args.test else pick_key()
                if not args.test and ki is None:
                    break
                text, tokens = mock_llm(prompt) if args.test else call_llm(prompt, KEYS[ki])
                spent += tokens
                m = usage.setdefault(MONTH, {"tokens": 0, "articles": 0})
                m["tokens"] += tokens
                if ki is not None:
                    m.setdefault("keys", {})
                    m["keys"][str(ki)] = m["keys"].get(str(ki), 0) + tokens
                data = parse_json(text)
                problems = validate(data)
                if problems:
                    print(f"    attempt {attempt} rejected: {'; '.join(problems)}")
                    continue
                img, credit = unsplash(f"{topic['name']} health") if not args.test else ("", None)
                article = to_article(data, topic, all_names, img, credit)
                print(f"    ok ({tokens:,} tokens)")
                break
            except KeyRejected as ex:
                DEAD.add(ki)
                print(f"    key {ki + 1} rejected ({ex}). Switching to the next key if there is one.")
                if pick_key() is None:
                    save_usage(usage)
                    sys.exit("ERROR: all keys rejected or used up.")
            except AuthError as ex:
                save_usage(usage)
                sys.exit(f"ERROR: {ex}")
            except Exception as ex:
                print(f"    attempt {attempt} failed: {ex}")
        if article:
            with open(f"data/articles/{topic['slug']}.json", "w", encoding="utf-8") as f:
                json.dump(article, f, indent=1, ensure_ascii=False)
            usage.setdefault(MONTH, {"tokens": 0, "articles": 0})["articles"] += 1
            made += 1
        else:
            failed += 1
        save_usage(usage)
        if not args.test:
            time.sleep(3)

    print(f"\nDone: {made} created, {failed} failed. Tokens this month: {usage.get(MONTH, {}).get('tokens', 0):,} (budget {BUDGET:,} per key)")
    if made == 0:
        sys.exit("ERROR: no article was created. See the messages above.")


if __name__ == "__main__":
    main()
