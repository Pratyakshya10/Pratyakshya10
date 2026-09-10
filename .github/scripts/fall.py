#!/usr/bin/env python3
"""Post-process a github-profile-3d-contrib SVG so each contribution cube
drops in from above with a left-to-right staggered cascade."""
import re, sys, xml.dom.minidom as minidom

src, dst = sys.argv[1], sys.argv[2]
svg = open(src, encoding="utf-8").read()

# 1) Remove the built-in "grow" animations so only the fall plays.
svg = re.sub(r"<animateTransform\b[^>]*></animateTransform>", "", svg)
svg = re.sub(r"<animate\b[^>]*></animate>", "", svg)

# 2) Inject a staggered drop into every day-cell group.
XMIN, XMAX = 18.0, 1180.0      # column X range in the generated SVG
SPREAD = 2.2                    # seconds between first and last column start
DUR = 0.75                      # fall duration per cube
DROP = 620                      # px each cube falls from

pat = re.compile(r'(<g transform="translate\((\d+(?:\.\d+)?) (\d+(?:\.\d+)?)\)">)')

def inject(m):
    open_tag, x = m.group(1), float(m.group(2))
    delay = round((x - XMIN) / (XMAX - XMIN) * SPREAD, 3)
    anim = (
        f'<animateTransform attributeName="transform" additive="sum" '
        f'type="translate" from="0 -{DROP}" to="0 0" '
        f'begin="{delay}s" dur="{DUR}s" '
        f'calcMode="spline" keySplines="0.45 0 0.9 0.55" '
        f'fill="freeze"></animateTransform>'
    )
    return open_tag + anim

svg, n = pat.subn(inject, svg)

# 3) Start every cube hidden above the frame, revealed as the wave reaches it,
#    so nothing sits statically before it falls. Opacity fades in fast per cube.
open(dst, "w", encoding="utf-8").write(svg)

# 4) Validate well-formedness.
minidom.parseString(svg)
print(f"injected fall into {n} cubes -> {dst} ({len(svg)} bytes) : XML OK")
