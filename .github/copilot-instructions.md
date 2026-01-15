# GitHub Pages Personal Academic Website

This is a static academic/personal website for Felipe del Canto, hosted on GitHub Pages. The site showcases research, teaching materials, and coursework.

## Site Architecture

**Multi-page structure:**
- [index.html](index.html) - Main landing page with About Me and Research sections
- [teaching.html](teaching.html) - Teaching materials organized by course
- [coursework.html](coursework.html) - Academic coursework with GitHub/Colab links

All pages share a consistent navigation bar, header structure, and footer. The site uses a fixed top navbar that collapses on mobile.

## Technology Stack

- **Framework:** Bootstrap 5.0.2 (via CDN)
- **CSS:** Custom styles in [css/styles.css](css/styles.css)
- **JavaScript:** jQuery 3.3.1 + custom scripts in [scripts/scripts.js](scripts/scripts.js)
- **Icons:** Font Awesome 6, Academicons, Friconix (coursework page only)
- **Fonts:** Google Fonts - Merriweather Sans (body), Montserrat (headings/nav)
- **Analytics:** Google Analytics (gtag.js) configured across all pages

## Design System

**Color Palette** (from colorhunt.co):
- Primary dark: `rgb(51, 66, 87)` - navbar background
- Secondary: `rgb(71, 96, 114)` - footer, card buttons
- Accent: `rgb(84, 140, 168)` - links
- Light background: `rgb(238, 238, 238)` - body background
- Colab accent: `rgb(249, 171, 0)` - Colab buttons

**Typography:**
- Body text: Merriweather Sans, weight 300
- Headings/Nav: Montserrat, weight 400-700
- Section titles use `section-title` class with Montserrat bold (700)

**Layout Patterns:**
- Sections use `.section-container` with min-height of `max(90vh, 500px)` and `padding-top: 120px`
- Content uses `.container-fluid` with 5% horizontal padding
- Two text alignment modes: `.centered-section` (About Me) and `.left-aligned-section` (Research, Teaching, Coursework)

## Key Components

### Navigation Bar
- Fixed top navbar with custom hamburger animation (`.custom-toggler`)
- Active state tracking with `.active` class
- Smooth scroll behavior for anchor links (`.scroll-link` class)
- Auto-collapse on mobile after navigation (implemented in [scripts/scripts.js](scripts/scripts.js))

### Research Section
Research papers structured with semantic classes:
- `.research-subsection` - Category groupings (Working Papers, Publications, Other)
- `.research-element` - Individual paper container
- `.paper-title`, `.paper-link` - Paper name/link
- `.paper-collaborators`, `.collaborator-link` - Co-authors
- `.paper-journal` - Journal/venue in italics

### Teaching/Coursework Cards
Bootstrap card grid system (`row-cols-1 row-cols-md-3 g-4`):
- `.course-container` - Course grouping with title
- `.card.border-dark` - Individual assignment/topic cards
- Button types: `.card-button` (default), `.colab-button` (yellow/Colab-branded)

### Custom Interactive Elements
- Smooth scrolling to anchors (jQuery animate, 400ms duration)
- Bootstrap tooltips enabled via `data-bs-toggle="tooltip"`
- Custom navbar toggler with animated hamburger → X transformation

## File Organization

```
/documents/
  /cv/               - CV PDF
  /other/            - Thesis and other research papers
  /teaching/         - Teaching materials by course code
    /EAE105A-2021-1/
    /EAF2010-2021-1/
/icons/              - Favicon package (generated via RealFaviconGenerator)
/images/             - Site images (profile photo, etc.)
```

## Development Guidelines

1. **Adding new pages:** Follow the existing HTML structure with navbar, sections, and footer. Include all CDN dependencies in `<head>`.

2. **Updating styles:** Modify [css/styles.css](css/styles.css). CSS is organized by component with `@` comment markers (e.g., `/* @Nav Bar */`).

3. **Adding research papers:** Use the `.research-element` pattern in [index.html](index.html#L138-L155). Include paper-title, collaborators, and journal/venue.

4. **Adding courses/assignments:** Use Bootstrap card grids. Teaching materials go in `documents/teaching/` with proper course code structure. If pages become too long, consider using Bootstrap's collapse component for collapsible sections.

5. **Color consistency:** Always reference the documented color palette. Avoid hardcoding colors outside [css/styles.css](css/styles.css).

6. **Responsive design:** Test changes at breakpoint 768px (mobile vs. desktop). Custom responsive adjustments in media queries at end of CSS.

## SEO & Analytics

- **Meta tags:** Each page has consistent `description` and `keywords` meta tags in `<head>`. Update these when adding new pages.
- **Google Analytics:** Tracking ID `G-C1ECHGQLBQ` configured on all pages. Keep gtag.js implementation consistent.
- **Search Console:** [googleeb1d2246e8c282cb.html](googleeb1d2246e8c282cb.html) is the Google Search Console verification file.
- **Sitemap:** When adding new pages or documents, manually update [sitemap.xml](sitemap.xml) with new URLs and lastmod dates.

## Deployment

This is a GitHub Pages site - push to `main` branch to deploy. No build process required. The site is accessible at `https://pipeton8.github.io/`.

**Important:** Sitemap exists at [sitemap.xml](sitemap.xml) but may need manual updates when adding new pages or documents.
