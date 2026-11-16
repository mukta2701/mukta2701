#!/usr/bin/env python3
"""Render the profile banner and metrics strip as light/dark SVG pairs.

Usage: python3 scripts/build_assets.py
Reads data/metrics.json and writes, into assets/:
  banner-{light,dark}.svg      banner-sm-{light,dark}.svg
  metrics-{light,dark}.svg     metrics-sm-{light,dark}.svg
The "-sm" variants are drawn for phone width and are selected in README.md
with a <picture> media query. SVGs are shown through <img>, so only system
fonts are used. No third-party dependencies.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

SERIF = "Georgia, 'Times New Roman', serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

THEMES = {
    "light": dict(bg="#FBF9F5", border="#D8D2C4", ink="#1B1F2A", muted="#5B6270",
                  accent="#0B6B63", cell="#E6E1D3", cell_on="#0B6B63"),
    "dark": dict(bg="#11161D", border="#2D333B", ink="#E6EDF3", muted="#9AA4B2",
                 accent="#5FD3C0", cell="#1E252E", cell_on="#5FD3C0"),
}

# control-matrix motif: a grid of cells, a few "evidenced" (filled)
ON_CELLS = {(0, 2), (1, 0), (1, 3), (2, 1), (2, 4), (3, 2), (4, 0), (4, 5),
            (5, 3), (6, 1), (6, 4), (7, 2)}


def banner(t: dict) -> str:
    w, h = 880, 220
    size, gap, x0, y0 = 18, 6, 646, 44
    cells = "".join(
        f'<rect x="{x0 + c * (size + gap)}" y="{y0 + r * (size + gap)}" width="{size}" height="{size}" '
        f'rx="3" fill="{t["cell_on"] if (c, r) in ON_CELLS else t["cell"]}"/>'
        for c in range(8) for r in range(6)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">Mukta Choudhury, AI Security and Compliance</title>
  <desc id="d">Profile banner with name, specialisms and a grid of control cells.</desc>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{t['bg']}" stroke="{t['border']}"/>
  <text x="44" y="58" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{t['accent']}">AI SECURITY  ·  APPLICATION SECURITY  ·  GRC</text>
  <text x="44" y="122" font-family="{SERIF}" font-size="52" font-weight="700" fill="{t['ink']}">Mukta Choudhury</text>
  <rect x="44" y="142" width="80" height="3" fill="{t['accent']}"/>
  <text x="44" y="180" font-family="{SANS}" font-size="17" fill="{t['muted']}">Privacy-by-design tooling, audit evidence and threat intelligence.</text>
  {cells}
</svg>
"""


def banner_sm(t: dict) -> str:
    w, h = 560, 190
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">Mukta Choudhury, AI Security and Compliance</title>
  <desc id="d">Profile banner with name and specialisms.</desc>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{t['bg']}" stroke="{t['border']}"/>
  <text x="28" y="48" font-family="{MONO}" font-size="12" letter-spacing="1.6" fill="{t['accent']}">AI SECURITY · APPSEC · GRC</text>
  <text x="28" y="100" font-family="{SERIF}" font-size="42" font-weight="700" fill="{t['ink']}">Mukta Choudhury</text>
  <rect x="28" y="118" width="64" height="3" fill="{t['accent']}"/>
  <text x="28" y="152" font-family="{SANS}" font-size="15" fill="{t['muted']}">Privacy-by-design tooling, audit evidence</text>
  <text x="28" y="173" font-family="{SANS}" font-size="15" fill="{t['muted']}">and threat intelligence.</text>
</svg>
"""


def _tile(t: dict, tile: dict, x: float, y: float, tw: float, th: float, vfs: int, lfs: int) -> str:
    return (
        f'<rect x="{x + 0.5:.1f}" y="{y + 0.5:.1f}" width="{tw - 1:.1f}" height="{th - 1:.1f}" rx="8" fill="{t["bg"]}" stroke="{t["border"]}"/>'
        f'<rect x="{x + 18:.1f}" y="{y + 16:.1f}" width="24" height="3" fill="{t["accent"]}"/>'
        f'<text x="{x + 18:.1f}" y="{y + 16 + vfs + 8:.1f}" font-family="{SANS}" font-size="{vfs}" font-weight="700" fill="{t["ink"]}">{escape(tile["value"])}</text>'
        f'<text x="{x + 18:.1f}" y="{y + th - 16:.1f}" font-family="{SANS}" font-size="{lfs}" fill="{t["muted"]}">{escape(tile["label"])}</text>'
    )


def _label(tiles: list) -> str:
    return "; ".join(escape(x["value"] + " " + x["label"]) for x in tiles)


def metrics(t: dict, tiles: list) -> str:
    w, h, gap = 880, 112, 12
    tw = (w - gap * (len(tiles) - 1)) / len(tiles)
    body = "".join(_tile(t, tile, i * (tw + gap), 0, tw, h, 34, 14) for i, tile in enumerate(tiles))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="Project metrics: {_label(tiles)}">{body}</svg>\n')


def metrics_sm(t: dict, tiles: list) -> str:
    w, gap, th = 560, 12, 100
    tw = (w - gap) / 2
    rows = (len(tiles) + 1) // 2
    h = rows * th + (rows - 1) * gap
    body = "".join(
        _tile(t, tile, (i % 2) * (tw + gap), (i // 2) * (th + gap), tw, th, 32, 15)
        for i, tile in enumerate(tiles)
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="Project metrics: {_label(tiles)}">{body}</svg>\n')


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    tiles = json.loads((ROOT / "data" / "metrics.json").read_text())["tiles"]
    for name, theme in THEMES.items():
        (OUT / f"banner-{name}.svg").write_text(banner(theme))
        (OUT / f"banner-sm-{name}.svg").write_text(banner_sm(theme))
        (OUT / f"metrics-{name}.svg").write_text(metrics(theme, tiles))
        (OUT / f"metrics-sm-{name}.svg").write_text(metrics_sm(theme, tiles))
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
