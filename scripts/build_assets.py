#!/usr/bin/env python3
"""Render the profile visuals (cyber-terminal theme) as SVGs.

Usage: python3 scripts/build_assets.py   (no third-party dependencies)

Every asset is written twice: a desktop version (~880px) and an "-sm" version
drawn for phone width, picked in README.md with a <picture> media query.
SVGs are shown through <img>, so only system fonts and inline CSS are used.
Animations are CSS-only and switch off under prefers-reduced-motion.

Figures come from the public READMEs of privacy-review-agent and
cybertrend-intelligence; update them in the constants below.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
CW = 0.62  # conservative monospace advance, in em

C = dict(
    bg="#0A0F14", panel="#0D1319", border="#1F2A33", ink="#E6EDF3", text="#C9D1D9",
    dim="#6E7B88", green="#3DFFA0", cyan="#4CC9F0", amber="#FFB454", violet="#B79CFF",
    red="#FF5F57", yellow="#FEBC2E", ok="#28C840",
)

DEFS = f"""<defs>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['green']}" stop-opacity=".10"/><stop offset="1" stop-color="{C['green']}" stop-opacity="0"/></linearGradient>
</defs>"""

STYLE = """<style>
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes dash{to{stroke-dashoffset:-14}}
@keyframes pulse{0%,100%{opacity:.55}50%{opacity:1}}
.dash{stroke-dasharray:7 7;animation:dash 1.1s linear infinite}
.pulse{animation:pulse 2.4s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>"""


def svg(w: float, h: float, body: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'role="img" aria-label="{escape(title)}">{STYLE}{DEFS}{body}</svg>\n')


def wrap(text: str, max_chars: int) -> list:
    words, lines, cur = text.split(), [], ""
    for wd in words:
        if cur and len(cur) + 1 + len(wd) > max_chars:
            lines.append(cur)
            cur = wd
        else:
            cur = f"{cur} {wd}".strip()
    if cur:
        lines.append(cur)
    return lines


def frame(w: float, h: float, accent: str | None = None) -> str:
    bar = f'<rect x="0.5" y="0.5" width="4" height="{h - 1:.1f}" rx="2" fill="{accent}"/>' if accent else ""
    return (f'<rect x="0.5" y="0.5" width="{w - 1:.1f}" height="{h - 1:.1f}" rx="12" fill="{C["panel"]}" stroke="{C["border"]}"/>'
            f'<rect x="0.5" y="0.5" width="{w - 1:.1f}" height="{h - 1:.1f}" rx="12" fill="url(#sheen)"/>{bar}')


# ---------------------------------------------------------------- terminal
def terminal(small: bool) -> str:
    w = 480 if small else 880
    fs = 12 if small else 15
    pad = 20 if small else 30
    lh = fs * 1.75
    maxc = int((w - 2 * pad) / (fs * CW))
    big = 28 if small else 38
    script = [
        ("cmd", "whoami"),
        ("big", "Mukta Choudhury"),
        ("out", "AI security · application security · GRC"),
        ("cmd", "cat focus.txt"),
        ("out", "Privacy-by-design tooling, audit evidence and threat intelligence."),
        ("cmd", "privacy-review-agent scan --path ./src"),
        ("note", "# 381 labelled benchmark cases · 100% near-miss precision"),
        ("cmd", "python run.py digest-full"),
        ("note", "# 7 security feeds + NVD, scored by CVSS · EPSS · CISA KEV"),
        ("cursor", ""),
    ]
    title_h = 40
    y = title_h + pad * 0.9 + fs
    t = 0.5
    parts = []
    for kind, text in script:
        if kind == "cmd":
            n = len(text) + 2
            dur = min(0.045 * n, 1.8)
            parts.append(
                f'<text x="{pad}" y="{y:.1f}" font-family="{MONO}" font-size="{fs}" '
                f'style="animation:type {dur:.2f}s steps({n}) {t:.2f}s both">'
                f'<tspan fill="{C["green"]}" filter="url(#glow)">$ </tspan><tspan fill="{C["ink"]}">{escape(text)}</tspan></text>')
            t += dur + 0.3
            y += lh
        elif kind == "big":
            y += big * 0.35
            parts.append(
                f'<text x="{pad}" y="{y:.1f}" font-family="{MONO}" font-size="{big}" font-weight="700" fill="{C["green"]}" '
                f'filter="url(#glow)" style="animation:fade .5s ease {t:.2f}s both">{escape(text)}</text>')
            t += 0.5
            y += big * 0.55
        elif kind in ("out", "note"):
            col = C["text"] if kind == "out" else C["dim"]
            for ln in wrap(text, maxc):
                parts.append(
                    f'<text x="{pad}" y="{y:.1f}" font-family="{MONO}" font-size="{fs}" fill="{col}" '
                    f'style="animation:fade .35s ease {t:.2f}s both">{escape(ln)}</text>')
                y += lh
            t += 0.55
        else:  # cursor line
            parts.append(
                f'<g style="animation:fade .2s ease {t:.2f}s both"><text x="{pad}" y="{y:.1f}" font-family="{MONO}" font-size="{fs}" fill="{C["green"]}" filter="url(#glow)">$ </text>'
                f'<rect x="{pad + 2 * fs * CW:.1f}" y="{y - fs * 0.85:.1f}" width="{fs * 0.55:.1f}" height="{fs * 1.05:.1f}" fill="{C["green"]}" style="animation:blink 1.1s steps(1,end) infinite"/></g>')
            y += lh
    h = y + pad * 0.5
    chrome = (
        frame(w, h)
        + f'<path d="M0.5 {title_h} H{w - 0.5}" stroke="{C["border"]}"/>'
        + f'<circle cx="{pad}" cy="{title_h / 2}" r="5.5" fill="{C["red"]}"/><circle cx="{pad + 18}" cy="{title_h / 2}" r="5.5" fill="{C["yellow"]}"/><circle cx="{pad + 36}" cy="{title_h / 2}" r="5.5" fill="{C["ok"]}"/>'
        + f'<text x="{w / 2:.0f}" y="{title_h / 2 + 4.5}" text-anchor="middle" font-family="{MONO}" font-size="{fs - 2}" fill="{C["dim"]}">mukta@security: ~</text>'
    )
    return svg(w, h, chrome + "".join(parts), "Terminal: whoami, Mukta Choudhury, AI security, application security and GRC")


# ------------------------------------------------------------------- cards
def flow(items, x0, y, max_w, row_h):
    """Place (width, draw(x,y)->svg) items left to right, wrapping rows. Returns (svg, y_after)."""
    out, x = [], x0
    for width, draw in items:
        if x > x0 and x + width > x0 + max_w:
            x, y = x0, y + row_h
        out.append(draw(x, y))
        x += width
    return "".join(out), y + row_h


def chip(text, accent, fs):
    width = len(text) * fs * CW + 22

    def draw(x, y):
        return (f'<rect x="{x:.1f}" y="{y - fs - 5:.1f}" width="{width - 8:.1f}" height="{fs + 12:.1f}" rx="{(fs + 12) / 2:.1f}" fill="none" stroke="{accent}" stroke-opacity=".45"/>'
                f'<text x="{x + 7:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="{fs}" fill="{C["text"]}">{escape(text)}</text>')
    return width, draw


def stat(value, label, accent, fs):
    width = (len(value) + 1 + len(label)) * fs * CW + 30

    def draw(x, y):
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="{fs}"><tspan fill="{accent}" font-weight="700" filter="url(#glow)">{escape(value)}</tspan>'
                f'<tspan fill="{C["dim"]}"> {escape(label)}</tspan></text>')
    return width, draw


def card(small, accent, tag, title, desc, stats, chips, label):
    w = 480 if small else 880
    pad = 22 if small else 30
    fs = 12 if small else 14
    inner = w - 2 * pad
    parts = [f'<text x="{pad}" y="{pad + 8}" font-family="{MONO}" font-size="{fs - 2}" letter-spacing="1.6" fill="{accent}">{escape(tag)}</text>',
             f'<text x="{w - pad}" y="{pad + 10}" text-anchor="end" font-family="{MONO}" font-size="{fs + 4}" fill="{C["dim"]}">↗</text>']
    y = pad + 8 + (30 if not small else 28)
    parts.append(f'<text x="{pad}" y="{y}" font-family="{MONO}" font-size="{fs + 8}" font-weight="700" fill="{C["ink"]}">{escape(title)}</text>')
    y += 12 + fs
    for ln in wrap(desc, int(inner / (fs * CW))):
        parts.append(f'<text x="{pad}" y="{y:.1f}" font-family="{MONO}" font-size="{fs}" fill="{C["text"]}">{escape(ln)}</text>')
        y += fs * 1.65
    y += 8
    if stats:
        s, y = flow([stat(v, l, accent, fs) for v, l in stats], pad, y, inner, fs * 1.8)
        parts.append(s)
    y += 4
    s, y = flow([chip(c, accent, fs - 1) for c in chips], pad, y, inner, fs * 2.2)
    parts.append(s)
    h = y - fs * 0.4 + pad * 0.3
    return svg(w, h, frame(w, h, accent) + "".join(parts), label)


CARDS = {
    "card-privacy": dict(
        accent=C["green"], tag="APPSEC · PRIVACY", title="privacy-review-agent",
        desc="Offline pre-commit and CI check that stops personal data and secrets reaching logs, AI prompts, analytics and third-party services.",
        stats=[("381", "benchmark cases"), ("100%", "near-miss precision"), ("460+", "CI tests")],
        chips=["Python", "Semgrep", "GDPR"],
        label="privacy-review-agent: offline privacy check for code. 381 benchmark cases, 100% near-miss precision, 460 plus CI tests."),
    "card-cybertrend": dict(
        accent=C["cyan"], tag="THREAT INTELLIGENCE", title="cybertrend-intelligence",
        desc="Daily digest of the vulnerabilities that matter, ranked by CVSS, EPSS and CISA KEV instead of headline severity.",
        stats=[("7", "feeds + NVD"), ("≥ 90", "score = instant alert")],
        chips=["Python", "PostgreSQL", "NVD API", "Docker"],
        label="cybertrend-intelligence: daily threat-intelligence digest from 7 feeds plus NVD, ranked by exploitability."),
    "card-rfid": dict(
        accent=C["amber"], tag="THREAT MODELLING", title="rfid-threat-modelling-imd",
        desc="Threat model for RFID-based implantable medical devices, built with STRIDE and OWASP.",
        stats=[],
        chips=["STRIDE", "OWASP", "Medical devices"],
        label="rfid-threat-modelling-imd: STRIDE and OWASP threat model for RFID implantable medical devices."),
}


# ---------------------------------------------------------------- pipeline
def node(x, y, w, h, title, sub, accent, dashed=False):
    d = ' stroke-dasharray="5 5"' if dashed else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="10" fill="{C["bg"]}" stroke="{accent}" stroke-opacity=".7"{d}/>'
            f'<text x="{x + 14:.1f}" y="{y + 28:.1f}" font-family="{MONO}" font-size="14" font-weight="700" fill="{accent}" filter="url(#glow)">{escape(title)}</text>'
            f'<text x="{x + 14:.1f}" y="{y + 50:.1f}" font-family="{MONO}" font-size="12" fill="{C["text"]}">{escape(sub)}</text>')


def pipeline(small: bool) -> str:
    steps = [("Collect", "7 feeds + NVD", C["cyan"]), ("Score", "CVSS · EPSS · KEV", C["green"]),
             ("Summarise", "8 structured fields", C["amber"]), ("Digest", "grouped by severity", C["violet"])]
    if not small:
        w, h, nw, nh, y0 = 880, 216, 190, 70, 28
        gap = (w - 2 * 20 - 4 * nw) / 3
        parts = [frame(w, h)]
        xs = [20 + i * (nw + gap) for i in range(4)]
        for (t, s, a), x in zip(steps, xs):
            parts.append(node(x, y0, nw, nh, t, s, a))
        for i in range(3):
            xa, xb = xs[i] + nw + 4, xs[i + 1] - 4
            parts.append(f'<path class="dash" d="M{xa:.1f} {y0 + nh / 2} H{xb:.1f}" stroke="{C["dim"]}" stroke-width="2" fill="none"/>'
                         f'<path d="M{xb - 6:.1f} {y0 + nh / 2 - 5} L{xb:.1f} {y0 + nh / 2} L{xb - 6:.1f} {y0 + nh / 2 + 5}" stroke="{C["dim"]}" stroke-width="2" fill="none"/>')
        ax, ay = xs[1], y0 + nh + 38
        parts.append(f'<path class="dash" d="M{ax + nw / 2:.1f} {y0 + nh + 2} V{ay - 2}" stroke="{C["red"]}" stroke-width="2" fill="none"/>')
        parts.append(node(ax, ay, nw, 56, "Alert now", "score ≥ 90", C["red"], dashed=True).replace('y="' + f"{ay + 50:.1f}" + '"', 'y="' + f"{ay + 46:.1f}" + '"'))
    else:
        w, nw, nh, gap, x = 480, 290, 64, 26, 22
        h = 20 + 4 * nh + 3 * gap + 20
        parts = [frame(w, h)]
        for i, (t, s_, a) in enumerate(steps):
            y = 20 + i * (nh + gap)
            parts.append(node(x, y, nw, nh, t, s_, a).replace(f'y="{y + 50:.1f}"', f'y="{y + 48:.1f}"'))
            if i < 3:
                parts.append(f'<path class="dash" d="M{x + nw / 2} {y + nh + 2} V{y + nh + gap - 2}" stroke="{C["dim"]}" stroke-width="2" fill="none"/>')
        sy, ax = 20 + (nh + gap), x + nw + 22
        parts.append(f'<path class="dash" d="M{x + nw + 2} {sy + nh / 2} H{ax - 2}" stroke="{C["red"]}" stroke-width="2" fill="none"/>')
        parts.append(node(ax, sy, w - ax - 16, nh, "Alert", "score ≥ 90", C["red"], dashed=True).replace(f'y="{sy + 50:.1f}"', f'y="{sy + 48:.1f}"'))
    return svg(w, h, "".join(parts), "Pipeline: collect from 7 feeds and NVD, score by CVSS, EPSS and KEV, summarise, then send a digest by severity. Scores of 90 or more send an immediate alert.")


# -------------------------------------------------------------- frameworks
ROWS = [
    ("controls & audit evidence", ["ISO 27001", "SOC 2"], C["green"]),
    ("assessing AI systems", ["EU AI Act"], C["cyan"]),
    ("privacy & data protection", ["GDPR"], C["amber"]),
    ("threat modelling & testing", ["STRIDE", "OWASP"], C["violet"]),
]


def frameworks(small: bool) -> str:
    w = 480 if small else 880
    pad = 22 if small else 30
    fs = 12 if small else 14
    parts, y = [], pad + 14
    for label, names, accent in ROWS:
        if small:
            parts.append(f'<text x="{pad}" y="{y}" font-family="{MONO}" font-size="{fs - 1}" fill="{C["dim"]}">{escape(label)}</text>')
            y += 26
            s, y = flow([chip(n, accent, fs) for n in names], pad, y, w - 2 * pad, 30)
            y += 8
        else:
            parts.append(f'<text x="{pad}" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{C["dim"]}">{escape(label)}</text>')
            s, _ = flow([chip(n, accent, fs) for n in names], 300, y, w - 330, 30)
            y += 44
        parts.append(s)
    h = y - (6 if small else 12) + pad * 0.4
    return svg(w, h, frame(w, h) + "".join(parts), "Frameworks: ISO 27001 and SOC 2 for controls and audit evidence, EU AI Act for AI systems, GDPR for privacy, STRIDE and OWASP for threat modelling.")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for small in (False, True):
        sfx = "-sm" if small else ""
        (OUT / f"terminal{sfx}.svg").write_text(terminal(small))
        (OUT / f"pipeline{sfx}.svg").write_text(pipeline(small))
        (OUT / f"frameworks{sfx}.svg").write_text(frameworks(small))
        for name, spec in CARDS.items():
            (OUT / f"{name}{sfx}.svg").write_text(card(small, **spec))
    print("wrote", len(list(OUT.glob("*.svg"))), "svgs")


if __name__ == "__main__":
    main()
