# Rest Mode — brand spec & implementation handoff

Single source of truth for the Rest Mode identity. Values are final; the SVG masters in `brand-assets/` are generated from exactly these numbers. Hand this file to Claude Code alongside the repo.

---

## 0. Decisions (read first)

- **Dark mode is the expected default.** The site skin leans on the dark "Slate" room; light ("Cream") is the secondary theme.
- **Primary monogram = the period mark (`rm.`)**, for both avatar and favicon. The strip monogram is kept as a **documented alternate** (full values in §5), not active. Rationale: the rim / legibility tradeoff only appears in light mode, and the period survives shrinking to favicon size best.
- **One rim color everywhere: `#575757`.** This overrides the earlier per-element `#6b6b6b`. The rim is a **light-mode-only** element (dark mode uses the amber glow instead), so it is invisible in the default dark skin.
- Wordmark, tone, and rooms are locked (§1).

---

## 1. Core tokens

| Token | Value | Use |
|---|---|---|
| `--rm-amber` | `#e07b1e` | gradient center; glow color |
| `--rm-amber-edge` | `#ffb25a` | gradient edge/core |
| `--rm-amber-end` | `rgba(255,178,90,0.15)` | gradient outer stops (edge color @ 0.15) |
| `--rm-ink-dark` | `#ece4d6` | text on dark |
| `--rm-ink-light` | `#1a1712` | text on light |
| `--rm-slate` | `#15181f` | dark room / site background |
| `--rm-tile` | `#0f1218` | icon tile background (near-black) |
| `--rm-cream` | `#f2ece1` | light room / paper |
| `--rm-rim` | `#575757` | light-mode rim (all elements) |
| Typeface | **Sora** (Google Fonts), weight **600** for the wordmark & monogram | |
| Body typeface | **Inter** (Google Fonts), 400 / 700 + real italic, **16px** body copy. Sora stays on headings, labels and nav | Alternate: **Plus Jakarta Sans** (runner-up; drop-in swap) |

Amber `#e07b1e` = `rgb(224,123,30)`. Rim `#575757` = `rgb(87,87,87)`.

---

## 2. The amber strip (shared construction)

The horizontal gradient is identical everywhere it appears; only width/height change.

```css
background: linear-gradient(90deg,
  rgba(255,178,90,0.15) 0%,   /* end fill */
  #ffb25a               15%,  /* fade position */
  #e07b1e               50%,
  #ffb25a               85%,
  rgba(255,178,90,0.15) 100%);
border-radius: 99px;
```

**Dark mode → glow** (no rim):
```css
box-shadow: 0 0 8px  rgba(224,123,30,0.60),
            0 0 20px rgba(224,123,30,0.30);
```

**Light mode → rim** (no glow). A blurred, downward layer sits *behind* the strip:
```css
position: relative;
/* the rim */
&::before{
  content:""; position:absolute;
  inset: calc(-1 * var(--rim-y)) calc(-1 * var(--rim-x));  /* Y X */
  transform: translateY(var(--rim-offset));
  border-radius: 99px;
  filter: blur(var(--rim-blur));
  opacity: var(--rim-opacity);
  background: linear-gradient(to top,
    #575757                    0%,
    rgba(87,87,87,0.45)       50%,
    transparent              100%);
}
```
The dot mark uses the same idea with a solid disc (`background: #575757`) and `border-radius: 50%` instead of the gradient bar.

**Period dot fill** (the amber indicator):
```css
background: radial-gradient(circle at 50% 42%, #ffb25a, #e07b1e 72%);
border-radius: 50%;
/* dark tile glow: */ box-shadow: 0 0 5px #e07b1e;
```

---

## 3. Wordmark  `rest mode`

Lowercase, Sora 600, letter-spacing **-0.025em**. Strip centered beneath, **18px** gap.

| Property | Value |
|---|---|
| Font size (desktop) | 52px (was `clamp(30px, 6vw, 52px)`) |
| Strip size | **290 × 6 px** |
| Gap (text → strip) | 18px |
| Gradient fade | 15% · end fill 0.15 |
| **Rim** (light only) | color `#575757` · opacity **0.6** · width X **3.5px** · Y **4.5px** · offset 0 · blur **6px** · type **downward** |
| Subtitle | *game reviews for people with limited time* (Oct 2026; replaces *when your devices get more sleep than game time*) |

Assets: `brand-assets/wordmark-dark.svg`, `brand-assets/wordmark-light.svg`.

---

## 4. Monogram — PERIOD  `rm.`  (PRIMARY)

Sora 600, letter-spacing -0.02em, tile radius as noted. Dark tiles use the glow; the light chip uses the rim.

**Avatar (large)**
| | |
|---|---|
| Tile radius | 22% |
| Dot | 9px · x +2px · **bottom aligned to the baseline** |
| Rim | `#575757` · opacity 0.3 · X 1.5 · Y 1.5 · offset 0 · blur 3 · downward |

**Favicon (small)**
| | |
|---|---|
| Tile radius | 26% |
| Dot | 5px · x +1px · **bottom aligned to the baseline** |
| Rim | opacity **0** (no rim — leans on the tile edge) · X 0 · Y 0 · blur 1.5 |

> **Dot placement:** the dot's *bottom* sits on the `rm` baseline (level with the bottom of the letters) and trails the `m` by the x offset — a true full-stop position, not a downward-offset bullet.

Assets: `brand-assets/avatar-period.svg`, `brand-assets/favicon-period.svg`.

---

## 5. Monogram — STRIP  `rm` + bar  (ALTERNATE — not active)

Recorded so a switch is a swap, not a rebuild.

**Avatar (large)** — bar **55 × 4px**, gap 0, fade 15% / end 0.15. Rim `#575757` · opacity 0.6 · X 2 · Y 1.5 · offset 0 · blur 3 · downward.

**Favicon (small)** — bar **18 × 2px**, gap 0, fade 15% / end 0.15. Rim `#575757` · opacity 0.6 · X 0.8 · Y 0.6 · offset 0 · blur 1.5 · downward.

Assets: `brand-assets/avatar-strip-ALT.svg`, `brand-assets/favicon-strip-ALT.svg`.

---

## 6. Theme behavior summary

| | Dark (Slate, default) | Light (Cream) |
|---|---|---|
| Background | `#15181f` | `#f2ece1` |
| Text ink | `#ece4d6` | `#1a1712` |
| Strip / dot treatment | amber **glow** (box-shadow) | grey **rim** (`#575757`, downward) |
| Icon tiles | `#0f1218`, glow | `#f2ece1` cream, grey rim |

The rim never shows in dark mode; the glow never shows in light mode. They are mutually exclusive per theme.

---

## 7. For Claude Code — implementation notes

1. **Tokens first.** Add §1 as CSS custom properties (or the repo's existing token system) before touching components.
2. **Wordmark = a component,** not a static image, so it inherits the theme (glow vs rim). Use the Sora webfont, weight 600. The two SVGs are visual references / OG-image sources.
3. **Favicon + avatar export.** The `*-period.svg` masters are outlined (no font dependency) — export the favicon to the sizes the repo needs (16/32/48 `.ico`, 180 apple-touch, 192/512 PNG for the web manifest) and wire `<link rel="icon">` + manifest. Keep the `*-strip-ALT.svg` files in the repo but unreferenced.
4. **OG / social image.** Build from `wordmark-dark.svg` on a `#15181f` field.
5. **Apply to scaffolding.** Swap placeholder logo/favicon/title in the existing pages; set the header lockup and the site name to *Rest Mode* with the subtitle where appropriate.
6. **Session note:** these values were chosen visually in an interactive lab; treat this file as authoritative if any inline comment in the old prototypes disagrees.

---

## 8. Asset inventory (`brand-assets/`)

**Wordmark**
- `wordmark-dark.svg` — full lockup, glow, transparent bg (dark headers / OG)
- `wordmark-light.svg` — full lockup, rim, transparent bg (cream headers)

**Primary marks — period**
- `avatar-period.svg` / `favicon-period.svg` — dark tiles (glow)
- `avatar-period-light.svg` / `favicon-period-light.svg` — cream tiles (rim; favicon has no rim by design)

**Alternate — strip** (keep unreferenced)
- `avatar-strip-ALT.svg` / `favicon-strip-ALT.svg` — dark tiles
- `avatar-strip-ALT-light.svg` / `favicon-strip-ALT-light.svg` — cream tiles

All SVGs use outlined Sora glyphs, so they render identically without the font installed.
