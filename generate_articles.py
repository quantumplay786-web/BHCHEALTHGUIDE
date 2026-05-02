import os, json, re, requests
import google.generativeai as genai
from datetime import date

genai.configure(api_key=os.environ["GEMINI_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")  # free tier

UNSPLASH_KEY = os.environ["UNSPLASH_KEY"]

# Pool of topics — add as many as you want
TOPICS = [
    ("Malaria", "viruses"), ("Cholera", "bacteria"), ("Lupus", "chronic"),
    ("Bipolar Disorder", "mental"), ("Psoriasis", "skin"), ("Measles", "viruses"),
    ("Lyme Disease", "bacteria"), ("Arthritis", "chronic"), ("Schizophrenia", "mental"),
    ("Rosacea", "skin"), ("Hepatitis B", "viruses"), ("Meningitis", "bacteria"),
    ("Fibromyalgia", "chronic"), ("ADHD", "mental"), ("Ringworm", "skin"),
    ("Rabies", "viruses"), ("Tetanus", "bacteria"), ("Celiac Disease", "chronic"),
    ("Insomnia", "mental"), ("Vitiligo", "skin"), ("Zika Virus", "viruses"),
    ("Salmonella", "bacteria"), ("Thyroid Disease", "chronic"), ("Autism", "mental"),
    ("Hives", "skin"), ("Monkeypox", "viruses"), ("Whooping Cough", "bacteria"),
]

def get_image(query):
    r = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query + " medical health", "per_page": 1, "orientation": "landscape"},
        headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    )
    if r.status_code == 200:
        results = r.json().get("results", [])
        if results:
            return results[0]["urls"]["regular"]
    return ""

def generate_article(disease, category):
    prompt = f"""Write a complete, medically accurate article about {disease} for a health website.
Return ONLY a JSON object with these exact keys:
{{
  "title": "disease name",
  "subtitle": "one sentence description",
  "severity": "Low/Medium/High",
  "spread": "how it spreads",
  "incubation": "incubation period or N/A",
  "overview": "2-3 paragraph overview",
  "symptoms": ["symptom1", "symptom2", "symptom3", "symptom4", "symptom5", "symptom6"],
  "causes": ["cause1", "cause2", "cause3", "cause4"],
  "transmission": ["method1", "method2", "method3"],
  "prevention": ["tip1", "tip2", "tip3", "tip4", "tip5", "tip6"],
  "treatment": ["treatment1", "treatment2", "treatment3", "treatment4"],
  "when_to_see_doctor": "paragraph about when to seek help",
  "related": ["Related Disease 1", "Related Disease 2", "Related Disease 3"]
}}
Return ONLY the JSON, no markdown, no extra text."""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text)

def build_html(disease, category, data, img_url):
    slug = disease.lower().replace(" ", "-")
    sev_class = {"High": "badge-red", "Medium": "badge-orange", "Low": "badge-green"}.get(data["severity"], "badge-blue")
    
    symptoms_html = "".join(f'<li>{s}</li>' for s in data["symptoms"])
    causes_html = "".join(f'<li>{c}</li>' for c in data["causes"])
    transmission_html = "".join(f'<li>{t}</li>' for t in data["transmission"])
    prevention_html = "".join(f'<li>{p}</li>' for p in data["prevention"])
    treatment_html = "".join(f'<li>{t}</li>' for t in data["treatment"])
    related_html = "".join(
        f'<a href="disease-{r.lower().replace(" ","-")}.html" class="sw-link"><span class="sw-dot"></span>{r}</a>'
        for r in data["related"]
    )
    img_tag = f'<img src="{img_url}" alt="{disease}" style="width:100%;height:340px;object-fit:cover;border-radius:14px 14px 0 0">' if img_url else f'<div class="dis-img-ph">🏥<span>{disease}</span></div>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{data["title"]} – HealthGuide</title>
<meta name="description" content="{data["subtitle"]}">
<link rel="stylesheet" href="../style.css">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="../index.html" class="nav-logo">
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><rect width="32" height="32" rx="8" fill="#e3f4fd"/><rect x="14" y="6" width="4" height="20" rx="2" fill="#1a8fd1"/><rect x="6" y="14" width="20" height="4" rx="2" fill="#1a8fd1"/><circle cx="16" cy="16" r="3" fill="white"/></svg>
      HealthGuide
    </a>
    <div class="nav-links">
      <a href="../index.html">Home</a>
      <a href="../Categories/category-viruses.html" class="active">Diseases</a>
      <a href="../index.html#prevention">Prevention</a>
      <a href="../index.html#articles">Articles</a>
    </div>
  </div>
</nav>

<section class="dis-hero">
  <div class="container">
    <div class="dis-hero-inner">
      <div style="padding-bottom:40px">
        <div class="breadcrumb">
          <a href="../index.html">Home</a><span class="bc-sep">›</span>
          <a href="../Categories/category-{category}.html">{category.title()}</a><span class="bc-sep">›</span>
          <span>{data["title"]}</span>
        </div>
        <h1>{data["title"]}</h1>
        <p class="dis-sub">{data["subtitle"]}</p>
        <div class="qbar">
          <div class="qbar-item"><div class="qb-lbl">Severity</div><div class="qb-val high"><span class="{sev_class}">{data["severity"]}</span></div></div>
          <div class="qbar-item"><div class="qb-lbl">Spread Type</div><div class="qb-val">{data["spread"]}</div></div>
          <div class="qbar-item"><div class="qb-lbl">Incubation Period</div><div class="qb-val">{data["incubation"]}</div></div>
        </div>
      </div>
      <div class="dis-hero-img">{img_tag}</div>
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
        <div class="acc-body"><ul>{symptoms_html}</ul></div>
      </div>

      <div class="acc">
        <div class="acc-h"><div class="acc-iw red"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke="#c53030" stroke-width="2"/><line x1="12" y1="9" x2="12" y2="13" stroke="#c53030" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="17" r="1" fill="#c53030"/></svg></div><span class="acc-title">Causes</span></div>
        <div class="acc-body"><ul class="one">{causes_html}</ul></div>
      </div>

      <div class="acc">
        <div class="acc-h"><div class="acc-iw blue"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" stroke="#1a8fd1" stroke-width="2"/><circle cx="9" cy="7" r="4" stroke="#1a8fd1" stroke-width="2"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="#1a8fd1" stroke-width="2" stroke-linecap="round"/></svg></div><span class="acc-title">Transmission</span></div>
        <div class="acc-body"><ul class="one">{transmission_html}</ul></div>
      </div>

      <div class="acc">
        <div class="acc-h"><div class="acc-iw green"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="#4caf50" stroke-width="2"/></svg></div><span class="acc-title">Prevention</span></div>
        <div class="acc-body"><ul>{prevention_html}</ul></div>
      </div>

      <div class="acc">
        <div class="acc-h"><div class="acc-iw purple"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3" stroke="#7c3aed" stroke-width="2"/><line x1="12" y1="8" x2="12" y2="16" stroke="#7c3aed" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="12" x2="16" y2="12" stroke="#7c3aed" stroke-width="2" stroke-linecap="round"/></svg></div><span class="acc-title">Treatment</span></div>
        <div class="acc-body"><ul>{treatment_html}</ul></div>
      </div>

      <div class="acc">
        <div class="acc-h"><div class="acc-iw orange"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div><span class="acc-title">When to See a Doctor</span></div>
        <div class="acc-body"><p>{data["when_to_see_doctor"]}</p></div>
      </div>
    </main>

    <aside class="dis-side">
      <div class="sw">
        <div class="sw-head">Related Conditions</div>
        <div class="sw-body">{related_html}</div>
      </div>
      <div class="ad-slot ad-side"><span>Advertisement</span></div>
    </aside>
  </div>
</div>

<footer class="footer">
  <div class="container">
    <div class="ft-bottom">
      <p class="ft-disc"><strong>Medical Disclaimer:</strong> Content on HealthGuide is for informational purposes only. Always consult a qualified healthcare provider.</p>
      <p class="ft-copy">&copy; 2025 HealthGuide. All rights reserved.</p>
    </div>
  </div>
</footer>

<script>
document.querySelectorAll('.acc-h').forEach(h=>h.addEventListener('click',()=>h.parentElement.classList.toggle('open')));
</script>
</body>
</html>'''

def main():
    import random
    today = date.today().isoformat()
    random.shuffle(TOPICS)
    daily_topics = TOPICS[:22]  # 22 articles per day
    
    os.makedirs("Diseases", exist_ok=True)
    
    for disease, category in daily_topics:
        slug = disease.lower().replace(" ", "-")
        filepath = f"Diseases/disease-{slug}.html"
        
        print(f"Generating: {disease}...")
        try:
            data = generate_article(disease, category)
            img_url = get_image(disease)
            html = build_html(disease, category, data, img_url)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  ✅ Saved {filepath}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")

if __name__ == "__main__":
    main()
