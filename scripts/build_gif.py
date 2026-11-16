#!/usr/bin/env python3
"""Render scripts/banner-anim.svg into assets/banner.gif (a seamless 6 s loop).

Needs Pillow (`pip install pillow`) and Google Chrome. Chrome renders each
frame with every CSS animation paused at the frame's timestamp.

Usage: python3 scripts/build_gif.py [fps]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LOOP_MS, W, H = 6000, 720, 300


def render_frames(tmp: Path, fps: int) -> list:
    svg = (ROOT / "scripts" / "banner-anim.svg").read_text()
    frames = []
    n = LOOP_MS * fps // 1000
    for i in range(n):
        t = i * 1000 // fps
        html = (f'<!doctype html><meta charset="utf-8"><body style="margin:0;background:#fff">{svg}'
                # Freeze each animation at time t, bake it into inline styles, then cancel it. A static page
                # is rasterised completely; paused composited animations can leave unpainted tiles.
                f'<script>document.getAnimations().forEach(a=>{{a.pause();a.currentTime={t};a.commitStyles();a.cancel()}})</script>')
        page, png = tmp / f"f{i:03d}.html", tmp / f"f{i:03d}.png"
        page.write_text(html)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={W},{H}", f"--screenshot={png}", f"file://{page}"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        frames.append(png)
    return frames


def main() -> None:
    fps = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    with tempfile.TemporaryDirectory() as d:
        paths = render_frames(Path(d), fps)
        out_w = 640  # keeps the file small; the GIF is shown at 350-880px wide
        out_h = round(H * out_w / W)
        imgs = [Image.open(p).convert("RGB").resize((out_w, out_h), Image.Resampling.LANCZOS) for p in paths]
        # one shared palette, built from a sample of frames, keeps colours steady between frames
        sample = Image.new("RGB", (out_w, out_h * 6))
        for k in range(6):
            sample.paste(imgs[k * len(imgs) // 6], (0, k * out_h))
        pal = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        out = [im.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG) for im in imgs]
        dest = ROOT / "assets" / "banner.gif"
        out[0].save(dest, save_all=True, append_images=out[1:], duration=1000 // fps, loop=0, optimize=False, disposal=1)
    print(f"wrote {dest} ({dest.stat().st_size / 1e6:.2f} MB, {len(imgs)} frames @ {fps} fps)")


if __name__ == "__main__":
    main()
