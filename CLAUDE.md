# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static academic/personal website for Felipe del Canto, hosted on GitHub Pages at `https://pipeton8.github.io/`. No build process, no package manager, no compilation — push to `main` to deploy.

## Deployment

```bash
git push origin main
```

That's the only "build" step. GitHub Pages serves the static files directly.

## Architecture

Three HTML pages sharing a consistent navbar/footer structure:
- `index.html` — About Me + Research sections
- `teaching.html` — Teaching materials organized by course
- `coursework.html` — Academic coursework with GitHub/Colab links

All dependencies are CDN-loaded (Bootstrap 5.0.2, jQuery 3.3.1, Font Awesome 6, Academicons, Google Fonts). The single custom CSS file (`css/styles.css`) and single JS file (`scripts/scripts.js`) cover all three pages.

## Design System

**Color palette** — always use these exact values, never hardcode colors outside `css/styles.css`:
- Primary dark: `rgb(51, 66, 87)` — navbar
- Secondary: `rgb(71, 96, 114)` — footer, card buttons
- Accent: `rgb(84, 140, 168)` — links
- Light background: `rgb(238, 238, 238)` — body background
- Colab accent: `rgb(249, 171, 0)` — Colab buttons

**Typography:**
- Body: Merriweather Sans, weight 300
- Headings/nav: Montserrat, weight 400–700
- Section titles: `.section-title` class, Montserrat bold (700)

**Layout:**
- Sections use `.section-container` (`min-height: max(90vh, 500px)`, `padding-top: 120px`)
- `.centered-section` for About Me; `.left-aligned-section` for Research/Teaching/Coursework

## Key CSS/HTML Conventions

- CSS is organized by component with `/* @ ComponentName */` section markers — follow this when adding styles
- Responsive breakpoint is 768px; media queries live at the end of `css/styles.css`
- HTML inline comments use `<!-- @ClassName -->` pattern to label sections

## Content Patterns

**Research papers** use these semantic classes in `index.html`:
```html
<div class="research-element">
  <span class="paper-title"><a class="paper-link" href="...">Title</a></span>
  <span class="paper-collaborators">with <a class="collaborator-link" href="...">Name</a></span>
  <span class="paper-journal"><em>Journal/venue</em></span>
</div>
```

**Teaching/coursework cards** use Bootstrap card grid (`row-cols-1 row-cols-md-3 g-4`) with `.card.border-dark` and button classes `.card-button` or `.colab-button`.

## JavaScript

`scripts/scripts.js` (67 lines, jQuery-based) handles:
- Smooth scroll to anchors (400ms jQuery animate, `.scroll-link` class)
- Navbar auto-collapse on mobile after navigation
- Show/hide subsection toggle buttons

## When Adding New Pages

1. Copy the `<head>` block from an existing page — all CDN deps must be present
2. Add consistent navbar and footer
3. Update `sitemap.xml` manually with the new URL and `lastmod` date
4. Add `description` and `keywords` meta tags in `<head>`
5. Ensure Google Analytics `gtag.js` snippet is included (Tracking ID: `G-C1ECHGQLBQ`)

## File Organization

```
documents/
  cv/          — CV PDFs
  other/       — Thesis and research papers
  teaching/    — Teaching materials by course code (e.g., EAE105A-2021-1/)
icons/         — Favicon package (generated via RealFaviconGenerator)
images/        — Profile photo and other images
```

Do not rename or move `googleeb1d2246e8c282cb.html` — it is the Google Search Console verification file.
