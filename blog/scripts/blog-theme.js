function toggleColorMode() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme') ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('busyGamerColorMode', next);
  updateThemeToggleIcon(next);
}

function updateThemeToggleIcon(mode) {
  const icon = document.querySelector('#theme-toggle i');
  if (icon) {
    icon.className = mode === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('busyGamerColorMode');
  const effective = saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  updateThemeToggleIcon(effective);
});
