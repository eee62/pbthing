"""Measure the supplied sleeve STL and XIAO STEP. Prints every number the design relies on.
Run: python src/measure.py  (writes out/logs/measure.txt)"""
import os, sys, json
import numpy as np
import trimesh
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from step_tools import load_step_solids  # noqa: E402

out = []


def p(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    out.append(s)


m = trimesh.load(os.path.join(ROOT, 'inputs', 'zen_v7_sleeve.stl'))
p('== SLEEVE zen_v7_sleeve.stl ==')
p('faces', len(m.faces), 'watertight', m.is_watertight, 'volume_mm3', round(m.volume, 2))
p('bounds_min', np.round(m.bounds[0], 3).tolist(), 'bounds_max', np.round(m.bounds[1], 3).tolist())
p('distinct z levels of vertices', sorted(set(np.round(m.vertices[:, 2], 3).tolist())))


def loops(z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    return [np.asarray(d)[:, :2] for d in s.discrete]


def corner_r(P):
    x0, y0, x1, y1 = P.bounds
    return float(np.sqrt(max((x1 - x0) * (y1 - y0) - P.area, 0) / (4 - np.pi)))


res = {}
for name, z in [('cavity_z=1', 1.0), ('cavity_z=70', 70.0), ('cavity_z=134', 134.0),
                ('lip_z=135.75', 135.75), ('bore_z=138.75', 138.75), ('bore_z=140.4', 140.4)]:
    Ls = sorted(loops(z), key=lambda L: -Polygon(L).area)
    outer, inner = Polygon(Ls[0]), Polygon(Ls[1])
    p(f'{name}: outer {np.round(outer.bounds, 3).tolist()} r~{corner_r(outer):.2f} | '
      f'inner {np.round(inner.bounds, 3).tolist()} size {inner.bounds[2]-inner.bounds[0]:.3f} x '
      f'{inner.bounds[3]-inner.bounds[1]:.3f} r~{corner_r(inner):.2f}')
    res[name] = dict(outer=list(outer.bounds), inner=list(inner.bounds), r_in=corner_r(inner))

p('\n== XIAO_ESP32S3_Sense.step (STEP frame) ==')
sol = load_step_solids(os.path.join(ROOT, 'inputs', 'XIAO_ESP32S3_Sense.step'))
p('solids', len(sol))
groups = {}
for path, s in sol:
    key = path.split('/')[1] if '/' in path else path
    bb = s.BoundingBox()
    g = groups.setdefault(key, [1e9, -1e9, 1e9, -1e9, 1e9, -1e9])
    g[0] = min(g[0], bb.xmin); g[1] = max(g[1], bb.xmax)
    g[2] = min(g[2], bb.ymin); g[3] = max(g[3], bb.ymax)
    g[4] = min(g[4], bb.zmin); g[5] = max(g[5], bb.zmax)
for k, g in sorted(groups.items()):
    p(f'  {k:45s} X_s {g[0]:7.2f}..{g[1]:7.2f}  Y_s {g[2]:6.2f}..{g[3]:6.2f}  Z_s {g[4]:7.2f}..{g[5]:7.2f}')
p('Notes: "MicroSD v2" is the inserted card (X_s up to 15.39, beyond the USB tip 13.81);')
p('       it is EXCLUDED (no card is used). "10067099-200LF" is the socket and is kept.')
p('       "Camer Module" is the stock OV2640 and is EXCLUDED (user camera modelled separately).')
p('       Stock FPC tail in the connector: X_s -7.2..-2.2, Y_s 5.6..5.88, Z_s -13.0..-0.5 (12.5 wide);')
p('       the FPC leaves the connector toward +X_s (toward the USB end).')
with open(os.path.join(ROOT, 'out', 'logs', 'measure.txt'), 'w') as f:
    f.write('\n'.join(out) + '\n')
