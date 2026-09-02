#!/usr/bin/env python3
"""
Shrink a generated schematic without changing how it looks.

Gemini returns JPEG, so every flat region arrives full of compression noise — a
drawing made of five tones comes back with several thousand colours, and PNG
cannot run-length any of it. This snaps each pixel to the drawing's own palette,
but only where it already sits within a small distance of one, so flat areas go
truly flat and antialiased edges are left alone.

The palette is taken by frequency, not by quantiser centroids: the colours a
schematic is actually made of are the ones covering the most pixels, and a
centroid sitting between two of them splits a flat region in half and makes the
file bigger rather than smaller.

usage: flatten.py IN OUT [--colors 6] [--tolerance 14] [--min-separation 18]
"""
import argparse, os, numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--colors", type=int, default=8)
ap.add_argument("--tolerance", type=float, default=14.0)
ap.add_argument("--min-separation", type=float, default=18.0)
a = ap.parse_args()

im = Image.open(a.src).convert("RGB")
orig = np.asarray(im).astype(np.int16)
flat = orig.reshape(-1, 3)

# most-covered colours, coarsely binned, kept apart from one another
key = (flat // 4).astype(np.int32)
key = key[:, 0] * 4096 + key[:, 1] * 64 + key[:, 2]
vals, counts = np.unique(key, return_counts=True)
order = np.argsort(-counts)
pal = []
for i in order:
    c = np.array([(vals[i] // 4096) * 4 + 2, ((vals[i] // 64) % 64) * 4 + 2, (vals[i] % 64) * 4 + 2])
    if all(np.linalg.norm(c - p) >= a.min_separation for p in pal):
        pal.append(c)
    if len(pal) == a.colors:
        break
pal = np.array(pal, dtype=np.int16)

# refine each entry to the true median of the pixels it owns
for _ in range(2):
    out = np.empty(len(flat), np.int16); best = np.full(len(flat), 1e9, np.float32)
    for j, p in enumerate(pal):
        d = np.linalg.norm((flat - p).astype(np.float32), axis=1)
        m = d < best; best[m] = d[m]; out[m] = j
    pal = np.array([np.median(flat[out == j], axis=0) if (out == j).any() else pal[j]
                    for j in range(len(pal))], dtype=np.int16)

hit = best < a.tolerance
res = flat.copy(); res[hit] = pal[out[hit]]
img = Image.fromarray(res.reshape(orig.shape).astype(np.uint8))
img.save(a.dst, optimize=True)

delta = np.abs(np.asarray(Image.open(a.dst).convert("RGB")).astype(int) - orig.astype(int))
print("%-26s %6.0f KB -> %5.0f KB   snapped %.1f%%   max delta %d   over 20: %.3f%%"
      % (os.path.basename(a.src), os.path.getsize(a.src) / 1024,
         os.path.getsize(a.dst) / 1024, 100 * hit.mean(),
         delta.max(), 100 * (delta.max(axis=2) > 20).mean()))
