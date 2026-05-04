// =============================================
// components.js — ONE file controls everything
// Nav, Footer, Share buttons, Ads on ALL pages
// =============================================

// Add Monetag verification to every page head
(function () {
  if (!document.querySelector('meta[name="monetag"]')) {
    var m = document.createElement('meta');
    m.name = 'monetag';
    m.content = 'b3195f88c823e794e73ceaf7aa86b93d';
    document.head.appendChild(m);
  }
})();

function getPrefix() {
  var p = window.location.pathname;
  if (p.includes('/Diseases/') || p.includes('/Categories/')) return '../';
  return '';
}

function buildNav() {
  var pre = getPrefix();
  var el = document.getElementById('nav-placeholder');
  if (!el) return;
  el.outerHTML = `
  <nav class="nav">
    <div class="nav-inner">
      <a href="${pre}index.html" class="nav-logo">
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
          <rect width="36" height="36" rx="9" fill="#1a8fd1"/>
          <path d="M10 18H26M18 10V26" stroke="white" stroke-width="3.5" stroke-linecap="round"/>
          <circle cx="18" cy="18" r="5" fill="none" stroke="white" stroke-width="2"/>
          <path d="M8 12C8 12 12 8 18 8C24 8 28 12 28 12" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
        </svg>
        <span style="display:flex;flex-direction:column;line-height:1.1">
          <span style="font-size:16px;font-weight:800;color:#1a232e">HBC</span>
          <span style="font-size:10px;font-weight:600;color:#1a8fd1;letter-spacing:.04em">HEALTH GUIDE</span>
        </span>
      </a>
      <div class="nav-links">
        <a href="${pre}index.html">Home</a>
        <a href="${pre}Categories/category-viruses.html">Diseases</a>
        <a href="${pre}index.html#prevention">Prevention</a>
        <a href="${pre}index.html#articles">Articles</a>
        <a href="${pre}contact.html">Contact</a>
      </div>
      <div class="nav-right">
        <div class="nav-sw">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
            <circle cx="11" cy="11" r="8" stroke="#94a3b8" stroke-width="2"/>
            <path d="m21 21-4.35-4.35" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <input type="text" placeholder="Search diseases, symptoms...">
        </div>
      </div>
      <button class="hamburger" id="hbg" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
  </nav>
  <div class="nav-drawer" id="drawer">
    <a href="${pre}index.html">Home</a>
    <a href="${pre}Categories/category-viruses.html">Diseases</a>
    <a href="${pre}Categories/category-bacteria.html">Bacterial Diseases</a>
    <a href="${pre}Categories/category-chronic.html">Chronic Illness</a>
    <a href="${pre}Categories/category-mental.html">Mental Health</a>
    <a href="${pre}Categories/category-skin.html">Skin Diseases</a>
    <a href="${pre}Categories/category-children.html">Children Health</a>
    <a href="${pre}Categories/category-neuro.html">Neurological</a>
    <a href="${pre}Categories/category-psychology.html">Psychology</a>
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
              <svg width="32" height="32" viewBox="0 0 36 36" fill="none">
                <rect width="36" height="36" rx="9" fill="#1a8fd1"/>
                <path d="M10 18H26M18 10V26" stroke="white" stroke-width="3.5" stroke-linecap="round"/>
                <circle cx="18" cy="18" r="5" fill="none" stroke="white" stroke-width="2"/>
              </svg>
              <span style="display:flex;flex-direction:column;line-height:1.1">
                <span style="font-size:15px;font-weight:800;color:#1a232e">HBC Health Guide</span>
              </span>
            </div>
            <p class="ft-desc">Your trusted source for accurate health information. We help you understand diseases, symptoms, and treatments clearly.</p>
            <div class="ft-social">
              <a href="#" class="soc-btn" aria-label="Facebook">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
              </a>
              <a href="#" class="soc-btn" aria-label="Instagram">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>
              </a>
              <a href="#" class="soc-btn" aria-label="X Twitter">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
              </a>
            </div>
          </div>
          <div>
            <div class="ft-col-title">Health Topics</div>
            <div class="ft-links">
              <a href="${pre}Categories/category-viruses.html">Viruses</a>
              <a href="${pre}Categories/category-bacteria.html">Bacterial Diseases</a>
              <a href="${pre}Categories/category-chronic.html">Chronic Illness</a>
              <a href="${pre}Categories/category-mental.html">Mental Health</a>
              <a href="${pre}Categories/category-skin.html">Skin Diseases</a>
              <a href="${pre}Categories/category-children.html">Childrens Health</a>
              <a href="${pre}Categories/category-neuro.html">Neurological</a>
              <a href="${pre}Categories/category-psychology.html">Psychology</a>
            </div>
          </div>
          <div>
            <div class="ft-col-title">Quick Links</div>
            <div class="ft-links">
              <a href="${pre}about.html">About Us</a>
              <a href="${pre}contact.html">Contact</a>
              <a href="${pre}privacy.html">Privacy Policy</a>
              <a href="${pre}terms.html">Terms of Service</a>
              <a href="${pre}disclaimer.html">Disclaimer</a>
            </div>
          </div>
        </div>
      </div>
      <div class="ft-bottom">
        <p class="ft-disc"><strong>Medical Disclaimer:</strong> Content on HBC Health Guide is for informational purposes only. It is not a substitute for professional medical advice. Always consult a qualified healthcare provider.</p>
        <p class="ft-copy">&copy; ${new Date().getFullYear()} HBC Health Guide. All rights reserved.</p>
      </div>
    </div>
  </footer>`;
}

function buildShareButtons() {
  var el = document.getElementById('share-placeholder');
  if (!el) return;
  var url = encodeURIComponent(window.location.href);
  var title = encodeURIComponent(document.title);
  el.outerHTML = `
  <div style="text-align:center;padding:32px 0 12px;background:#f8fafc;border-top:1.5px solid #dde8f0;margin-top:8px">
    <p style="font-size:13px;color:#94a3b8;margin-bottom:14px;font-weight:600">SHARE THIS ARTICLE</p>
    <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap">
      <a href="https://wa.me/?text=${title}%20${url}" target="_blank" rel="noopener"
         style="display:inline-flex;align-items:center;gap:6px;padding:10px 20px;background:#25d366;color:#fff;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.123.554 4.118 1.528 5.852L0 24l6.335-1.652A11.955 11.955 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.885 0-3.65-.518-5.166-1.418l-.371-.22-3.762.982.998-3.662-.242-.381A9.944 9.944 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>
        WhatsApp
      </a>
      <a href="https://www.facebook.com/sharer/sharer.php?u=${url}" target="_blank" rel="noopener"
         style="display:inline-flex;align-items:center;gap:6px;padding:10px 20px;background:#1877f2;color:#fff;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
        Facebook
      </a>
      <a href="https://twitter.com/intent/tweet?text=${title}&url=${url}" target="_blank" rel="noopener"
         style="display:inline-flex;align-items:center;gap:6px;padding:10px 20px;background:#000;color:#fff;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        X
      </a>
      <button onclick="navigator.clipboard.writeText(window.location.href);this.textContent='Copied!';setTimeout(()=>this.textContent='Copy Link',2000)"
         style="display:inline-flex;align-items:center;gap:6px;padding:10px 20px;background:#edf4fb;color:#1a8fd1;border:1.5px solid #dde8f0;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
        Copy Link
      </button>
    </div>
  </div>`;
}

function buildAccordion() {
  document.querySelectorAll('.acc-section-h').forEach(function (h) {
    h.addEventListener('click', function () {
      h.parentElement.classList.toggle('open');
    });
  });
}

// ── ADS: Paste Monetag ad code here when approved ──
function buildAds() {
  // When Monetag sends your ad code, paste it here like:
  // var s = document.createElement('script');
  // s.src = 'https://monetag-ad-code.js';
  // document.head.appendChild(s);
}

document.addEventListener('DOMContentLoaded', function () {
  buildNav();
  buildFooter();
  buildShareButtons();
  buildAccordion();
  buildAds();
});
