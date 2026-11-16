#!/usr/bin/env python3
"""Generate the profile's SVG pieces (no third-party dependencies).

Usage: python3 scripts/build_assets.py

Writes:
  scripts/banner-anim.svg      source animation for the banner GIF (see build_gif.py)
  assets/frameworks{,-sm}.svg  one-strip frameworks panel, desktop and phone
  assets/btn-*.svg             social/portfolio buttons

SVGs are shown through <img>, so only system fonts and inline CSS are used.
Every animation in the banner loops in exactly 6 seconds so the GIF is seamless.
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
CW = 0.58
NAVY, SLATE = "#0F172A", "#94A3B8"
G = {
    "hero": ["#4F46E5", "#9333EA", "#EC4899", "#F97316"],
    "violet": ["#7C3AED", "#D946EF"], "teal": ["#059669", "#06B6D4"],
    "sunset": ["#F97316", "#EC4899"], "ocean": ["#2563EB", "#06B6D4"],
    "indigo": ["#4F46E5", "#8B5CF6"],
}
STYLE = """<style>
@keyframes wv{to{transform:translateX(calc(-1 * var(--p)))}}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
@keyframes gp{0%,100%{opacity:.6}50%{opacity:1}}
@keyframes rot{0%{opacity:0;transform:translateY(14px)}6%,30%{opacity:1;transform:translateY(0)}36%,100%{opacity:0;transform:translateY(-14px)}}
.fl{animation:fl 6s ease-in-out infinite}
.gp{animation:gp 3s ease-in-out infinite}
.rot{animation:rot 6s ease infinite both}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>"""
EXTRA = ('<radialGradient id="orb"><stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
         '<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="8"/></filter>')


def gdefs(*names):
    out = []
    for n in names:
        st = G[n]
        s = "".join(f'<stop offset="{i / (len(st) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(st))
        out.append(f'<linearGradient id="g-{n}" x1="0" y1="0" x2="1" y2="1">{s}</linearGradient>')
    return "".join(out)


def svg(w, h, body, title, *grads):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{escape(title)}">'
            f'{STYLE}<defs>{gdefs(*grads)}{EXTRA}</defs>{body}</svg>\n')


def txt(x, y, s, size, weight=400, fill="#fff", op=1, anchor="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{SANS}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'fill-opacity="{op}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')


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
        d = f"M0 {base} Q{period / 4} {base - amp} {period / 2} {base}"
        x = period
        while x < w + 2 * period:
            d += f" T{x} {base}"
            x += period / 2
        out.append(f'<path d="{d} V{h + 4} H0 Z" fill="#fff" fill-opacity="{op}" style="--p:{period}px;animation:wv {secs}s linear infinite"/>')
    return "".join(out)


def shield(cx, cy, s):
    path = "M0 -60 L50 -40 V5 C50 40 25 62 0 75 C-25 62 -50 40 -50 5 V-40 Z"
    return (f'<g transform="translate({cx} {cy}) scale({s})"><g class="fl"><path d="{path}" fill="#fff" fill-opacity=".5" filter="url(#soft)" class="gp"/>'
            f'<path d="{path}" fill="#fff" fill-opacity=".16" stroke="#fff" stroke-width="3.5" stroke-linejoin="round"/>'
            f'<circle cx="0" cy="-8" r="10" fill="#fff"/><path d="M-5 0 H5 L8 26 H-8 Z" fill="#fff"/></g></g>')


# ------------------------------------------------------- banner (GIF source)
PHRASES = ["AI Security", "Application Security", "Governance, Risk & Compliance"]


def banner_anim():
    w, h = 720, 300
    body = [f'<rect width="{w}" height="{h}" fill="url(#g-hero)"/>',
            '<circle cx="560" cy="60" r="130" fill="url(#orb)" class="fl"/>',
            f'<circle cx="80" cy="{h - 20}" r="100" fill="url(#orb)" opacity=".7"/>',
            '<circle cx="360" cy="20" r="60" fill="url(#orb)" opacity=".6"/>',
            waves(w, h, [(h - 62, 14, 360, .14, 6), (h - 46, 12, 240, .14, 3), (h - 28, 10, 300, .22, 6)]),
            txt(40, 86, "Hi, I'm", 26, 600, op=.95),
            txt(40, 152, "Mukta Choudhury", 62, 800)]
    for i, p in enumerate(PHRASES):
        body.append(txt(40, 204, p, 28, 700, extra=f'class="rot" style="animation-delay:{2 * i}s"'))
    body.append(shield(w - 80, 118, 0.85))
    return svg(w, h, "".join(body), "Mukta Choudhury, AI security, application security and governance, risk and compliance", "hero")


# ------------------------------------------------------------- frameworks
FW = [("ISO 27001", "teal"), ("SOC 2", "teal"), ("EU AI Act", "violet"), ("GDPR", "sunset"), ("STRIDE", "ocean"), ("OWASP", "ocean")]


def gpill(text, g, fs):
    width = len(text) * fs * 0.62 + 34

    def draw(x, y):
        return (f'<rect x="{x:.1f}" y="{y - fs - 8:.1f}" width="{width - 8:.1f}" height="{fs + 18:.1f}" rx="{(fs + 18) / 2:.1f}" fill="url(#g-{g})"/>'
                + txt(x + (width - 8) / 2, y + 0.5, text, fs, 700, anchor="middle"))
    return width, draw


def frameworks(small):
    w = 480 if small else 880
    pad, fs = (22, 14) if small else (30, 15)
    label = txt(pad, pad + 8, "FRAMEWORKS I WORK WITH", 11.5, 700, fill=SLATE, extra='letter-spacing="1.6"')
    s, y = flow([gpill(n, g, fs) for n, g in FW], pad, pad + 48, w - 2 * pad, 40)
    h = y - 8 + pad * 0.5
    return svg(w, h, f'<rect width="{w}" height="{h:.0f}" rx="16" fill="{NAVY}"/>' + label + s,
               "Frameworks: ISO 27001, SOC 2, EU AI Act, GDPR, STRIDE and OWASP", "teal", "violet", "sunset", "ocean")


# ---------------------------------------------------------------- buttons
def button(label, g, glyph):
    w, h = 190, 52
    body = (f'<rect width="{w}" height="{h}" rx="26" fill="url(#g-{g})"/><circle cx="30" cy="26" r="14" fill="#fff" fill-opacity=".25"/>{glyph}'
            + txt(54, 32, label, 16, 700))
    return svg(w, h, body, label, g)


G_IN = '<text x="30" y="31" font-family="Georgia, serif" font-size="15" font-weight="700" fill="#fff" text-anchor="middle">in</text>'
G_WEB = ('<g transform="translate(30 26)" fill="none" stroke="#fff" stroke-width="1.8"><circle r="8"/><ellipse rx="3.4" ry="8"/>'
         '<path d="M-8 0 H8"/></g>')


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    (ROOT / "scripts" / "banner-anim.svg").write_text(banner_anim())
    (OUT / "frameworks.svg").write_text(frameworks(False))
    (OUT / "frameworks-sm.svg").write_text(frameworks(True))
    (OUT / "btn-linkedin.svg").write_text(button("LinkedIn", "ocean", G_IN))
    (OUT / "btn-portfolio.svg").write_text(button("Portfolio", "violet", G_WEB))
    print("wrote banner-anim.svg +", len(list(OUT.glob("*.svg"))), "svgs")


if __name__ == "__main__":
    main()
