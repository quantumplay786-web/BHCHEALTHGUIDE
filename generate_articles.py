import os
import json
import re
import requests
import google.generativeai as genai
from datetime import date

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")
UNSPLASH_KEY = os.environ["UNSPLASH_KEY"]

# ── ALL TOPICS ─────────────────────────────────
TOPICS = [
    # Viruses
    ("Malaria", "viruses"), ("Measles", "viruses"), ("Zika Virus", "viruses"),
    ("Hepatitis B", "viruses"), ("Rabies", "viruses"), ("Monkeypox", "viruses"),
    ("Polio", "viruses"), ("Mumps", "viruses"), ("Chickenpox", "viruses"),
    ("Shingles", "viruses"), ("Ebola", "viruses"), ("Yellow Fever", "viruses"),
    ("West Nile Virus", "viruses"), ("Dengue Fever", "viruses"),
    ("HIV AIDS", "viruses"), ("Herpes Simplex", "viruses"),
    ("Norovirus", "viruses"), ("Rotavirus", "viruses"),

    # Bacteria
    ("Cholera", "bacteria"), ("Lyme Disease", "bacteria"),
    ("Meningitis", "bacteria"), ("Whooping Cough", "bacteria"),
    ("Tetanus", "bacteria"), ("Salmonella", "bacteria"),
    ("Diphtheria", "bacteria"), ("Sepsis", "bacteria"),
    ("Typhoid Fever", "bacteria"), ("Tuberculosis", "bacteria"),
    ("Pneumonia", "bacteria"), ("Strep Throat", "bacteria"),
    ("MRSA", "bacteria"), ("Gonorrhea", "bacteria"),
    ("Chlamydia", "bacteria"), ("Leprosy", "bacteria"),

    # Chronic
    ("Lupus", "chronic"), ("Arthritis", "chronic"),
    ("Celiac Disease", "chronic"), ("Kidney Stones", "chronic"),
    ("Gout", "chronic"), ("Cataracts", "chronic"),
    ("Glaucoma", "chronic"), ("Thyroid Disease", "chronic"),
    ("Anemia", "chronic"), ("Osteoporosis", "chronic"),
    ("Crohns Disease", "chronic"), ("Sleep Apnea", "chronic"),
    ("Vertigo", "chronic"), ("Fibromyalgia", "chronic"),
    ("Irritable Bowel Syndrome", "chronic"), ("Heart Disease", "chronic"),
    ("High Cholesterol", "chronic"), ("Obesity", "chronic"),

    # Mental
    ("Bipolar Disorder", "mental"), ("Schizophrenia", "mental"),
    ("ADHD", "mental"), ("Insomnia", "mental"),
    ("Autism", "mental"), ("Panic Disorder", "mental"),
    ("Eating Disorders", "mental"), ("Borderline Personality Disorder", "mental"),
    ("Addiction", "mental"), ("Social Anxiety", "mental"),

    # Skin
    ("Psoriasis", "skin"), ("Rosacea", "skin"),
    ("Ringworm", "skin"), ("Vitiligo", "skin"),
    ("Hives", "skin"), ("Scabies", "skin"),
    ("Cold Sores", "skin"), ("Alopecia", "skin"),
    ("Impetigo", "skin"), ("Cellulitis", "skin"),

    # Neuro
    ("Epilepsy", "neuro"), ("Migraine", "neuro"),
    ("Alzheimers", "neuro"), ("Parkinsons", "neuro"),
    ("Multiple Sclerosis", "neuro"), ("Stroke", "neuro"),
    ("Brain Tumor", "neuro"), ("Meningitis", "neuro"),
    ("Cerebral Palsy", "neuro"), ("ALS", "neuro"),

    # Psychology
    ("Anxiety Disorder", "psychology"), ("OCD", "psychology"),
    ("PTSD", "psychology"), ("Phobias", "psychology"),
    ("Depression", "psychology"), ("Narcissistic Personality Disorder", "psychology"),
    ("Dissociative Disorder", "psychology"),

    # Children
    ("Hand Foot and Mouth Disease", "children"),
    ("Kawasaki Disease", "children"), ("Croup", "children"),
    ("Meningitis in Children", "children"), ("RSV", "children"),
    ("Childhood Asthma", "children"), ("Whooping Cough in Children", "children"),
]


def get_image(query):
    """Fetch a relevant image from Unsplash."""
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": query + " medical health hospital doctor",
                "per_page": 1,
                "orientation": "landscape"
            },
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            timeout=10
        )
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                return results[0]["urls"]["regular"]
    except Exception:
        pass
    return "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&q=80"


def generate_article(disease, category):
    """Generate article data using Gemini AI."""
    prompt = f"""Write a detailed, medically accurate article about {disease} for a health website called HBC Health Guide.

STRICT WRITING RULES - follow every single one:
- Write like a doctor talking directly to a patient. Short sentences. Plain everyday words.
- NEVER use hyphens to join adjectives before nouns. Write "long term" not "long-term", "high risk" not "high-risk", "well known" not "well-known".
- NEVER use em dashes (—) or en dashes (–) anywhere at all.
- NEVER use these words: furthermore, moreover, additionally, consequently, utilize, crucial, optimal, leverage, facilitate, implement, comprehensive, vital, essentially, notably, significantly.
- NEVER use filler phrases like "It is worth noting", "In conclusion", "It is important to note".
- Each symptom must have a clear name and a simple one-sentence plain description.
- Write naturally. A real person should not be able to tell this was written by AI.

Return ONLY valid JSON. No markdown. No backticks. No extra text before or after:
{{
  "title": "Full proper disease name",
  "subtitle": "One plain sentence describing what this disease is",
  "severity": "Low or Medium or High or Common",
  "spread": "3 to 5 plain words describing how it spreads",
  "incubation": "Time range like 2 to 14 Days, or N/A",
  "vaccine": "Available or Not Available or In Development",
  "overview": "Two short plain paragraphs as one string. No hyphens. No dashes. No filler words.",
  "symptoms": [
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom with no hyphens"}},
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom with no hyphens"}},
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom with no hyphens"}},
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom with no hyphens"}},
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom with no hyphens"}},
    {{"name": "Symptom Name", "description": "One plain sentence about this symptom with no hyphens"}}
  ],
  "causes_overview": "One short plain paragraph. No hyphens.",
  "causes": ["cause 1", "cause 2", "cause 3", "cause 4"],
  "transmission_overview": "One short plain paragraph about how it spreads. No hyphens.",
  "transmission": ["method 1", "method 2", "method 3", "method 4", "method 5"],
  "prevention_overview": "One short plain paragraph about prevention. No hyphens.",
  "prevention": ["tip 1", "tip 2", "tip 3", "tip 4", "tip 5", "tip 6"],
  "treatment_overview": "One short plain paragraph about treatment. No hyphens.",
  "treatment": ["treatment 1", "treatment 2", "treatment 3", "treatment 4", "treatment 5"],
  "diagnosis_overview": "One short plain paragraph about how doctors diagnose this. No hyphens.",
  "diagnosis": ["method 1", "method 2", "method 3", "method 4"],
  "quick_facts": {{
    "also_known_as": "Other common names or None",
    "affected_organs": "List of main organs affected",
    "recovery_time": "Typical recovery time in plain words",
    "contagious": "Yes or No or Sometimes"
  }},
  "when_to_see_doctor": "One short plain paragraph. No hyphens. Tell patient clearly when to go to doctor.",
  "related": ["Disease 1", "Disease 2", "Disease 3", "Disease 4", "Disease 5"]
}}"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    # Clean any markdown wrapping
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()
    return json.loads(text)


def clean_ai_phrases(text):
    """Remove AI writing patterns from text."""
    replacements = [
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
        (r'\bFurthermore,?\b', 'Also,'),
        (r'\bMoreover,?\b', 'Also,'),
        (r'\bAdditionally,?\b', 'Also,'),
        (r'\bUtilize\b', 'Use'),
        (r'\butilize\b', 'use'),
        (r'\bCrucial\b', 'Important'),
        (r'\bcrucial\b', 'important'),
        (r'\bOptimal\b', 'Best'),
        (r'\boptimal\b', 'best'),
        (r'\bIn conclusion,?\b', 'Overall,'),
        (r'\bIt is worth noting that\b', 'Note that'),
        (r'\bIt is important to note\b', 'Note'),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def build_html(disease, category, data, img_url):
    """Build the complete HTML page for a disease article."""
    slug = disease.lower().replace(" ", "-").replace("'", "").replace("/", "-")

    # Severity badge colors
    sev_colors = {
        "High": ("#fff0f0", "#c53030"),
        "Medium": ("#fff4e6", "#c2410c"),
        "Low": ("#e8f5e9", "#2e7d32"),
        "Common": ("#fff4e6", "#c2410c"),
    }
    sev_bg, sev_color = sev_colors.get(data.get("severity", "Medium"), ("#e3f4fd", "#1a8fd1"))

    # Vaccine status
    vaccine_val = data.get("vaccine", "Not Available")
    vaccine_color = "#2e7d32" if vaccine_val == "Available" else "#c53030"
    vaccine_icon = "✓" if vaccine_val == "Available" else "✗"

    # Symptom icons cycle
    sym_colors = ["#ef4444", "#3b82f6", "#22c55e", "#f97316", "#8b5cf6", "#ec4899"]

    symptoms_html = ""
    for i, s in enumerate(data.get("symptoms", [])):
        color = sym_colors[i % len(sym_colors)]
        name = clean_ai_phrases(s.get("name", ""))
        desc = clean_ai_phrases(s.get("description", ""))
        symptoms_html += f"""
        <div style="background:#f8fafc;border-radius:10px;padding:16px 18px;display:flex;align-items:flex-start;gap:14px;margin-bottom:10px;cursor:pointer" onclick="this.querySelector('.sym-detail').style.display=this.querySelector('.sym-detail').style.display==='none'?'block':'none'">
          <div style="width:36px;height:36px;border-radius:50%;background:{color}22;display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <div style="width:10px;height:10px;border-radius:50%;background:{color}"></div>
          </div>
          <div style="flex:1">
            <div style="font-size:15px;font-weight:700;color:#1a232e;margin-bottom:3px">{name}</div>
            <div class="sym-detail" style="font-size:13px;color:#94a3b8;display:block">{desc}</div>
          </div>
          <span style="color:#cbd5e1;font-size:20px;margin-left:auto">›</span>
        </div>"""

    def make_li(items, color):
        result = ""
        for item in items:
            item_clean = clean_ai_phrases(str(item))
            result += f'<li style="display:flex;align-items:flex-start;gap:10px;font-size:14px;color:#4a5568;margin-bottom:10px;line-height:1.6"><span style="width:8px;height:8px;background:{color};border-radius:50%;margin-top:7px;flex-shrink:0;display:inline-block"></span>{item_clean}</li>'
        return result

    causes_li = make_li(data.get("causes", []), "#1a8fd1")
    transmission_li = make_li(data.get("transmission", []), "#1a8fd1")
    prevention_li = make_li(data.get("prevention", []), "#4caf50")
    treatment_li = make_li(data.get("treatment", []), "#7c3aed")
    diagnosis_li = make_li(data.get("diagnosis", []), "#1a8fd1")

    related_html = ""
    for r in data.get("related", []):
        r_slug = r.lower().replace(" ", "-").replace("'", "").replace("/", "-")
        related_html += f'<div style="padding:13px 0;border-bottom:1px solid #f0f4f8;display:flex;align-items:center;gap:12px"><span style="width:10px;height:10px;border-radius:50%;border:2.5px solid #1a8fd1;display:inline-block;flex-shrink:0"></span><a href="disease-{r_slug}.html" style="font-size:14px;color:#1a232e;text-decoration:none;font-weight:500;transition:color .2s" onmouseover="this.style.color=\'#1a8fd1\'" onmouseout="this.style.color=\'#1a232e\'">{r}</a></div>'

    qf = data.get("quick_facts", {})
    overview_clean = clean_ai_phrases(data.get("overview", ""))
    causes_ov_clean = clean_ai_phrases(data.get("causes_overview", ""))
    trans_ov_clean = clean_ai_phrases(data.get("transmission_overview", ""))
    prev_ov_clean = clean_ai_phrases(data.get("prevention_overview", ""))
    treat_ov_clean = clean_ai_phrases(data.get("treatment_overview", ""))
    diag_ov_clean = clean_ai_phrases(data.get("diagnosis_overview", ""))
    doctor_clean = clean_ai_phrases(data.get("when_to_see_doctor", ""))
    category_display = category.replace("-", " ").title()

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{data.get("title", disease)} | HBC Health Guide</title>
<meta name="description" content="{data.get("subtitle", "")}">
<meta name="monetag" content="b3195f88c823e794e73ceaf7aa86b93d">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{data.get("title", disease)} | HBC Health Guide">
<meta property="og:description" content="{data.get("subtitle", "")}">
<meta property="og:image" content="{img_url}">
<meta property="og:type" content="article">
<meta property="og:url" content="">
<link rel="stylesheet" href="../style.css">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
.acc-section{{background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);margin-bottom:16px;overflow:hidden}}
.acc-section-h{{display:flex;align-items:center;gap:12px;padding:18px 20px;cursor:pointer;user-select:none;transition:background .2s}}
.acc-section-h:hover{{background:#f8fafc}}
.acc-icon{{width:42px;height:42px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:20px}}
.acc-chevron{{margin-left:auto;color:#94a3b8;transition:transform .25s ease;font-size:22px;font-weight:300}}
.acc-body{{padding:0 20px;max-height:0;overflow:hidden;transition:max-height .4s ease,padding .25s ease}}
.acc-section.open .acc-chevron{{transform:rotate(180deg)}}
.acc-section.open .acc-body{{padding:6px 20px 24px;max-height:3000px}}
@media(max-width:768px){{
  .dis-layout-custom{{grid-template-columns:1fr !important}}
  .dis-aside-custom{{display:none}}
}}
</style>
</head>
<body>
<div id="nav-placeholder"></div>

<section style="background:linear-gradient(130deg,#d6ebf7 0%,#e8f4fd 55%,#f0f8ff 100%);padding:36px 0 0;border-bottom:1.5px solid #dde8f0">
  <div class="container">
    <nav class="breadcrumb" aria-label="breadcrumb">
      <a href="../index.html">Home</a>
      <span class="bc-sep">›</span>
      <a href="../Categories/category-{category}.html">{category_display}</a>
      <span class="bc-sep">›</span>
      <span>{data.get("title", disease)}</span>
    </nav>

    <div style="display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap">
      <span style="display:inline-block;padding:4px 14px;background:{sev_bg};color:{sev_color};border-radius:20px;font-size:12px;font-weight:700">{data.get("severity","Medium")} Risk</span>
      <span style="display:inline-block;padding:4px 14px;background:#e3f4fd;color:#1a8fd1;border-radius:20px;font-size:12px;font-weight:700">{category_display}</span>
    </div>

    <h1 style="font-size:clamp(26px,4vw,40px);font-weight:800;color:#1a232e;margin-bottom:10px;line-height:1.2">{data.get("title", disease)}</h1>
    <p style="font-size:15px;color:#4a5568;max-width:620px;line-height:1.7;margin-bottom:28px">{data.get("subtitle", "")}</p>

    <div style="background:#fff;border-radius:14px;overflow:hidden;border:1.5px solid #dde8f0;margin-bottom:0">
      <div style="display:grid;grid-template-columns:1fr 1fr;border-bottom:1.5px solid #f0f4f8">
        <div style="padding:16px 20px;border-right:1.5px solid #f0f4f8">
          <div style="font-size:10px;font-weight:700;color:#94a3b8;letter-spacing:.08em;text-transform:uppercase;margin-bottom:7px">SEVERITY</div>
          <div style="font-size:15px;font-weight:700;color:{sev_color};display:flex;align-items:center;gap:6px">⚠ {data.get("severity","Medium")}</div>
        </div>
        <div style="padding:16px 20px">
          <div style="font-size:10px;font-weight:700;color:#94a3b8;letter-spacing:.08em;text-transform:uppercase;margin-bottom:7px">SPREAD TYPE</div>
          <div style="font-size:15px;font-weight:700;color:#1a232e;display:flex;align-items:center;gap:6px">🦠 {data.get("spread","")}</div>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr">
        <div style="padding:16px 20px;border-right:1.5px solid #f0f4f8">
          <div style="font-size:10px;font-weight:700;color:#94a3b8;letter-spacing:.08em;text-transform:uppercase;margin-bottom:7px">INCUBATION</div>
          <div style="font-size:15px;font-weight:700;color:#1a232e;display:flex;align-items:center;gap:6px">🕐 {data.get("incubation","N/A")}</div>
        </div>
        <div style="padding:16px 20px">
          <div style="font-size:10px;font-weight:700;color:#94a3b8;letter-spacing:.08em;text-transform:uppercase;margin-bottom:7px">VACCINE</div>
          <div style="font-size:15px;font-weight:700;color:{vaccine_color};display:flex;align-items:center;gap:6px">{vaccine_icon} {vaccine_val}</div>
        </div>
      </div>
    </div>
  </div>
</section>

<div style="background:#fff">
  <img src="{img_url}" alt="{disease}" loading="lazy" style="width:100%;height:280px;object-fit:cover;display:block">
</div>

<div class="container" style="padding-top:28px;padding-bottom:60px">
  <div class="dis-layout-custom" style="display:grid;grid-template-columns:1fr 320px;gap:24px">

    <main>

      <div class="acc-section open">
        <div class="acc-section-h">
          <div class="acc-icon" style="background:#e3f4fd">📍</div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Symptoms</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.75;margin-bottom:16px">{overview_clean}</p>
          {symptoms_html}
        </div>
      </div>

      <div class="acc-section open">
        <div class="acc-section-h">
          <div class="acc-icon" style="background:#fff0f0">🎯</div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Causes</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.75;margin-bottom:14px">{causes_ov_clean}</p>
          <ul style="list-style:none;padding:0;margin:0">{causes_li}</ul>
        </div>
      </div>

      <div class="acc-section open">
        <div class="acc-section-h">
          <div class="acc-icon" style="background:#e3f4fd">🤝</div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Transmission</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.75;margin-bottom:14px">{trans_ov_clean}</p>
          <ul style="list-style:none;padding:0;margin:0">{transmission_li}</ul>
        </div>
      </div>

      <div class="acc-section">
        <div class="acc-section-h">
          <div class="acc-icon" style="background:#e8f5e9">🛡</div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Prevention</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.75;margin-bottom:14px">{prev_ov_clean}</p>
          <ul style="list-style:none;padding:0;margin:0">{prevention_li}</ul>
        </div>
      </div>

      <div class="acc-section">
        <div class="acc-section-h">
          <div class="acc-icon" style="background:#f0eaff">💊</div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Treatment</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.75;margin-bottom:14px">{treat_ov_clean}</p>
          <ul style="list-style:none;padding:0;margin:0">{treatment_li}</ul>
        </div>
      </div>

      <div class="acc-section">
        <div class="acc-section-h">
          <div class="acc-icon" style="background:#e3f4fd">🔍</div>
          <span style="font-size:17px;font-weight:700;color:#1a232e">Diagnosis</span>
          <span class="acc-chevron">⌄</span>
        </div>
        <div class="acc-body">
          <p style="font-size:14px;color:#4a5568;line-height:1.75;margin-bottom:14px">{diag_ov_clean}</p>
          <ul style="list-style:none;padding:0;margin:0">{diagnosis_li}</ul>
        </div>
      </div>

      <div style="background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);padding:22px;margin-bottom:16px">
        <h3 style="font-size:16px;font-weight:800;color:#1a232e;margin:0 0 16px;padding-bottom:12px;border-bottom:1.5px solid #f0f4f8">Quick Facts</h3>
        <div style="padding:12px 0;border-bottom:1px solid #f0f4f8"><span style="font-size:13px;font-weight:700;color:#1a232e">Also known as:</span><br><span style="font-size:13px;color:#94a3b8;margin-top:3px;display:block">{qf.get("also_known_as","N/A")}</span></div>
        <div style="padding:12px 0;border-bottom:1px solid #f0f4f8"><span style="font-size:13px;font-weight:700;color:#1a232e">Affected organs:</span><br><span style="font-size:13px;color:#94a3b8;margin-top:3px;display:block">{qf.get("affected_organs","N/A")}</span></div>
        <div style="padding:12px 0;border-bottom:1px solid #f0f4f8"><span style="font-size:13px;font-weight:700;color:#1a232e">Recovery time:</span><br><span style="font-size:13px;color:#94a3b8;margin-top:3px;display:block">{qf.get("recovery_time","N/A")}</span></div>
        <div style="padding:12px 0"><span style="font-size:13px;font-weight:700;color:#1a232e">Contagious:</span><br><span style="font-size:13px;color:#94a3b8;margin-top:3px;display:block">{qf.get("contagious","N/A")}</span></div>
      </div>

      <div style="background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);padding:22px;margin-bottom:16px">
        <h3 style="font-size:16px;font-weight:800;color:#1a232e;margin:0 0 12px;padding-bottom:12px;border-bottom:1.5px solid #f0f4f8">When to See a Doctor</h3>
        <p style="font-size:14px;color:#4a5568;line-height:1.75;margin:0">{doctor_clean}</p>
      </div>

      <div style="background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);padding:22px;margin-bottom:16px">
        <h3 style="font-size:16px;font-weight:800;color:#1a232e;margin:0 0 16px;padding-bottom:12px;border-bottom:1.5px solid #f0f4f8">Related Diseases</h3>
        {related_html}
      </div>

      <div style="background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);padding:22px">
        <h3 style="font-size:16px;font-weight:800;color:#1a232e;margin:0 0 16px;padding-bottom:12px;border-bottom:1.5px solid #f0f4f8">Take Action</h3>
        <a href="../index.html#prevention" style="display:block;padding:14px;background:#1a8fd1;color:#fff;border-radius:10px;font-size:15px;font-weight:700;text-align:center;text-decoration:none;margin-bottom:10px">Check Prevention Tips</a>
        <a href="../contact.html" style="display:block;padding:13px;background:transparent;color:#1a8fd1;border:1.5px solid #1a8fd1;border-radius:10px;font-size:15px;font-weight:700;text-align:center;text-decoration:none">Ask a Health Question</a>
      </div>

    </main>

    <aside class="dis-aside-custom">
      <div style="background:#fff;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,.06);overflow:hidden;margin-bottom:16px;position:sticky;top:80px">
        <div style="padding:16px 18px;border-bottom:1.5px solid #f0f4f8;font-size:15px;font-weight:700;color:#1a232e">Browse Categories</div>
        <div style="padding:10px 18px 14px">
          <a href="../Categories/category-viruses.html" style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f0f4f8;font-size:13px;color:#1a232e;text-decoration:none;font-weight:500">🦠 Viruses</a>
          <a href="../Categories/category-bacteria.html" style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f0f4f8;font-size:13px;color:#1a232e;text-decoration:none;font-weight:500">🧫 Bacterial Diseases</a>
          <a href="../Categories/category-chronic.html" style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f0f4f8;font-size:13px;color:#1a232e;text-decoration:none;font-weight:500">❤ Chronic Illness</a>
          <a href="../Categories/category-mental.html" style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f0f4f8;font-size:13px;color:#1a232e;text-decoration:none;font-weight:500">🧠 Mental Health</a>
          <a href="../Categories/category-skin.html" style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f0f4f8;font-size:13px;color:#1a232e;text-decoration:none;font-weight:500">🩹 Skin Diseases</a>
          <a href="../Categories/category-children.html" style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f0f4f8;font-size:13px;color:#1a232e;text-decoration:none;font-weight:500">👶 Children Health</a>
          <a href="../Categories/category-neuro.html" style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f0f4f8;font-size:13px;color:#1a232e;text-decoration:none;font-weight:500">⚡ Neurological</a>
          <a href="../Categories/category-psychology.html" style="display:flex;align-items:center;gap:10px;padding:10px 0;font-size:13px;color:#1a232e;text-decoration:none;font-weight:500">💬 Psychology</a>
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
    print(f"Starting generation for {date.today().isoformat()}...")
    topics_copy = list(TOPICS)
    random.shuffle(topics_copy)
    daily = topics_copy[:22]
    os.makedirs("Diseases", exist_ok=True)

    success = 0
    fail = 0
    for disease, category in daily:
        slug = disease.lower().replace(" ", "-").replace("'", "").replace("/", "-")
        path = f"Diseases/disease-{slug}.html"
        print(f"  Generating: {disease}...")
        try:
            data = generate_article(disease, category)
            img = get_image(disease)
            html = build_html(disease, category, data, img)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  Saved: {path}")
            success += 1
        except Exception as e:
            print(f"  FAILED {disease}: {e}")
            fail += 1

    print(f"\nDone: {success} generated, {fail} failed.")


if __name__ == "__main__":
    main()
