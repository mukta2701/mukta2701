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
                 txt(pad, 142, "Securing AI systems and turning", 15, 500, op=.95),
                 txt(pad, 162, "controls into audit evidence.", 15, 500, op=.95),
                 shield(w - 58, 112, 0.62)]
    else:
        body += [txt(pad, 135, "Mukta Choudhury", 60, 800),
                 txt(pad, 172, "Securing AI systems and turning controls into audit evidence.", 18, 500, op=.95),
                 shield(w - 100, 120, 1.05)]
    return svg(w, h, "".join(body), "Mukta Choudhury: AI security, application security and GRC", "hero")


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


WHAT = [("AI & application security", "Assessing risks in AI-enabled applications and APIs.", "violet", icon_shield),
        ("Governance & compliance", "Reviewing AWS controls and tracking remediation and audit evidence with engineering teams.", "ocean", icon_doc),
        ("Threat modelling", "Structured threat modelling with STRIDE and OWASP.", "sunset", icon_radar)]


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
    return svg(w, h, "".join(parts), "What I do: AI and application security, governance and compliance, threat modelling", *{g for _, _, g, _ in WHAT})


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


def deco_shield(cx, cy, s):
    return (f'<g transform="translate({cx} {cy}) scale({s})" opacity=".26"><path d="M0 -60 L50 -40 V5 C50 40 25 62 0 75 C-25 62 -50 40 -50 5 V-40 Z" fill="none" stroke="#fff" stroke-width="5"/>'
            f'<path d="M-22 4 L-7 20 L26 -16" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g>')


# -------------------------------------------------------------- highlights
def deco_cap(cx, cy, s):
    return (f'<g transform="translate({cx} {cy}) scale({s})" opacity=".28" fill="#fff"><path d="M-62 -8 L0 -40 L62 -8 L0 24 Z"/>'
            f'<path d="M-36 8 V34 C-16 48 16 48 36 34 V8 L0 26 Z"/><rect x="58" y="-8" width="4" height="40" rx="2"/></g>')


def tile(x, y, w, h, g, tag, title, sub, desc, deco, tsize):
    pw, pdraw = pill(tag, 11, True)
    parts = [f'<clipPath id="t{g}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16"/></clipPath>'
             f'<g clip-path="url(#t{g})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#g-{g})"/>'
             f'<circle cx="{x + w - 20}" cy="{y}" r="110" fill="#fff" fill-opacity=".11"/><circle cx="{x + w * 0.4:.0f}" cy="{y + h}" r="60" fill="#fff" fill-opacity=".07"/></g>',
             deco, pdraw(x + 26, y + 40), txt(x + 26, y + 84, title, tsize, 800), txt(x + 26, y + 84 + tsize * 1.2, sub, 16, 600, op=.95)]
    yy = y + 84 + tsize * 1.2 + 28
    for ln in wrap(desc, int((w - 52) / (13 * CW))):
        parts.append(txt(x + 26, yy, ln, 13, 500, op=.93))
        yy += 19
    return "".join(parts)


def highlights(small):
    if small:
        w, h1, h2, gap = 480, 168, 168, 12
        h = h1 + h2 + gap
        body = (tile(0, 0, w, h1, "violet", "EDUCATION", "MSc Cyber Security & AI", "University of Sheffield", "Awarded with Merit.", deco_cap(w - 70, 84, 1.0), 24)
                + tile(0, h1 + gap, w, h2, "ocean", "CURRENT ROLE", "AI Security & Compliance", "AdTecher", "Risk assessment, AWS controls and audit evidence.", deco_shield(w - 62, h1 + gap + 84, .9), 22))
    else:
        w, h, gap, w1 = 880, 196, 12, 520
        body = (tile(0, 0, w1, h, "violet", "EDUCATION", "MSc Cyber Security & AI", "University of Sheffield", "Awarded with Merit.", deco_cap(w1 - 90, 100, 1.4), 28)
                + tile(w1 + gap, 0, w - w1 - gap, h, "ocean", "CURRENT ROLE", "AI Security & Compliance", "AdTecher", "Risk assessment, AWS controls and audit evidence with engineering teams.", deco_shield(w - 56, h - 54, .6), 20))
    return svg(w, h, body, "Highlights: MSc Cyber Security and AI with Merit from the University of Sheffield; AI Security and Compliance at AdTecher", "violet", "ocean")


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
        (OUT / f"highlights{sfx}.svg").write_text(highlights(small))
        (OUT / f"whatido{sfx}.svg").write_text(whatido(small))
        (OUT / f"frameworks{sfx}.svg").write_text(frameworks(small))
        (OUT / f"footer{sfx}.svg").write_text(footer(small))
    print("wrote", len(list(OUT.glob("*.svg"))), "svgs")


if __name__ == "__main__":
    main()
