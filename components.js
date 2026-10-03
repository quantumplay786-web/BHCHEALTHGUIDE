// =====================================================
// components.js  -  ONE file controls nav, footer, share
// buttons, accordions and search on EVERY page.
// Edit here and every page updates. No ad code lives
// here: AdSense is switched on from data/site.json.
// =====================================================

function getPrefix() {
  var p = window.location.pathname;
  if (p.indexOf('/Diseases/') > -1 || p.indexOf('/Categories/') > -1) return '../';
  return '';
}

// BHC Health Guide logo (base64, includes the name, so no extra text is added next to it)
var LOGO_B64 = "data:image/png;base64,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";
function logoImg(height) {
  var w = Math.round(height * 242/150);
  return '<img src="' + LOGO_B64 + '" width="' + w + '" height="' + height + '" alt="BHC Health Guide" style="display:block;height:' + height + 'px;width:auto">';
}

function buildNav() {
  var pre = getPrefix();
  var el = document.getElementById('nav-placeholder');
  if (!el) return;
  el.outerHTML = `
  <nav class="nav">
    <div class="nav-inner">
      <a href="${pre}index.html" class="nav-logo" aria-label="BHC Health Guide home">
        ${logoImg(50)}
      </a>
      <div class="nav-links">
        <a href="${pre}index.html">Home</a>
        <a href="${pre}diseases.html">All Conditions</a>
        <a href="${pre}index.html#articles">Articles</a>
        <a href="${pre}index.html#prevention">Prevention</a>
        <a href="${pre}about.html">About</a>
        <a href="${pre}contact.html">Contact</a>
      </div>
      <div class="nav-right">
        <div class="nav-sw" style="position:relative">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><circle cx="11" cy="11" r="8" stroke="#94a3b8" stroke-width="2"/><path d="m21 21-4.35-4.35" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/></svg>
          <input type="text" id="nav-q" placeholder="Search diseases, symptoms..." aria-label="Search conditions" autocomplete="off">
        </div>
      </div>
      <button class="hamburger" id="hbg" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
  </nav>
  <div class="nav-drawer" id="drawer">
    <a href="${pre}index.html">Home</a>
    <a href="${pre}diseases.html">All Conditions</a>
    <a href="${pre}index.html#articles">Articles</a>
    <a href="${pre}index.html#prevention">Prevention</a>
    <a href="${pre}about.html">About Us</a>
    <a href="${pre}contact.html">Contact</a>
  </div>`;

  var hbg = document.getElementById('hbg');
  var drawer = document.getElementById('drawer');
  if (hbg && drawer) {
    hbg.addEventListener('click', function () {
      hbg.classList.toggle('open');
      drawer.classList.toggle('open');
    });
    drawer.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        hbg.classList.remove('open');
        drawer.classList.remove('open');
      });
    });
  }
}

function buildFooter() {
  var pre = getPrefix();
  var el = document.getElementById('footer-placeholder');
  if (!el) return;
  el.outerHTML = `
  <footer class="footer">
    <div class="container">
      <div class="ft-top">
        <div class="ft-grid">
          <div>
            <div class="ft-brand">
              ${logoImg(88)}
            </div>
            <p class="ft-desc">Plain-language information about diseases, symptoms, causes and prevention. For education only, never a replacement for a doctor.</p>
          </div>
          <div>
            <div class="ft-col-title">Explore</div>
            <div class="ft-links">
              <a href="${pre}diseases.html">All Conditions A to Z</a>
              <a href="${pre}Categories/category-viruses.html">Viruses</a>
              <a href="${pre}Categories/category-bacteria.html">Bacterial Diseases</a>
              <a href="${pre}Categories/category-chronic.html">Chronic Illness</a>
              <a href="${pre}Categories/category-cancer.html">Cancer</a>
              <a href="${pre}Categories/category-mental.html">Mental Health</a>
              <a href="${pre}Categories/category-children.html">Children's Health</a>
            </div>
          </div>
          <div>
            <div class="ft-col-title">Company</div>
            <div class="ft-links">
              <a href="${pre}about.html">About Us</a>
              <a href="${pre}editorial-policy.html">Editorial Policy</a>
              <a href="${pre}contact.html">Contact</a>
              <a href="${pre}privacy.html">Privacy Policy</a>
              <a href="${pre}terms.html">Terms of Service</a>
              <a href="${pre}disclaimer.html">Medical Disclaimer</a>
              <a href="${pre}copyright.html">Copyright</a>
            </div>
          </div>
        </div>
      </div>
      <div class="ft-bottom">
        <p class="ft-disc"><strong>Medical Disclaimer:</strong> Content on BHC Health Guide is for information only. It is not reviewed by a doctor and is not a substitute for professional medical advice. In an emergency, call your local emergency number.</p>
        <p class="ft-copy">&copy; ${new Date().getFullYear()} BHC Health Guide. All rights reserved.</p>
      </div>
    </div>
  </footer>`;
}

function buildShareButtons() {
  var el = document.getElementById('share-placeholder');
  if (!el) return;
  var url = encodeURIComponent(window.location.href);
  var title = encodeURIComponent(document.title);
  var btn = 'display:inline-flex;align-items:center;gap:6px;padding:10px 20px;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none;color:#fff;';
  el.outerHTML = `
  <div style="text-align:center;padding:32px 0 12px;background:#f8fafc;border-top:1.5px solid #dde8f0;margin-top:8px">
    <p style="font-size:13px;color:#94a3b8;margin-bottom:14px;font-weight:600">SHARE THIS ARTICLE</p>
    <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap">
      <a href="https://wa.me/?text=${title}%20${url}" target="_blank" rel="noopener" style="${btn}background:#25d366">WhatsApp</a>
      <a href="https://www.facebook.com/sharer/sharer.php?u=${url}" target="_blank" rel="noopener" style="${btn}background:#1877f2">Facebook</a>
      <a href="https://twitter.com/intent/tweet?text=${title}&url=${url}" target="_blank" rel="noopener" style="${btn}background:#000">X</a>
      <button id="copy-link" style="${btn}background:#edf4fb;color:#1a8fd1;border:1.5px solid #dde8f0;cursor:pointer;font-family:inherit">Copy Link</button>
    </div>
  </div>`;
  var c = document.getElementById('copy-link');
  if (c) c.addEventListener('click', function () {
    if (navigator.clipboard) navigator.clipboard.writeText(window.location.href);
    c.textContent = 'Copied!';
    setTimeout(function () { c.textContent = 'Copy Link'; }, 2000);
  });
}

// Accordion sections on article pages (this function was missing before,
// which is why sections never opened or closed).
function toggleAcc(id) {
  var el = document.getElementById(id);
  if (el) el.classList.toggle('open');
}
document.addEventListener('keydown', function (ev) {
  if ((ev.key === 'Enter' || ev.key === ' ') && ev.target && ev.target.classList && ev.target.classList.contains('acc-h')) {
    ev.preventDefault();
    ev.target.click();
  }
});

// ---------------- search (uses search-index.json, built by build.py) ----------------
var SEARCH_DATA = null;
function loadSearch(cb) {
  if (SEARCH_DATA) return cb(SEARCH_DATA);
  fetch(getPrefix() + 'search-index.json')
    .then(function (r) { return r.json(); })
    .then(function (d) { SEARCH_DATA = d; cb(d); })
    .catch(function () { cb([]); });
}
// Split what the visitor typed into search words (also tries the word without a trailing "s").
function bhcTerms(q) {
  return String(q || '').toLowerCase().split(/[^a-z0-9]+/).filter(function (w) { return w.length > 1; });
}
function bhcScore(x, terms) {
  var t = x.t.toLowerCase(), c = (x.c || '').toLowerCase(), s = (x.s || '').toLowerCase(),
      k = (x.k || ''), a = (x.a || ''), total = 0;
  for (var i = 0; i < terms.length; i++) {
    var w = terms[i], alt = w.length > 3 && w.slice(-1) === 's' ? w.slice(0, -1) : w, sc = 0;
    function has(str) { return str.indexOf(w) > -1 || str.indexOf(alt) > -1; }
    if (t.indexOf(w) === 0) sc += 12; else if (has(t)) sc += 7;
    if (has(a)) sc += 6;
    if (has(c)) sc += 2;
    if (has(s)) sc += 3;
    if (has(k)) sc += 1;
    if (!sc) return 0;            // every word must match somewhere
    total += sc;
  }
  return total;
}
function bhcSearch(q, data, limit) {
  var terms = bhcTerms(q);
  if (!terms.length) return [];
  return data.map(function (x) { return [bhcScore(x, terms), x]; })
    .filter(function (p) { return p[0] > 0; })
    .sort(function (a, b) { return b[0] - a[0] || a[1].t.localeCompare(b[1].t); })
    .slice(0, limit || 8).map(function (p) { return p[1]; });
}
function runSearch(q, data) { return bhcSearch(q, data, 8); }
function attachSearch(input, goBtn) {
  if (!input) return;
  var box = document.createElement('div');
  box.style.cssText = 'position:absolute;left:0;right:0;top:100%;margin-top:6px;background:#fff;border:1.5px solid #dde8f0;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.12);z-index:999;display:none;overflow:hidden;min-width:260px;text-align:left';
  input.parentElement.style.position = 'relative';
  input.parentElement.appendChild(box);
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function show() {
    loadSearch(function (data) {
      var res = runSearch(input.value, data);
      if (!res.length) {
        box.style.display = input.value.trim().length > 1 ? 'block' : 'none';
        box.innerHTML = '<div style="padding:12px 16px;font-size:13px;color:#94a3b8">No guide found yet. Try another word.</div>';
        return;
      }
      box.innerHTML = res.map(function (r) {
        return '<a href="' + getPrefix() + r.u + '" style="display:block;padding:10px 16px;border-bottom:1px solid #f0f4f8;text-decoration:none"><span style="font-size:14px;font-weight:700;color:#1a232e">' + esc(r.t) + '</span><br><span style="font-size:12px;color:#94a3b8">' + esc(r.c) + '</span></a>';
      }).join('') + '<a href="' + getPrefix() + 'search.html?q=' + encodeURIComponent(input.value.trim()) + '" style="display:block;padding:10px 16px;text-align:center;font-size:13px;font-weight:700;color:#1a8fd1;text-decoration:none;background:#f8fafc">See all results</a>';
      box.style.display = 'block';
    });
  }
  function go() {
    var v = input.value.trim();
    if (v) window.location.href = getPrefix() + 'search.html?q=' + encodeURIComponent(v);
  }
  input.addEventListener('input', show);
  input.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') go(); });
  if (goBtn) goBtn.addEventListener('click', go);
  document.addEventListener('click', function (ev) { if (!input.parentElement.contains(ev.target)) box.style.display = 'none'; });
}

document.addEventListener('DOMContentLoaded', function () {
  buildNav();
  buildFooter();
  buildShareButtons();
  attachSearch(document.getElementById('nav-q'), null);
  attachSearch(document.getElementById('hero-q'), document.getElementById('hero-go'));
});
