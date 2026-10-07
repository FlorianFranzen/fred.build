# Design sources

The site's visual decisions were made in four rounds of comparison sheets (logo candidates,
three style directions, seven typefaces, photo treatments, the Mind the Gap mark). The sheets were
removed once the decisions were final; they are in the git history up to commit `61aab37`.

What remains here is what the site is built from. The accent colour comes from `config.toml`
(`[extra] accent`, `accent_bright`); every script reads it from there, so a colour change is one
edit there, one in `sass/_tokens.scss` (palette) and one in `static/site.webmanifest`, then a rerun.

| File | Purpose |
|------|---------|
| `build-assets.py` | Instances Inter from nixpkgs at 400/600/800, subsets it and JetBrains Mono to Latin as woff2 into `static/fonts/`; shapes the F.R.E.D. wordmark into `static/logo.svg`; writes the keycap favicon `static/favicon.svg` (letters cut out of a square accent tile). |
| `build-cards.py` | Draws the business card into `design/cards/` as SVG and a two-page PDF: 85 × 55 mm with 3 mm bleed, all text outlined. Front: wordmark, name, title and contact fields; back: a QR code (a MECARD: name, phone, mail, key link, PGP fingerprint) with the favicon tile in its centre, error correction H. `--pgp site\|keyserver\|fingerprint` picks the key link, `--logo` the tile size (0.26 of the code; larger stops scanning reliably). Contact details are in `CARD` at the top. |
| `build-og.py` | Renders the Open Graph image `static/og.jpg` (1200 × 630): hero band with a fade, the wordmark, headline and location. |
| `build-plates.py` | Draws the 5:2 cover plates `content/projects/*/cover.svg`: surface colour, mark in the text colour, accent as a detail, light/dark via a media query inside the SVG. Never run `svgo` on the plates: it inlines the `svg{--bg…}` rule as a style attribute, which overrides the dark-mode rule. |
| `clean-logo.py` | Reduces a client logo to one `currentColor` fill and minifies it with `svgo` when available. Sources of every logo are in `static/logos/SOURCES.md`. |
| `contributions.py` | Collects upstream pull requests (REST search) and credited commits (GraphQL, needs `GITHUB_TOKEN` or a logged-in `gh`) into `data/contributions.toml`, sorted into major and popular repositories; `[[manual]]` entries and `hide` / `pinned` flags survive a rerun. |
| `cards/` | The card as written by `build-cards.py`; `card.pdf` goes to the printer. |
| `logo/` | Reference copies of the wordmark and favicon written by `build-assets.py`. |
| `marks/` | Third-party marks placed on plates (Nix snowflake, Polkadot, Open Ephys, the Mind the Gap mark from its own repository). |

One-off raster assets were produced with ImageMagick and resvg inside `nix develop` and are
committed as files, not regenerated:

```sh
# icons from the favicon
resvg -w 192 -h 192 static/favicon.svg static/icon-192.png
resvg -w 512 -h 512 static/favicon.svg static/icon-512.png
resvg -w 180 -h 180 --background white static/favicon.svg static/apple-touch-icon.png
resvg -w 16 -h 16 static/favicon.svg /tmp/f16.png; resvg -w 32 -h 32 static/favicon.svg /tmp/f32.png
magick /tmp/f16.png /tmp/f32.png static/favicon.ico

# hero band: the studio photo, cropped to the bench, muted colour with a warm white balance
# to sit with the Marmalade accent (the fade is CSS)
magick IMG_20250702_094943_660.jpg -auto-orient -crop 3784x1430+148+335 +repage \
  -modulate 100,53,100 -brightness-contrast 3x7 \
  -channel R -evaluate multiply 1.05 -channel B -evaluate multiply 0.89 +channel hero-master.png
for w in 2400 1600 1000 600; do magick hero-master.png -resize ${w}x -quality 78 -define webp:method=6 -strip static/img/hero-$w.webp; done
magick hero-master.png -resize 1600x -quality 80 -strip static/img/hero-1600.jpg
```

`static/site.webmanifest` repeats the site name and the accent colour on purpose: a manifest is a
static file and cannot read `config.toml`.
