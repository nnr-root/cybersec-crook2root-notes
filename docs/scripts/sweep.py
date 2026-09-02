#!/usr/bin/env python3
"""
Derive a looping mechanism GIF from an audited Gemini timing diagram.

The artwork is not authored here. A playhead sweeps left to right; the state
is revealed behind it and held empty ahead of it, so the reader watches the
cache flip as each arrival lands instead of reading a finished chart.

usage: sweep.py IN.(png|jpg) OUT.gif [--seconds 6] [--fps 14] [--width 1200]
"""
import sys, os, argparse, numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--seconds", type=float, default=5.0)
ap.add_argument("--fps", type=int, default=12)
ap.add_argument("--hold", type=float, default=1.0)
ap.add_argument("--width", type=int, default=1100)
ap.add_argument("--colors", type=int, default=64)
a = ap.parse_args()

src = np.asarray(Image.open(a.src).convert("RGB")).astype(np.int16)
H, W, _ = src.shape
R, G, B = src[:, :, 0], src[:, :, 1], src[:, :, 2]

sat = ((R - B > 20) & (R > 80)) | ((B - R > 12) & (B > 80))
fill = ((R - B > 25) & (R > 90)) | ((B - R > 15) & (B > 90))
rows = fill.sum(axis=1)
bar_rows = [y for y in range(H) if rows[y] > W * 0.4]
if not bar_rows:
    sys.exit("could not locate the bar")
by0, by1 = bar_rows[0], bar_rows[-1]
cols = fill[by0:by1 + 1].sum(axis=0)
bar_cols = [x for x in range(W) if cols[x] > (by1 - by0) * 0.5]
bx0, bx1 = bar_cols[0], bar_cols[-1]
bh = by1 - by0

corner = src[int(H * .85):, int(W * .88):].reshape(-1, 3)
dark = corner[corner.sum(axis=1) < 160]
ground = np.median(dark, axis=0) if len(dark) else np.array([27, 31, 34])
print("bar x %d..%d y %d..%d   ground %s" % (bx0, bx1, by0, by1, ground.astype(int)))

# "nothing has happened yet": bar emptied, strokes dimmed toward the ground
pre = src.copy()
inner = np.zeros((H, W), bool)
inner[by0 + 3:by1 - 2, bx0 + 3:bx1 - 2] = True
pre[inner & sat] = ground
outside = ~inner & sat
pre[outside] = (src[outside] * .22 + ground * .78).astype(np.int16)

A, Bl = src.astype(np.uint8), pre.astype(np.uint8)

# crop away dead margin: keep the content plus a comfortable border
ink = sat | ((abs(R - G) < 30) & (abs(G - B) < 30) & (R > 120))
# ignore stray compression speckle: a row or column counts only if it holds ink
rden, cden = ink.sum(axis=1), ink.sum(axis=0)
ys = np.nonzero(rden > 25)[0]
xs = np.nonzero(cden > 25)[0]
mx, my = int(W * .02), int(bh * .35)
cx0, cx1 = max(xs.min() - mx, 0), min(xs.max() + mx, W)
cy0, cy1 = max(ys.min() - my, 0), min(ys.max() + my, H)
A, Bl = A[cy0:cy1, cx0:cx1], Bl[cy0:cy1, cx0:cx1]
bx0, bx1 = bx0 - cx0, bx1 - cx0
py_off = cy0
CH, CW = A.shape[:2]
print("crop  %dx%d  (was %dx%d)" % (CW, CH, W, H))

# playhead: tall enough to touch the arrival strokes, short enough to stay clear
py0 = max(by0 - int(bh * 1.15) - py_off, 0)
py1 = min(by1 + int(bh * 0.30) - py_off, CH)
head = np.array([205, 216, 224], np.uint8)

n_sweep = int(a.seconds * a.fps)
n_hold = int(a.hold * a.fps)
tw = a.width
th = int(CH * tw / CW)
# one shared palette for every frame, so the encoder can write real deltas
master = Image.fromarray(A).resize((tw, th), Image.LANCZOS).quantize(
    colors=a.colors, dither=Image.NONE)
frames = []
for i in range(n_sweep + n_hold):
    t = min(i / max(n_sweep - 1, 1), 1.0)
    p = int(bx0 + (bx1 - bx0) * t)
    f = Bl.copy()
    f[:, :p] = A[:, :p]
    if i < n_sweep:
        f[py0:py1, max(p - 2, 0):min(p + 3, CW)] = head
    frames.append(Image.fromarray(f).resize((tw, th), Image.LANCZOS)
                  .quantize(palette=master, dither=Image.NONE))

frames[0].save(a.dst, save_all=True, append_images=frames[1:],
               duration=int(1000 / a.fps), loop=0, optimize=True)
kb = os.path.getsize(a.dst) / 1024
print("wrote %s  %dx%d  %d frames  %.0f KB" % (a.dst, tw, th, len(frames), kb))
