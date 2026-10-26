#!/usr/bin/env python3
"""demo_media.py — the example works behind the sample portfolio's highlights.

Rowan Hale is fictional, so the work is too: every file here is drawn by this
script, not photographed or filmed. The point is to show what a highlight
looks like with the work itself attached: charts, drawings, a deck, essays,
three short films. Writes into assets/demo/<COURSE>/ ; demo_portfolio.py
lists the files per course and reads their sizes from disk at build time.

Run once, commit the output. Not part of the site build: the images depend on
the fonts and Pillow version of the machine that drew them, and CI's drift
check would never agree with them byte for byte.

    python3 scripts/demo_media.py            # everything
    python3 scripts/demo_media.py ART-410    # one course

The films need the frame encoder in scripts/tools/frames2mp4.swift (macOS;
compiled on first use into a temp folder). Without swiftc, posters are still
drawn and the films are skipped.
"""
from __future__ import annotations

import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "demo"
TOOLS = ROOT / "scripts" / "tools"

# ── Palette (the site's) ─────────────────────────────────────────────────────
PAPER = (252, 251, 248)
INK = (16, 28, 44)
GOLD = (184, 146, 58)
MARINE = (31, 78, 121)
MUTED = (110, 116, 124)
HAIR = (222, 219, 212)
SOFT = (244, 242, 237)
SEA = (26, 60, 86)
KELP = (120, 118, 44)
RUST = (168, 92, 52)

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
_F = {}


def font(kind: str, size: int):
    files = {
        "serif": "Georgia.ttf", "serif_i": "Georgia Italic.ttf", "serif_b": "Georgia Bold.ttf",
        "sans": "Arial.ttf", "sans_b": "Arial Bold.ttf", "mono": "Courier New.ttf", "mono_b": "Courier New Bold.ttf",
    }
    key = (kind, size)
    if key not in _F:
        try:
            _F[key] = ImageFont.truetype(str(FONT_DIR / files[kind]), size)
        except OSError:
            _F[key] = ImageFont.load_default()
    return _F[key]


# ── Drawing helpers ──────────────────────────────────────────────────────────

def canvas(w: int, h: int, color=PAPER) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (w, h), color)
    return im, ImageDraw.Draw(im)


def wrap(d: ImageDraw.ImageDraw, text: str, f, width: int) -> list[str]:
    lines = []
    for para in text.split("\n"):
        words, line = para.split(), ""
        if not words:
            lines.append("")
            continue
        for w in words:
            trial = (line + " " + w).strip()
            if d.textlength(trial, font=f) <= width:
                line = trial
            else:
                lines.append(line)
                line = w
        lines.append(line)
    return lines


def block(d, xy, text, f, fill=INK, width=900, leading=1.35) -> int:
    """Draw wrapped text; return the y below it."""
    x, y = xy
    lh = int(f.size * leading)
    for line in wrap(d, text, f, width):
        d.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def eyebrow(d, xy, text, fill=GOLD, size=22):
    d.text(xy, text.upper(), font=font("mono", size), fill=fill)


def hairline(d, x0, y, x1, fill=HAIR, w=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def vignette(im: Image.Image, strength=0.35) -> Image.Image:
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([-w * 0.25, -h * 0.35, w * 1.25, h * 1.35], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w * 0.18))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(im, Image.blend(im, dark, strength), mask)


def grain(im: Image.Image, amount=10, seed=1) -> Image.Image:
    rnd = random.Random(seed)
    w, h = im.size
    noise = Image.effect_noise((w, h), amount).convert("L")
    noise = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(im, noise, 0.08)


def save(im: Image.Image, path: Path, quality=82):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in (".jpg", ".jpeg"):
        im.convert("RGB").save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    else:
        im.save(path, "PNG", optimize=True)
    print(f"  {path.relative_to(ROOT)}  {path.stat().st_size // 1024} KB")


def save_pdf(pages: list[Image.Image], path: Path, dpi=120):
    path.parent.mkdir(parents=True, exist_ok=True)
    rgb = [p.convert("RGB") for p in pages]
    rgb[0].save(path, "PDF", save_all=True, append_images=rgb[1:], resolution=dpi, quality=70)
    print(f"  {path.relative_to(ROOT)}  {path.stat().st_size // 1024} KB · {len(pages)} pages")


def save_text(text: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    print(f"  {path.relative_to(ROOT)}  {len(text.split())} words")


def axes(d, box, xlim, ylim, xticks=(), yticks=(), xfmt=str, yfmt=str, title=None, ylabel=None, f=None):
    """A plain chart frame. Returns a function mapping data → pixels."""
    x0, y0, x1, y1 = box
    f = f or font("sans", 20)
    d.line([(x0, y0), (x0, y1), (x1, y1)], fill=INK, width=2)
    sx = (x1 - x0) / (xlim[1] - xlim[0]) if xlim[1] != xlim[0] else 1
    sy = (y1 - y0) / (ylim[1] - ylim[0]) if ylim[1] != ylim[0] else 1

    def P(x, y):
        return (x0 + (x - xlim[0]) * sx, y1 - (y - ylim[0]) * sy)
    for t in xticks:
        px, _ = P(t, ylim[0])
        d.line([(px, y1), (px, y1 + 8)], fill=INK, width=2)
        d.text((px, y1 + 14), xfmt(t), font=f, fill=MUTED, anchor="mt")
    for t in yticks:
        _, py = P(xlim[0], t)
        d.line([(x0 - 8, py), (x0, py)], fill=INK, width=2)
        d.line([(x0, py), (x1, py)], fill=HAIR, width=1)
        d.text((x0 - 14, py), yfmt(t), font=f, fill=MUTED, anchor="rm")
    if title:
        d.text((x0, y0 - 34), title, font=font("sans_b", 22), fill=INK)
    if ylabel:
        d.text((x0, y0 - 8), ylabel, font=font("sans", 18), fill=MUTED, anchor="ld")
    return P


def polyline(d, P, xs, ys, fill=MARINE, width=3):
    pts = [P(x, y) for x, y in zip(xs, ys)]
    if len(pts) > 1:
        d.line(pts, fill=fill, width=width, joint="curve")


def dot(d, xy, r=5, fill=GOLD, outline=None):
    x, y = xy
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=outline)


def page(title=None, eyebrow_text=None, w=1650, h=2200):
    im, d = canvas(w, h)
    y = 170
    if eyebrow_text:
        eyebrow(d, (170, y), eyebrow_text)
        y += 48
    if title:
        y = block(d, (170, y), title, font("serif", 64), width=w - 340, leading=1.15) + 24
        hairline(d, 170, y, w - 170)
        y += 40
    return im, d, y


def footer(d, text, w=1650, h=2200):
    d.text((170, h - 120), text, font=font("mono", 18), fill=MUTED)


# ── Films: frames → MP4 ──────────────────────────────────────────────────────

_ENC = None


def encoder() -> Path | None:
    global _ENC
    if _ENC is not None:
        return _ENC or None
    src = TOOLS / "frames2mp4.swift"
    if not src.exists() or not shutil.which("swiftc"):
        _ENC = False
        return None
    out = Path(tempfile.gettempdir()) / "sdit-frames2mp4"
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        r = subprocess.run(["swiftc", "-O", str(src), "-o", str(out)], capture_output=True, text=True)
        if r.returncode != 0:
            print("  (no film: swiftc failed)", r.stderr[-300:])
            _ENC = False
            return None
    _ENC = out
    return out


def film(frames, path: Path, fps=24, poster_at=0.4):
    """frames: iterable of PIL images, all the same size. Writes the MP4 and a
    JPEG poster beside it (same stem)."""
    enc = encoder()
    frames = list(frames)
    poster = frames[int(len(frames) * poster_at)]
    save(poster, path.with_suffix(".jpg"), quality=80)
    if not enc:
        print(f"  (skipped {path.name}: no encoder)")
        return
    with tempfile.TemporaryDirectory() as tmp:
        for i, fr in enumerate(frames):
            fr.save(f"{tmp}/{i:05d}.png")
        r = subprocess.run([str(enc), tmp, str(path), str(fps)], capture_output=True, text=True)
    ok = r.returncode == 0 and "ok" in r.stdout
    print(f"  {path.relative_to(ROOT)}  {path.stat().st_size // 1024 if path.exists() else 0} KB  {'ok' if ok else r.stdout + r.stderr}")


def ease(t):
    return t * t * (3 - 2 * t)


def title_card(im, d, text, sub=None, fade=1.0, fill=PAPER):
    w, h = im.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    a = int(255 * max(0, min(1, fade)))
    ld.text((w / 2, h / 2 - (28 if sub else 0)), text, font=font("serif", 64), fill=fill + (a,), anchor="mm")
    if sub:
        ld.text((w / 2, h / 2 + 44), sub, font=font("mono", 22), fill=fill + (a,), anchor="mm")
    im.paste(layer, (0, 0), layer)


# ─────────────────────────────────────────────────────────────────────────────
# The sixteen highlights
# ─────────────────────────────────────────────────────────────────────────────

def hum101():
    """The Mast — a film: a phone left in a kitchen overnight."""
    out = OUT / "HUM-101"
    W, H, N = 960, 540, 24 * 9

    def frame(i):
        t = i / N
        im, d = canvas(W, H, (10, 12, 20))
        # Counter and wall.
        d.rectangle([0, 360, W, H], fill=(28, 24, 22))
        d.rectangle([0, 352, W, 360], fill=(52, 44, 38))
        # Window: night to first light.
        dawn = ease(max(0, (t - 0.55) / 0.45))
        sky = tuple(int(a + (b - a) * dawn) for a, b in zip((14, 18, 36), (120, 110, 130)))
        d.rectangle([640, 60, 900, 300], fill=sky)
        d.rectangle([640, 60, 900, 300], outline=(40, 40, 48), width=10)
        d.line([(770, 60), (770, 300)], fill=(40, 40, 48), width=8)
        d.line([(640, 180), (900, 180)], fill=(40, 40, 48), width=8)
        # The phone, face up, glowing then dimming to black.
        glow = 1.0 if t < 0.08 else max(0.0, 1 - (t - 0.08) / 0.12)
        glow = max(glow, 0.9 if 0.46 < t < 0.5 else 0)          # one notification, ignored
        pr = [250, 300, 370, 352]
        halo = Image.new("RGB", (W, H), (0, 0, 0))
        hd = ImageDraw.Draw(halo)
        hd.rectangle([pr[0] - 80, pr[1] - 120, pr[2] + 80, pr[3] + 20], fill=(int(90 * glow), int(120 * glow), int(170 * glow)))
        halo = halo.filter(ImageFilter.GaussianBlur(50))
        im = ImageChops.lighter(im, halo)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([pr[0], pr[1] - 10, pr[2], pr[3]], radius=10, fill=(18, 18, 20), outline=(60, 60, 66), width=3)
        screen = tuple(int(c * glow) for c in (190, 205, 230))
        d.rounded_rectangle([pr[0] + 8, pr[1] - 2, pr[2] - 8, pr[3] - 6], radius=6, fill=screen)
        # Timecode: 23:14 → 06:02.
        mins = 23 * 60 + 14 + (6 * 60 + 2 + 24 * 60 - (23 * 60 + 14)) * t
        hh, mm = int(mins // 60) % 24, int(mins % 60)
        d.text((W - 40, 40), f"{hh:02d}:{mm:02d}", font=font("mono", 26), fill=(150, 150, 160), anchor="rt")
        if t < 0.14:
            title_card(im, d, "THE MAST", "a phone · a kitchen · one night", fade=min(1, t / 0.03) if t < 0.1 else (0.14 - t) / 0.04)
        if t > 0.9:
            title_card(im, d, "I slept. I missed nothing.", "HUM 101 · Rowan Hale", fade=(t - 0.9) / 0.06)
        return im

    film((frame(i) for i in range(N)), out / "the-mast.mp4", poster_at=0.48)
    save_text("""
THE MAST — shot list and cut

Odysseus had himself tied to the mast so he could hear the Sirens and not
steer toward them. The film is one night of my phone on the kitchen counter,
tied to nothing but the far end of the apartment.

1. 23:14  Phone face up, lit, on the counter. Hold 20 s. Screen goes dark.
2. 01:40  Dark kitchen. Window. The refrigerator hum is the only sound.
3. 03:02  One notification lights the counter. Nobody comes. It fades.
4. 05:30  First grey in the window. The phone is a black rectangle.
5. 06:02  Cut to the bedroom. I am asleep. Card: "I slept. I missed nothing."

Cut against: the Sirens episode (Odyssey XII, Lectio), 40 s of The Endless
Summer (the bit where they wait out the swell), and the sound of my own
kitchen. Three minutes ten. Defended in seminar 12 April 2027.

What I'd change: the notification shot is too on the nose. Everyone laughed,
which was the point, but the better film doesn't need the laugh.
""", out / "shot-list.txt")


def math110():
    """Drop-In at Washington Street — a motion study."""
    out = OUT / "MATH-110"
    # Quarter-pipe drop-in: angle from vertical θ(t) on a radius R=2.1 m,
    # frictionless-ish pendulum from the coping; 1/30 s frames for 1.6 s.
    R, g = 2.1, 9.81
    dt = 1 / 30
    ts, th, om = [], [], []
    theta, omega = 0.30, 0.9            # leaning in off the coping, already moving
    for i in range(49):
        ts.append(i * dt)
        th.append(theta)
        om.append(omega)
        if theta < math.pi / 2:
            alpha = (g / R) * math.sin(theta) * 0.92   # a little loss to the wheels
            omega += alpha * dt
            theta = min(theta + omega * dt, math.pi / 2)
        else:
            omega *= 0.995                              # the flat: only the wheels slow it
            theta = math.pi / 2
    # arc length along the ramp, then along the flat once the ramp is done
    s, run = [], 0.0
    for i, x in enumerate(th):
        if x < math.pi / 2 or i == 0:
            s.append(R * x)
        else:
            run += om[i] * R * dt
            s.append(R * math.pi / 2 + run)
    v = [R * w for w in om]
    a = [(v[i + 1] - v[i - 1]) / (2 * dt) if 0 < i < len(v) - 1 else 0 for i in range(len(v))]
    a[0], a[-1] = a[1], a[-2]
    imax = max(range(len(a)), key=lambda i: a[i])

    # The plot: three stacked charts.
    im, d = canvas(1600, 1500)
    eyebrow(d, (110, 70), "MATH 110 · a motion study · Washington Street skatepark")
    d.text((110, 110), "Drop-in: position, velocity, acceleration", font=font("serif", 48), fill=INK)
    d.text((110, 175), "49 frames at 1/30 s from a phone clip, radius 2.1 m, wheels on at t = 0", font=font("sans", 22), fill=MUTED)
    rows = [("position along the ramp, s (m)", s, (0, 3.5), (0, 1, 2, 3)),
            ("velocity, v = ds/dt (m/s)", v, (0, 6.5), (0, 2, 4, 6)),
            ("acceleration, a = dv/dt (m/s²)", a, (-1, 10), (0, 3, 6, 9))]
    y = 260
    for title, ys, ylim, yt in rows:
        P = axes(d, (180, y, 1480, y + 300), (0, 1.6), ylim, xticks=[0, 0.4, 0.8, 1.2, 1.6], yticks=yt,
                 xfmt=lambda t: f"{t:.1f} s", ylabel=title)
        polyline(d, P, ts, ys, fill=MARINE, width=4)
        for x, yy in zip(ts[::6], ys[::6]):
            dot(d, P(x, yy), 5, GOLD)
        y += 400
    px, py = axes(d, (180, 1060, 1480, 1360), (0, 1.6), (-1, 10), xticks=[], yticks=[])(ts[imax], a[imax])
    d.line([(px, 1060), (px, 1360)], fill=RUST, width=2)
    d.text((px + 12, 1070), f"greatest acceleration · t = {ts[imax]:.2f} s · {a[imax]:.1f} m/s²", font=font("sans_b", 20), fill=RUST)
    d.text((110, 1420), "The tangent line at each frame is the velocity. Where the velocity's own slope is steepest is where it felt like falling.", font=font("serif_i", 24), fill=INK)
    save(im, out / "drop-in-plot.png")

    # The frame strip: silhouettes on the arc.
    im, d = canvas(1600, 900)
    eyebrow(d, (110, 60), "eight of the forty-nine frames")
    cx, cy, rad = 300, 160, 560
    d.arc([cx - rad, cy - rad, cx + rad, cy + rad], 0, 90, fill=INK, width=6)
    d.rectangle([cx - 40, cy - 14, cx, cy + 14], fill=INK)               # coping
    d.line([(cx + rad, cy + rad), (1500, cy + rad)], fill=INK, width=6)  # flat
    for n, i in enumerate(range(0, 49, 7)):
        ang = th[i]
        x = cx + rad * math.sin(ang)
        yy = cy + rad * (1 - math.cos(ang))
        # a stick figure leaning into the slope
        d.ellipse([x - 10, yy - 92, x + 10, yy - 72], fill=MARINE)
        d.line([(x, yy - 72), (x + 10 * math.sin(ang), yy - 20)], fill=MARINE, width=6)
        d.line([(x - 24, yy - 6), (x + 24, yy - 6)], fill=GOLD, width=8)  # board
        d.text((x, yy + 20), f"f{i:02d}", font=font("mono", 18), fill=MUTED, anchor="mt")
    d.text((110, 820), "Position read off the wall tiles (30 cm each); the phone was on a tripod at the top of the opposite wall.", font=font("sans", 22), fill=MUTED)
    save(im, out / "drop-in-frames.png")

    # The report, three pages.
    p1, d1, y = page("Drop-In at Washington Street", "MATH 110 · The Mathematics of Motion · a motion study")
    y = block(d1, (170, y), "Rowan Hale · defended 9 April 2027", font("sans", 26), MUTED, 1300) + 40
    y = block(d1, (170, y), (
        "One drop-in on the 7-foot quarter at Washington Street, filmed at 30 frames a second, measured against the "
        "wall tiles, and explained with the calculus that governs it. The question the course asked on Day 1 was "
        "\"changing how fast, right now?\" This is the answer for 1.6 seconds of my own life."), font("serif", 30), INK, 1300) + 40
    strip = Image.open(out / "drop-in-frames.png").resize((1310, 737))
    p1.paste(strip, (170, y))
    footer(d1, "1 / 3")
    p2, d2, y = page("The data", "frames 0–48, every third frame shown")
    f = font("mono", 24)
    d2.text((170, y), f"{'frame':>6} {'t (s)':>8} {'s (m)':>8} {'v (m/s)':>9} {'a (m/s²)':>10}", font=font("mono_b", 24), fill=INK)
    y += 44
    for i in range(0, 49, 3):
        d2.text((170, y), f"{i:>6} {ts[i]:>8.3f} {s[i]:>8.3f} {v[i]:>9.3f} {a[i]:>10.3f}", font=f, fill=INK)
        y += 36
    y = block(d2, (170, y + 30), "Velocity is the central difference of position; acceleration the central difference of velocity. The first and last frames borrow their neighbours.", font("serif_i", 26), MUTED, 1300)
    footer(d2, "2 / 3")
    p3, d3, y = page("The calculus", "what the numbers are doing")
    y = block(d3, (170, y), (
        f"s(t) is the distance along the ramp. Its derivative, v(t) = ds/dt, is the slope of the position curve at each "
        f"instant: the speed the wall tiles were going past. Its second derivative, a(t) = dv/dt, is how fast that speed "
        f"was changing. The greatest acceleration came at t = {ts[imax]:.2f} s, {a[imax]:.1f} m/s², about a third of the way "
        f"down, where the ramp is steepest under the wheels and gravity's pull along the surface, g·sin θ, is largest.\n\n"
        f"By the flat the velocity reached {max(v):.1f} m/s and the acceleration fell toward zero: the slope was gone, so "
        f"there was nothing left to change the speed except the wheels.\n\n"
        f"Energy check: ½v² at the bottom should equal g·h with h = 2.1 m, so v ≈ {math.sqrt(2 * 9.81 * 2.1):.1f} m/s. The "
        f"measured {max(v):.1f} m/s is lower by about what the wheels and the wind cost. The difference is the friction I "
        f"could feel and now can also count."), font("serif", 30), INK, 1300)
    plot = Image.open(out / "drop-in-plot.png").resize((1310, 1228))
    p3.paste(plot, (170, y + 30))
    footer(d3, "3 / 3")
    save_pdf([p1, p2, p3], out / "drop-in-report.pdf")


def cs120():
    """Eight Bits from Nothing — a computer from NAND gates."""
    out = OUT / "CS-120"
    im, d = canvas(1600, 1000)
    eyebrow(d, (90, 60), "CS 120 · How Machines Think · from one gate to eight bits")
    d.text((90, 100), "Eight Bits from Nothing", font=font("serif", 54), fill=INK)
    d.text((90, 170), "NAND → NOT, AND, OR, XOR → half adder → full adder → 8-bit ripple-carry adder → a program that runs on it", font=font("sans", 22), fill=MUTED)

    def box(x, y, w, h, label, sub=None, fill=SOFT):
        d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=fill, outline=INK, width=2)
        d.text((x + w / 2, y + h / 2 - (10 if sub else 0)), label, font=font("mono_b", 22), fill=INK, anchor="mm")
        if sub:
            d.text((x + w / 2, y + h / 2 + 18), sub, font=font("mono", 16), fill=MUTED, anchor="mm")

    def wire(a, b):
        d.line([a, (a[0] + (b[0] - a[0]) / 2, a[1]), (a[0] + (b[0] - a[0]) / 2, b[1]), b], fill=MARINE, width=3)

    # Layer 1: the one gate.
    box(90, 300, 150, 80, "NAND", "the only primitive", fill=(236, 230, 212))
    # Layer 2
    for i, (lab, sub) in enumerate([("NOT", "1 NAND"), ("AND", "2 NAND"), ("OR", "3 NAND"), ("XOR", "4 NAND")]):
        box(340, 240 + i * 110, 150, 80, lab, sub)
        wire((240, 340), (340, 280 + i * 110))
    # Layer 3
    box(620, 330, 190, 90, "half adder", "XOR + AND")
    wire((490, 280 + 330), (620, 375)); wire((490, 280 + 110), (620, 375))
    box(620, 470, 190, 90, "full adder", "2 half + OR")
    wire((810, 375), (620, 515)); wire((490, 280 + 220), (620, 515))
    # Layer 4: ripple
    for i in range(8):
        box(920 + i * 78, 420, 66, 70, f"FA{i}", fill=(226, 234, 242))
        if i:
            d.line([(920 + (i - 1) * 78 + 66, 455), (920 + i * 78, 455)], fill=RUST, width=3)
    wire((810, 515), (920, 455))
    d.text((920, 400), "A₀..A₇, B₀..B₇ in", font=font("mono", 16), fill=MUTED, anchor="ld")
    d.text((920 + 8 * 78 - 12, 510), "carry ripples left → right · 9 bits out", font=font("mono", 16), fill=RUST, anchor="rt")
    # Layer 5
    box(920, 620, 612, 120, "8 registers · 16 bytes RAM · 4-instruction control", "LOAD · ADD · STORE · HALT")
    wire((1230, 490), (1230, 620))
    box(920, 800, 612, 90, "swell-adder.bin runs", "Mon 3 + Tue 4 + Wed 2 + Thu 6 + Fri 5 + Sat 8 + Sun 7 = 35", fill=(236, 230, 212))
    wire((1230, 740), (1230, 800))
    d.text((90, 920), "Simulated gate by gate in the course's logic simulator; every box above is built only from the boxes to its left.", font=font("serif_i", 22), fill=INK)
    save(im, out / "eight-bit-schematic.png")
    save_text("""
; swell-adder.asm — adds the week's swell heights (feet) on the eight-bit machine
; Rowan Hale · CS 120 · assembled by hand, 4 instructions, 16 bytes of RAM
;
; op  mnemonic   what it does
; 00  LOAD  a    R0 <- RAM[a]
; 01  ADD   a    R0 <- R0 + RAM[a]   (carry out ripples through FA0..FA7)
; 10  STORE a    RAM[a] <- R0
; 11  HALT

        LOAD  0x08      ; Mon  3
        ADD   0x09      ; Tue  4
        ADD   0x0A      ; Wed  2
        ADD   0x0B      ; Thu  6
        ADD   0x0C      ; Fri  5
        ADD   0x0D      ; Sat  8
        ADD   0x0E      ; Sun  7
        STORE 0x0F      ; total -> 0x0F
        HALT

; data (bytes 0x08–0x0E, from the Scripps buoy, week of 7 June 2027)
; 0x08: 03  0x09: 04  0x0A: 02  0x0B: 06  0x0C: 05  0x0D: 08  0x0E: 07

; run log
; cycle 00  PC=0  LOAD  R0=00000011
; cycle 01  PC=1  ADD   R0=00000111  carry=0
; cycle 02  PC=2  ADD   R0=00001001  carry=0
; cycle 03  PC=3  ADD   R0=00001111  carry=0
; cycle 04  PC=4  ADD   R0=00010100  carry=0   <- the carry ran four places here
; cycle 05  PC=5  ADD   R0=00011100  carry=0
; cycle 06  PC=6  ADD   R0=00100011  carry=0
; cycle 07  PC=7  STORE RAM[0x0F]=00100011     (35)
; cycle 08  PC=8  HALT
;
; 35 feet of swell in a week. The machine does not know what a foot is.
""", out / "swell-adder.txt")


def phys120():
    """A 6'2" Fish, by the Numbers — the board, designed and defended."""
    out = OUT / "PHYS-120"
    im, d = canvas(1600, 1000)
    eyebrow(d, (90, 60), "PHYS 120 · Why Waves Break · plan view, 1:8")
    d.text((90, 100), "A 6'2\" Fish, by the Numbers", font=font("serif", 54), fill=INK)
    # Outline: a fish, nose left. Parametric half-width along length.
    L, Wd = 1200, 300        # px
    ox, oy = 200, 520
    pts_top, pts_bot = [], []
    for i in range(0, 201):
        u = i / 200
        half = Wd / 2 * (math.sin(math.pi * u ** 0.78) ** 0.55) * (1 - 0.18 * max(0, u - 0.85) / 0.15)
        pts_top.append((ox + u * L, oy - half))
        pts_bot.append((ox + u * L, oy + half))
    # swallow tail: notch
    tail = [(ox + L, oy - 95), (ox + L - 110, oy), (ox + L, oy + 95)]
    outline = pts_top + [tail[0], tail[1], tail[2]] + pts_bot[::-1]
    d.polygon(outline, fill=(246, 241, 228), outline=INK)
    d.line(outline + [outline[0]], fill=INK, width=4, joint="curve")
    d.line([(ox, oy), (ox + L - 110, oy)], fill=HAIR, width=2)                    # stringer
    for fx in (ox + L - 330,):
        for sy in (-1, 1):
            d.polygon([(fx, oy + sy * 108), (fx + 90, oy + sy * 100), (fx + 20, oy + sy * 56)], fill=MARINE)  # twin fins (keel-ish)
    # Dimensions.
    def dim(a, b, label, off=0, vertical=False):
        d.line([a, b], fill=RUST, width=2)
        for p in (a, b):
            if vertical:
                d.line([(p[0] - 10, p[1]), (p[0] + 10, p[1])], fill=RUST, width=2)
            else:
                d.line([(p[0], p[1] - 10), (p[0], p[1] + 10)], fill=RUST, width=2)
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        d.text((mid[0] + (off if vertical else 0), mid[1] + (0 if vertical else off)), label, font=font("mono", 20), fill=RUST, anchor="mm" if vertical else "mt")
    dim((ox, oy + 230), (ox + L, oy + 230), "6' 2\"  (1880 mm)", off=12)
    wp = ox + L * 0.47
    dim((wp, oy - Wd / 2), (wp, oy + Wd / 2), "21\"", off=46, vertical=True)
    dim((ox + L * 0.3, oy - 195), (ox + L * 0.3, oy - 195), "", 0)
    d.text((ox + 300, 250), "wide point 2\" ahead of centre · nose 16\" · tail 17½\" · thickness 2⅝\"", font=font("sans", 22), fill=MUTED)
    d.text((ox + 300, 285), "rocker: nose 4¼\" · tail 1⅞\" · volume 38.4 L (Simpson's rule, 13 stations) · twin keels 5¼\" base", font=font("sans", 22), fill=MUTED)
    d.text((90, 880), "Volume by stations, buoyancy for a 72 kg rider in 14 °C water, fin area against the wave speeds measured at the Cove in PHYS 110. Then the foam was cut.", font=font("serif_i", 22), fill=INK)
    save(im, out / "fish-template.png")

    im, d = canvas(1600, 900)
    eyebrow(d, (110, 60), "rocker profile and volume by station")
    P = axes(d, (180, 140, 1480, 420), (0, 74), (0, 5), xticks=[0, 12, 24, 37, 50, 62, 74], yticks=[0, 2, 4],
             xfmt=lambda t: f'{t}"', yfmt=lambda t: f'{t}"', ylabel="rocker (inches above the flat)")
    xs = [i for i in range(0, 75)]
    rock = [4.25 * ((37 - x) / 37) ** 2.6 if x < 37 else 1.875 * ((x - 37) / 37) ** 2.2 for x in xs]
    polyline(d, P, xs, rock, MARINE, 4)
    P2 = axes(d, (180, 540, 1480, 800), (0, 13), (0, 5), xticks=list(range(0, 13)), yticks=[0, 2, 4],
              xfmt=lambda t: f"S{t}", yfmt=lambda t: f"{t} L", ylabel="volume per station (litres), Simpson's rule")
    vols = [0.4, 1.4, 2.5, 3.5, 4.2, 4.6, 4.7, 4.5, 4.0, 3.3, 2.5, 1.8, 1.0]
    for i, vv in enumerate(vols):
        x0, y0 = P2(i + 0.2, vv); x1, y1 = P2(i + 0.8, 0)
        d.rectangle([x0, y0, x1, y1], fill=GOLD)
    d.text((1480, 830), f"total {sum(vols):.1f} L", font=font("sans_b", 22), fill=INK, anchor="rt")
    save(im, out / "rocker-and-volume.png")

    p1, d1, y = page("Design calculations", "PHYS 120 · a shaped board with design calculations, defended")
    y = block(d1, (170, y), "Rowan Hale · defended 1 December 2027 · shaped in WKSP 102", font("sans", 26), MUTED, 1300) + 30
    y = block(d1, (170, y), (
        "1. Volume. Thirteen cross-sections at 6-inch stations, each area from the template's width and the foil's "
        "thickness, summed by Simpson's rule: V ≈ (h/3)[A₀ + 4A₁ + 2A₂ + … + A₁₂] = 38.4 L.\n\n"
        "2. Buoyancy. 38.4 L of foam, glass and resin displaces 38.4 kg of seawater (ρ = 1,025 kg/m³ at 14 °C) and weighs "
        "3.1 kg, so the board holds 35.3 kg before I touch it. A 72 kg rider sits the board 2.0 L under at rest, which is "
        "the paddling depth I measured on the old board and wanted to keep.\n\n"
        "3. Fins. The Cove's waves in PHYS 110 ran 4.1–6.3 m/s on the face. A twin keel of 5¼\" base and 4½\" depth gives "
        "about 95 cm² a side; at 5 m/s and 8° of yaw that is roughly 110 N of lateral force a side, enough to hold a line "
        "on a waist-high wall and let go on a cutback, which is what a fish is for.\n\n"
        "4. Rocker. 4¼\" nose, 1⅞\" tail, a continuous curve so the board paddles flat and still turns. Less rocker than "
        "the old board by ¾\", which is why it paddles into waves a second earlier.\n\n"
        "Defended before the PHYS 120 panel with the board on sawhorses. Asked: what would you change? More tail rocker "
        "for the winter. The numbers say so and now so does the riding."), font("serif", 30), INK, 1300)
    footer(d1, "1 / 2")
    p2, d2, y = page("The stations", "areas and the Simpson weights")
    f = font("mono", 24)
    d2.text((170, y), f"{'station':>8} {'x (in)':>8} {'width':>8} {'thick':>8} {'area cm²':>10} {'weight':>7} {'contrib L':>10}", font=font("mono_b", 24), fill=INK)
    y += 44
    widths = [3.0, 9.5, 14.0, 17.2, 19.4, 20.6, 21.0, 20.7, 19.6, 17.8, 15.5, 13.0, 10.5]
    thick = [0.6, 1.2, 1.7, 2.1, 2.4, 2.55, 2.625, 2.55, 2.35, 2.0, 1.6, 1.2, 0.8]
    for i in range(13):
        area = widths[i] * thick[i] * 0.72 * 6.4516
        wgt = 1 if i in (0, 12) else (4 if i % 2 else 2)
        d2.text((170, y), f"{i:>8} {i * 6:>8} {widths[i]:>8.1f} {thick[i]:>8.2f} {area:>10.1f} {wgt:>7} {area * wgt * 15.24 / 3 / 1000:>10.2f}", font=f, fill=INK)
        y += 36
    rv = Image.open(out / "rocker-and-volume.png").resize((1310, 737))
    p2.paste(rv, (170, y + 40))
    footer(d2, "2 / 2")
    save_pdf([p1, p2], out / "design-calculations.pdf")


def wksp102():
    """The Fish, Glassed — the shipped board, shown."""
    out = OUT / "WKSP-102"
    W, H = 1600, 1067
    im, d = canvas(W, H, (74, 62, 50))
    # Shop wall: boards, tools as shapes.
    for i in range(0, W, 64):
        d.rectangle([i, 0, i + 58, 620], fill=(84 + (i // 64 % 3) * 6, 70 + (i // 64 % 2) * 5, 56))
    for x in (220, 300, 360, 1180, 1260):
        d.rounded_rectangle([x, 80, x + 28, 420], radius=14, fill=(50, 44, 40))
    d.rectangle([0, 620, W, H], fill=(96, 84, 70))       # floor
    for i in range(0, W, 180):
        d.line([(i, 620), (i - 200, H)], fill=(88, 77, 64), width=3)
    # Sawhorses.
    for sx in (430, 1050):
        d.polygon([(sx, 640), (sx + 140, 640), (sx + 190, 980), (sx + 150, 980), (sx + 110, 690), (sx + 30, 690), (sx - 10, 980), (sx - 50, 980)], fill=(60, 52, 44))
        d.rectangle([sx - 30, 626, sx + 170, 650], fill=(120, 100, 80))
    # The board, in perspective-ish plan, resin glossy.
    L, Wd = 1260, 250
    ox, oy = 180, 560
    pts = []
    for i in range(0, 201):
        u = i / 200
        half = Wd / 2 * (math.sin(math.pi * u ** 0.78) ** 0.55) * (1 - 0.18 * max(0, u - 0.85) / 0.15)
        pts.append((ox + u * L, oy - half))
    bot = [(x, 2 * oy - y) for x, y in pts]
    tail = [(ox + L, oy - 80), (ox + L - 95, oy), (ox + L, oy + 80)]
    outline = pts + tail + bot[::-1]
    d.polygon(outline, fill=(232, 222, 196))
    d.line(outline + [outline[0]], fill=(150, 130, 100), width=3, joint="curve")
    d.polygon([(ox + 260, oy - 60), (ox + 700, oy - 8), (ox + 700, oy + 8), (ox + 260, oy + 60)], fill=(220, 160, 90))  # resin tint panel
    d.line([(ox + 40, oy), (ox + L - 95, oy)], fill=(190, 175, 150), width=3)
    # gloss
    gloss = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(gloss)
    gd.polygon([(ox + 120, oy - 90), (ox + 1000, oy - 30), (ox + 1000, oy - 10), (ox + 120, oy - 60)], fill=140)
    gloss = gloss.filter(ImageFilter.GaussianBlur(18))
    im.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), gloss)
    d = ImageDraw.Draw(im)
    for sy in (-1, 1):
        fx = ox + L - 300
        d.polygon([(fx, oy + sy * 92), (fx + 80, oy + sy * 86), (fx + 18, oy + sy * 48)], fill=(50, 70, 90))
    # Exhibition tag hanging off the nose.
    d.rectangle([ox - 40, oy + 120, ox + 180, oy + 230], fill=PAPER)
    d.line([(ox + 30, oy + 20), (ox + 50, oy + 120)], fill=(200, 200, 200), width=2)
    d.text((ox - 24, oy + 132), "THE FISH, GLASSED", font=font("mono", 15), fill=GOLD)
    d.text((ox - 24, oy + 156), "Rowan Hale · 6'2\" × 21\"", font=font("sans", 17), fill=INK)
    d.text((ox - 24, oy + 182), "Year-End Exhibition 2028", font=font("sans", 15), fill=MUTED)
    im = grain(vignette(im, 0.45), 14)
    save(im, out / "fish-glassed.jpg", 78)

    im, d = canvas(1200, 700)
    d.rectangle([0, 0, 1199, 699], outline=HAIR, width=6)
    eyebrow(d, (90, 80), "San Diego Institute of Technology · The Workshop · year-end exhibition")
    d.text((90, 140), "The Fish, Glassed", font=font("serif", 60), fill=INK)
    d.text((90, 230), "Rowan Hale · Semester 2", font=font("sans", 26), fill=MUTED)
    y = block(d, (90, 300), ("Polyurethane blank, 4 oz + 4 oz deck, 4 oz bottom, polyester resin with a tint panel. 6'2\" × 21\" × 2⅝\", 38.4 L. "
                              "Shaped from the template defended in PHYS 120, glassed over three weeks in the Workshop, sanded twice because the first time was not finished.\n\n"
                              "Ridden the morning after the show at Tourmaline. It paddles a second earlier than the old board, as the rocker said it would."),
              font("serif", 26), INK, 1020)
    d.text((90, 600), "shown 20 May 2028 · touch it", font=font("mono", 20), fill=GOLD)
    save(im, out / "exhibition-card.png")


ESSAY_FINAL = """
# Leave It in the Kitchen

My phone sleeps in the kitchen now. It has for seven months. People ask whether I miss it at night, and the honest answer is that I cannot remember what I was doing with it there, which is the whole argument.

The case for keeping a phone by the bed is built on one word: in case. In case someone calls. In case something happens. In case I wake at three and need to know the time, the surf, the news, the score. I kept the phone there for ten years on the strength of that word and it never once earned its keep. Nobody called. The things that happened waited until morning, as things do. And the three-a.m. check was never a check. It was an hour.

Odysseus knew what he was dealing with. He did not resolve to be strong when the Sirens sang. He had himself tied up beforehand, by people he trusted, and told them to ignore whatever he said once the singing started. The design assumed he would fail, and it worked because of that assumption, not in spite of it. The kitchen is my mast. The forty feet of hallway is the rope. At midnight I am not a person who can be trusted with a glowing rectangle, and I have stopped pretending otherwise.

Here is what changed. I sleep about forty minutes longer, by the watch I started wearing for the purpose. I read in bed, a paper book, which I had not done since I was sixteen. I wake up and lie there for a while, thinking about nothing in particular, which turns out to be where most of my ideas for the Workshop come from. The morning check still happens. It happens standing in the kitchen with coffee, and it takes four minutes, because standing is not a position you scroll in.

The objection is emergencies, so let me take it seriously. In seven months there has been one: my mother in the hospital at two in the morning. The call came to the kitchen. The kitchen is forty feet away. I heard it on the second ring, which is one ring later than I would have heard it from the nightstand. That is the entire cost of the mast, one ring, and I paid it gladly for two hundred nights of sleep.

I am not telling anyone to do this. I am telling you that the thing you are sure you need by the bed is something you have never once needed by the bed, and that the test is cheap: one week, forty feet, a book. If I am wrong you can have it back. You will not want it back.
"""

ESSAY_DRAFT = """
# Why I Think You Should Probably Keep Your Phone Out of the Bedroom

I think that it is probably important to note that a lot of people keep their phones next to their bed, and I used to be one of them, and honestly I think it was kind of a problem for me, so in this essay I want to argue that it's better to keep it somewhere else, like the kitchen.

The main reason people say they need their phone by the bed is in case of emergencies. I understand this. I used to think this too. But if you actually think about it, how many emergencies have there been? For me the answer is basically none. Most of the time when I picked up my phone in the night it was not because of an emergency, it was just because it was there, and then I would end up scrolling for a long time, sometimes like an hour, which obviously is not good for sleep.

In HUM 101 we read the part of the Odyssey with the Sirens, where Odysseus gets tied to the mast so he can hear them but not go to them. I think this is kind of a good metaphor for the phone situation. Basically he knew he would be weak so he set things up ahead of time so that his weakness would not matter. I think that's smart, and I think that's basically what putting your phone in the kitchen is. It's like tying yourself to the mast.

Since I started doing this I have noticed that I sleep better and I read more books. I also think I have more ideas in the morning, although it is hard to prove that. The morning check still happens but it's shorter because I'm standing up.

Some people might say what about emergencies, and I did have one, when my mom went to the hospital. But the phone rang in the kitchen and I heard it anyway, so it was fine. It was maybe one ring later.

In conclusion, I think that if you try keeping your phone in the kitchen for a week you will probably find that you don't really need it by the bed, and that you sleep better. I'm not saying everyone has to do it, but I think it's worth trying, and I think Odysseus would agree.
"""


def rhet110():
    """Four Essays, Drafts Beside Finals."""
    out = OUT / "RHET-110"
    save_text(ESSAY_FINAL, out / "essay-2-final.txt")
    save_text(ESSAY_DRAFT, out / "essay-2-draft-1.txt")
    # Two pages, draft left, final right.
    pages = []
    for n, (dt, ft) in enumerate([(ESSAY_DRAFT, ESSAY_FINAL)]):
        im, d, y = page("Essay 2 · the argument", "RHET 110 · Writing That Lands · drafts beside finals")
        d.text((170, y), "DRAFT 1 · 14 February 2028 · 512 words", font=font("mono", 18), fill=RUST)
        d.text((870, y), "FINAL · 4 March 2028 · 496 words", font=font("mono", 18), fill=MARINE)
        y += 36
        f = font("serif", 19)
        yl = yr = y
        for para in dt.strip().split("\n\n")[1:]:
            yl = block(d, (170, yl), para, f, INK, 620, 1.3) + 14
        for para in ft.strip().split("\n\n")[1:]:
            yr = block(d, (870, yr), para, f, INK, 620, 1.3) + 14
        d.line([(830, y - 40), (830, max(yl, yr))], fill=HAIR, width=2)
        y2 = max(yl, yr) + 30
        block(d, (170, y2), "What the line-edit took out: \"I think that,\" \"probably,\" \"kind of,\" \"basically,\" \"in conclusion.\" What it put in: the watch, the forty feet, the one ring. The argument did not change. The sentences stopped apologising for it.", font("serif_i", 22), MUTED, 1300)
        footer(d, "the distance between the drafts is the point · 1 / 1")
        pages.append(im)
    save_pdf(pages, out / "drafts-beside-finals.pdf")


def math220():
    """Forty Calls — public swell forecasts, scored."""
    out = OUT / "MATH-220"
    rnd = random.Random(220)
    calls = []
    for i in range(40):
        p = round(min(0.95, max(0.05, rnd.betavariate(2.2, 2.0))), 2)
        hit = 1 if rnd.random() < (0.15 + 0.7 * p) else 0
        calls.append((i + 1, p, hit))
    brier = sum((p - h) ** 2 for _, p, h in calls) / 40
    im, d = canvas(1600, 1000)
    eyebrow(d, (110, 60), "MATH 220 · Forecasting & Games · forty public calls for the Cove")
    d.text((110, 100), f"Forty Calls · Brier score {brier:.2f}", font=font("serif", 50), fill=INK)
    d.text((110, 168), "Each call: \"waist-high or better at La Jolla Cove at 7 a.m. on <day>\", posted 48 hours ahead with a probability. Scored against what the morning showed.", font=font("sans", 20), fill=MUTED)
    P = axes(d, (180, 260, 1060, 760), (0, 41), (0, 1), xticks=[1, 10, 20, 30, 40], yticks=[0, 0.25, 0.5, 0.75, 1],
             yfmt=lambda t: f"{t:.2f}", ylabel="probability I gave")
    for n, p, h in calls:
        dot(d, P(n, p), 8, MARINE if h else PAPER, outline=MARINE)
    d.text((180, 790), "● happened   ○ did not", font=font("sans", 20), fill=MUTED)
    # Calibration inset.
    P2 = axes(d, (1180, 300, 1480, 600), (0, 1), (0, 1), xticks=[0, 0.5, 1], yticks=[0, 0.5, 1], ylabel="calibration")
    d.line([P2(0, 0), P2(1, 1)], fill=HAIR, width=2)
    bins = {}
    for _, p, h in calls:
        b = min(int(p * 4), 3)
        bins.setdefault(b, []).append(h)
    for b, hs in sorted(bins.items()):
        x = (b + 0.5) / 4
        dot(d, P2(x, sum(hs) / len(hs)), 9, GOLD)
        d.text((P2(x, sum(hs) / len(hs))[0], P2(x, sum(hs) / len(hs))[1] - 16), f"n={len(hs)}", font=font("mono", 14), fill=MUTED, anchor="mb")
    d.text((1180, 640), "Overconfident above 0.75: I called 9 sure things and 6 came.", font=font("sans", 18), fill=RUST)
    d.text((110, 880), "Better than guessing (0.25) and worse than the buoy model (0.14). The gap is the part of the morning I cannot see from the night before.", font=font("serif_i", 22), fill=INK)
    save(im, out / "forty-calls.png")
    lines = ["# Forty Calls — the log", "# call, posted, for, p, happened, brier", ""]
    import datetime as dt
    day = dt.date(2028, 9, 4)
    for n, p, h in calls:
        day += dt.timedelta(days=rnd.choice([1, 2, 2, 3]))
        lines.append(f"{n:>2}, {(day - dt.timedelta(days=2)).isoformat()}, {day.isoformat()} 07:00, {p:.2f}, {'yes' if h else 'no '}, {(p - h) ** 2:.3f}")
    lines += ["", f"mean Brier {brier:.3f} · guessing 0.250 · the buoy model 0.140",
              "", "Rule I set on Day 3 and kept: post before looking at the model. Score every call, including the embarrassing ones. Never delete a call."]
    save_text("\n".join(lines), out / "forecast-log.txt")


def sig201():
    """Ninety Seconds at Sunset Cliffs — a short piece released into a feed."""
    out = OUT / "SIG-201"
    W, H, N = 960, 540, 24 * 8
    rnd = random.Random(201)
    cliff = [(0, 390)] + [(x, 390 - 40 * math.sin(x / 90) - 30 * math.sin(x / 37) - (x / 12 if x > 600 else 0)) for x in range(0, W + 1, 20)] + [(W, 540), (0, 540)]
    birds = [(rnd.randint(100, 800), rnd.randint(80, 220), rnd.uniform(0.6, 1.4)) for _ in range(5)]

    def frame(i):
        t = i / N
        im, d = canvas(W, H)
        top = tuple(int(a + (b - a) * t) for a, b in zip((250, 170, 90), (40, 30, 70)))
        mid = tuple(int(a + (b - a) * t) for a, b in zip((255, 120, 60), (120, 50, 70)))
        for y in range(0, 330):
            u = y / 330
            c = tuple(int(top[k] + (mid[k] - top[k]) * u) for k in range(3))
            d.line([(0, y), (W, y)], fill=c)
        sun_y = 150 + 190 * t
        d.ellipse([460 - 46, sun_y - 46, 460 + 46, sun_y + 46], fill=(255, 220, 170))
        # Sea.
        sea = tuple(int(a + (b - a) * t) for a, b in zip((70, 110, 140), (24, 36, 60)))
        d.rectangle([0, 330, W, H], fill=sea)
        for k in range(12):
            yy = 334 + k * 8 + (i % 8) * 0.3
            d.line([(0, yy), (W, yy)], fill=tuple(min(255, c + 18) for c in sea), width=1)
        # Sun path on water.
        if sun_y < 330:
            d.rectangle([440, 332, 480, 400], fill=tuple(min(255, int(c * 0.6 + 90)) for c in sea))
        d.polygon(cliff, fill=(30, 24, 24))
        for bx, by, sp in birds:
            x = (bx + i * sp) % (W + 40) - 20
            d.line([(x - 8, by), (x, by - 5), (x + 8, by)], fill=(40, 30, 30), width=2)
        if t < 0.14:
            title_card(im, d, "NINETY SECONDS AT SUNSET CLIFFS", "a short piece · released 14 March 2029", fade=min(1, t / 0.03) if t < 0.1 else (0.14 - t) / 0.04)
        if t > 0.9:
            title_card(im, d, "SIG 201 · Rowan Hale", "how it moved: 11,400 views in 21 days", fade=(t - 0.9) / 0.06)
        return im

    film((frame(i) for i in range(N)), out / "ninety-seconds.mp4", poster_at=0.45)
    # How it moved.
    im, d = canvas(1600, 900)
    eyebrow(d, (110, 60), "SIG 201 · How Images Move · the written account's one chart")
    d.text((110, 100), "How it moved", font=font("serif", 50), fill=INK)
    views = [120, 340, 2900, 2100, 1400, 900, 700, 650, 520, 400, 350, 300, 260, 230, 200, 180, 170, 150, 140, 130, 120]
    P = axes(d, (180, 220, 1480, 760), (1, 21), (0, 3200), xticks=[1, 3, 7, 14, 21], yticks=[0, 1000, 2000, 3000],
             xfmt=lambda t: f"day {t}", ylabel="views per day")
    polyline(d, P, list(range(1, 22)), views, MARINE, 4)
    for x, yv, note in [(3, 2900, "a local surf account reposted it, 7:40 a.m."), (7, 700, "the comments turned to the parking"), (14, 230, "a teacher used it in class; I found out later")]:
        dot(d, P(x, yv), 8, GOLD)
        d.text((P(x, yv)[0] + 14, P(x, yv)[1] - 10), note, font=font("sans", 18), fill=INK)
    d.text((110, 800), f"{sum(views):,} views · 61% watched to the end · median watch 71 s of 90. It moved because of one repost, not because of anything I did after posting.", font=font("serif_i", 22), fill=INK)
    save(im, out / "how-it-moved.png")


def wksp202():
    """A Carburetor for a 1978 CB400 — a client project, shipped."""
    out = OUT / "WKSP-202"
    W, H = 1600, 1067
    im, d = canvas(W, H, (40, 70, 110))
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(44, 76, 118), width=2)
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(44, 76, 118), width=2)
    parts = [
        ("carburetor body", (200, 220, 560, 560), "rounded"), ("float bowl", (640, 300, 900, 520), "rounded"),
        ("float", (960, 330, 1100, 420), "ellipse"), ("main jet #105", (1180, 300, 1210, 400), "rect"),
        ("pilot jet #38", (1260, 300, 1282, 380), "rect"), ("needle", (1340, 260, 1352, 460), "rect"),
        ("slide", (240, 640, 380, 860), "rounded"), ("spring", (440, 640, 480, 880), "spring"),
        ("bowl gasket", (560, 660, 820, 860), "ring"), ("o-rings ×4", (900, 700, 1160, 780), "orings"),
        ("drain screw", (1240, 700, 1270, 790), "rect"), ("choke lever", (1320, 640, 1500, 680), "rect"),
    ]
    metal, dark = (176, 178, 170), (120, 122, 118)
    for name, (x0, y0, x1, y1), kind in parts:
        if kind == "rounded":
            d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=metal, outline=dark, width=3)
            d.ellipse([x0 + 40, y0 + 40, x1 - 40, y1 - 40], fill=dark)
            d.ellipse([x0 + 70, y0 + 70, x1 - 70, y1 - 70], fill=(60, 60, 60))
        elif kind == "ellipse":
            d.ellipse([x0, y0, x1, y1], fill=(220, 215, 200), outline=dark, width=3)
        elif kind == "rect":
            d.rectangle([x0, y0, x1, y1], fill=(200, 170, 90), outline=dark, width=2)
        elif kind == "spring":
            for k in range(12):
                yy = y0 + k * 20
                d.line([(x0, yy), (x1, yy + 10)], fill=metal, width=5)
        elif kind == "ring":
            d.ellipse([x0, y0, x1, y1], outline=(30, 30, 30), width=14)
        elif kind == "orings":
            for k in range(4):
                d.ellipse([x0 + k * 68, y0, x0 + k * 68 + 60, y1], outline=(30, 30, 30), width=9)
        tag_y = y1 + 14
        d.rectangle([x0, tag_y, x0 + 12 + d.textlength(name, font=font("sans", 18)), tag_y + 30], fill=PAPER)
        d.text((x0 + 6, tag_y + 6), name, font=font("sans", 18), fill=INK)
    d.rectangle([60, 40, 760, 130], fill=PAPER)
    d.text((80, 52), "CB400 (1978) · Keihin carb #2 · stripped, ultrasonic, rebuilt", font=font("sans_b", 24), fill=INK)
    d.text((80, 90), "client: M. Ortega · brief: starts cold, idles at 1,100 · deadline 20 Nov 2028", font=font("sans", 20), fill=MUTED)
    im = grain(vignette(im, 0.4), 12)
    save(im, out / "carb-bench.jpg", 78)
    save_text("""
CLIENT BRIEF — WKSP 202, client project

Client: Marisol Ortega (a neighbour; found me through the shop)
Machine: 1978 Honda CB400T, 31,000 miles, sat four years
Complaint: will not start cold; when it does, idles at 2,500 and dies when the choke comes off
Brief: "Make it start on the second kick and idle like a motorcycle." Budget $180 in parts. Deadline 20 November 2028 (her brother's visit).

What I did
- Week 1: pulled both carbs, found varnish in the pilot circuits and a float set 3 mm high on #2. Photographed every step. Agreed the brief in writing; she signed it.
- Week 2: ultrasonic clean, new jets (#38 pilot, #105 main, as stock), bowl gaskets, o-rings, float needles. Set float height 14.5 mm with the gauge from ENGR 310. Synced with the manometer I built in PHYS 120.
- Week 3: idle 1,100 warm. Starts on the second kick cold, every morning for a week, logged.

Delivered 17 November. $164 in parts, 11 hours. She paid for the parts and brought tamales. The portfolio review before the Declaration used this as the Design piece: a brief, a deadline, a thing that works for someone else.

Sign-off
  "Second kick, like you said. Idles like a motorcycle." — M. Ortega, 17 Nov 2028
""", out / "client-brief.txt")


def art310():
    """Tide Clock — an interactive piece on a café counter."""
    out = OUT / "ART-310"
    W, H = 1600, 1067
    im, d = canvas(W, H, (150, 112, 74))
    for i in range(0, W, 120):
        d.rectangle([i, 0, i + 112, H], fill=(146 + (i // 120 % 2) * 10, 108 + (i // 120 % 3) * 4, 70))
    # Device: a small round dial in a wooden puck.
    cx, cy, r = 700, 520, 250
    d.ellipse([cx - r - 24, cy - r - 24, cx + r + 24, cy + r + 24], fill=(60, 44, 32))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PAPER)
    _dial(d, cx, cy, r)
    # A coffee cup.
    d.ellipse([1120, 420, 1420, 720], fill=(238, 236, 230))
    d.ellipse([1150, 450, 1390, 690], fill=(70, 44, 30))
    d.ellipse([1180, 470, 1360, 670], fill=(96, 62, 40))
    # A pastry plate edge.
    d.ellipse([-120, 760, 420, 1100], fill=(236, 232, 224))
    im = grain(vignette(im, 0.5), 12)
    save(im, out / "tide-clock-counter.jpg", 78)
    im, d = canvas(1200, 1200)
    _dial(d, 600, 600, 520, big=True)
    save(im, out / "tide-clock-face.png")
    save_text("""
TIDE CLOCK — two weeks on the counter at Lazy Hummingbird, Newport Ave

What it is: a dial the size of a saucer. One hand is the tide right now, the arc behind it is today's curve, and one word in the middle says GO or WAIT: whether the reef at the end of the street is worth the walk in the next two hours. No screen glow, no phone, no account. It reads the NOAA tide table once a day and the buoy once an hour.

Who it's for: the barista, who gets twenty minutes at 7 a.m. and no time to open an app. She was the first user and the brief came from watching her check her phone with wet hands.

Observations (14 days, 6:30–9:30 a.m., sitting at the end of the counter with a notebook)
- 212 people looked at it for more than two seconds.
- 61 touched it (it does nothing when touched; three people tried to turn the dial).
- 38 asked the barista what it was. She explained it 38 times. By day 5 she had a two-sentence version.
- 9 regulars started checking it on the way in and said so.
- 2 people photographed it. One asked to buy one.
- Day 3: moved it 40 cm left, out of the line of the pastry case. Looks tripled.
- Day 8: changed WAIT to NOT YET after the barista said WAIT sounded like an order. Nobody has objected to NOT YET.
- Day 11: the word GO at 7:05 and four people left without ordering. The owner laughed. We talked about it. It stays.

What I learned: the piece works when it answers the one question the person actually has, in the second they have for it. Everything I added in the first prototype (wind, water temperature, a swell arrow) was for me, not for her, and came off.

Defended 2 May 2029 with the clock on the table and the barista in the room.
""", out / "observations.txt")


def _dial(d, cx, cy, r, big=False):
    s = r / 250
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PAPER, outline=INK, width=int(4 * s))
    # today's tide curve around the rim (24 h) as a ring whose radius varies.
    pts = []
    for k in range(0, 361, 3):
        a = math.radians(k - 90)
        hgt = 0.5 + 0.5 * math.sin(math.radians(k) * 2 - 0.9) * 0.9
        rr = r * (0.70 + 0.16 * hgt)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.line(pts + [pts[0]], fill=(200, 212, 222), width=int(14 * s), joint="curve")
    for k in range(0, 24):
        a = math.radians(k * 15 - 90)
        x0, y0 = cx + r * 0.92 * math.cos(a), cy + r * 0.92 * math.sin(a)
        x1, y1 = cx + r * 0.98 * math.cos(a), cy + r * 0.98 * math.sin(a)
        d.line([(x0, y0), (x1, y1)], fill=INK, width=int(3 * s))
        if k % 6 == 0:
            d.text((cx + r * 0.84 * math.cos(a), cy + r * 0.84 * math.sin(a)), ["00", "06", "12", "18"][k // 6], font=font("mono", int(16 * s)), fill=MUTED, anchor="mm")
    # the hand: now = 07:10
    a = math.radians((7 + 10 / 60) * 15 - 90)
    d.line([(cx, cy), (cx + r * 0.86 * math.cos(a), cy + r * 0.86 * math.sin(a))], fill=GOLD, width=int(8 * s))
    dot(d, (cx, cy), int(10 * s), INK)
    d.text((cx, cy - r * 0.22), "GO", font=font("serif_b", int(110 * s)), fill=INK, anchor="mm")
    d.text((cx, cy + r * 0.26), "low 2.1 ft at 08:14", font=font("mono", int(20 * s)), fill=MUTED, anchor="mm")
    d.text((cx, cy + r * 0.38), "the reef shows for 2 h", font=font("mono", int(20 * s)), fill=MUTED, anchor="mm")
    if big:
        d.text((cx, cy + r * 0.56), "TIDE CLOCK · Newport Ave", font=font("mono", int(16 * s)), fill=GOLD, anchor="mm")


def engr310():
    """A Fin Box That Doesn't Crack — drawings, tolerances, a load test."""
    out = OUT / "ENGR-310"
    im, d = canvas(1600, 1100)
    # Title block.
    d.rectangle([40, 40, 1560, 1060], outline=INK, width=3)
    d.rectangle([1100, 900, 1560, 1060], outline=INK, width=3)
    d.text((1120, 915), "FIN BOX, REDESIGN · Rev C", font=font("sans_b", 22), fill=INK)
    d.text((1120, 950), "ENGR 310 · Design & Fabrication · R. Hale", font=font("sans", 18), fill=MUTED)
    d.text((1120, 980), "material: glass-filled nylon, cast · scale 1:1 · mm", font=font("sans", 18), fill=MUTED)
    d.text((1120, 1010), "general tolerance ±0.2 unless noted · 11 Dec 2029", font=font("sans", 18), fill=MUTED)
    lw = 3

    def dimh(x0, x1, y, label):
        d.line([(x0, y), (x1, y)], fill=RUST, width=2)
        d.line([(x0, y - 8), (x0, y + 8)], fill=RUST, width=2); d.line([(x1, y - 8), (x1, y + 8)], fill=RUST, width=2)
        d.text(((x0 + x1) / 2, y - 6), label, font=font("mono", 18), fill=RUST, anchor="mb")

    def dimv(x, y0, y1, label):
        d.line([(x, y0), (x, y1)], fill=RUST, width=2)
        d.line([(x - 8, y0), (x + 8, y0)], fill=RUST, width=2); d.line([(x - 8, y1), (x + 8, y1)], fill=RUST, width=2)
        d.text((x + 10, (y0 + y1) / 2), label, font=font("mono", 18), fill=RUST, anchor="lm")
    # Top view: the slot.
    ox, oy = 120, 140
    d.text((ox, oy - 50), "TOP", font=font("sans_b", 20), fill=INK)
    d.rectangle([ox, oy, ox + 560, oy + 120], outline=INK, width=lw)
    d.rectangle([ox + 40, oy + 44, ox + 520, oy + 76], fill=SOFT, outline=INK, width=lw)
    for x in (ox + 110, ox + 450):
        d.ellipse([x - 9, oy + 60 - 9, x + 9, oy + 60 + 9], outline=INK, width=lw)
    dimh(ox, ox + 560, oy - 20, "140.0")
    dimh(ox + 40, ox + 520, oy + 150, "120.0 ±0.1")
    dimv(ox + 580, oy, oy + 120, "30.0")
    dimv(ox + 600, oy + 44, oy + 76, "8.0 +0.05/−0")
    # Section A-A: the change — a radiused root and a flange.
    sx, sy = 120, 440
    d.text((sx, sy - 50), "SECTION A–A  (the crack started here on Rev A: a sharp inside corner)", font=font("sans_b", 20), fill=INK)
    body = [(sx, sy), (sx + 560, sy), (sx + 560, sy + 60), (sx + 470, sy + 60), (sx + 470, sy + 190), (sx + 90, sy + 190), (sx + 90, sy + 60), (sx, sy + 60)]
    d.polygon(body, outline=INK, fill=SOFT)
    d.line(body + [body[0]], fill=INK, width=lw)
    # hatch
    for k in range(-200, 600, 18):
        d.line([(sx + k, sy), (sx + k + 60, sy + 60)], fill=HAIR, width=1)
    d.arc([sx + 90, sy + 150, sx + 170, sy + 230], 180, 270, fill=RUST, width=4)
    d.text((sx + 180, sy + 200), "R4.0 ±0.2  (was R0 — sharp)", font=font("mono", 18), fill=RUST)
    d.rectangle([sx + 200, sy + 70, sx + 360, sy + 180], outline=INK, width=lw, fill=PAPER)
    d.text((sx + 280, sy + 125), "slot", font=font("mono", 16), fill=MUTED, anchor="mm")
    dimv(sx + 590, sy, sy + 190, "32.0")
    dimv(sx + 610, sy, sy + 60, "6.0 flange")
    dimh(sx, sx + 560, sy + 270, "140.0 flange (was 100)")
    # Side view.
    vx, vy = 820, 140
    d.text((vx, vy - 50), "SIDE", font=font("sans_b", 20), fill=INK)
    d.polygon([(vx, vy + 60), (vx + 600, vy + 60), (vx + 600, vy + 120), (vx + 520, vy + 250), (vx + 80, vy + 250), (vx, vy + 120)], outline=INK, fill=SOFT)
    d.line([(vx, vy + 60), (vx + 600, vy + 60), (vx + 600, vy + 120), (vx + 520, vy + 250), (vx + 80, vy + 250), (vx, vy + 120), (vx, vy + 60)], fill=INK, width=lw)
    d.text((vx + 300, vy + 160), "tapered walls 8° · draft for the mould", font=font("mono", 18), fill=MUTED, anchor="mm")
    dimh(vx, vx + 600, vy + 40, "140.0")
    dimv(vx + 620, vy + 60, vy + 250, "32.0")
    # Notes.
    y = block(d, (820, 450), "NOTES\n1. All inside corners R4.0 min. The Rev A failure (410 N) began at the sharp slot root; the fracture face showed it.\n2. Flange widened 100 → 140 to spread the fin's lever load into the deck glass.\n3. Cast in two-part silicone from the Workshop's 3D-printed master; vacuum degassed. Seam on the non-bearing face.\n4. Tested to failure on the bench rig (see load-test.png). Design load 650 N = a 72 kg rider's worst cutback, ×1.5.\n5. Three castings tested: 940, 980, 1,010 N. All failed in the wall, none at the root.", font("sans", 20), INK, 700, 1.4)
    save(im, out / "fin-box-drawing.png")
    im, d = canvas(1600, 900)
    eyebrow(d, (110, 60), "bench test · lever arm 110 mm · 2 mm/min")
    d.text((110, 100), "Load to failure", font=font("serif", 50), fill=INK)
    P = axes(d, (180, 200, 1480, 760), (0, 12), (0, 1100), xticks=[0, 2, 4, 6, 8, 10, 12], yticks=[0, 250, 500, 750, 1000],
             xfmt=lambda t: f"{t} mm", yfmt=lambda t: f"{t} N", ylabel="force at the fin tip")
    xs = [i / 10 for i in range(0, 121)]
    rev_a = [(410 * (1 - math.exp(-x / 1.4)) * 1.25) if x < 3.2 else None for x in xs]
    polyline(d, P, [x for x, y in zip(xs, rev_a) if y], [y for y in rev_a if y], RUST, 4)
    d.text((P(3.3, 420)[0], P(3.3, 420)[1]), "Rev A · cracked at the slot root · 410 N", font=font("sans_b", 18), fill=RUST)
    for k, (fail, col) in enumerate([(940, (120, 150, 180)), (980, MARINE), (1010, (60, 100, 140))]):
        ys = [fail * (1 - math.exp(-x / 3.8)) * 1.12 if x < 9.5 + k * 0.6 else None for x in xs]
        polyline(d, P, [x for x, y in zip(xs, ys) if y], [y for y in ys if y], col, 4)
    d.text((P(10.2, 990)[0], P(10.2, 990)[1]), "Rev C × 3 · 940 / 980 / 1,010 N", font=font("sans_b", 18), fill=MARINE)
    d.line([P(0, 650), P(12, 650)], fill=GOLD, width=3)
    d.text((P(0.2, 650)[0], P(0.2, 650)[1] - 8), "design load 650 N", font=font("mono", 18), fill=GOLD, anchor="lb")
    d.text((110, 800), "It failed above the load I designed for, and in the wall, where I meant it to. The radius did what the drawing said it would.", font=font("serif_i", 22), fill=INK)
    save(im, out / "load-test.png")


def engr320():
    """Pier Logger — five weeks in saltwater."""
    out = OUT / "ENGR-320"
    rnd = random.Random(320)
    days = 35
    hours = list(range(days * 24))
    station_t = [15.2 + 1.4 * math.sin(h / 24 / 7 * 2 * math.pi) + 0.6 * math.sin((h % 24) / 24 * 2 * math.pi - 1.2) + rnd.gauss(0, 0.08) for h in hours]
    logger_t = [t + 0.05 + rnd.gauss(0, 0.07) + (0.3 if 500 < h < 520 else 0) for h, t in zip(hours, station_t)]
    tide = [0.9 + 0.8 * math.sin(h / 12.42 * 2 * math.pi) + 0.35 * math.sin(h / 24 * 2 * math.pi + 0.5) for h in hours]
    logger_tide = [x + rnd.gauss(0, 0.03) for x in tide]
    im, d = canvas(1600, 1300)
    eyebrow(d, (110, 60), "ENGR 320 · Machines That Sense · Scripps Pier, 9 Feb – 15 Mar 2030")
    d.text((110, 100), "Pier Logger · five weeks against the station", font=font("serif", 48), fill=INK)
    P = axes(d, (180, 220, 1480, 560), (0, days), (12, 19), xticks=[0, 7, 14, 21, 28, 35], yticks=[12, 14, 16, 18],
             xfmt=lambda t: f"day {t}", yfmt=lambda t: f"{t} °C", ylabel="water temperature · logger (gold) vs Scripps station (blue)")
    polyline(d, P, [h / 24 for h in hours][::3], station_t[::3], MARINE, 3)
    polyline(d, P, [h / 24 for h in hours][::3], logger_t[::3], GOLD, 2)
    d.text((P(21.2, 18.4)[0], P(21.2, 18.4)[1]), "day 21: the 0.3 °C step is the cable chafe, not the ocean", font=font("sans", 17), fill=RUST)
    P2 = axes(d, (180, 660, 1480, 940), (28, 35), (-0.5, 2.5), xticks=[28, 29, 30, 31, 32, 33, 34, 35], yticks=[0, 1, 2],
              xfmt=lambda t: f"day {t}", yfmt=lambda t: f"{t:.0f} m", ylabel="tide, last week · logger (gold) vs NOAA 9410230 (blue)")
    sl = slice(28 * 24, 35 * 24)
    polyline(d, P2, [h / 24 for h in hours][sl], tide[sl], MARINE, 3)
    polyline(d, P2, [h / 24 for h in hours][sl], logger_tide[sl], GOLD, 2)
    P3 = axes(d, (180, 1040, 1480, 1200), (0, days), (-0.5, 0.5), xticks=[0, 7, 14, 21, 28, 35], yticks=[-0.4, 0, 0.4],
              xfmt=lambda t: f"day {t}", yfmt=lambda t: f"{t:+.1f}", ylabel="temperature residual, logger − station (°C)")
    polyline(d, P3, [h / 24 for h in hours][::2], [a - b for a, b in zip(logger_t, station_t)][::2], (90, 90, 90), 2)
    d.line([P3(0, 0), P3(days, 0)], fill=HAIR, width=2)
    d.text((110, 1240), "Mean residual +0.05 °C, σ 0.10 °C, over 840 hourly readings. The station costs $4,000. The logger cost $61 and a bracket I should have checked.", font=font("serif_i", 22), fill=INK)
    save(im, out / "pier-logger-data.png")
    # "Photo": the logger strapped to a piling.
    W, H = 1600, 1067
    im, d = canvas(W, H, (112, 140, 160))
    for y in range(0, 520):
        u = y / 520
        d.line([(0, y), (W, y)], fill=(int(150 - 40 * u), int(170 - 30 * u), int(185 - 20 * u)))
    d.rectangle([0, 520, W, H], fill=(40, 76, 96))
    for k in range(30):
        yy = 530 + k * 18
        d.line([(0, yy), (W, yy)], fill=(48, 86, 108), width=2)
    d.rectangle([640, 0, 860, H], fill=(70, 58, 48))
    for k in range(0, H, 36):
        d.line([(640, k), (860, k + 10)], fill=(58, 48, 40), width=3)
    d.rectangle([640, 480, 860, 560], fill=(90, 110, 90))  # weed line
    d.rounded_rectangle([690, 300, 810, 470], radius=18, fill=(230, 228, 220), outline=(120, 120, 120), width=3)
    d.text((750, 385), "RH", font=font("mono_b", 28), fill=MUTED, anchor="mm")
    for yy in (330, 440):
        d.rectangle([630, yy, 870, yy + 16], fill=(30, 30, 30))
    d.line([(750, 470), (760, 560), (740, 700), (780, 1067)], fill=(20, 20, 20), width=6)
    d.rectangle([880, 420, 1000, 450], fill=(160, 90, 60))   # the bracket
    im = grain(vignette(im, 0.45), 14)
    save(im, out / "logger-on-pier.jpg", 78)
    im, d = canvas(1200, 800, (28, 96, 60))
    for x in range(0, 1200, 25):
        d.line([(x, 0), (x, 800)], fill=(26, 90, 56), width=1)
    for y in range(0, 800, 25):
        d.line([(0, y), (1200, y)], fill=(26, 90, 56), width=1)
    for (x0, y0, x1, y1, lab) in [(120, 120, 420, 320, "MCU"), (520, 120, 680, 220, "RTC"), (760, 120, 1080, 300, "SD"), (120, 440, 320, 620, "pressure"), (420, 440, 620, 560, "temp"), (760, 420, 1080, 680, "LiFePO4")]:
        d.rectangle([x0, y0, x1, y1], fill=(20, 20, 24), outline=(200, 200, 200), width=2)
        d.text(((x0 + x1) / 2, (y0 + y1) / 2), lab, font=font("mono", 22), fill=(220, 220, 220), anchor="mm")
        for k in range(x0 + 10, x1 - 10, 20):
            d.rectangle([k, y0 - 10, k + 8, y0], fill=(200, 180, 120)); d.rectangle([k, y1, k + 8, y1 + 10], fill=(200, 180, 120))
    for pts in [((420, 220), (520, 170)), ((680, 170), (760, 210)), ((320, 530), (420, 500)), ((620, 500), (760, 550)), ((270, 320), (270, 440))]:
        d.line(pts, fill=(200, 180, 120), width=4)
    d.text((120, 720), "pier-logger rev 2 · 61 USD · R. Hale · ENGR 320", font=font("mono", 20), fill=(220, 220, 220))
    save(im, out / "logger-board.png")


def fld301():
    """Twelve Weeks at an Instrument Shop — the field report."""
    out = OUT / "FLD-301"
    pages = []
    p, d, y = page("Twelve Weeks at an Instrument Shop", "FLD 301 · The Field Term · field report")
    y = block(d, (170, y), "Rowan Hale · placement: Sea Grant instrument shop, Point Loma · mentor: J. Alvarez · 8 Jan – 30 Mar 2030", font("sans", 24), MUTED, 1300) + 40
    y = block(d, (170, y), (
        "The shop builds and repairs the instruments the oceanographers put in the water: CTDs, current meters, the "
        "cabled sensors on the pier. I went to learn how instruments survive the sea. I came back having learned mostly "
        "about the people who keep checking them.\n\n"
        "Summary. Twelve weeks, four days a week. Weeks 1–3 on the bench, rebuilding connectors and potting cables. "
        "Weeks 4–8 on a mooring refit, where I built the housing that became ENGR 320's logger. Weeks 9–12 on my own "
        "project with the shop's blessing: a maintenance log for the pier's instruments, which they still use.\n\n"
        "What I assumed. That saltwater is the enemy and the work is sealing things against it.\n\n"
        "What I found. Salt is slow. Chafe, fatigue, and forgetting are fast. Nine of the eleven failures I saw in twelve "
        "weeks were mechanical, at a point where something moved against something else, or they were human: a thing "
        "that had worked for so long that nobody opened it. The instruments that lasted were the ones with a date "
        "written on them."), font("serif", 29), INK, 1300)
    footer(d, "1 / 4"); pages.append(p)
    p, d, y = page("Weeks 1–6", "the bench, then the mooring")
    y = block(d, (170, y), (
        "Week 1. Twenty-two underwater connectors, cleaned and re-greased. J. made me do the first one three times. "
        "By the twentieth I understood why: the grease is not the seal. The clean surface under it is.\n\n"
        "Week 2. Potting cables in urethane. Bubbles are failures you cannot see for six months. We learned to pour "
        "slowly, in a warm room, and to write the pour date on the boot.\n\n"
        "Week 3. A current meter back from eighteen months at 300 m, perfect inside, a bearing ground to dust outside. "
        "The first time I understood that the sea's main tool is repetition.\n\n"
        "Week 4. The mooring refit begins. I assumed the salt was the enemy. It was the cable chafing on the piling. I "
        "noticed in week four, on a cable that had been chafing for a year.\n\n"
        "Week 5. Designed the housing for my own logger from what the shop's housings taught me: a straight pull on "
        "every cable, no sharp bends, a bracket that can be inspected without a diver.\n\n"
        "Week 6. First deployment of the logger from the shop's skiff. It came back dry. J. said: good, now do it ten "
        "more times before you believe it."), font("serif", 29), INK, 1300)
    footer(d, "2 / 4"); pages.append(p)
    p, d, y = page("Weeks 7–12", "the log, and what it changed")
    y = block(d, (170, y), (
        "Week 7–8. Mooring back in the water. I kept a notebook of every assumption I made and every one that turned "
        "out wrong. Eleven of thirty-four. The wrong ones were all of the same kind: I assumed something that had not "
        "failed would not fail.\n\n"
        "Weeks 9–12. The shop had no single place where the pier's instruments' service history lived. I built one: a "
        "plain spreadsheet and a laminated card by the door, with the date each thing was last opened. It is not "
        "technology. It is a habit with a surface. They still use it, and the bracket on my own logger is on it, with "
        "the date I should have checked it and did not.\n\n"
        "What I'd tell the next learner. Go to the bench first and the design second. Write the date on everything. "
        "Ask what failed last year before you ask what the sensor measures."), font("serif", 29), INK, 1300)
    footer(d, "3 / 4"); pages.append(p)
    p, d, y = page("Mentor evaluation", "J. Alvarez · shop lead · excerpt, with permission")
    y = block(d, (170, y), (
        "\"Rowan arrived wanting to design and left wanting to maintain, which is the right direction. Careful hands by "
        "week three. Asks the right question, which is 'what broke last time.' The maintenance card is the most useful "
        "thing a student has left here in years because it is the simplest. Would take them back. Would hire them "
        "after the degree.\"\n\n"
        "Hours: 384. Attendance: full. Unassisted assessment (the shop's own, no notes): rebuild a connector and "
        "explain each step. Passed.\n\n"
        "Reviewed against the rubric for the Field Term: Judgment, proficient. The report, the journal (12 weeks, "
        "41 pages), and the evaluation enter the Portfolio together."), font("serif", 29), INK, 1300)
    footer(d, "4 / 4"); pages.append(p)
    save_pdf(pages, out / "field-report.pdf")
    save_text("""
FIELD JOURNAL — week 4 (29 Jan – 1 Feb 2030)

Mon. Mooring refit starts. J. has me trace every cable from the junction box to the instrument before we touch anything. Forty minutes. I think it's a waste of time. By the end of the week I'll know it was the week's most useful forty minutes.

Tue. The cable to the lower CTD has a flat spot where it crosses the piling. Not cut. Flat, shiny, the jacket worn thin as paper. It has been like this for a year, J. thinks. Nobody saw it because nobody was looking for it; they were looking for corrosion. I assumed the salt was the enemy. It was the cable chafing on the piling.

Wed. Wrote in the notebook: "What else am I protecting against the wrong thing?" Went back to my logger housing drawing and found two sharp bends. Fixed them.

Thu. Re-ran the cable through a length of split hose, strapped above and below the crossing. Cost: four dollars. J.: "Now write the date on the hose." I wrote the date on the hose.

Fri. Day off. Surfed the Cove. Thought about the hose the whole time.

Assumptions proved wrong this week: 3 (the salt; the "perfect" connector that wasn't; that the tracing was a waste of time).
""", out / "journal-week-4.txt")


def art320():
    """Low Tide, Six Minutes — the Crossing: a short film, screened."""
    out = OUT / "ART-320"
    W, H, N = 960, 540, 24 * 8
    rnd = random.Random(320)
    rocks = [(rnd.randint(0, W), rnd.randint(300, 500), rnd.randint(40, 140), rnd.randint(14, 40)) for _ in range(26)]

    def frame(i):
        t = i / N
        im, d = canvas(W, H, (196, 198, 190))
        for y in range(0, 260):
            u = y / 260
            d.line([(0, y), (W, y)], fill=(int(196 - 20 * u), int(198 - 14 * u), int(190 - 8 * u)))
        water = 290 + 150 * ease(t)      # the waterline falls
        d.rectangle([0, 250, W, H], fill=(96, 118, 118))
        for (x, y, rw, rh) in rocks:
            top = y - rh
            if top < water:
                d.ellipse([x - rw, top, x + rw, y + rh], fill=(70, 62, 58))
                if y + rh > water:
                    d.ellipse([x - rw * 0.7, top + rh * 0.6, x + rw * 0.7, y - rh * 0.3], fill=(60, 54, 52))
        d.rectangle([0, water, W, H], fill=(120, 146, 146))
        for k in range(14):
            yy = water + k * 12 + (i % 12)
            d.line([(0, yy), (W, yy)], fill=(132, 158, 156), width=1)
        for (x, y, rw, rh) in rocks:        # pools left behind
            if y + rh < water and t > 0.3:
                d.ellipse([x - rw * 0.5, y - 4, x + rw * 0.5, y + rh * 0.4], fill=(150, 170, 165))
        # small figure, far, standing on the reef late in the film
        if t > 0.6:
            fx = 760
            d.line([(fx, 330), (fx, 362)], fill=(40, 40, 44), width=3); d.ellipse([fx - 4, 322, fx + 4, 330], fill=(40, 40, 44))
        d.text((W - 40, 36), f"{int(t * 6):02d}:{int((t * 6 % 1) * 60):02d}", font=font("mono", 24), fill=(80, 80, 80), anchor="rt")
        if t < 0.14:
            title_card(im, d, "LOW TIDE, SIX MINUTES", "the hour the reef shows itself", fade=min(1, t / 0.03) if t < 0.1 else (0.14 - t) / 0.04, fill=INK)
        if t > 0.9:
            title_card(im, d, "ART 320 · Rowan Hale", "screened 7 June 2029", fade=(t - 0.9) / 0.06, fill=INK)
        return im

    film((frame(i) for i in range(N)), out / "low-tide-six-minutes.mp4", poster_at=0.7)
    im, d = canvas(1200, 700, INK)
    d.rectangle([24, 24, 1175, 675], outline=GOLD, width=3)
    d.text((600, 150), "SCREENING", font=font("mono", 26), fill=GOLD, anchor="mm")
    d.text((600, 260), "Low Tide, Six Minutes", font=font("serif", 64), fill=PAPER, anchor="mm")
    d.text((600, 340), "a film by Rowan Hale · 6 min · one take, one tide", font=font("sans", 26), fill=(200, 200, 200), anchor="mm")
    d.text((600, 460), "ART 320 · the Crossing · 7 June 2029 · 7:30 p.m.", font=font("mono", 22), fill=(180, 180, 180), anchor="mm")
    d.text((600, 520), "the Workshop, with the doors open", font=font("serif_i", 24), fill=(180, 180, 180), anchor="mm")
    save(im, out / "screening-card.png")


def art410():
    """Kelp — a generative work; the rules are mine."""
    out = OUT / "ART-410"
    W, H = 1200, 1600

    def one(seed):
        rnd = random.Random(seed)
        im, d = canvas(W, H, (14, 34, 48))
        for y in range(H):
            u = y / H
            d.line([(0, y), (W, y)], fill=(int(14 + 30 * (1 - u)), int(34 + 50 * (1 - u)), int(48 + 60 * (1 - u))))
        light = (W * rnd.uniform(0.3, 0.7), -200)
        # light shafts
        shafts = Image.new("L", (W, H), 0)
        sd = ImageDraw.Draw(shafts)
        for k in range(6):
            x = rnd.uniform(0, W)
            sd.polygon([(x, 0), (x + 90, 0), (x + 400 + rnd.uniform(-100, 100), H), (x + 160, H)], fill=rnd.randint(20, 50))
        shafts = shafts.filter(ImageFilter.GaussianBlur(40))
        im.paste(Image.new("RGB", (W, H), (120, 170, 170)), (0, 0), shafts)
        d = ImageDraw.Draw(im)

        def stipe(x, y, angle, length, width, depth, hue):
            if depth == 0 or length < 10:
                return
            # grows toward the light: bend the angle a little toward it
            to_light = math.atan2(light[1] - y, light[0] - x)
            da = (to_light - angle + math.pi) % (2 * math.pi) - math.pi
            angle += da * 0.18 + rnd.uniform(-0.25, 0.25)
            nx, ny = x + math.cos(angle) * length, y + math.sin(angle) * length
            col = (int(hue[0] + rnd.uniform(-12, 12)), int(hue[1] + rnd.uniform(-12, 12)), int(hue[2]))
            d.line([(x, y), (nx, ny)], fill=col, width=max(1, int(width)))
            # blades: ellipses off the stipe
            if depth < 9 and rnd.random() < 0.8:
                bl = length * rnd.uniform(0.6, 1.3)
                for side in (-1, 1):
                    if rnd.random() < 0.7:
                        bx = (x + nx) / 2 + math.cos(angle + side * 1.2) * bl * 0.35
                        by = (y + ny) / 2 + math.sin(angle + side * 1.2) * bl * 0.35
                        bw, bh = bl * 0.55, bl * 0.22
                        blade = Image.new("RGBA", (int(bw * 2) + 4, int(bh * 2) + 4), (0, 0, 0, 0))
                        bd = ImageDraw.Draw(blade)
                        bd.ellipse([2, 2, bw * 2, bh * 2], fill=(col[0] + 20, col[1] + 25, col[2], 150))
                        blade = blade.rotate(-math.degrees(angle + side * 0.5), expand=True)
                        im.paste(blade, (int(bx - blade.width / 2), int(by - blade.height / 2)), blade)
            stipe(nx, ny, angle, length * rnd.uniform(0.86, 0.96), width * 0.9, depth - 1, hue)
            if rnd.random() < 0.22 and depth > 3:
                stipe(nx, ny, angle + rnd.choice([-0.7, 0.7]), length * 0.7, width * 0.6, depth - 2, hue)

        for k in range(rnd.randint(6, 9)):
            x = rnd.uniform(80, W - 80)
            hue = rnd.choice([(126, 118, 44), (150, 130, 50), (100, 104, 40), (168, 128, 60)])
            stipe(x, H + 20, -math.pi / 2 + rnd.uniform(-0.3, 0.3), rnd.uniform(90, 130), rnd.uniform(8, 14), rnd.randint(12, 16), hue)
            d = ImageDraw.Draw(im)
        # sand
        d = ImageDraw.Draw(im)
        d.rectangle([0, H - 60, W, H], fill=(60, 66, 60))
        d.text((W - 40, H - 26), f"kelp · {seed:02d} / 40", font=font("mono", 18), fill=(170, 180, 170), anchor="rm")
        return im

    for seed in (7, 19, 33, 40):
        save(one(seed), out / f"kelp-{seed:02d}.jpg", 80)
    save_text("""
KELP — the rules

The system is mine; the drawing is the machine's; the forty I kept are the taste. The rules, in the order the program applies them:

1. A forest is six to nine stipes. Each begins at the sand and grows upward in segments.
2. Each segment bends toward the light by 18% of the angle between where it points and where the light is, plus a little noise (±0.25 rad). The light is above the frame and off-centre, a different place each time.
3. Each segment is 86–96% the length of the one before it. A stipe ends when it is too thin to see or it has made sixteen segments.
4. A segment grows blades on either side with probability 0.7, each blade an ellipse about half the segment's length, turned 0.5 rad off the stipe.
5. With probability 0.22 a stipe forks. The fork inherits the parent's colour and most of its length.
6. Colour is one of four olive-ambers, varied by ±12 per channel per segment, so no two segments match and no stipe is flat.
7. Six shafts of light fall from the top, blurred. They are drawn before the kelp and never move.

What is not in the rules: which forty of the four thousand to keep. I ran the system 4,000 times over three nights and chose by one test: would I stop in front of it. The ledger of every run, every parameter change, and the forty choices is in the Workshop with the prints. The model drew. I decided. I can say which calls were mine, and these were all of them.

Shown in the Workshop, 40 prints at 30 × 40 cm, with this page on the wall beside them. 12 December 2030.
""", out / "the-rules.txt")


def cap402():
    """Cheap Eyes on the Water — the capstone, defended."""
    out = OUT / "CAP-402"
    W, H = 1600, 900

    def slide(n, eyebrow_text, title, body=None, dark=False):
        im, d = canvas(W, H, INK if dark else PAPER)
        fg, mu = (PAPER, (190, 190, 190)) if dark else (INK, MUTED)
        eyebrow(d, (100, 80), eyebrow_text, fill=GOLD)
        y = block(d, (100, 130), title, font("serif", 60), fg, 1400, 1.12) + 30
        hairline(d, 100, y, W - 100, fill=(60, 70, 90) if dark else HAIR)
        if body:
            block(d, (100, y + 40), body, font("sans", 30), fg, 1400, 1.45)
        d.text((W - 100, H - 60), f"{n} / 8", font=font("mono", 18), fill=mu, anchor="rm")
        d.text((100, H - 60), "Cheap Eyes on the Water · CAP 402 · defended 4 May 2031", font=font("mono", 18), fill=mu)
        return im, d

    s1, d = slide(1, "CAP 402 · the capstone, defended", "Cheap Eyes on the Water", dark=True)
    block(d, (100, 420), "An open coastal temperature and tide sensor anyone can build for about forty dollars.", font("serif_i", 40), (220, 220, 220), 1300, 1.3)
    block(d, (100, 600), "Rowan Hale · Design · defended on the sand at the Cove before faculty, two outside examiners, and the five people who use it", font("sans", 26), (170, 170, 170), 1300)
    s2, _ = slide(2, "the problem", "The station on the pier costs $4,000.\nThere is one.",
                  "The coast is 70 miles long. Scientists, lifeguards, teachers, and people who fish all want to know the water, and the data comes from a handful of points. Every other station is a budget line nobody wins.\n\nThe question from Day 4 of CAP 401: what would it take to make the number cheap enough that anyone who wanted one could have one?")
    s3, d = slide(3, "the build", "$41.60, from parts you can buy today")
    f = font("mono", 26)
    bom = [("microcontroller (LoRa)", 12.40), ("pressure/temperature sensor", 9.80), ("LiFePO4 cell + charger", 8.20), ("housing (PVC, cast end caps)", 5.10), ("cable gland, bracket, strap", 3.60), ("solar 1 W", 2.50)]
    y = 330
    for name, cost in bom:
        d.text((100, y), f"{name:<34} ${cost:>6.2f}", font=f, fill=INK); y += 44
    d.text((100, y + 10), f"{'total':<34} ${sum(c for _, c in bom):>6.2f}", font=font("mono_b", 26), fill=INK)
    d.text((100, y + 70), "The build guide is 11 steps and 40 minutes. It assumes you have never soldered.", font=font("sans", 26), fill=MUTED)
    s4, d = slide(4, "the housing", "Every lesson from the pier, in PVC")
    d.rounded_rectangle([1000, 300, 1180, 720], radius=40, fill=(236, 234, 226), outline=INK, width=4)
    d.rectangle([980, 380, 1200, 400], fill=INK); d.rectangle([980, 640, 1200, 660], fill=INK)
    d.line([(1090, 720), (1100, 820)], fill=INK, width=6)
    d.text((1090, 500), "RH", font=font("mono_b", 36), fill=MUTED, anchor="mm")
    block(d, (100, 330), "Straight pull on the cable, no bends (FLD 301, week 4).\n\nR4 radii on every inside corner of the cast caps (ENGR 310).\n\nA bracket you can inspect from the pier without a diver, with the date written on it (ENGR 320, the one that rusted).\n\nTested to 10 m, five weeks in saltwater, three builds.", font("sans", 28), INK, 820, 1.45)
    s5, d = slide(5, "does it agree?", "Three builds vs the pier, 21 days")
    chart = _three_builds_chart(out)
    s5.paste(chart.resize((1300, 540)), (150, 300))
    s6, _ = slide(6, "what failed", "The thing that never failed is the thing you stopped checking",
                  "Build 2's bracket in week 3: the strap crept 2 cm and the housing began to knock the piling. The data showed it before the diver did: a 0.3 °C spike every swell.\n\nThe guide now has a step 11: write today's date on the bracket, and a date one month out. Everyone who built one has done it.")
    s7, _ = slide(7, "who built one", "Three people who are not me",
                  "A marine science teacher at Point Loma High, with her class, in one afternoon. Their numbers matched the pier to 0.1 °C.\n\nA lifeguard at Black's who wanted the water temperature on his own stretch. $38.90; he found a cheaper cell.\n\nMy mother, in the kitchen, from the guide alone, to prove the guide. It took her 70 minutes and it works.")
    s8, d = slide(8, "what's next", "The kit ships 1 May.", dark=True)
    block(d, (100, 420), "sdit.org/eyes · the guide, the files, the data, all open · $44 as a kit, $0 as a PDF\n\nThe company that builds the forty-dollar sensor for the scientists who cannot buy the four-thousand-dollar one. The Portfolio is the pitch.", font("sans", 30), (220, 220, 220), 1400, 1.45)
    slides = [s1, s2, s3, s4, s5, s6, s7, s8]
    save_pdf(slides, out / "defense-deck.pdf", dpi=96)
    save(s1, out / "deck-cover.png")
    # The sensor, "photographed" on a rock at the Cove.
    im, d = canvas(1600, 1067, (170, 170, 160))
    for y in range(0, 1067):
        u = y / 1067
        d.line([(0, y), (1600, y)], fill=(int(200 - 60 * u), int(205 - 50 * u), int(200 - 40 * u)))
    d.rectangle([0, 380, 1600, 1067], fill=(76, 104, 112))
    rnd = random.Random(402)
    for _ in range(40):
        x, y = rnd.randint(-100, 1700), rnd.randint(600, 1100)
        d.ellipse([x, y, x + rnd.randint(200, 500), y + rnd.randint(80, 200)], fill=(70, 62, 58))
    d.ellipse([400, 520, 1300, 1000], fill=(84, 76, 70))
    d.rounded_rectangle([720, 380, 880, 760], radius=40, fill=(236, 234, 226), outline=(90, 90, 90), width=4)
    d.rectangle([700, 450, 900, 470], fill=(20, 20, 20)); d.rectangle([700, 690, 900, 710], fill=(20, 20, 20))
    d.text((800, 560), "RH", font=font("mono_b", 34), fill=MUTED, anchor="mm")
    d.rectangle([740, 300, 860, 380], fill=(30, 40, 70))   # solar
    d.line([(800, 760), (820, 860), (780, 1000)], fill=(20, 20, 20), width=6)
    d.rectangle([1050, 820, 1400, 900], fill=PAPER)
    d.text((1070, 835), "build 1 · bracket checked 3 May 2031", font=font("mono", 20), fill=INK)
    d.text((1070, 865), "next: 3 Jun 2031", font=font("mono", 20), fill=RUST)
    im = grain(vignette(im, 0.45), 14)
    save(im, out / "sensor-at-the-cove.jpg", 78)
    save_text("""
CHEAP EYES ON THE WATER — build guide v1.0
A coastal temperature and tide sensor for about forty dollars. 11 steps, 40 minutes, no experience assumed.

Bill of materials ($41.60)
  1  microcontroller board with LoRa radio ............ 12.40
  1  pressure + temperature sensor, I2C, 0–10 m ........ 9.80
  1  LiFePO4 cell 3.2 V 1500 mAh + charger board ....... 8.20
  1  PVC pipe 50 mm × 300 mm + two cast end caps ....... 5.10
  1  cable gland M12, stainless bracket, 2 straps ...... 3.60
  1  solar panel 1 W ..................................... 2.50

Steps
  1. Flash the board (one file, one button). Test it blinks.
  2. Solder four wires: sensor to board. Red, black, yellow, blue. Photos in the appendix.
  3. Solder the cell and charger. Test the voltage: 3.2–3.6 V.
  4. Pass the sensor cable through the gland in the lower cap. Straight. No bend inside the housing.
  5. Pot the gland with the urethane in the kit. Pour slowly. Write the date on the cap.
  6. Fit the upper cap with the solar panel and antenna. Hand tight plus a quarter turn.
  7. Power on. Wait for the green light: it found the network.
  8. Lower it into a bucket of water. The reading should go to the depth of the bucket within 2 cm.
  9. Mount the bracket where it can be seen from above: not under a ledge, not where a cable crosses an edge.
 10. Strap the housing. Check it does not move when pushed hard.
 11. Write today's date on the bracket, and a date one month from today. Come back on that date.

What to expect
  Readings every 10 minutes to the open map. Temperature within 0.1 °C of a reference station; depth within 3 cm.
  Battery: indefinite with 2 h of sun a day. A week in the dark.

If it stops
  Check the bracket first. Then the gland. Then the cell. The sensor itself has not failed yet in any build.

License: CERN-OHL-P. Files: sdit.org/eyes. Data: open. Questions: the forum, or ask someone who built one.
""", out / "build-guide.txt")


def _three_builds_chart(out: Path) -> Image.Image:
    rnd = random.Random(4020)
    im, d = canvas(1600, 660)
    P = axes(d, (160, 60, 1500, 540), (0, 21), (13, 18), xticks=[0, 7, 14, 21], yticks=[13, 14, 15, 16, 17, 18],
             xfmt=lambda t: f"day {t}", yfmt=lambda t: f"{t} °C", ylabel="water temperature · pier station (blue) · builds 1–3 (gold, amber, rust)")
    xs = [i / 4 for i in range(0, 85)]
    base = [15.3 + 0.9 * math.sin(x / 21 * 2 * math.pi) + 0.5 * math.sin(x * 2 * math.pi - 1) for x in xs]
    polyline(d, P, xs, base, MARINE, 4)
    for col, off in ((GOLD, 0.04), ((200, 150, 80), -0.03), (RUST, 0.06)):
        polyline(d, P, xs, [b + off + rnd.gauss(0, 0.06) for b in base], col, 2)
    d.text((160, 580), "mean difference from the station: +0.04, −0.03, +0.06 °C · all three within 0.1 °C · the pier station costs 96× as much", font=font("sans", 22), fill=INK)
    save(im, out / "three-builds-vs-pier.png")
    return im


ALL = {
    "HUM-101": hum101, "MATH-110": math110, "CS-120": cs120, "PHYS-120": phys120, "WKSP-102": wksp102,
    "RHET-110": rhet110, "MATH-220": math220, "SIG-201": sig201, "WKSP-202": wksp202, "ART-310": art310,
    "ENGR-310": engr310, "ENGR-320": engr320, "FLD-301": fld301, "ART-320": art320, "ART-410": art410, "CAP-402": cap402,
}


def main(argv):
    which = argv[1:] or list(ALL)
    for d in which:
        print(d)
        ALL[d]()
    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"total {total / 1024 / 1024:.1f} MB in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv)
