import os, json, re, requests
import google.generativeai as genai
from datetime import date

genai.configure(api_key=os.environ["GEMINI_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")
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
    ("Osteoporosis","chronic"),("Crohns Disease","chronic"),("Panic Disorder","mental"),
    ("Eating Disorders","mental"),("Sleep Apnea","chronic"),("Vertigo","chronic"),
    ("Diphtheria","bacteria"),("Yellow Fever","viruses"),("Epilepsy","neuro"),
    ("Migraine","neuro"),("Alzheimers","neuro"),("Parkinsons","neuro"),
    ("Multiple Sclerosis","neuro"),("Anxiety Disorder","psychology"),
    ("OCD","psychology"),("PTSD","psychology"),("Phobias","psychology"),
]

def get_image(query):
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query + " medical health doctor", "per_page": 1, "orientation": "landscape"},
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
    prompt = f"""Write a detailed, medically accurate article about {disease} for a health website.

STRICT RULES:
- Write like a doctor talking directly to a patient. Short sentences. Plain words.
- NEVER use hyphens to join words (no well-known, long-term, evidence-based, up-to-date, high-risk)
- NEVER use em dashes or en dashes
- NEVER use: furthermore, moreover, additionally, consequently, utilize, crucial, optimal
- No filler phrases

Return ONLY valid JSON with no markdown or backticks:
{{
  "title": "Full disease name",
  "subtitle": "One plain sentence describing what it is",
  "severity": "Low or Medium or High or Common",
  "spread": "How it spreads in 2 to 4 plain words",
  "incubation": "Time range like 2 to 14 Days or N/A",
  "vaccine": "Available or Not Available or In Development",
  "overview": "Two short paragraphs as one string, plain language",
  "symptoms": [
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom"}},
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom"}},
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom"}},
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom"}},
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom"}}
  ],
  "causes_overview": "One short paragraph about causes",
  "causes": ["cause 1", "cause 2", "cause 3", "cause 4"],
  "transmission_overview": "One short paragraph about how it spreads",
  "transmission": ["way 1", "way 2", "way 3", "way 4"],
  "prevention_overview": "One short paragraph about prevention",
  "prevention": ["tip 1", "tip 2", "tip 3", "tip 4", "tip 5"],
  "treatment_overview": "One short paragraph about treatment",
  "treatment": ["treatment 1", "treatment 2", "treatment 3", "treatment 4"],
  "diagnosis_overview": "One short paragraph about how it is diagnosed",
  "diagnosis": ["method 1", "method 2", "method 3"],
  "quick_facts": {{
    "also_known_as": "Other common names",
    "affected_organs": "Main organs affected",
    "recovery_time": "Typical recovery time",
    "contagious": "Yes or No or Sometimes"
  }},
  "when_to_see_doctor": "One short plain paragraph",
  "related": ["Disease Name", "Disease Name", "Disease Name", "Disease Name", "Disease Name"]
}}"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text)

def build_html(disease, category, data, img_url):
    slug = disease.lower().replace(" ", "-").replace("'", "")

    sev_colors = {
        "High": ("#fff0f0", "#c53030"),
        "Medium": ("#fff4e6", "#c2410c"),
        "Low": ("#e8f5e9", "#2e7d32"),
        "Common": ("#fff4e6", "#c2410c"),
    }
    sev_bg, sev_color = sev_colors.get(data["severity"], ("#e3f4fd", "#1a8fd1"))

    vaccine_color = "#2e7d32" if data["vaccine"] == "Available" else "#c53030"
    vaccine_icon = "✓" if data["vaccine"] == "Available" else "✗"

    # Symptoms HTML
    sym_icons = ["🔴", "🔵", "🟢", "🟠", "🟣", "🔴", "🔵"]
    symptoms_html = ""
    for i, s in enumerate(data["symptoms"]):
        symptoms_html += f'''
        <div style="background:#f8fafc;border-radius:10px;padding:16px 18px;display:flex;align-items:flex-start;gap:14px;margin-bottom:10px">
          <span style="font-size:20px;flex-shrink:0">{sym_icons[i % len(sym_icons)]}</span>
          <div>
            <div style="font-size:15px;font-weight:700;color:#1a232e;margin-bottom:3px">{s["name"]}</div>
            <div style="font-size:13px;color:#94a3b8">{s["description"]}</div>
          </div>
          <span style="margin-left:auto;color:#cbd5e1;font-size:18px">›</span>
        </div>'''

    causes_li = "".join(f'<li style="display:flex;align-items:flex-start;gap:8px;font-size:14px;color:#4a5568;margin-bottom:8px"><span style="width:8px;height:8px;background:#1a8fd1;border-radius:50%;margin-top:6px;flex-shrink:0"></span>{c}</li>' for c in data["causes"])
    transmission_li = "".join(f'<li style="display:flex;align-items:flex-start;gap:8px;font-size:14px;color:#4a5568;margin-bottom:8px"><span style="width:8px;height:8px;background:#1a8fd1;border-radius:50%;margin-top:6px;flex-shrink:0"></span>{t}</li>' for t in data["transmission"])
    prevention_li = "".join(f'<li style="display:flex;align-items:flex-start;gap:8px;font-size:14px;color:#4a5568;margin-bottom:8px"><span style="width:8px;height:8px;background:#4caf50;border-radius:50%;margin-top:6px;flex-shrink:0"></span>{p}</li>' for p in data["prevention"])
    treatment_li = "".join(f'<li style="display:flex;align-items:flex-start;gap:8px;font-size:14px;color:#4a5568;margin-bottom:8px"><span style="width:8px;height:8px;background:#7c3aed;border-radius:50%;margin-top:6px;flex-shrink:0"></span>{t}</li>' for t in data["treatment"])
    diagnosis_li = "".join(f'<li style="display:flex;align-items:flex-start;gap:8px;font-size:14px;color:#4a5568;margin-bottom:8px"><span style="width:8px;height:8px;background:#1a8fd1;border-radius:50%;margin-top:6px;flex-shrink:0"></span>{d}</li>' for d in data["diagnosis"])

    related_html = ""
    for r in data["related"]:
        r_slug = r.lower().replace(" ", "-").replace("'", "")
        related_html += f'<div style="padding:14px 0;border-bottom:1px solid #f0f4f8;display:flex;align-items:center;gap:10px"><span style="width:10px;height:10px;border-radius:50%;border:2px solid #1a8fd1;display:inline-block;flex-shrink:0"></span><a href="disease-{r_slug}.html" style="font-size:14px;color:#1a232e;text-decoration:none;font-weight:500">{r}</a></div>'

    qf = data.get("quick_facts", {})

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{data["title"]} | HealthGuide</title>
<meta name="description" content="{data["subtitle"]}">
<meta name="monetag" content="b3195f88c823e794e73ceaf7aa86b93d">
<meta property="og:title" content="{data["title"]} | HealthGuide">
<meta property="og:description" content="{data["subtitle"]}">
<meta property="og:image" content="{img_url}">
<meta property="og:type" content="article">
<link rel="stylesheet" href="../style.css">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
.acc-section{{background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);margin-bottom:16px;overflow:hidden}}
.acc-section-h{{display:flex;align-items:center;gap:12px;padding:18px 20px;cursor:pointer;user-select:none}}
.acc-section-body{{padding:0 20px;max-height:0;overflow:hidden;transition:max-height .35s ease,padding .25s ease}}
.acc-section.open .acc-section-body{{padding:4px 20px 22px;max-height:2000px}}
.acc-icon{{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:18px}}
.acc-chevron{{margin-left:auto;color:#94a3b8;transition:transform .25s ease;font-size:20px}}
.acc-section.open .acc-chevron{{transform:rotate(180deg)}}
</style>
</head>
<body>
<div id="nav-placeholder"></div>

<section style="background:linear-gradient(130deg,#d6ebf7 0%,#e8f4fd 55%,#f0f8ff 100%);padding:40px 0 0;border-bottom:1.5px solid #dde8f0">
  <div class="container">
    <div class="breadcrumb">
      <a href="../index.html">Home</a>
      <span class="bc-sep">›</span>
      <a href="../Categories/category-{category}.html">{category.replace("-"," ").title()}</a>
      <span class="bc-sep">›</span>
      <span>{data["title"]}</span>
    </div>

    <div style="display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap">
      <span style="display:inline-block;padding:4px 12px;background:{sev_bg};color:{sev_color};border-radius:20px;font-size:12px;font-weight:700">{data["severity"]} Risk</span>
      <span style="display:inline-block;padding:4px 12px;background:#e3f4fd;color:#1a8fd1;border-radius:20px;font-size:12px;font-weight:700">{category.replace("-"," ").title()} Disease</span>
    </div>

    <h1 style="font-size:clamp(28px,4vw,42px);font-weight:800;color:#1a232e;margin-bottom:10px;line-height:1.2">{data["title"]}</h1>
    <p style="font-size:15px;color:#4a5568;max-width:600px;line-height:1.7;margin-bottom:28px">{data["subtitle"]}</p>

    <div style="background:#fff;border-radius:14px;padding:0;margin-bottom:0;overflow:hidden;border:1.5px solid #dde8f0">
      <div style="display:grid;grid-template-columns:1fr 1fr;border-bottom:1.5px solid #f0f4f8">
        <div style="padding:18px 20px;border-right:1.5px solid #f0f4f8">
          <div style="font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px">SEVERITY</div>
          <div style="font-size:15px;font-weight:700;color:{sev_color};display:flex;align-items:center;gap:6px">
            <span>⚠</span> {data["severity"]}
          </div>
        </div>
        <div style="padding:18px 20px">
          <div style="font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px">SPREAD TYPE</div>
          <div style="font-size:15px;font-weight:700;color:#1a232e;display:flex;align-items:center;gap:6px">
            <span>🦠</span> {data["spread"]}
          </div>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr">
        <div style="padding:18px 20px;border-right:1.5px solid #f0f4f8">
          <div style="font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px">INCUBATION</div>
          <div style="font-size:15px;font-weight:700;color:#1a232e;display:flex;align-items:center;gap:6px">
            <span>🕐</span> {data["incubation"]}
          </div>
        </div>
        <div style="padding:18px 20px">
          <div style="font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px">VACCINE</div>
          <div style="font-size:15px;font-weight:700;color:{vaccine_color};display:flex;align-items:center;gap:6px">
            <span>{vaccine_icon}</span> {data["vaccine"]}
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<div style="background:#fff;padding:0">
  <img src="{img_url}" alt="{disease}" style="width:100%;height:280px;object-fit:cover;display:block">
</div>

<div class="container" style="padding-top:28px;padding-bottom:60px">
  <div style="display:grid;grid-template-columns:1fr 320px;gap:24px">
    <main>

      <div class="acc-section open">
        <div class="acc-section-h" onclick="this.parentElement.classList.toggle('open')">
          <div class="acc-icon" style="background:#e3f4fd"><span>📍</span></div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Symptoms</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-section-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.7;margin-bottom:14px">{data["overview"]}</p>
          {symptoms_html}
        </div>
      </div>

      <div class="acc-section open">
        <div class="acc-section-h" onclick="this.parentElement.classList.toggle('open')">
          <div class="acc-icon" style="background:#fff0f0"><span>🎯</span></div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Causes</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-section-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.7;margin-bottom:14px">{data["causes_overview"]}</p>
          <ul style="list-style:none;padding:0;margin:0">{causes_li}</ul>
        </div>
      </div>

      <div class="acc-section open">
        <div class="acc-section-h" onclick="this.parentElement.classList.toggle('open')">
          <div class="acc-icon" style="background:#e3f4fd"><span>🤝</span></div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Transmission</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-section-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.7;margin-bottom:14px">{data["transmission_overview"]}</p>
          <ul style="list-style:none;padding:0;margin:0">{transmission_li}</ul>
        </div>
      </div>

      <div class="acc-section">
        <div class="acc-section-h" onclick="this.parentElement.classList.toggle('open')">
          <div class="acc-icon" style="background:#e8f5e9"><span>🛡</span></div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Prevention</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-section-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.7;margin-bottom:14px">{data["prevention_overview"]}</p>
          <ul style="list-style:none;padding:0;margin:0">{prevention_li}</ul>
        </div>
      </div>

      <div class="acc-section">
        <div class="acc-section-h" onclick="this.parentElement.classList.toggle('open')">
          <div class="acc-icon" style="background:#f0eaff"><span>💊</span></div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Treatment</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-section-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.7;margin-bottom:14px">{data["treatment_overview"]}</p>
          <ul style="list-style:none;padding:0;margin:0">{treatment_li}</ul>
        </div>
      </div>

      <div class="acc-section">
        <div class="acc-section-h" onclick="this.parentElement.classList.toggle('open')">
          <div class="acc-icon" style="background:#e3f4fd"><span>🔍</span></div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Diagnosis</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-section-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.7;margin-bottom:14px">{data["diagnosis_overview"]}</p>
          <ul style="list-style:none;padding:0;margin:0">{diagnosis_li}</ul>
        </div>
      </div>

      <div style="background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);padding:22px;margin-bottom:16px">
        <h3 style="font-size:16px;font-weight:800;color:#1a232e;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid #f0f4f8">Quick Facts</h3>
        <div style="padding:12px 0;border-bottom:1px solid #f0f4f8"><span style="font-size:13px;font-weight:700;color:#1a232e">Also known as:</span><br><span style="font-size:13px;color:#94a3b8">{qf.get("also_known_as","N/A")}</span></div>
        <div style="padding:12px 0;border-bottom:1px solid #f0f4f8"><span style="font-size:13px;font-weight:700;color:#1a232e">Affected organs:</span><br><span style="font-size:13px;color:#94a3b8">{qf.get("affected_organs","N/A")}</span></div>
        <div style="padding:12px 0;border-bottom:1px solid #f0f4f8"><span style="font-size:13px;font-weight:700;color:#1a232e">Recovery time:</span><br><span style="font-size:13px;color:#94a3b8">{qf.get("recovery_time","N/A")}</span></div>
        <div style="padding:12px 0"><span style="font-size:13px;font-weight:700;color:#1a232e">Contagious:</span><br><span style="font-size:13px;color:#94a3b8">{qf.get("contagious","N/A")}</span></div>
      </div>

      <div style="background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);padding:22px;margin-bottom:16px">
        <h3 style="font-size:16px;font-weight:800;color:#1a232e;margin-bottom:4px;padding-bottom:12px;border-bottom:1.5px solid #f0f4f8">When to See a Doctor</h3>
        <p style="font-size:14px;color:#4a5568;line-height:1.7;margin:12px 0 0">{data["when_to_see_doctor"]}</p>
      </div>

      <div style="background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);padding:22px;margin-bottom:16px">
        <h3 style="font-size:16px;font-weight:800;color:#1a232e;margin-bottom:4px;padding-bottom:12px;border-bottom:1.5px solid #f0f4f8">Take Action</h3>
        <a href="../index.html#symptoms" style="display:block;width:100%;padding:14px;background:#1a8fd1;color:#fff;border-radius:10px;font-size:15px;font-weight:700;text-align:center;text-decoration:none;margin-top:14px;box-sizing:border-box">Check Your Symptoms</a>
        <a href="../contact.html" style="display:block;width:100%;padding:13px;background:transparent;color:#1a8fd1;border:1.5px solid #1a8fd1;border-radius:10px;font-size:15px;font-weight:700;text-align:center;text-decoration:none;margin-top:10px;box-sizing:border-box">Ask a Health Question</a>
      </div>

    </main>

    <aside>
      <div style="background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);overflow:hidden;margin-bottom:16px;position:sticky;top:80px">
        <div style="padding:16px 18px;border-bottom:1.5px solid #f0f4f8;font-size:15px;font-weight:700;color:#1a232e">Related Diseases</div>
        <div style="padding:0 18px 8px">
          {related_html}
        </div>
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
        slug = disease.lower().replace(" ", "-").replace("'", "")
        path = f"Diseases/disease-{slug}.html"
        print(f"Generating: {disease}...")
        try:
            data = generate_article(disease, category)
            img = get_image(disease)
            html = build_html(disease, category, data, img)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  Failed {disease}: {e}")

if __name__ == "__main__":
    main()
