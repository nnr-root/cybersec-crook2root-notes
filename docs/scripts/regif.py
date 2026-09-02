#!/usr/bin/env python3
"""Re-encode a GIF against one shared palette so the encoder can write deltas."""
import sys, os, numpy as np
from PIL import Image, ImageSequence
src, dst = sys.argv[1], sys.argv[2]
colors = int(sys.argv[3]) if len(sys.argv) > 3 else 64
im = Image.open(src)
dur = im.info.get("duration", 80)
fr = [f.copy().convert("RGB") for f in ImageSequence.Iterator(im)]
# palette from every frame, not just the first — a moving drawing shows tones
# in frame 40 that frame 0 never contains
import math
step = max(1, len(fr) // 12)
sample = fr[::step]
w, h = fr[0].size
strip = Image.new("RGB", (w, h * len(sample)))
for i, f in enumerate(sample):
    strip.paste(f, (0, i * h))
master = strip.quantize(colors=colors, dither=Image.NONE)
q = []
for f in fr:
    g = f.quantize(palette=master, dither=Image.NONE)
    g.info = {}                      # the source GIF carries a transparency tuple PIL will choke on
    q.append(g)
q[0].save(dst, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=True)
print("%-24s %6.0f KB -> %5.0f KB   %d frames  %s"
      % (os.path.basename(src), os.path.getsize(src)/1024,
         os.path.getsize(dst)/1024, len(fr), fr[0].size))
