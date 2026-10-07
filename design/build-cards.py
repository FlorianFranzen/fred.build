#!/usr/bin/env python3
"""Draw the business card as print-ready SVG and PDF.

Run inside `nix develop` (needs FONT_INTER, FONT_JBMONO, fontTools, uharfbuzz, segno, rsvg-convert):

    python3 design/build-cards.py [--accent "#rrggbb"] [--pgp site|keyserver|fingerprint] [--logo 0.26]

Writes design/cards/card-front.svg, card-back.svg and card.pdf (front and back as two pages).
The back carries a QR code with the contact (a MECARD) and the keycap tile in its centre; --pgp
picks how it points to the PGP key, --logo sizes the tile.
The card is 85 x 55 mm (the Swiss and European size) with 3 mm bleed on every side, so each page is
91 x 61 mm; all text is converted to outlines, the PDF needs no fonts. The wordmark and
the keycap tile are read from static/logo.svg and static/favicon.svg, so the card follows
build-assets.py.
"""
import argparse, os, pathlib, re, subprocess, tomllib
import segno
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

ROOT = pathlib.Path(__file__).resolve().parent.parent
INTER = pathlib.Path(os.environ["FONT_INTER"]) / "share/fonts/truetype/InterVariable.ttf"
JBM = pathlib.Path(os.environ["FONT_JBMONO"]) / "share/fonts/truetype/JetBrainsMono-Regular.ttf"
OUT = ROOT / "design/cards"

W, H, BLEED = 85.0, 55.0, 3.0
M = 6.0  # inner margin; no text below 1.75 mm em (5 pt)
PAPER, INK, MUTED, RULE = "#ffffff", "#111111", "#6b6b6b", "#cfcfcf"
ACCENT = tomllib.loads((ROOT / "config.toml").read_text())["extra"]["accent"]

CARD = {
    "name": "Florian Franzen",
    "role": "Chief Engineer",
    "mail": "florian@fred.build",
    "phone": "+41 79 000 00 00",  # placeholder
    "web": "fred.build",
    "place": "Zug, Switzerland",
    "legal": "Franzen Research, Engineering & Development",
    "fields": "Prototyping · Embedded · Protocols · Infrastructure",
    "pgp": "E291C49EF7461F6DDC5BAA959E496CBDB62766C1",
}

def contact(pgp="site"):
    """The contact as a MECARD, the compact QR contact format iOS and Android cameras read: one name
    field, phone, mail, and the PGP fingerprint in the note; `pgp` adds a link to the key as URL."""
    c = CARD
    fpr = " ".join(c["pgp"][i:i + 4] for i in range(0, 40, 4))
    first, last = c["name"].split(" ", 1)
    fields = [f"N:{last},{first}", f"TEL:{c['phone'].replace(' ', '')}", f"EMAIL:{c['mail']}"]
    if pgp == "site":
        fields.append(f"URL:https://{c['web']}/florian.asc")
    elif pgp == "keyserver":
        fields.append(f"URL:https://keys.openpgp.org/vks/v1/by-fingerprint/{c['pgp']}")
    fields.append(f"NOTE:PGP {fpr}")
    return "MECARD:" + ";".join(fields) + ";;"

def qr(data, x, y, size, logo=0.26, accent=ACCENT, quiet=3):
    """A QR code on a white tile `size` mm wide, with the keycap tile in the middle covering `logo`
    of its width (error correction H restores the modules under it; 0 drops the logo and uses M).
    Returns (svg, version, module mm)."""
    q = segno.make(data, error="h" if logo else "m", micro=False, boost_error=False)
    rows = [list(r) for r in q.matrix]
    n = len(rows); m = size / (n + 2 * quiet)
    k = 0
    if logo:
        k = round(n * logo) | 1  # odd, so the logo sits on the centre module
        lo, hi = (n - k) // 2 - 1, (n + k) // 2 + 1  # one module of white around it
        for j in range(lo, hi):
            for i in range(lo, hi):
                rows[j][i] = 0
    d = []
    for j, row in enumerate(rows):  # one rectangle per horizontal run of dark modules
        i = 0
        while i < n:
            if row[i]:
                e = i
                while e < n and row[e]: e += 1
                d.append(f"M{x + (quiet + i) * m:.3f} {y + (quiet + j) * m:.3f}h{(e - i) * m:.3f}v{m:.3f}h{-(e - i) * m:.3f}Z")
                i = e
            else:
                i += 1
    out = (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" style="fill:{PAPER}"/>'
           f'<path style="fill:{INK}" d="{"".join(d)}"/>')
    if logo:
        t = k * m; o = (size - t) / 2
        out += f'<path transform="translate({x + o:.3f} {y + o:.3f}) scale({t / 96:.5f})" fill-rule="evenodd" style="fill:{accent}" d="{TILE}"/>'
    return out, q.version, m

# Text as outlines --------------------------------------------------------------------------
_fonts = {}
def _font(path, axes):
    key = (path, tuple(sorted(axes.items())))
    if key not in _fonts:
        f = TTFont(path)
        if "fvar" in f:
            f = instancer.instantiateVariableFont(f, dict(axes), inplace=True)
        blob = hb.Blob.from_file_path(str(path)); face = hb.Face(blob); hbf = hb.Font(face)
        if axes: hbf.set_variations(dict(axes))
        _fonts[key] = (f, hbf, face.upem, f.getGlyphOrder())
    return _fonts[key]

def text(s, x, y, size, fill, weight=400, mono=False, track=0.0, anchor="start"):
    """One line of text as a <path>; x, y is the baseline origin, size the em in mm."""
    path, axes = (JBM, {}) if mono else (INTER, {"wght": weight, "opsz": 14 if size < 3 else 32})
    font, hbf, upem, names = _font(path, axes)
    buf = hb.Buffer(); buf.add_str(s); buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": not mono, "calt": True})
    k = size / upem
    glyphs, adv = [], 0.0
    for i, p in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs.append((names[i.codepoint], adv + p.x_offset * k))
        adv += p.x_advance * k + track * size
    adv -= track * size
    x0 = x - (adv if anchor == "end" else adv / 2 if anchor == "middle" else 0)
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.3f}".rstrip("0").rstrip("."))
    for name, gx in glyphs:
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, x0 + gx, y)))
    return f'<path style="fill:{fill}" d="{pen.getCommands()}"/>', adv

# Brand marks from static/ ------------------------------------------------------------------
_logo = (ROOT / "static/logo.svg").read_text()
LOGO_LETTERS = re.search(r'<path fill="currentColor" d="([^"]+)"', _logo).group(1)
LOGO_DOTS = re.search(r'<path class="d" d="([^"]+)"', _logo).group(1)
LOGO_W, LOGO_CAP = float(re.search(r'viewBox="0 \S+ (\S+)', _logo).group(1)), 100.0

# the keycap tile (96 units, letters cut out with even-odd)
TILE = re.search(r'<path fill-rule="evenodd" d="([^"]+)"', (ROOT / "static/favicon.svg").read_text()).group(1)

def wordmark(x, y, cap, letters, dots):
    """The wordmark with its cap height `cap` mm, top-left of the capitals at x, y."""
    s = cap / LOGO_CAP
    return (f'<g transform="translate({x:.3f} {y:.3f}) scale({s:.5f})">'
            f'<path style="fill:{letters}" d="{LOGO_LETTERS}"/><path style="fill:{dots}" d="{LOGO_DOTS}"/></g>'), LOGO_W * s

def ground(fill):
    return f'<rect x="{-BLEED}" y="{-BLEED}" width="{W + 2 * BLEED}" height="{H + 2 * BLEED}" style="fill:{fill}"/>'

def rule(y, fill=RULE):
    return f'<rect x="{M}" y="{y:.3f}" width="{W - 2 * M}" height="0.15" style="fill:{fill}"/>'

# Layout -------------------------------------------------------------------------------------
def card(acc, pgp="site", logo=0.26):
    """Front: wordmark, name, and the contact details as labelled mono fields, like a datasheet.
    Back: the contact QR code centred on the accent, the name spelled out and the fields of work
    centred below it; QR and text are centred vertically as one group."""
    c = CARD
    front = [ground(PAPER), wordmark(M, M, 4.2, INK, acc)[0],
             text(c["name"], M, 36.5, 3.7, INK, 800)[0],
             text(c["role"], M, 40.6, 2.4, MUTED)[0],
             rule(44.2)]
    for x, label, value in ((M, "Mail", c["mail"]), (38.5, "Web", c["web"]), (57.5, "Studio", c["place"])):
        front.append(text(label.upper(), x, 47.5, 1.75, MUTED, mono=True, track=0.12)[0])
        front.append(text(value, x, 50.6, 2.05, INK, mono=True)[0])
    T = 27.0  # QR tile
    gap, lead = 5.6, 4.3  # QR to the first baseline, first to second baseline
    y0 = (H - (T + gap + lead)) / 2
    code, version, module = qr(contact(pgp), (W - T) / 2, y0, T, logo, acc)
    back = [ground(acc), code,
            text(c["legal"], W / 2, y0 + T + gap, 2.6, PAPER, 800, anchor="middle")[0],
            text(c["fields"], W / 2, y0 + T + gap + lead, 2.0, PAPER, mono=True, anchor="middle")[0]]
    return front, back, version, module

def svg(parts, mm=True):
    size = f' width="{W + 2 * BLEED}mm" height="{H + 2 * BLEED}mm"' if mm else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-BLEED} {-BLEED} {W + 2 * BLEED} {H + 2 * BLEED}"{size}>'
            + "".join(parts) + "</svg>\n")

def render(acc, pgp="site", logo=0.26):
    """(front, back, QR version, module size in mm); `acc` may be a colour or a CSS var() for previews."""
    front, back, version, module = card(acc, pgp, logo)
    return svg(front), svg(back), version, module

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--accent", default=ACCENT)
    ap.add_argument("--pgp", choices=["keyserver", "site", "fingerprint"], default="site")
    ap.add_argument("--logo", type=float, default=0.26, help="keycap width in the QR code as a fraction; 0 for none")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    front, back, version, module = render(args.accent, args.pgp, args.logo)
    files = []
    for side, s in (("front", front), ("back", back)):
        f = OUT / f"card-{side}.svg"; f.write_text(s); files.append(str(f))
    pdf = OUT / "card.pdf"
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(pdf), *files], check=True)
    print(f"{pdf.relative_to(ROOT)}  {W + 2 * BLEED:g} x {H + 2 * BLEED:g} mm incl. {BLEED:g} mm bleed;"
          f" QR version {version}, modules {module:.2f} mm")
