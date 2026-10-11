# SlidesViewer settings

`SlidesViewer/` is generated: ModernSlides' `tools/deploy-site.mjs` writes it from the ModernSlides
repository (`~/GitHub/_misc/ModernSlides`) after every commit on its `main`, and pushes it here.
Do not edit `SlidesViewer/` by hand; the next deploy replaces it. Change these files instead:

- `site.json`: the folder to publish (`target`), whether search engines may index it (`noindex`),
  whether the viewer's own home-screen icon is kept (`appleTouchIcon`; false lets the site icon
  win), and the viewer settings:
  - `storage`: `"ask"` keeps decks in the tab until a visitor turns on "Remember decks on this
    device"; `"device"` always keeps them in the browser.
  - `linkedDecks`: `"same-origin"` opens `?deck=` links only from this site; `"any"` from anywhere.
  - `publish`: `false` hides the Publish button (GitHub Pages cannot run its PHP endpoint).
  - `start`: `"blank"` opens a blank deck when there is nothing to reopen; `"demo"` the demo.
    `?demo` always opens the demo.
- `site.css`: the editor's colours, applied after the app's own styles.

The folder starts with `_`, so Jekyll does not publish it. A deploy reads these files from
`origin/main`, so commit and push changes here before the next deploy (or run
`node tools/deploy-site.mjs` in ModernSlides afterwards).
