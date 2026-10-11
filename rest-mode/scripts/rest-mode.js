// rest mode: theme toggle, mobile menu, masthead -> nav morph, review filters.

// ---------------------------------------------------------------------------
// Theme. Dark is the default; light is opt-in and remembered per browser.
// The <head> snippet applies a saved choice before first paint; CSS picks the
// sun or moon icon from the data-theme attribute.
// ---------------------------------------------------------------------------
const THEME_KEY = 'restModeColorMode';

function currentColorMode() {
  return document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
}

function toggleColorMode() {
  const next = currentColorMode() === 'dark' ? 'light' : 'dark';
  if (next === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
  try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* storage blocked */ }
}

// ---------------------------------------------------------------------------
// Mobile hamburger menu
// ---------------------------------------------------------------------------
function setNavMenu(open) {
  const nav = document.querySelector('.blog-nav');
  const btn = document.querySelector('.nav-menu-btn');
  if (!nav || !btn) return;
  nav.classList.toggle('nav-open', open);
  btn.setAttribute('aria-expanded', String(open));
  btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
}

function toggleNavMenu() {
  setNavMenu(!document.querySelector('.blog-nav').classList.contains('nav-open'));
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') setNavMenu(false);
});

document.addEventListener('click', (e) => {
  // Close when a menu link is followed or when tapping outside the nav
  if (e.target.closest('.blog-nav-links a') || !e.target.closest('.blog-nav')) setNavMenu(false);
});

window.matchMedia('(min-width: 769px)').addEventListener('change', (e) => {
  if (e.matches) setNavMenu(false);
});

// ---------------------------------------------------------------------------
// Home page: the big masthead wordmark scrolls with the page, shrinks and
// slides into the nav bar, and the bar fades in behind it. The nav wordmark
// is laid out at masthead size and only ever scaled down, so it stays crisp.
// With reduced motion the nav simply appears once the masthead is gone.
// ---------------------------------------------------------------------------
(function mastheadMorph() {
  const root = document.documentElement;
  if (!document.body.classList.contains('page-home')) return;

  const nav = document.getElementById('blog-nav');
  const brand = nav.querySelector('.blog-nav-brand');
  const slot = document.getElementById('masthead-wordmark');
  const subtitle = document.getElementById('masthead-subtitle');
  const cue = document.getElementById('scroll-cue');
  const masthead = document.getElementById('masthead');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const narrow = window.matchMedia('(max-width: 768px)');

  const clamp = (x) => Math.min(1, Math.max(0, x));
  const smooth = (x) => x * x * (3 - 2 * x);
  let geo = null;
  let ticking = false;

  function measure() {
    if (reduceMotion.matches) {
      root.classList.remove('rm-morph');
      geo = null;
      return;
    }
    root.classList.add('rm-morph');
    brand.style.transform = 'none';
    const b = brand.getBoundingClientRect();
    const s = slot.getBoundingClientRect();
    brand.style.transform = '';
    const heroFont = parseFloat(getComputedStyle(slot).fontSize);
    const navFont = narrow.matches ? 18 : 20;
    const sEnd = navFont / heroFont;
    const navH = nav.offsetHeight;
    const ty0 = s.top + window.scrollY - b.top;   // where the masthead wordmark sits at scroll 0
    const ty1 = (navH - b.height * sEnd) / 2;     // vertically centred in the bar
    geo = { tx0: s.left - b.left, ty0, ty1, sEnd, dist: Math.max(1, ty0 - ty1) };
  }

  function update() {
    ticking = false;
    const y = window.scrollY;
    if (!geo) {
      nav.classList.toggle('nav-solid', y > masthead.offsetHeight - nav.offsetHeight);
      return;
    }
    const p = clamp(y / geo.dist);
    const e = smooth(p);
    brand.style.setProperty('--tx', `${geo.tx0 * (1 - e)}px`);
    brand.style.setProperty('--ty', `${geo.ty1 + geo.dist * (1 - p)}px`);  // glued to the page until docked
    brand.style.setProperty('--s', String(1 + (geo.sEnd - 1) * e));
    nav.style.setProperty('--nav-bg', String(smooth(clamp((p - 0.7) / 0.3))));
    subtitle.style.opacity = String(1 - clamp(p * 1.8));
    cue.style.opacity = String(0.7 * (1 - clamp(p * 4)));
  }

  function requestUpdate() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }

  function remeasure() {
    measure();
    update();
  }

  remeasure();
  window.addEventListener('scroll', requestUpdate, { passive: true });
  window.addEventListener('resize', remeasure);
  reduceMotion.addEventListener('change', remeasure);
  if (document.fonts) document.fonts.ready.then(remeasure);  // Sora changes the wordmark size
})();

// ---------------------------------------------------------------------------
// Review filters (verdict, device)
// ---------------------------------------------------------------------------
(function reviewFilters() {
  const grid = document.getElementById('review-grid');
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll('.review-card'));
  const count = document.getElementById('reviews-count');
  const empty = document.getElementById('reviews-empty');
  const active = {};

  function apply() {
    let shown = 0;
    cards.forEach((card) => {
      const match = Object.entries(active).every(([key, value]) => !value || card.dataset[toCamel(key)] === value);
      card.hidden = !match;
      if (match) shown += 1;
    });
    count.textContent = `Showing ${shown} review${shown === 1 ? '' : 's'}`;
    empty.hidden = shown > 0;
  }

  function toCamel(key) {
    return key.replace(/-(\w)/g, (_, c) => c.toUpperCase());
  }

  document.querySelectorAll('.filter-group').forEach((group) => {
    const key = group.dataset.filter;
    active[key] = '';
    group.addEventListener('click', (e) => {
      const chip = e.target.closest('.filter-chip');
      if (!chip) return;
      group.querySelectorAll('.filter-chip').forEach((c) => {
        c.classList.toggle('is-active', c === chip);
        c.setAttribute('aria-pressed', String(c === chip));
      });
      active[key] = chip.dataset.value;
      apply();
    });
  });
})();
