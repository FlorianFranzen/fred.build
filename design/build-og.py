#!/usr/bin/env python3
"""Render the Open Graph image static/og.jpg (1200 x 630): the hero band fading into white, the
wordmark from static/logo.svg, and the headline and location below it as outlined Inter.

Run inside `nix develop` (needs FONT_INTER, fontTools, uharfbuzz, resvg, ImageMagick):

    python3 design/build-og.py
"""
import base64, os, pathlib, re, subprocess, tempfile, tomllib
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

ROOT = pathlib.Path(__file__).resolve().parent.parent
INTER = pathlib.Path(os.environ["FONT_INTER"]) / "share/fonts/truetype/InterVariable.ttf"
W, H = 1200, 630
EXTRA = tomllib.loads((ROOT / "config.toml").read_text())["extra"]
ACCENT, LOCATION = EXTRA["accent"], EXTRA["location"]
HEADLINE = tomllib.loads((ROOT / "content/_index.md").read_text().split("+++")[1])["extra"]["headline"]
MARGIN = 78

def text(s, x, baseline, size, fill, weight=400):
    """One line of Inter as a <path>, starting at x on `baseline`."""
    font = instancer.instantiateVariableFont(TTFont(INTER), {"wght": weight, "opsz": 32})
    blob = hb.Blob.from_file_path(str(INTER)); face = hb.Face(blob); hbf = hb.Font(face)
    hbf.set_variations({"wght": weight, "opsz": 32})
    buf = hb.Buffer(); buf.add_str(s); buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": True, "calt": True})
    names, gs, k = font.getGlyphOrder(), font.getGlyphSet(), size / face.upem
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    adv = 0
    for i, p in zip(buf.glyph_infos, buf.glyph_positions):
        gs[names[i.codepoint]].draw(TransformPen(pen, (k, 0, 0, -k, x + (adv + p.x_offset) * k, baseline)))
        adv += p.x_advance
    return f'<path fill="{fill}" d="{pen.getCommands()}"/>'

logo = (ROOT / "static/logo.svg").read_text()
letters = re.search(r'<path fill="currentColor" d="([^"]+)"', logo).group(1)
dots = re.search(r'<path class="d" d="([^"]+)"', logo).group(1)
cap = 84  # wordmark cap height in px (the logo's paths have a cap height of 100)
hero = base64.b64encode((ROOT / "static/img/hero-1600.jpg").read_bytes()).decode()
band = W * 605 / 1600  # the hero image's height at full width

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0.45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/>
</linearGradient></defs>
<rect width="{W}" height="{H}" fill="#fff"/>
<image href="data:image/jpeg;base64,{hero}" width="{W}" height="{band:.1f}" preserveAspectRatio="xMidYMid slice"/>
<rect width="{W}" height="{band + 1:.1f}" fill="url(#fade)"/>
<g transform="translate({MARGIN} 462) scale({cap / 100})"><path fill="#111" d="{letters}"/><path fill="{ACCENT}" d="{dots}"/></g>
{text(f"{HEADLINE} · {LOCATION}", MARGIN, 600, 34, "#6b6b6b")}
</svg>
'''

with tempfile.TemporaryDirectory() as tmp:
    src, png = pathlib.Path(tmp) / "og.svg", pathlib.Path(tmp) / "og.png"
    src.write_text(svg)
    subprocess.run(["resvg", "-w", str(W), str(src), str(png)], check=True)
    subprocess.run(["magick", str(png), "-strip", "-quality", "85", str(ROOT / "static/og.jpg")], check=True)
print(f"static/og.jpg  {W} x {H}")
