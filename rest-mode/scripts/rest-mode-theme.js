// Dark is the default theme; light is opt-in and remembered per browser.
// The matching <head> snippet applies a saved choice before first paint.
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
  updateThemeToggleIcon(next);
}

function updateThemeToggleIcon(mode) {
  const icon = document.querySelector('#theme-toggle i');
  if (icon) {
    icon.className = mode === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
}

window.addEventListener('DOMContentLoaded', () => {
  updateThemeToggleIcon(currentColorMode());
});
