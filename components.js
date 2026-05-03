// ============================================
// components.js — Edit this ONE file to update
// nav, footer, ads, and share buttons on ALL pages
// ============================================

function getPrefix() {
  const p = window.location.pathname;
  if (p.includes('/Diseases/') || p.includes('/Categories/')) return '../';
  return '';
}

// Add Monetag verification meta tag to every page
(function() {
  if (!document.querySelector('meta[name="monetag"]')) {
    const m = document.createElement('meta');
    m.name = 'monetag';
    m.content = 'b3195f88c823e794e73ceaf7aa86b93d';
    document.head.appendChild(m);
  }
})();

function buildNav() {
  const pre = getPrefix();
  const el = document.getElementById('nav-placeholder');
  if (!el) return;
  el.outerHTML = `
  <nav class="nav">
    <div class="nav-inner">
      <a href="${pre}index.html" class="nav-logo">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="8" fill="#e3f4fd"/>
          <rect x="14" y="6" width="4" height="20" rx="2" fill="#1a8fd1"/>
          <rect x="6" y="14" width="20" height="4" rx="2" fill="#1a8fd1"/>
          <circle cx="16" cy="16" r="3" fill="white"/>
        </svg>
        HealthGuide
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
      <button class="hamburger" id="hbg"><span></span><span></span><span></span></button>
    </div>
  </nav>
  <div class="nav-drawer" id="drawer">
    <a href="${pre}index.html">Home</a>
    <a href="${pre}Categories/category-viruses.html">Diseases</a>
    <a href="${pre}index.html#prevention">Prevention</a>
    <a href="${pre}index.html#articles">Articles</a>
    <a href="${pre}contact.html">Contact</a>
  </div>`;

  const hbg = document.getElementById('hbg');
  const drawer = document.getElementById('drawer');
  if (hbg && drawer) {
    hbg.addEventListener('click', () => {
      hbg.classList.toggle('open');
      drawer.classList.toggle('open');
    });
    drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      hbg.classList.remove('open');
      drawer.classList.remove('open');
    }));
  }
}

function buildFooter() {
  const pre = getPrefix();
  const el = document.getElementById('footer-placeholder');
  if (!el) return;
  el.outerHTML = `
  <footer class="footer">
    <div class="container">
      <div class="ft-top">
        <div class="ft-grid">
          <div>
            <div class="ft-brand">
              <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="8" fill="#e3f4fd"/>
                <rect x="14" y="6" width="4" height="20" rx="2" fill="#1a8fd1"/>
                <rect x="6" y="14" width="20" height="4" rx="2" fill="#1a8fd1"/>
                <circle cx="16" cy="16" r="3" fill="white"/>
              </svg>
              HealthGuide
            </div>
            <p class="ft-desc">Your trusted source for accurate health information. We help you understand diseases, symptoms, and treatments clearly.</p>
            <div class="ft-social">
              <a href="#" class="soc-btn" aria-label="Facebook">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
              </a>
              <a href="#" class="soc-btn" aria-label="Instagram">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>
              </a>
              <a href="#" class="soc-btn" aria-label="X">
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
        <p class="ft-disc"><strong>Medical Disclaimer:</strong> Content on HealthGuide is for informational purposes only. Always consult a qualified healthcare provider.</p>
        <p class="ft-copy">&copy; ${new Date().getFullYear()} HealthGuide. All rights reserved.</p>
      </div>
    </div>
  </footer>`;
}

function buildShareButtons() {
  const el = document.getElementById('share-placeholder');
  if (!el) return;
  const url = encodeURIComponent(window.location.href);
  const title = encodeURIComponent(document.title);
  el.outerHTML = `
  <div style="text-align:center;padding:28px 0 8px">
    <p style="font-size:13px;color:#94a3b8;margin-bottom:12px">Share this article</p>
    <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap">
      <a href="https://wa.me/?text=${title}%20${url}" target="_blank"
         style="display:inline-flex;align-items:center;gap:6px;padding:9px 18px;background:#25d366;color:#fff;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.123.554 4.118 1.528 5.852L0 24l6.335-1.652A11.955 11.955 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.885 0-3.65-.518-5.166-1.418l-.371-.22-3.762.982.998-3.662-.242-.381A9.944 9.944 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>
        WhatsApp
      </a>
      <a href="https://www.facebook.com/sharer/sharer.php?u=${url}" target="_blank"
         style="display:inline-flex;align-items:center;gap:6px;padding:9px 18px;background:#1877f2;color:#fff;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
        Facebook
      </a>
      <a href="https://twitter.com/intent/tweet?text=${title}&url=${url}" target="_blank"
         style="display:inline-flex;align-items:center;gap:6px;padding:9px 18px;background:#000;color:#fff;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        X
      </a>
      <button onclick="navigator.clipboard.writeText(window.location.href);this.textContent='Copied!';setTimeout(()=>this.textContent='Copy Link',2000)"
         style="display:inline-flex;align-items:center;gap:6px;padding:9px 18px;background:#edf4fb;color:#1a8fd1;border:1.5px solid #dde8f0;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
        Copy Link
      </button>
    </div>
  </div>`;
}

function buildAccordion() {
  document.querySelectorAll('.acc-h').forEach(h => {
    h.addEventListener('click', () => h.parentElement.classList.toggle('open'));
  });
}

// ── ADS SECTION ─────────────────────────────────
// When Monetag approves you, paste their ad code here.
// It will show on EVERY page automatically.
function buildAds() {
  // Example when ready:
  // const script = document.createElement('script');
  // script.src = 'https://your-monetag-ad-code.js';
  // document.head.appendChild(script);
}

document.addEventListener('DOMContentLoaded', () => {
  buildNav();
  buildFooter();
  buildShareButtons();
  buildAccordion();
  buildAds();
});
