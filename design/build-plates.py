#!/usr/bin/env python3
"""Generate the project cover "plates": 1000x400 SVGs on the surface colour, each project's
mark drawn in the text colour with the accent as a detail. They follow the viewer's colour scheme through a media query,
which works inside <img>. Do not run svgo on the output: it inlines the `svg{--bg…}` rule as a
style attribute, which then overrides the dark-mode media rule. Run inside `nix develop`:

    python3 design/build-plates.py

Writes content/projects/<slug>/cover.svg for every project listed below.
"""
import base64, math, os, pathlib, random, re, tomllib
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARKS = ROOT / "design/marks"
INTER = pathlib.Path(os.environ["FONT_INTER"]) / "share/fonts/truetype/InterVariable.ttf"
JBM = pathlib.Path(os.environ["FONT_JBMONO"]) / "share/fonts/truetype/JetBrainsMono-Bold.ttf"
W, H = 1000, 400

ACCENT = tomllib.loads((ROOT / "config.toml").read_text())["extra"]["accent"]  # same in both themes
STYLE = f"""<style>svg{{--bg:#f6f6f4;--fg:#111;--accent:{ACCENT}}}@media (prefers-color-scheme:dark){{svg{{--bg:#181818;--fg:#f1f1f1}}}}</style>"""

def plate(body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {W} {H}" role="img" aria-label="{title}">{STYLE}'
            f'<rect width="{W}" height="{H}" fill="var(--bg)"/>{body}</svg>\n')

def text_paths(text, font_path, size, cx, baseline, **axes):
    """Centre `text` at cx on `baseline`, return SVG path data (glyphs as outlines)."""
    tt = TTFont(font_path)
    if "fvar" in tt:
        tt = instancer.instantiateVariableFont(tt, axes, inplace=True)
    blob = hb.Blob.from_file_path(str(font_path)); face = hb.Face(blob); font = hb.Font(face)
    if axes: font.set_variations(axes)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": False})
    names = tt.getGlyphOrder(); gs = tt.getGlyphSet(); s = size / face.upem
    total = sum(p.x_advance for p in buf.glyph_positions) * s
    x = cx - total / 2; out = []
    for i, p in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        gs[names[i.codepoint]].draw(TransformPen(pen, (s, 0, 0, -s, x + p.x_offset * s, baseline)))
        out.append(pen.getCommands()); x += p.x_advance * s
    return " ".join(out)

def inner_svg(path):
    """Body of a cleaned mark (everything inside <svg>…</svg>) plus its viewBox."""
    s = path.read_text()
    head_end = s.index(">") + 1
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s[:head_end]).group(1).split()]
    return s[head_end:s.rindex("</svg>")], vb

def place(mark, vb, cx, cy, height, fill="var(--fg)"):
    # resolve currentColor explicitly: some renderers do not carry `color` into <use> copies;
    # plain href on <use> needs no xlink namespace
    mark = mark.replace("currentColor", fill).replace("xlink:href", "href")
    scale = height / vb[3]; w = vb[2] * scale
    return (f'<g transform="translate({cx - w/2:.1f} {cy - height/2:.1f}) scale({scale:.4f}) '
            f'translate({-vb[0]} {-vb[1]})" fill="{fill}" color="{fill}">{mark}</g>')

plates = {}

# Mind the Gap: the project's official mark, copied from gliology/mind-the-gap assets/logo.svg
# (red shield, blue bar, white words). It is maintained there; here it is only placed and
# recoloured for the plate.
m, vb = inner_svg(MARKS / "mind-the-gap.svg")
# On this site the mark takes the site palette: shield in the accent, bar in the text colour,
# words in the page colour.
m = m.replace("#dc241f", "var(--accent)").replace("#0019a8", "var(--fg)").replace('fill="#fff"', 'fill="var(--bg)"')
plates["mind-the-gap"] = plate(place(m, vb, 500, 200, 260), "The Mind the Gap mark in the site's colours: a shield with a bar reading MIND THE GAP")

# nixpkgs: the Nix snowflake, CC-BY 4.0, NixOS/nixos-artwork
m, vb = inner_svg(MARKS / "nixos.svg")
# The snowflake is two arm shapes, each drawn once and reused twice. Like the original's
# two blues, one shape takes the accent, the other the text colour, so the arms alternate.
m = re.sub(r'(<path id="e" [^>]*?)fill:currentColor', r'\1fill:var(--accent)', m, count=1)
plates["nixpkgs"] = plate(place(m, vb, 500, 200, 240), "The Nix snowflake, three arms in the accent")

# Polkadot spec: the Polkadot mark
m, vb = inner_svg(MARKS / "polkadot.svg")
plates["polkadot-spec"] = plate(place(m, vb, 500, 200, 220), "The Polkadot mark")

# NeuroSuite: a spike train; one spike in the accent
rnd = random.Random(7)
pts = []
for x in range(100, 901, 4):
    y = 200 + rnd.uniform(-7, 7)
    pts.append((x, y))
def spike(x0, depth, width=22):
    for k, (x, y) in enumerate(pts):
        d = x - x0
        if -width <= d <= width:
            pts[k] = (x, y - depth * math.exp(-(d / (width / 2.4)) ** 2) + (depth * 0.28 if d > width * 0.35 else 0) * math.exp(-((d - width * 0.7) / 8) ** 2))
spike(260, 120); spike(480, 95); spike(700, 130)
d = "M" + " L".join(f"{x} {y:.1f}" for x, y in pts)
accent = [p for p in pts if 650 <= p[0] <= 750]
da = "M" + " L".join(f"{x} {y:.1f}" for x, y in accent)
plates["neurosuite"] = plate(
    f'<path d="{d}" fill="none" stroke="var(--fg)" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>'
    f'<path d="{da}" fill="none" stroke="var(--accent)" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>',
    "An extracellular spike train with one spike highlighted")

# Open Ephys: the wordmark as a raster, inverted in dark mode
png = base64.b64encode((MARKS / "open-ephys.png").read_bytes()).decode()
plates["open-ephys"] = plate(
    '<style>@media (prefers-color-scheme:dark){image{filter:invert(1)}}</style>'
    f'<image href="data:image/png;base64,{png}" x="250" y="130" width="500" height="140" preserveAspectRatio="xMidYMid meet"/>',
    "The Open Ephys wordmark")

# KaTeXify: a dollar-delimited sigma, the thing the extension turns into mathematics
plates["katexify"] = plate(
    f'<path d="{text_paths("$", JBM, 190, 360, 268)}" fill="var(--accent)"/>'
    f'<path d="{text_paths("Σ", INTER, 200, 500, 272, wght=600, opsz=32)}" fill="var(--fg)"/>'
    f'<path d="{text_paths("$", JBM, 190, 640, 268)}" fill="var(--accent)"/>',
    "A sigma between dollar signs")

# the arrow used between two things on a plate, as on btrborg
ARROW = '<path d="M{x0} 200h{w}" stroke="var(--accent)" stroke-width="8" stroke-linecap="round"/><path d="M{x1} 180l26 20-26 20" fill="none" stroke="var(--accent)" stroke-width="8" stroke-linejoin="round" stroke-linecap="round"/>'

# ceclaunchd: a remote control, an arrow, a shell prompt
plates["ceclaunchd"] = plate(
    '<rect x="300" y="95" width="110" height="210" rx="28" fill="none" stroke="var(--fg)" stroke-width="6"/>'
    + "".join(f'<circle cx="{cx}" cy="{cy}" r="11" fill="var(--fg)"/>' for cx in (333, 377) for cy in (190, 230, 270))
    + '<circle cx="355" cy="140" r="16" fill="var(--accent)"/>'
    + ARROW.format(x0=450, w=70, x1=506) +
    '<rect x="560" y="130" width="200" height="140" rx="8" fill="none" stroke="var(--fg)" stroke-width="6"/>'
    f'<path d="{text_paths(">_", JBM, 90, 660, 232)}" fill="var(--fg)"/>',
    "A remote control triggering a shell")

# pseudocode-ruby: an indented algorithm, keywords in the text colour, a ruby beside it
plates["pseudocode-ruby"] = plate(
    "".join(f'<rect x="{x}" y="{y}" width="{w}" height="18" rx="3" fill="var(--fg)"/>'
            for x, y, w in ((260, 120, 200), (300, 160, 160), (340, 200, 190), (340, 240, 120), (300, 280, 90)))
    + '<rect x="260" y="120" width="60" height="18" rx="3" fill="var(--accent)"/>'
    + '<path d="M640 130h120l40 45-100 105-100-105z" fill="var(--accent)"/>'
    '<path d="M600 175h200M640 130l20 45 40 105 40-105 20-45M660 175l40-45 40 45" fill="none" stroke="var(--bg)" stroke-width="5" stroke-linejoin="round"/>',
    "Pseudocode lines beside a ruby")

# lxc-wold: the magic packet's six FF bytes waking a container
plates["lxc-wold"] = plate(
    f'<path d="{text_paths("FF FF FF", JBM, 54, 340, 186)}" fill="var(--fg)"/>'
    f'<path d="{text_paths("FF FF FF", JBM, 54, 340, 250)}" fill="var(--fg)"/>'
    + ARROW.format(x0=500, w=70, x1=556) +
    '<rect x="610" y="120" width="170" height="160" rx="10" fill="none" stroke="var(--fg)" stroke-width="6"/>'
    '<path d="M666 165a48 48 0 1 0 58 0" fill="none" stroke="var(--accent)" stroke-width="10" stroke-linecap="round"/>'
    '<path d="M695 145v55" stroke="var(--accent)" stroke-width="10" stroke-linecap="round"/>',
    "A magic packet powering on a container")

# asciidoctor-kaitai: a struct drawn as stacked fields, one field in the accent, an arrow to a page
fields = "".join(f'<rect x="300" y="{110 + i * 48}" width="200" height="38" rx="3" fill="none" stroke="var(--fg)" stroke-width="5"/>' for i in range(4))
plates["asciidoctor-kaitai"] = plate(
    fields + '<rect x="300" y="206" width="200" height="38" rx="3" fill="var(--accent)"/>'
    '<path d="M530 200h90" stroke="var(--fg)" stroke-width="6" stroke-linecap="round"/><path d="M606 184l24 16-24 16" fill="none" stroke="var(--fg)" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>'
    '<rect x="650" y="95" width="80" height="210" rx="4" fill="none" stroke="var(--fg)" stroke-width="5"/>'
    + "".join(f'<rect x="666" y="{118 + i * 22}" width="{48 if i % 3 else 30}" height="7" rx="2" fill="var(--fg)" opacity=".55"/>' for i in range(8)),
    "A binary format definition rendered into a document")

# btrborg: a snapshot block becoming an archive block, the arrow in the accent
plates["btrborg"] = plate(
    '<rect x="230" y="150" width="200" height="100" rx="8" fill="var(--fg)"/>'
    '<rect x="250" y="130" width="200" height="100" rx="8" fill="none" stroke="var(--fg)" stroke-width="6"/>'
    '<path d="M480 200h70" stroke="var(--accent)" stroke-width="8" stroke-linecap="round"/><path d="M536 180l26 20-26 20" fill="none" stroke="var(--accent)" stroke-width="8" stroke-linejoin="round" stroke-linecap="round"/>'
    '<rect x="590" y="140" width="190" height="120" rx="8" fill="none" stroke="var(--fg)" stroke-width="6"/>'
    '<path d="M590 180h190M685 140v120" stroke="var(--fg)" stroke-width="6"/>',
    "A snapshot archived into a repository")

# linux-mobile-wallet: a phone outline with a QR-like block, the camera dot in the accent
plates["linux-mobile-wallet"] = plate(
    '<rect x="430" y="60" width="140" height="280" rx="18" fill="none" stroke="var(--fg)" stroke-width="7"/>'
    '<circle cx="500" cy="84" r="5" fill="var(--accent)"/>'
    + "".join(f'<rect x="{458 + (i % 4) * 22}" y="{130 + (i // 4) * 22}" width="16" height="16" fill="var(--fg)"/>' for i in range(16) if i not in (5, 6, 9, 10, 1, 14)),
    "A phone showing a QR code")

# neuro-tools (draft): a file block with a waveform
plates["neuro-tools"] = plate(
    '<rect x="330" y="110" width="340" height="180" rx="8" fill="none" stroke="var(--fg)" stroke-width="6"/>'
    '<path d="M360 200h40l12-40 14 80 12-60 10 20h60l10-30 14 60 12-50 10 20h90" fill="none" stroke="var(--accent)" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>',
    "A recording file with a waveform")

# wii-u-gamepad (draft): a gamepad outline, the screen in the text colour, one button in the accent
plates["wii-u-gamepad"] = plate(
    '<rect x="300" y="130" width="400" height="150" rx="40" fill="none" stroke="var(--fg)" stroke-width="7"/>'
    '<rect x="400" y="160" width="200" height="90" rx="6" fill="var(--fg)"/>'
    '<circle cx="350" cy="205" r="16" fill="none" stroke="var(--fg)" stroke-width="6"/>'
    '<circle cx="650" cy="205" r="16" fill="none" stroke="var(--fg)" stroke-width="6"/><circle cx="650" cy="205" r="5" fill="var(--accent)"/>',
    "A gamepad with a screen")

for slug, svg in plates.items():
    out = ROOT / "content/projects" / slug / "cover.svg"
    out.write_text(svg)
    print(f"{out.relative_to(ROOT)}  {len(svg) // 1024} KB")
