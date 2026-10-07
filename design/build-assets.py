#!/usr/bin/env python3
"""Generate the brand assets from the source fonts.

Run inside `nix develop` (needs FONT_INTER, FONT_JBMONO, fontTools, uharfbuzz):

    python3 design/build-assets.py

Writes:
    static/fonts/*.woff2        Latin subsets of Inter 400/600/800 and JetBrains Mono 400
    static/logo.svg             the F.R.E.D. wordmark as paths (dots carry class "d")
    static/favicon.svg          favicon: square accent tile with the letters cut out
    design/logo/*.svg           copies of the two above, for reference
"""
import os, pathlib, tomllib
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.ttLib.removeOverlaps import removeOverlaps
from fontTools import subset
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

ROOT = pathlib.Path(__file__).resolve().parent.parent
INTER = pathlib.Path(os.environ["FONT_INTER"]) / "share/fonts/truetype/InterVariable.ttf"
JBM = pathlib.Path(os.environ["FONT_JBMONO"]) / "share/fonts/truetype/JetBrainsMono-Regular.ttf"
FONTS = ROOT / "static/fonts"; FONTS.mkdir(parents=True, exist_ok=True)
LOGO = ROOT / "design/logo"; LOGO.mkdir(parents=True, exist_ok=True)

# the accent (marks: logo dots, favicon tile), the same in light and dark; set in config.toml
ACCENT = tomllib.loads((ROOT / "config.toml").read_text())["extra"]["accent"]

# Latin + punctuation + the few symbols the site uses.
UNICODES = (list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + list(range(0x2010, 0x2027))
            + [0x2030, 0x2039, 0x203A, 0x2044, 0x20AC, 0x2122, 0x2190, 0x2192, 0x2194, 0x2212, 0x2260, 0x2264, 0x2265, 0x25B6, 0x00D7])
FEATURES = ["calt", "ccmp", "clig", "kern", "liga", "locl", "mark", "mkmk", "rlig", "rvrn", "tnum", "case", "frac", "dnom", "numr", "ss01"]

def instance(path, **axes):
    f = TTFont(path)
    if "fvar" in f:
        f = instancer.instantiateVariableFont(f, axes, inplace=True)
    return f

def write_subset(font, out):
    opts = subset.Options()
    opts.layout_features = FEATURES
    opts.flavor = "woff2"
    opts.name_IDs = [1, 2, 3, 4, 6]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    font.flavor = "woff2"
    font.save(out)
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB")

# 1. web fonts
for w in (400, 600, 800):
    write_subset(instance(INTER, wght=w, opsz=14), FONTS / f"inter-{w}.woff2")
write_subset(TTFont(JBM), FONTS / "jetbrains-mono-400.woff2")

# 2. shaping helper: returns [(glyph name, x, advance)] in font units, kerned
def shape(path, text, features=(), **axes):
    blob = hb.Blob.from_file_path(str(path)); face = hb.Face(blob); font = hb.Font(face)
    if axes: font.set_variations(axes)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True, "calt": True, **{f: True for f in features}})
    names = TTFont(path).getGlyphOrder()
    out, x = [], 0
    for i, p in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((names[i.codepoint], x + p.x_offset, p.x_advance))
        x += p.x_advance
    return out, x, face.upem

def glyph_path(font, name, scale, dx, dy):
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, dx, dy)))
    return pen.getCommands()

# 3. wordmark: Inter 800 at optical size 32, cap height 100 units in a tight viewBox
wm_font = instance(INTER, wght=800, opsz=32)
cap = wm_font["OS/2"].sCapHeight
# ss07 is Inter's square punctuation: the dots are squares
glyphs, width, upem = shape(INTER, "F.R.E.D.", features=("ss07",), wght=800, opsz=32)
H = 100.0; s = H / cap  # scale so the cap height is 100
# tracking of 0.02em between glyphs, as in the design sheet
track = 0.02 * upem
letters, dots = [], []
for i, (name, gx, _adv) in enumerate(glyphs):
    d = glyph_path(wm_font, name, s, (gx + i * track) * s, H)
    (dots if name.startswith("period") else letters).append(d)
W = (width + (len(glyphs) - 1) * track) * s
# width/height give the inline SVG its header size (18 px tall) before the stylesheet applies
wordmark = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-H*0.02:.2f} {W:.2f} {H*1.04:.2f}" width="{18*W/(H*1.04):.0f}" height="18" role="img" aria-label="F.R.E.D.">
<style>.d{{fill:{ACCENT}}}</style>
<path fill="currentColor" d="{' '.join(letters)}"/>
<path class="d" d="{' '.join(dots)}"/>
</svg>
'''
(ROOT / "static/logo.svg").write_text(wordmark); (LOGO / "wordmark.svg").write_text(wordmark)
print(f"static/logo.svg  viewBox 0 0 {W:.1f} x {H:.0f}")

# 4. favicon: the keycap tile, a full 96-unit square (no rounded corners), Inter 800 letters cut out
#    with even-odd; letters in a square block with equal margins inside the 2..94 area
fav_font = instance(INTER, wght=800, opsz=14)
# the variable font keeps overlapping contours (R's leg, D's stem); even-odd would cut holes there
removeOverlaps(fav_font, ["F", "R", "E", "D"])
f = 34.0; sc = f / upem; c = fav_font["OS/2"].sCapHeight * sc   # cap height in tile units
gv = 12.0; block = 2 * c + gv; m = (92 - block) / 2  # equal margins, square block
y1 = 2 + m + c; y2 = y1 + gv + c
parts = ["M0 0H96V96H0Z"]
# left column letters start at the left margin, right column letters end at the right margin
for ch, side, by in (("F", "l", y1), ("R", "r", y1), ("E", "l", y2), ("D", "r", y2)):
    g, w, _ = shape(INTER, ch, wght=800, opsz=14)
    name, _gx, adv = g[0]
    x0 = 2 + m if side == "l" else 94 - m - adv * sc
    parts.append(glyph_path(fav_font, name, sc, x0, by))
favicon = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">
<style>path{{fill:{ACCENT}}}</style>
<path fill-rule="evenodd" d="{' '.join(parts)}"/>
</svg>
'''
(ROOT / "static/favicon.svg").write_text(favicon); (LOGO / "favicon.svg").write_text(favicon)
print(f"static/favicon.svg  letters f={f}, cap={c:.1f}, margin={m:.1f}, rows {y1:.1f}/{y2:.1f}")
