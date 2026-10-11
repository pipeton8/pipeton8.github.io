// Dark is the default theme; light is opt-in and remembered per browser.
// The matching <head> snippet applies a saved choice before first paint;
// CSS picks the sun or moon icon from the data-theme attribute.
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

// Mobile hamburger menu
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
