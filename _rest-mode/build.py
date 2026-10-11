# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "jinja2==3.1.6",
#     "markdown==3.8",
#     "pyyaml==6.0.2",
#     "pillow==11.3.0",
# ]
# ///
"""Rest Mode site builder.

Markdown sources in _rest-mode/content/ are rendered with the Jinja templates
in _rest-mode/templates/ into static HTML under rest-mode/. The folder name
starts with "_" so GitHub Pages (Jekyll) never publishes the sources.

Commands (run from anywhere):
    uv run _rest-mode/build.py build [--no-placeholders] [--refresh-images]
    uv run _rest-mode/build.py import "Note title" [--slug SLUG]
    uv run _rest-mode/build.py import-about [--note About]
    uv run _rest-mode/build.py template [--copy]

See _rest-mode/README.md for the writing workflow.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import html
import io
import re
import subprocess
import sys
import unicodedata
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from PIL import Image

SRC = Path(__file__).resolve().parent
REPO = SRC.parent
OUT = REPO / "rest-mode"
CONTENT = SRC / "content"
REVIEWS = CONTENT / "reviews"
SITE_URL = "https://pipeton8.github.io/rest-mode/"

# Verdict scale: the PS5 light strip. Order matters (best first) for filters/legend.
VERDICTS = {
    "no-rest":   {"name": "No rest",   "meaning": "Strongly recommended"},
    "turn-on":   {"name": "Turn on",   "meaning": "Recommended"},
    "rest-mode": {"name": "Rest mode", "meaning": "Mixed"},
    "turn-off":  {"name": "Turn off",  "meaning": "Avoid"},
}

# Metadata keys accepted in a review (Notes block or YAML front matter).
# Values are display labels for the game-info grid; None = not shown there.
META_KEYS = {
    "game": None, "slug": None, "date": None, "verdict": None, "excerpt": None,
    "cover": None, "hero": None, "placeholder": None,
    "played-on": "Played on",
    "session": "Session length",
    "time-to-beat": "Time to beat",
    "genre": "Genre",
    "developer": "Developer",
    "release": "Release",
    "platforms": "Also on",
}

MD_EXTENSIONS = ["extra", "smarty", "sane_lists"]


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def split_front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, flags=re.S)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def write_md(path: Path, meta: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000).strip()
    path.write_text(f"---\n{fm}\n---\n\n{body.strip()}\n", encoding="utf-8")


def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=MD_EXTENSIONS, output_format="html")


def to_date(value) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value).strip())


def human_date(d: dt.date) -> str:
    return f"{d:%B} {d.day}, {d.year}"


def split_sections(md_text: str) -> list[tuple[str | None, str]]:
    """Split markdown into (h2 heading, text) chunks; the first chunk may have no heading."""
    parts = re.split(r"(?m)^##[ \t]+(.+?)[ \t]*#*[ \t]*$", md_text)
    sections = [(None, parts[0])]
    for i in range(1, len(parts), 2):
        sections.append((parts[i].strip(), parts[i + 1]))
    return sections


def list_items(md_text: str) -> list[str]:
    items = []
    for line in md_text.splitlines():
        m = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$", line)
        if m:
            items.append(markdown.markdown(m.group(1), extensions=["smarty"])[3:-4])  # strip <p></p>
    return items


# --------------------------------------------------------------------------
# Images: download/copy once into rest-mode/images/<slug>/
# --------------------------------------------------------------------------

IMAGE_SPECS = {"cover": (600, 900), "hero": (1600, 900)}  # max width, max height


def ensure_image(slug: str, kind: str, src: str | None, refresh: bool) -> str | None:
    if not src:
        return None
    out = OUT / "images" / slug / f"{kind}.jpg"
    if out.exists() and not refresh:
        return f"images/{slug}/{kind}.jpg"
    if re.match(r"^https?://", src):
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0 rest-mode-builder"})
        data = urllib.request.urlopen(req, timeout=30).read()
    else:
        path = Path(src).expanduser()
        if not path.is_absolute():
            path = (SRC / path) if (SRC / path).exists() else (REPO / path)
        data = path.read_bytes()
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail(IMAGE_SPECS[kind], Image.Resampling.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"  image  {out.relative_to(REPO)}  ({img.width}x{img.height})")
    return f"images/{slug}/{kind}.jpg"


# --------------------------------------------------------------------------
# Content model
# --------------------------------------------------------------------------

@dataclass
class Review:
    slug: str
    meta: dict
    title: str
    date: dt.date
    verdict: str
    body_html: str
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    verdict_html: str = ""
    cover: str | None = None
    hero: str | None = None
    words: int = 0

    @property
    def url(self) -> str:
        return f"reviews/{self.slug}.html"

    @property
    def info(self) -> list[tuple[str, str]]:
        return [(label, str(self.meta[k])) for k, label in META_KEYS.items()
                if label and self.meta.get(k)]

    @property
    def read_minutes(self) -> int:
        return max(1, round(self.words / 220))


def load_review(path: Path, refresh: bool) -> Review:
    meta, body = split_front_matter(path.read_text(encoding="utf-8"))
    meta = {k.replace("_", "-"): v for k, v in meta.items()}
    unknown = set(meta) - set(META_KEYS) - {"title"}
    if unknown:
        print(f"  warning: {path.name}: unknown keys {sorted(unknown)}", file=sys.stderr)
    slug = meta.get("slug") or path.stem
    verdict = str(meta.get("verdict", "")).strip().lower().replace(" ", "-")
    if verdict not in VERDICTS:
        raise SystemExit(f"{path.name}: verdict must be one of {list(VERDICTS)}, got {verdict!r}")

    pros, cons, verdict_md, rest = [], [], "", []
    for heading, text in split_sections(body):
        key = (heading or "").lower()
        if key in ("pros", "the good"):
            pros = list_items(text)
        elif key in ("cons", "the bad"):
            cons = list_items(text)
        elif key in ("verdict", "final verdict"):
            verdict_md = text
        else:
            rest.append(text if heading is None else f"## {heading}\n{text}")
    body_md = "\n".join(rest)

    return Review(
        slug=slug, meta=meta,
        title=meta.get("title") or f"{meta.get('game', slug)}",
        date=to_date(meta.get("date", dt.date.today())),
        verdict=verdict,
        body_html=md_to_html(body_md),
        pros=pros, cons=cons,
        verdict_html=md_to_html(verdict_md) if verdict_md.strip() else "",
        cover=ensure_image(slug, "cover", meta.get("cover"), refresh),
        hero=ensure_image(slug, "hero", meta.get("hero"), refresh),
        words=len(re.findall(r"\w+", body)),
    )


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def build(no_placeholders: bool, refresh_images: bool) -> None:
    env = Environment(loader=FileSystemLoader(SRC / "templates"), undefined=StrictUndefined,
                      autoescape=True, trim_blocks=True, lstrip_blocks=True)
    env.filters["human_date"] = human_date
    env.globals.update(verdicts=VERDICTS, site_url=SITE_URL)

    reviews = [load_review(p, refresh_images) for p in sorted(REVIEWS.glob("*.md"))]
    if no_placeholders:
        reviews = [r for r in reviews if not r.meta.get("placeholder")]
    reviews.sort(key=lambda r: r.date, reverse=True)

    about_meta, about_md = split_front_matter((CONTENT / "about.md").read_text(encoding="utf-8"))

    played_on = sorted({str(r.meta["played-on"]) for r in reviews if r.meta.get("played-on")})

    def render(template: str, out: Path, **ctx) -> None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(env.get_template(template).render(**ctx), encoding="utf-8")
        print(f"  page   {out.relative_to(REPO)}")

    render("index.html", OUT / "index.html", depth=0, page="home",
           reviews=reviews, featured=reviews[:2], played_on=played_on)
    render("about.html", OUT / "about.html", depth=0, page="about",
           about_html=md_to_html(about_md), about_meta=about_meta)
    for r in reviews:
        render("review.html", OUT / r.url, depth=1, page="review", r=r)

    # Remove pages of reviews that no longer exist (or are hidden placeholders)
    live = {OUT / r.url for r in reviews}
    for stale in (OUT / "reviews").glob("*.html"):
        if stale not in live:
            stale.unlink()
            print(f"  removed {stale.relative_to(REPO)}")

    update_sitemap(reviews, about_meta)
    print(f"Built {len(reviews)} review(s).")


def update_sitemap(reviews: list[Review], about_meta: dict) -> None:
    """Rewrite the Rest Mode block of sitemap.xml; placeholder reviews are left out."""
    path = REPO / "sitemap.xml"
    xml = path.read_text(encoding="utf-8")
    xml = re.sub(r"\s*<url>\s*<loc>https://pipeton8\.github\.io/(?:rest-mode|blog)/.*?</url>", "", xml, flags=re.S)
    real = [r for r in reviews if not r.meta.get("placeholder")]
    newest = max((r.date for r in real), default=dt.date.today())
    about_date = to_date(about_meta.get("updated", newest))

    def entry(loc: str, lastmod: dt.date, freq: str, prio: str) -> str:
        return (f"  <url>\n       <loc>{SITE_URL}{loc}</loc>\n"
                f"       <lastmod>{lastmod.isoformat()}T00:00:00+00:00</lastmod>\n"
                f"       <changefreq>{freq}</changefreq>\n       <priority>{prio}</priority>\n  </url>")

    block = [entry("index.html", newest, "weekly", "0.8000"), entry("about.html", about_date, "monthly", "0.6400")]
    block += [entry(r.url, r.date, "monthly", "0.6400") for r in real]
    xml = xml.replace("</urlset>", "\n".join(block) + "\n</urlset>")
    path.write_text(xml, encoding="utf-8")


# --------------------------------------------------------------------------
# Apple Notes import
# --------------------------------------------------------------------------

def read_note(title: str) -> tuple[str, str]:
    """Return (body_html, modification date ISO) of the first note with this exact title."""
    quoted = title.replace('"', '\\"')
    script = f'''
    tell application "Notes"
        set matches to every note whose name is "{quoted}"
        if (count of matches) is 0 then error "No note named {title}"
        set n to item 1 of matches
        set d to modification date of n
        return ((year of d) as string) & "-" & text -2 thru -1 of ("0" & ((month of d) as integer)) & "-" & text -2 thru -1 of ("0" & day of d) & linefeed & (body of n)
    end tell'''
    res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if res.returncode != 0:
        raise SystemExit(f"Could not read note {title!r}: {res.stderr.strip()}")
    date, _, body = res.stdout.partition("\n")
    return body, date.strip()


class NotesHTML(HTMLParser):
    """Convert the HTML that Notes returns into a list of (kind, text) blocks.

    Notes puts every line in its own <div>, headings in <h1>-<h3>, and blank
    lines as <div><br></div>. Markdown typed as plain text (links, _italics_)
    passes through untouched; Notes' own bold/italic become ** and *.
    """

    INLINE = {"b": "**", "strong": "**", "i": "*", "em": "*"}

    def __init__(self, image_sink):
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple[str, str]] = []
        self.buf: list[str] = []
        self.kind = "p"
        self.list_stack: list[str] = []
        self.href: str | None = None
        self.link_text: list[str] = []
        self.image_sink = image_sink

    def _flush(self):
        text = "".join(self.buf).replace("\xa0", " ").strip()
        if text or self.kind == "p":
            self.blocks.append((self.kind, text))
        self.buf, self.kind = [], "p"

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("h1", "h2", "h3", "h4"):
            self.kind = tag
        elif tag in ("ul", "ol"):
            self.list_stack.append(tag)
        elif tag == "li":
            self.kind = "li-" + (self.list_stack[-1] if self.list_stack else "ul")
        elif tag in self.INLINE:
            self.buf.append(self.INLINE[tag])
        elif tag == "a":
            self.href, self.link_text = a.get("href"), []
        elif tag == "img" and a.get("src", "").startswith("data:"):
            self.buf.append(f"![]({self.image_sink(a['src'])})")

    def handle_endtag(self, tag):
        if tag in ("div", "p", "li", "h1", "h2", "h3", "h4"):
            self._flush()
        elif tag in ("ul", "ol") and self.list_stack:
            self.list_stack.pop()
        elif tag in self.INLINE:
            self.buf.append(self.INLINE[tag])
        elif tag == "a":
            text = "".join(self.link_text)
            # Notes auto-links URLs typed inside [text](url): keep the raw text then
            self.buf.append(text if not self.href or text.strip() == self.href.strip()
                            else f"[{text}]({self.href})")
            self.href = None

    def handle_data(self, data):
        (self.link_text if self.href is not None else self.buf).append(data)


def normalize_headings(body_html: str) -> str:
    """Treat whole-line bold text as headings, as well as real <h1>-<h3>.

    Notes stores Title/Heading/Subheading as <h1>/<h2>/<h3>, but text written
    back into a note by a script (or pasted from elsewhere) comes out as bold
    spans: 24px+ -> title, 18px+ -> heading, plain bold line -> subheading.
    """
    def sized(m):
        size, text = int(m.group(1)), m.group(2)
        level = 1 if size >= 24 else 2 if size >= 18 else 3
        return f"<div><h{level}>{text}</h{level}></div>"
    body_html = re.sub(r'<div><b><span style="font-size: (\d+)px">([^<]*)</span></b></div>', sized, body_html)
    return re.sub(r"<div><b>([^<]+)</b></div>", r"<div><h3>\1</h3></div>", body_html)


def notes_to_blocks(body_html: str, image_dir: Path | None = None) -> list[tuple[str, str]]:
    counter = iter(range(1, 1000))

    def sink(data_uri: str) -> str:
        if image_dir is None:
            return ""
        m = re.match(r"data:image/(\w+);base64,(.*)", data_uri, flags=re.S)
        if not m:
            return ""
        n = next(counter)
        image_dir.mkdir(parents=True, exist_ok=True)
        img = Image.open(io.BytesIO(base64.b64decode(m.group(2)))).convert("RGB")
        img.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        out = image_dir / f"inline-{n}.jpg"
        img.save(out, "JPEG", quality=82, optimize=True)
        return f"../images/{image_dir.name}/inline-{n}.jpg"

    parser = NotesHTML(sink)
    parser.feed(normalize_headings(body_html))
    parser._flush()
    return parser.blocks


def blocks_to_md(blocks: list[tuple[str, str]], shift: int = 0) -> str:
    """Join blocks into markdown. shift moves heading levels (e.g. -1 turns h3 into ##)."""
    lines: list[str] = []
    for kind, text in blocks:
        if kind.startswith("h"):
            level = max(2, int(kind[1]) + shift)
            lines += ["", "#" * level + " " + text, ""]
        elif kind.startswith("li-"):
            lines.append(("1. " if kind == "li-ol" else "- ") + text)
        else:
            lines += [text, ""] if text else [""]
    md = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"


def import_review(title: str, slug: str | None) -> None:
    body_html, modified = read_note(title)
    blocks = notes_to_blocks(body_html)
    n_blocks = len(blocks)
    # Title: the note's first heading/line. Then "key: value" lines up to a line "---".
    while blocks and not blocks[0][1]:
        blocks.pop(0)
    review_title = blocks.pop(0)[1].lstrip("# ").strip()
    meta: dict = {"title": review_title}
    while blocks:
        kind, text = blocks[0]
        if not text:
            blocks.pop(0)
            continue
        if text.strip() in ("---", "—", "–"):  # Notes may turn --- into a dash
            blocks.pop(0)
            break
        m = re.match(r"^([A-Za-z][\w -]*?)\s*:\s*(.*)$", text)
        if not m or m.group(1).strip().lower().replace(" ", "-") not in META_KEYS:
            break
        meta[m.group(1).strip().lower().replace(" ", "-")] = m.group(2).strip()
        blocks.pop(0)

    slug = slug or meta.get("slug") or slugify(str(meta.get("game", review_title)))
    meta.setdefault("date", modified)
    # Pasted images: convert again, now saving them into the review's image folder,
    # and skip the same leading blocks (title + metadata) consumed above.
    if "data:image" in body_html:
        consumed = n_blocks - len(blocks)
        blocks = notes_to_blocks(body_html, OUT / "images" / slug)[consumed:]
    path = REVIEWS / f"{slug}.md"
    if path.exists():
        old_meta, _ = split_front_matter(path.read_text(encoding="utf-8"))
        old_meta.pop("placeholder", None)
        meta = {**old_meta, **meta}
    write_md(path, meta, blocks_to_md(blocks))
    print(f"Imported note {title!r} -> {path.relative_to(REPO)}")
    print("Next: uv run _rest-mode/build.py build")


def import_about(note: str) -> None:
    body_html, modified = read_note(note)
    blocks = notes_to_blocks(body_html)
    sections: dict[str, list] = {"intro": [], "about": []}
    current = None
    for kind, text in blocks:
        if kind == "h2" and "landing" in text.lower():
            current = "intro"
            continue
        if kind == "h2" and "about" in text.lower():
            current = "about"
            continue
        if current:
            sections[current].append((kind, text))
    if not sections["about"]:
        raise SystemExit('The note needs a "##" heading with "About" in it (an optional "Landing" section is kept in content/intro.md).')
    if sections["intro"]:
        write_md(CONTENT / "intro.md", {"updated": modified}, blocks_to_md(sections["intro"]))
    write_md(CONTENT / "about.md", {"updated": modified}, blocks_to_md(sections["about"], shift=-1))
    print(f"Imported note {note!r} -> content/about.md" + (" + content/intro.md" if sections["intro"] else ""))
    print("Next: uv run _rest-mode/build.py build")


NOTE_TEMPLATE = """Game title — a short, catchy review title
game: Game title
verdict: turn-on
played-on: PS5
session: 30–60 min
time-to-beat: 12 h
genre: Adventure
developer: Studio name
release: 2024
platforms: PC, PS5, Xbox, Switch
excerpt: One or two sentences for the review card.
cover: https://link-to-a-portrait-image.jpg
hero: https://link-to-a-wide-image.jpg
---
## First section
Write freely in Markdown: _italics_, **bold**, [links](https://example.com).

## Pros
- Something good

## Cons
- Something less good

## Verdict
The closing paragraph that sits next to the light strip.
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="render rest-mode/ from the markdown sources")
    b.add_argument("--no-placeholders", action="store_true", help="leave out reviews marked placeholder: true")
    b.add_argument("--refresh-images", action="store_true", help="re-download cover/hero images")
    i = sub.add_parser("import", help="import a review from Apple Notes")
    i.add_argument("note", help="exact note title in Notes")
    i.add_argument("--slug")
    a = sub.add_parser("import-about", help="import the landing text + About page from Apple Notes")
    a.add_argument("--note", default="About")
    t = sub.add_parser("template", help="print a blank review template to paste into Notes")
    t.add_argument("--copy", action="store_true", help="copy it to the clipboard instead")
    args = ap.parse_args()

    if args.cmd == "build":
        build(args.no_placeholders, args.refresh_images)
    elif args.cmd == "import":
        import_review(args.note, args.slug)
    elif args.cmd == "import-about":
        import_about(args.note)
    elif args.cmd == "template":
        if args.copy:
            subprocess.run(["pbcopy"], input=NOTE_TEMPLATE, text=True, check=True)
            print("Template copied to the clipboard.")
        else:
            print(NOTE_TEMPLATE)


if __name__ == "__main__":
    main()
