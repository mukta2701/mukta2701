#!/usr/bin/env python3
"""Render the vibrant profile visuals as SVGs.

Usage: python3 scripts/build_assets.py   (no third-party dependencies)

Every asset is written twice: a desktop version (~880px wide) and an "-sm"
version drawn for phone width, picked in README.md with a <picture> media
query. SVGs are shown through <img>, so only system fonts and inline CSS are
used. Animations are CSS-only and switch off under prefers-reduced-motion.

Figures come from the public READMEs of privacy-review-agent and
cybertrend-intelligence; update them in the constants below.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
CW = 0.58  # conservative average advance of the sans stack, in em

NAVY, SLATE = "#0F172A", "#94A3B8"
G = {  # gradient name -> stops
    "hero": ["#4F46E5", "#9333EA", "#EC4899", "#F97316"],
    "violet": ["#7C3AED", "#D946EF"],
    "teal": ["#059669", "#06B6D4"],
    "sunset": ["#F97316", "#EC4899"],
    "ocean": ["#2563EB", "#06B6D4"],
    "amber": ["#F59E0B", "#EF4444"],
    "indigo": ["#4F46E5", "#8B5CF6"],
}

STYLE = """<style>
@keyframes wv{to{transform:translateX(calc(-1 * var(--p)))}}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
@keyframes gp{0%,100%{opacity:.6}50%{opacity:1}}
@keyframes dash{to{stroke-dashoffset:-14}}
@keyframes spin{to{transform:rotate(360deg)}}
.fl{animation:fl 6s ease-in-out infinite}
.gp{animation:gp 3s ease-in-out infinite}
.dash{stroke-dasharray:7 7;animation:dash 1s linear infinite}
.spin{transform-box:fill-box;transform-origin:center;animation:spin 8s linear infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>"""


def gdefs(*names) -> str:
    out = []
    for n in names:
        stops = G[n]
        s = "".join(f'<stop offset="{i / (len(stops) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(stops))
        out.append(f'<linearGradient id="g-{n}" x1="0" y1="0" x2="1" y2="1">{s}</linearGradient>')
    return "".join(out)


EXTRA_DEFS = ('<radialGradient id="orb"><stop offset="0" stop-color="#fff" stop-opacity=".45"/>'
              '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
              '<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="8"/></filter>')


def svg(w, h, body, title, *grads) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'role="img" aria-label="{escape(title)}">{STYLE}<defs>{gdefs(*grads)}{EXTRA_DEFS}'
            f'<clipPath id="c"><rect width="{w:.0f}" height="{h:.0f}" rx="16"/></clipPath></defs>{body}</svg>\n')


def wrap(text, max_chars):
    lines, cur = [], ""
    for wd in text.split():
        if cur and len(cur) + 1 + len(wd) > max_chars:
            lines.append(cur)
            cur = wd
        else:
            cur = f"{cur} {wd}".strip()
    if cur:
        lines.append(cur)
    return lines


def txt(x, y, s, size, weight=400, fill="#fff", op=1, anchor="start", ls=0, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{SANS}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'fill-opacity="{op}" text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{escape(s)}</text>')


def pill(text, fs, caps=False):
    width = len(text) * fs * (0.7 if caps else CW) + 26

    def draw(x, y):
        return (f'<rect x="{x:.1f}" y="{y - fs - 6:.1f}" width="{width - 8:.1f}" height="{fs + 14:.1f}" rx="{(fs + 14) / 2:.1f}" fill="#fff" fill-opacity=".2"/>'
                + txt(x + 9, y, text, fs, 700 if caps else 600, ls=1.2 if caps else 0))
    return width, draw


def flow(items, x0, y, max_w, row_h):
    out, x = [], x0
    for width, draw in items:
        if x > x0 and x + width > x0 + max_w:
            x, y = x0, y + row_h
        out.append(draw(x, y))
        x += width
    return "".join(out), y + row_h


def waves(w, h, specs):
    out = []
    for base, amp, period, op, secs in specs:
        q = period / 4
        d = f"M0 {base} Q{q} {base - amp} {period / 2} {base}"
        x = period
        while x < w + 2 * period:
            d += f" T{x} {base}"
            x += period / 2
        d += f" V{h + 4} H0 Z"
        out.append(f'<path d="{d}" fill="#fff" fill-opacity="{op}" style="--p:{period}px;animation:wv {secs}s linear infinite"/>')
    return "".join(out)


def shield(cx, cy, s, glow=True):
    path = "M0 -60 L50 -40 V5 C50 40 25 62 0 75 C-25 62 -50 40 -50 5 V-40 Z"
    g = f'<path d="{path}" fill="#fff" fill-opacity=".5" filter="url(#soft)" class="gp"/>' if glow else ""
    return (f'<g transform="translate({cx} {cy}) scale({s})"><g class="fl">{g}'
            f'<path d="{path}" fill="#fff" fill-opacity=".16" stroke="#fff" stroke-width="3.5" stroke-linejoin="round"/>'
            f'<circle cx="0" cy="-8" r="10" fill="#fff"/><path d="M-5 0 H5 L8 26 H-8 Z" fill="#fff"/></g></g>')


# ------------------------------------------------------------------ banner
def banner(small):
    w, h = (480, 250) if small else (880, 270)
    fs = 11 if small else 12
    names = ["AI SECURITY", "APPSEC", "GRC"] if small else ["AI SECURITY", "APPLICATION SECURITY", "GRC"]
    pad = 24 if small else 44
    pills, _ = flow([pill(n, fs, True) for n in names], pad, 52 if small else 60, w - 2 * pad, 30)
    body = [f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#g-hero)"/>',
            f'<circle cx="{w * 0.78:.0f}" cy="70" r="120" fill="url(#orb)" class="fl"/>',
            f'<circle cx="{w * 0.12:.0f}" cy="{h - 40}" r="90" fill="url(#orb)" opacity=".7"/>',
            f'<circle cx="{w * 0.55:.0f}" cy="30" r="50" fill="url(#orb)" opacity=".6"/>',
            waves(w, h, [(h - 62, 14, 440, .14, 12), (h - 46, 12, 300, .14, 8), (h - 28, 10, 360, .22, 6)]),
            '</g>', pills]
    if small:
        body += [txt(pad, 108, "Mukta Choudhury", 38, 800),
                 txt(pad, 142, "Privacy-by-design tooling, audit", 15, 500, op=.95),
                 txt(pad, 162, "evidence and threat intelligence.", 15, 500, op=.95),
                 shield(w - 58, 112, 0.62)]
    else:
        body += [txt(pad, 135, "Mukta Choudhury", 60, 800),
                 txt(pad, 172, "Privacy-by-design tooling, audit evidence and threat intelligence.", 18, 500, op=.95),
                 shield(w - 100, 120, 1.05)]
    return svg(w, h, "".join(body), "Mukta Choudhury: AI security, application security and GRC", "hero")


# ------------------------------------------------------------------- stats
STATS = [("381", "labelled benchmark cases", "violet"), ("100%", "near-miss precision", "teal"),
         ("460+", "automated tests in CI", "sunset"), ("7", "threat feeds + NVD", "ocean")]


def stats(small):
    w, gap = (480, 12) if small else (880, 12)
    cols = 2 if small else 4
    th = 96 if small else 108
    tw = (w - gap * (cols - 1)) / cols
    rows = (len(STATS) + cols - 1) // cols
    h = rows * th + (rows - 1) * gap
    parts = []
    for i, (v, label, g) in enumerate(STATS):
        x, y = (i % cols) * (tw + gap), (i // cols) * (th + gap)
        parts.append(f'<g clip-path="url(#c{i})"><rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="14" fill="url(#g-{g})"/>'
                     f'<circle cx="{x + tw - 18:.1f}" cy="{y + 14}" r="56" fill="#fff" fill-opacity=".14"/>'
                     f'<circle cx="{x + tw - 70:.1f}" cy="{y + th}" r="34" fill="#fff" fill-opacity=".1"/></g>'
                     + txt(x + 20, y + th * 0.56, v, 38 if not small else 34, 800)
                     + txt(x + 20, y + th * 0.84, label, 13 if not small else 12.5, 500, op=.92))
        clip = f'<clipPath id="c{i}"><rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="14"/></clipPath>'
        parts.insert(0, clip)
    return svg(w, h, "".join(parts), "Metrics: 381 labelled benchmark cases, 100% near-miss precision, 460 plus CI tests, 7 threat feeds plus NVD",
               *{g for _, _, g in STATS})


# --------------------------------------------------------------- what I do
def icon_shield(cx, cy):
    return (f'<g transform="translate({cx} {cy}) scale(.26)"><path d="M0 -60 L50 -40 V5 C50 40 25 62 0 75 C-25 62 -50 40 -50 5 V-40 Z" fill="none" stroke="#fff" stroke-width="9" stroke-linejoin="round"/>'
            f'<path d="M-20 6 L-6 22 L24 -14" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></g>')


def icon_doc(cx, cy):
    return (f'<g transform="translate({cx} {cy})"><rect x="-10" y="-13" width="20" height="26" rx="3" fill="none" stroke="#fff" stroke-width="2.6"/>'
            f'<path d="M-5 -4 H5 M-5 2 H5 M-5 8 H1" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></g>')


def icon_radar(cx, cy):
    return (f'<g transform="translate({cx} {cy})" fill="none" stroke="#fff" stroke-width="2.4"><circle r="13"/><circle r="6.5"/>'
            f'<path d="M0 0 L11 -9" stroke-linecap="round"/><circle r="2" fill="#fff"/></g>')


WHAT = [("Application security", "Pre-commit checks that stop personal data and secrets reaching logs, AI prompts and third parties.", "violet", icon_shield),
        ("Governance & compliance", "Control mapping, risk assessment and audit evidence across ISO 27001, SOC 2 and AWS.", "ocean", icon_doc),
        ("Threat intelligence", "Vulnerabilities prioritised by exploitability (CVSS, EPSS, CISA KEV), not headline severity.", "sunset", icon_radar)]


def whatido(small):
    w, gap = 880 if not small else 480, 12
    parts = []
    if small:
        th = 104
        h = 3 * th + 2 * gap
        for i, (title, desc, g, icon) in enumerate(WHAT):
            y = i * (th + gap)
            parts.append(f'<clipPath id="c{i}"><rect y="{y}" width="{w}" height="{th}" rx="14"/></clipPath>'
                         f'<g clip-path="url(#c{i})"><rect y="{y}" width="{w}" height="{th}" rx="14" fill="url(#g-{g})"/><circle cx="{w - 20}" cy="{y}" r="62" fill="#fff" fill-opacity=".13"/></g>'
                         f'<circle cx="38" cy="{y + 36}" r="22" fill="#fff" fill-opacity=".22"/>{icon(38, y + 36)}'
                         + txt(76, y + 32, title, 16, 700))
            for j, ln in enumerate(wrap(desc, 44)):
                parts.append(txt(76, y + 54 + j * 17, ln, 12.5, 500, op=.93))
    else:
        tw, th = (w - 2 * gap) / 3, 192
        h = th
        for i, (title, desc, g, icon) in enumerate(WHAT):
            x = i * (tw + gap)
            parts.append(f'<clipPath id="c{i}"><rect x="{x:.1f}" width="{tw:.1f}" height="{th}" rx="14"/></clipPath>'
                         f'<g clip-path="url(#c{i})"><rect x="{x:.1f}" width="{tw:.1f}" height="{th}" rx="14" fill="url(#g-{g})"/><circle cx="{x + tw - 10:.1f}" cy="6" r="70" fill="#fff" fill-opacity=".13"/></g>'
                         f'<circle cx="{x + 42:.1f}" cy="44" r="24" fill="#fff" fill-opacity=".22"/>{icon(x + 42, 44)}'
                         + txt(x + 22, 96, title, 17, 700))
            for j, ln in enumerate(wrap(desc, int((tw - 44) / (13 * CW)))):
                parts.append(txt(x + 22, 120 + j * 19, ln, 13, 500, op=.93))
    return svg(w, h, "".join(parts), "What I do: application security, governance and compliance, threat intelligence", *{g for _, _, g, _ in WHAT})


# ------------------------------------------------------------------- cards
def deco_shield(cx, cy, s):
    return (f'<g transform="translate({cx} {cy}) scale({s})" opacity=".22"><path d="M0 -60 L50 -40 V5 C50 40 25 62 0 75 C-25 62 -50 40 -50 5 V-40 Z" fill="none" stroke="#fff" stroke-width="5"/>'
            f'<path d="M-22 4 L-7 20 L26 -16" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g>')


def deco_radar(cx, cy, s):
    return (f'<g transform="translate({cx} {cy}) scale({s})" opacity=".26" fill="none" stroke="#fff" stroke-width="3"><circle r="22"/><circle r="44"/><circle r="66"/>'
            f'<path d="M-66 0 H66 M0 -66 V66" stroke-width="1.5"/><path d="M0 0 L46 -46 A66 66 0 0 1 66 0 Z" fill="#fff" fill-opacity=".35" stroke="none" class="spin"/></g>')


def deco_pulse(cx, cy, s):
    return (f'<g transform="translate({cx} {cy}) scale({s})" opacity=".3" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
            f'<circle r="62" stroke-width="3"/><path d="M-50 4 H-22 L-12 -26 L2 36 L14 -12 L22 4 H50"/></g>')


CARDS = {
    "card-privacy": dict(g="violet", deco=deco_shield, tag="APPSEC · PRIVACY", title="privacy-review-agent",
                         desc="Offline pre-commit and CI check that stops personal data and secrets reaching logs, AI prompts, analytics and third-party services.",
                         stats=[("381", "benchmark cases"), ("100%", "near-miss precision"), ("460+", "CI tests")],
                         chips=["Python", "Semgrep", "GDPR"], url="https://github.com/mukta2701/privacy-review-agent",
                         label="privacy-review-agent: offline privacy check for code. 381 benchmark cases, 100% near-miss precision, 460 plus CI tests."),
    "card-cybertrend": dict(g="ocean", deco=deco_radar, tag="THREAT INTELLIGENCE", title="cybertrend-intelligence",
                            desc="Daily digest of the vulnerabilities that matter, ranked by CVSS, EPSS and CISA KEV instead of headline severity.",
                            stats=[("7", "feeds + NVD"), ("≥ 90", "score sends an instant alert")],
                            chips=["Python", "PostgreSQL", "NVD API", "Docker"], url="",
                            label="cybertrend-intelligence: daily threat-intelligence digest from 7 feeds plus NVD, ranked by exploitability."),
    "card-rfid": dict(g="amber", deco=deco_pulse, tag="THREAT MODELLING", title="rfid-threat-modelling-imd",
                      desc="Threat model for RFID-based implantable medical devices, built with STRIDE and OWASP.",
                      stats=[], chips=["STRIDE", "OWASP", "Medical devices"], url="",
                      label="rfid-threat-modelling-imd: STRIDE and OWASP threat model for RFID implantable medical devices."),
}


def card(small, g, deco, tag, title, desc, stats_, chips, label, url=""):
    w = 480 if small else 880
    pad = 22 if small else 32
    textw = w - 2 * pad if small else 600
    fs = 13 if small else 14.5
    parts = []
    tw_, tdraw = pill(tag, 11, True)
    parts.append(tdraw(pad, pad + 14))
    y = pad + 14 + 38
    parts.append(txt(pad, y, title, 25 if small else 29, 800))
    y += 14 + fs
    for ln in wrap(desc, int(textw / (fs * CW))):
        parts.append(txt(pad, y, ln, fs, 500, op=.95))
        y += fs * 1.55
    y += 10
    if stats_:
        items = []
        for v, lab in stats_:
            width = len(v) * 16 + len(lab) * 6.6 + 36
            items.append((width, lambda x, yy, v=v, lab=lab: txt(x, yy, v, 22, 800) + txt(x + len(v) * 16 + 10, yy, lab, 12.5, 500, op=.9)))
        s, y = flow(items, pad, y + 14, textw, 30)
        parts.append(s)
        y -= 2
    s, y = flow([pill(c, 12) for c in chips], pad, y + 14, textw, 30)
    parts.append(s)
    h = y - 4 + pad * 0.4
    dx = w - 120 if not small else w - 62
    dec = deco(dx, h / 2 if not small else 74, 1.2 if not small else .62)
    body = (f'<g clip-path="url(#c)"><rect width="{w}" height="{h:.0f}" fill="url(#g-{g})"/><circle cx="{w - 30}" cy="0" r="120" fill="#fff" fill-opacity=".1"/>'
            f'<circle cx="{w * 0.55:.0f}" cy="{h:.0f}" r="70" fill="#fff" fill-opacity=".07"/></g>' + dec + "".join(parts)
            + txt(w - pad, pad + 14, "↗", 20, 700, anchor="end", op=.9))
    return svg(w, h, body, label, g)


# ---------------------------------------------------------------- pipeline
def node(x, y, w, h, n, title, sub, g, dashed=False):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="14" fill="url(#g-{g})"' + (' stroke="#fff" stroke-opacity=".7" stroke-dasharray="5 4"' if dashed else "") + '/>'
            f'<circle cx="{x + 24:.1f}" cy="{y + h / 2:.1f}" r="14" fill="#fff" fill-opacity=".25"/>' + txt(x + 24, y + h / 2 + 5, str(n), 14, 800, anchor="middle")
            + txt(x + 48, y + h / 2 - 3, title, 15, 700) + txt(x + 48, y + h / 2 + 16, sub, 12, 500, op=.92))


def pipeline(small):
    steps = [("Collect", "7 feeds + NVD", "ocean"), ("Score", "CVSS · EPSS · KEV", "teal"),
             ("Summarise", "8 structured fields", "amber"), ("Digest", "by severity", "violet")]
    parts = []
    if not small:
        w, h, nw, nh, y0 = 880, 214, 184, 64, 30
        gap = (w - 40 - 4 * nw) / 3
        xs = [20 + i * (nw + gap) for i in range(4)]
        parts.append(f'<rect width="{w}" height="{h}" rx="16" fill="{NAVY}"/>')
        for i, ((t, s, g), x) in enumerate(zip(steps, xs)):
            parts.append(node(x, y0, nw, nh, i + 1, t, s, g))
        for i in range(3):
            xa, xb = xs[i] + nw + 5, xs[i + 1] - 5
            parts.append(f'<path class="dash" d="M{xa:.1f} {y0 + nh / 2} H{xb - 6:.1f}" stroke="#fff" stroke-opacity=".7" stroke-width="2.5" fill="none"/>'
                         f'<path d="M{xb - 8:.1f} {y0 + nh / 2 - 6} L{xb:.1f} {y0 + nh / 2} L{xb - 8:.1f} {y0 + nh / 2 + 6}" stroke="#fff" stroke-opacity=".85" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        ay = y0 + nh + 44
        parts.append(f'<path class="dash" d="M{xs[1] + nw / 2:.1f} {y0 + nh + 4} V{ay - 4}" stroke="#F87171" stroke-width="2.5" fill="none"/>')
        parts.append(node(xs[1], ay, nw, 56, "!", "Alert now", "score ≥ 90", "amber", True))
    else:
        w, nw, nh, gap, x = 480, 290, 62, 22, 18
        h = 36 + 4 * nh + 3 * gap
        parts.append(f'<rect width="{w}" height="{h}" rx="16" fill="{NAVY}"/>')
        for i, (t, s, g) in enumerate(steps):
            y = 18 + i * (nh + gap)
            parts.append(node(x, y, nw, nh, i + 1, t, s, g))
            if i < 3:
                parts.append(f'<path class="dash" d="M{x + nw / 2} {y + nh + 2} V{y + nh + gap - 2}" stroke="#fff" stroke-opacity=".7" stroke-width="2.5" fill="none"/>')
        sy, ax = 18 + (nh + gap), x + nw + 20
        parts.append(f'<path class="dash" d="M{x + nw + 2} {sy + nh / 2} H{ax - 2}" stroke="#F87171" stroke-width="2.5" fill="none"/>')
        parts.append(f'<rect x="{ax}" y="{sy}" width="{w - ax - 14}" height="{nh}" rx="14" fill="url(#g-amber)" stroke="#fff" stroke-opacity=".7" stroke-dasharray="5 4"/>'
                     + txt(ax + (w - ax - 14) / 2, sy + 28, "Alert", 14, 700, anchor="middle") + txt(ax + (w - ax - 14) / 2, sy + 47, "score ≥ 90", 11.5, 500, anchor="middle", op=.92))
    return svg(w, h, "".join(parts), "Pipeline: collect from 7 feeds and NVD, score by CVSS, EPSS and KEV, summarise, then send a digest by severity. Scores of 90 or more send an immediate alert.",
               "ocean", "teal", "amber", "violet")


# -------------------------------------------------------------- frameworks
ROWS = [("Controls & audit evidence", ["ISO 27001", "SOC 2"], "teal"), ("Assessing AI systems", ["EU AI Act"], "violet"),
        ("Privacy & data protection", ["GDPR"], "sunset"), ("Threat modelling & testing", ["STRIDE", "OWASP"], "ocean")]


def gpill(text, g, fs):
    width = len(text) * fs * 0.62 + 34

    def draw(x, y):
        return (f'<rect x="{x:.1f}" y="{y - fs - 8:.1f}" width="{width - 8:.1f}" height="{fs + 18:.1f}" rx="{(fs + 18) / 2:.1f}" fill="url(#g-{g})"/>'
                + txt(x + (width - 8) / 2, y + 0.5, text, fs, 700, anchor="middle"))
    return width, draw


def frameworks(small):
    w = 480 if small else 880
    pad = 22 if small else 30
    fs = 14 if small else 15
    parts, y = [], pad + 10
    for label, names, g in ROWS:
        if small:
            parts.append(txt(pad, y, label, 12.5, 500, fill=SLATE))
            s, y2 = flow([gpill(n, g, fs) for n in names], pad, y + 30, w - 2 * pad, 38)
            y = y2 + 8
        else:
            parts.append(txt(pad, y + 5, label, 14, 500, fill=SLATE))
            s, _ = flow([gpill(n, g, fs) for n in names], 310, y + 6, w - 340, 38)
            y += 50
        parts.append(s)
    h = y + (0 if small else -6) + pad * 0.3
    return svg(w, h, f'<rect width="{w}" height="{h:.0f}" rx="16" fill="{NAVY}"/>' + "".join(parts),
               "Frameworks: ISO 27001 and SOC 2 for controls and audit evidence, EU AI Act for AI systems, GDPR for privacy, STRIDE and OWASP for threat modelling.",
               *{g for _, _, g in ROWS})


# ------------------------------------------------------------------ footer
def footer(small):
    w, h = (480, 120) if small else (880, 130)
    body = (f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#g-hero)"/>'
            f'<circle cx="{w * 0.2:.0f}" cy="30" r="70" fill="url(#orb)"/><circle cx="{w * 0.85:.0f}" cy="{h}" r="80" fill="url(#orb)"/>'
            + waves(w, h, [(h - 40, 12, 360, .16, 9), (h - 24, 10, 280, .2, 6)]) + '</g>'
            + txt(w / 2, 52, "Thanks for stopping by", 26 if not small else 21, 800, anchor="middle")
            + txt(w / 2, 78, "Let's talk AI security, privacy and compliance", 14 if not small else 12.5, 500, anchor="middle", op=.95))
    return svg(w, h, body, "Thanks for stopping by", "hero")


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for small in (False, True):
        sfx = "-sm" if small else ""
        (OUT / f"banner{sfx}.svg").write_text(banner(small))
        (OUT / f"stats{sfx}.svg").write_text(stats(small))
        (OUT / f"whatido{sfx}.svg").write_text(whatido(small))
        (OUT / f"pipeline{sfx}.svg").write_text(pipeline(small))
        (OUT / f"frameworks{sfx}.svg").write_text(frameworks(small))
        (OUT / f"footer{sfx}.svg").write_text(footer(small))
        for name, spec in CARDS.items():
            kw = {("stats_" if k == "stats" else k): v for k, v in spec.items() if k != "url"}
            (OUT / f"{name}{sfx}.svg").write_text(card(small, **kw))
    print("wrote", len(list(OUT.glob("*.svg"))), "svgs")


if __name__ == "__main__":
    main()
