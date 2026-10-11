# rest mode: writing pipeline

You write in Apple Notes using Markdown. `build.py` turns that into the static pages in `rest-mode/`. GitHub Pages never publishes this folder, because its name starts with `_`.

```
Notes app ──import──▶ _rest-mode/content/*.md ──build──▶ rest-mode/*.html
```

Every command runs from the repo root. `uv` installs the Python packages the first time.

| What | Command |
|---|---|
| Get a blank review template (copied to the clipboard) | `uv run _rest-mode/build.py template --copy` |
| Import a review note | `uv run _rest-mode/build.py import "Exact note title"` |
| Import the About note | `uv run _rest-mode/build.py import-about` |
| Rebuild every page | `uv run _rest-mode/build.py build` |
| Rebuild without the placeholder reviews | `uv run _rest-mode/build.py build --no-placeholders` |

To check the result, open `rest-mode/index.html` in a browser.

## Writing a review in Notes

The first line is the review title. Next come `key: value` lines. A line with just `---` ends them, and the review text follows.

```
What Remains of Edith Finch — a house full of short stories
game: What Remains of Edith Finch
verdict: no-rest
played-on: PS5
session: 30–60 min
time-to-beat: 2–3 h
genre: Narrative adventure
developer: Giant Sparrow
release: 2017
platforms: PC, PS4, Xbox, Switch
excerpt: One or two sentences for the review card and link previews.
cover: https://…portrait image…
hero: https://…wide image…
---
## The pitch
Write freely: _italics_, **bold**, [links](https://…).

## Pros
- …

## Cons
- …

## Verdict
The closing paragraph shown next to the light strip.
```

- **verdict**: one of `no-rest`, `turn-on`, `rest-mode` or `turn-off`.
- **Special sections**: `## Pros`, `## Cons` and `## Verdict` are pulled out into their own boxes. Every other `##` heading stays in the review body.
- **Optional keys**: anything except `game` and `verdict` can be left out. Empty fields don't appear on the page.
- **date**: defaults to the note's last-modified day. Add `date: 2026-07-20` to set it yourself.
- **slug**: the page address defaults to the game name (e.g. `reviews/what-remains-of-edith-finch.html`). Add `slug:` to override it.
- **Images**: `cover` is the portrait image on the review card. `hero` is the wide image at the top of the review and on the home page. Each can be a web link or a file path. The build downloads, resizes and saves both in `rest-mode/images/<slug>/`. It downloads them once; add `--refresh-images` to fetch them again.
- **Importing twice is fine.** The `.md` file is overwritten with the note's current text. Keys you added to the `.md` by hand are kept unless the note sets them too.

## The About note

The note named **About** needs a `##` heading containing "About". Everything under it becomes the About page, and its `###` headings become the page's section headings. An optional `##` section containing "Landing" is saved to `content/intro.md`; the site doesn't use it at the moment.

Headings can be Notes' real Title/Heading/Subheading styles or plain bold lines. Text written into a note by a script comes back as bold lines, and both forms import the same way.

## Placeholders

The sample reviews have `placeholder: true`. Delete those files from `content/reviews/` once real reviews exist. `build --no-placeholders` hides them without deleting them. Placeholder reviews are never added to `sitemap.xml`.

## Gotchas

- **Note titles must match exactly**, including capitals and accents.
- **The importer only handles text.** Notes' own formatting (bold, italic, headings, bulleted lists) converts, and Markdown typed as text passes through unchanged. Tables, checklists and drawings don't come across.
- **Images pasted into a note** get saved under `rest-mode/images/<slug>/`, but only if Notes includes them in what it hands out. That path is untested.
- **Edit sources, not output.** The HTML files in `rest-mode/` are generated, so hand edits there are lost on the next build. Change the content, the templates in `_rest-mode/templates/`, or `rest-mode/css/rest-mode.css` instead.
- **`build` also rewrites the rest mode block of `sitemap.xml`.**
