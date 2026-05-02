import os, json, re, requests
import google.generativeai as genai
from datetime import date

genai.configure(api_key=os.environ["GEMINI_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")
UNSPLASH_KEY = os.environ["UNSPLASH_KEY"]

TOPICS = [
    ("Malaria","viruses"),("Cholera","bacteria"),("Lupus","chronic"),
    ("Bipolar Disorder","mental"),("Psoriasis","skin"),("Measles","viruses"),
    ("Lyme Disease","bacteria"),("Arthritis","chronic"),("Schizophrenia","mental"),
    ("Rosacea","skin"),("Hepatitis B","viruses"),("Meningitis","bacteria"),
    ("Fibromyalgia","chronic"),("ADHD","mental"),("Ringworm","skin"),
    ("Rabies","viruses"),("Tetanus","bacteria"),("Celiac Disease","chronic"),
    ("Insomnia","mental"),("Vitiligo","skin"),("Zika Virus","viruses"),
    ("Salmonella","bacteria"),("Thyroid Disease","chronic"),("Autism","mental"),
    ("Hives","skin"),("Monkeypox","viruses"),("Whooping Cough","bacteria"),
    ("Kidney Stones","chronic"),("Gout","chronic"),("Cataracts","chronic"),
    ("Glaucoma","chronic"),("Scabies","skin"),("Cold Sores","viruses"),
    ("Sepsis","bacteria"),("Polio","viruses"),("Mumps","viruses"),
    ("Chickenpox","viruses"),("Shingles","viruses"),("Anemia","chronic"),
    ("Osteoporosis","chronic"),("Irritable Bowel Syndrome","chronic"),
    ("Crohns Disease","chronic"),("Panic Disorder","mental"),
    ("Eating Disorders","mental"),("Sleep Apnea","chronic"),("Vertigo","chronic"),
    ("Diphtheria","bacteria"),("Leprosy","bacteria"),("Brucellosis","bacteria"),
    ("Yellow Fever","viruses"),("West Nile Virus","viruses"),
]

def get_image(query):
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query + " medical health", "per_page": 1, "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            timeout=10
        )
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                return results[0]["urls"]["regular"]
    except:
        pass
    return "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&q=80"

def generate_article(disease, category):
    prompt = f"""Write a medically accurate article about {disease}.

STRICT RULES:
- Write like a doctor talking to a patient. Short sentences. Plain words.
- NEVER use hyphens to join words (no well-known, long-term, evidence-based, up-to-date)
- NEVER use em dashes or en dashes
- NEVER use: furthermore, moreover, additionally, consequently, utilize, crucial, optimal
- No filler phrases like "It is worth noting" or "In conclusion"

Return ONLY valid JSON, no markdown, no backticks:
{{
  "title": "disease name",
  "subtitle": "one plain sentence about what it is",
  "severity": "Low or Medium or High",
  "spread": "how it spreads in plain words",
  "incubation": "time range or N/A",
  "overview": "2 short plain paragraphs joined as one string",
  "symptoms": ["symptom 1","symptom 2","symptom 3","symptom 4","symptom 5","symptom 6"],
  "causes": ["cause 1","cause 2","cause 3","cause 4"],
  "transmission": ["way 1","way 2","way 3"],
  "prevention": ["tip 1","tip 2","tip 3","tip 4","tip 5","tip 6"],
  "treatment": ["treatment 1","treatment 2","treatment 3","treatment 4"],
  "when_to_see_doctor": "one short paragraph in plain language",
  "related": ["Disease Name","Disease Name","Disease Name"]
}}"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = re.sub(r'^```json\s*','',text)
    text = re.sub(r'\s*```$','',text)
    return json.loads(text)

def build_html(disease, category, data, img_url):
    slug = disease.lower().replace(" ","-")
    sev_class = {"High":"badge-red","Medium":"badge-orange","Low":"badge-green"}.get(data["severity"],"badge-blue")
    li = lambda items: "".join(f'<li>{i}</li>' for i in items)
    related = "".join(
        f'<a href="disease-{r.lower().replace(" ","-")}.html" class="sw-link"><span class="sw-dot"></span>{r}</a>'
        for r in data["related"]
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{data["title"]} | HealthGuide</title>
<meta name="description" content="{data["subtitle"]}">
<meta property="og:title" content="{data["title"]} | HealthGuide">
<meta property="og:description" content="{data["subtitle"]}">
<meta property="og:image" content="{img_url}">
<meta property="og:type" content="article">
<link rel="stylesheet" href="../style.css">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
<div id="nav-placeholder"></div>

<section class="dis-hero">
  <div class="container">
    <div class="dis-hero-inner">
      <div style="padding-bottom:40px">
        <div class="breadcrumb">
          <a href="../index.html">Home</a>
          <span class="bc-sep">›</span>
          <a href="../Categories/category-{category}.html">{category.title()}</a>
          <span class="bc-sep">›</span>
          <span>{data["title"]}</span>
        </div>
        <h1>{data["title"]}</h1>
        <p class="dis-sub">{data["subtitle"]}</p>
        <div class="qbar">
          <div class="qbar-item"><div class="qb-lbl">Severity</div><div class="qb-val"><span class="{sev_class}">{data["severity"]}</span></div></div>
          <div class="qbar-item"><div class="qb-lbl">Spread Type</div><div class="qb-val">{data["spread"]}</div></div>
          <div class="qbar-item"><div class="qb-lbl">Incubation Period</div><div class="qb-val">{data["incubation"]}</div></div>
        </div>
      </div>
      <div class="dis-hero-img">
        <img src="{img_url}" alt="{disease}" style="width:100%;height:340px;object-fit:cover;border-radius:14px 14px 0 0">
      </div>
    </div>
  </div>
</section>

<div class="container">
  <div class="dis-layout">
    <main class="dis-main">
      <div class="acc open">
        <div class="acc-h"><div class="acc-iw blue"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#1a8fd1" stroke-width="2"/><line x1="12" y1="8" x2="12" y2="12" stroke="#1a8fd1" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="16" r="1" fill="#1a8fd1"/></svg></div><span class="acc-title">Overview</span></div>
        <div class="acc-body"><p>{data["overview"]}</p></div>
      </div>
      <div class="acc open">
        <div class="acc-h"><div class="acc-iw orange"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="#f97316" stroke-width="2" fill="#f97316" fill-opacity=".2"/></svg></div><span class="acc-title">Symptoms</span></div>
        <div class="acc-body"><ul>{li(data["symptoms"])}</ul></div>
      </div>
      <div class="acc">
        <div class="acc-h"><div class="acc-iw red"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke="#c53030" stroke-width="2"/><line x1="12" y1="9" x2="12" y2="13" stroke="#c53030" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="17" r="1" fill="#c53030"/></svg></div><span class="acc-title">Causes</span></div>
        <div class="acc-body"><ul class="one">{li(data["causes"])}</ul></div>
      </div>
      <div class="acc">
        <div class="acc-h"><div class="acc-iw blue"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" stroke="#1a8fd1" stroke-width="2"/><circle cx="9" cy="7" r="4" stroke="#1a8fd1" stroke-width="2"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="#1a8fd1" stroke-width="2" stroke-linecap="round"/></svg></div><span class="acc-title">Transmission</span></div>
        <div class="acc-body"><ul class="one">{li(data["transmission"])}</ul></div>
      </div>
      <div class="acc">
        <div class="acc-h"><div class="acc-iw green"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="#4caf50" stroke-width="2"/></svg></div><span class="acc-title">Prevention</span></div>
        <div class="acc-body"><ul>{li(data["prevention"])}</ul></div>
      </div>
      <div class="acc">
        <div class="acc-h"><div class="acc-iw purple"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3" stroke="#7c3aed" stroke-width="2"/><line x1="12" y1="8" x2="12" y2="16" stroke="#7c3aed" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="12" x2="16" y2="12" stroke="#7c3aed" stroke-width="2" stroke-linecap="round"/></svg></div><span class="acc-title">Treatment</span></div>
        <div class="acc-body"><ul>{li(data["treatment"])}</ul></div>
      </div>
      <div class="acc">
        <div class="acc-h"><div class="acc-iw orange"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div><span class="acc-title">When to See a Doctor</span></div>
        <div class="acc-body"><p>{data["when_to_see_doctor"]}</p></div>
      </div>
    </main>
    <aside class="dis-side">
      <div class="sw">
        <div class="sw-head">Related Conditions</div>
        <div class="sw-body">{related}</div>
      </div>
    </aside>
  </div>
</div>

<div id="share-placeholder"></div>
<div id="footer-placeholder"></div>
<script src="../components.js"></script>
</body>
</html>'''

def main():
    import random
    random.shuffle(TOPICS)
    daily = TOPICS[:22]
    os.makedirs("Diseases", exist_ok=True)
    for disease, category in daily:
        slug = disease.lower().replace(" ","-")
        path = f"Diseases/disease-{slug}.html"
        print(f"Generating: {disease}...")
        try:
            data = generate_article(disease, category)
            img = get_image(disease)
            html = build_html(disease, category, data, img)
            with open(path,"w",encoding="utf-8") as f:
                f.write(html)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  Failed {disease}: {e}")

if __name__ == "__main__":
    main()
