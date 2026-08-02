#!/usr/bin/env python3
"""Build the social card from source, so its version cannot go stale silently.

The card is what a link to this site *is*, everywhere it is shared. Until this
tool existed it was a hand-exported PNG, and both cards in the repository had
gone wrong in ways nothing could catch:

- **Both said v0.3** while the programme was at v0.4. `check_counts.py` verifies
  every stated number against its source, but a number rendered into pixels is
  invisible to it, so the most-shared surface carried the only unchecked version
  string on the site.
- **`og.png` was visibly broken** -- the headline ran off the right edge and the
  bottom fifth was blank white. Fifteen of the twenty-seven pages served it.
- **Two different cards were live at once**: the canonical page and the eleven
  translations pointed at `og-v2.png`, everything under `journal/` at `og.png`.

The cause of the cropping is worth writing down, because it will bite the next
person. `qlmanage -t` is the only rasteriser on a stock macOS, and it scales an
SVG so the **viewBox height** fills the requested square, then clips the width
and pads the bottom. A 1200x630 viewBox therefore renders 1.9x too wide and
loses a third of itself. The fix is to author a **square** canvas with the card
drawn in a centred 1200x630 band, render at 1200, and take the centre crop --
which `sips -c 630 1200` does exactly, because its crop is centred.

Everything the card asserts is read from a file:

    version   CITATION.cff  (the machine-readable record)
    headline  the `data-i18n-src="move"` passage in docs/index.html

so the card cannot drift from the site without the build failing or the string
changing with it. `check_counts.py` then checks the version in the generated
SVG, which is text and therefore checkable, unlike the PNG.

    python3 tools/build_og.py            # regenerate docs/og.svg and docs/og.png
    python3 tools/build_og.py --check    # fail if the card is stale, write nothing

Exit status is what CI reads.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SVG_OUT = DOCS / "og.svg"
PNG_OUT = DOCS / "og.png"

W, H = 1200, 630
PAD = (W - H) // 2          # band offset inside the square canvas

# The site's dark palette, copied from the :root block under
# prefers-color-scheme: dark. A card in the light palette would not read as the
# same object as the page it links to.
PLATE, FIELD = "#0f1317", "#161b20"
INK, GRAPHITE = "#d7d9d4", "#8c9299"
PHANTOM = "#e0705f"
RULE = "#262c32"

SERIF = ("Iowan Old Style, Palatino Linotype, Palatino, Charter, "
         "Bitstream Charter, Book Antiqua, Georgia, Times New Roman, serif")
MONO = ("SF Mono, SFMono-Regular, Menlo, DejaVu Sans Mono, Liberation Mono, "
        "Consolas, monospace")


def version() -> str:
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    m = re.search(r"^version:\s*([0-9]+\.[0-9]+)", text, re.M)
    if not m:
        raise SystemExit("build_og: no version in CITATION.cff")
    return m.group(1)


def headline() -> str:
    text = (DOCS / "index.html").read_text(encoding="utf-8")
    m = re.search(r'data-i18n-src="move"[^>]*>(.*?)</h2>', text, re.S)
    if not m:
        raise SystemExit("build_og: the 'move' passage moved; card would lie")
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).split())


def wrap(text: str, per_line: int) -> list:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > per_line and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def svg() -> str:
    v = version()
    lines = wrap(headline(), 46)[:3]
    y0 = PAD                                   # top of the visible band
    sub = "".join(
        '<text x="80" y="%d" font-family="%s" font-size="40" fill="%s">%s</text>'
        % (y0 + 300 + i * 54, SERIF, GRAPHITE, html.escape(t))
        for i, t in enumerate(lines))
    return """<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" \
viewBox="0 0 {W} {W}">
  <rect width="{W}" height="{W}" fill="{plate}"/>
  <rect x="0" y="{y0}" width="{W}" height="{H}" fill="{plate}"/>
  <rect x="40" y="{ruleTop}" width="{inner}" height="{ruleH}" fill="none" \
stroke="{rule}" stroke-width="2"/>
  <text x="80" y="{titleY}" font-family="{serif}" font-size="128" \
letter-spacing="2" fill="{ink}">NOOPHORICS</text>
  <line x1="80" y1="{lineY}" x2="{lineX2}" y2="{lineY}" stroke="{rule}" \
stroke-width="2"/>
  {sub}
  <text x="80" y="{footY}" font-family="{mono}" font-size="26" \
letter-spacing="3" fill="{phantom}">&#934;</text>
  <text x="118" y="{footY}" font-family="{mono}" font-size="24" \
letter-spacing="3" fill="{graphite}">PHANTOM AGREEMENT</text>
  <text x="{rightX}" y="{footY}" text-anchor="end" font-family="{mono}" \
font-size="24" letter-spacing="3" fill="{graphite}">NOOPHORICS.ORG \
&#183; V{v}</text>
</svg>
""".format(W=W, H=H, y0=y0, plate=PLATE, field=FIELD, ink=INK,
           graphite=GRAPHITE, phantom=PHANTOM, rule=RULE,
           serif=SERIF, mono=MONO, v=v, sub=sub,
           inner=W - 80, ruleTop=y0 + 40, ruleH=H - 80,
           titleY=y0 + 200, lineY=y0 + 240, lineX2=W - 80,
           footY=y0 + H - 70, rightX=W - 80)


def rasterise(svg_text: str, dest: Path) -> None:
    """Square render via qlmanage, then the centred crop that recovers 1200x630.

    Both steps are load-bearing and neither is obvious; see the module
    docstring for why a 1200x630 viewBox produces a clipped card instead.
    """
    if not shutil.which("qlmanage") or not shutil.which("sips"):
        raise SystemExit("build_og: needs qlmanage and sips (macOS)")
    tmp = Path(tempfile.mkdtemp())
    try:
        src = tmp / "card.svg"
        src.write_text(svg_text, encoding="utf-8")
        subprocess.run(["qlmanage", "-t", "-s", str(W), "-o", str(tmp), str(src)],
                       check=True, capture_output=True)
        rendered = tmp / "card.svg.png"
        if not rendered.exists():
            raise SystemExit("build_og: qlmanage produced nothing")
        subprocess.run(["sips", "-c", str(H), str(W), str(rendered)],
                       check=True, capture_output=True)
        shutil.copyfile(rendered, dest)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def png_size(path: Path):
    import struct
    d = path.read_bytes()
    return struct.unpack(">II", d[16:24])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if the committed card is stale; write nothing")
    args = ap.parse_args()

    want = svg()
    if args.check:
        if not SVG_OUT.exists() or not PNG_OUT.exists():
            print("build_og: card missing; run tools/build_og.py")
            return 1
        if SVG_OUT.read_text(encoding="utf-8") != want:
            print("build_og: the card is stale -- the version or the headline "
                  "moved since it was built. Run tools/build_og.py.")
            return 1
        w, h = png_size(PNG_OUT)
        if (w, h) != (W, H):
            print("build_og: og.png is %dx%d, not %dx%d -- the rasteriser "
                  "clipped it. Run tools/build_og.py." % (w, h, W, H))
            return 1
        print("build_og: card current (v%s, %dx%d, %.0f KB)"
              % (version(), w, h, PNG_OUT.stat().st_size / 1024))
        return 0

    SVG_OUT.write_text(want, encoding="utf-8")
    rasterise(want, PNG_OUT)
    w, h = png_size(PNG_OUT)
    if (w, h) != (W, H):
        print("build_og: rasteriser returned %dx%d, expected %dx%d" % (w, h, W, H))
        return 1
    print("  og.svg + og.png  v%s  %dx%d  %.0f KB"
          % (version(), w, h, PNG_OUT.stat().st_size / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
