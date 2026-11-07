"""Radar header clearances and their sensitivity to the header size (plastic +-0.3 mm, spacer, pin).
Usage: python src/header_study.py   (exact B-rep distances against the real insert, keepers, tact, sleeve)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import params as P, parts as PT, components as C
from geo import solid_of
from OCP.BRepExtrema import BRepExtrema_DistShapeShape


def dmin(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped); d.Perform(); return d.Value()


def vol(a, b):
    try: return a.intersect(b).Volume()
    except Exception: return 0.0


static = {'insert': solid_of(PT.insert()), 'keeper_a': solid_of(PT.keeper_a()), 'sleeve': solid_of(C.sleeve())}
ka = PT.keeper_a()


def run(label, **kw):
    saved = {k: getattr(C, k) for k in kw}
    for k, v in kw.items(): setattr(C, k, v)
    H = solid_of(C.radar_header())
    for k, v in saved.items(): setattr(C, k, v)
    bb = H.BoundingBox()
    res = {k: dmin(H, s) for k, s in static.items()}
    path = [d for d in np.arange(0, 41, 2.0) if vol(H, solid_of(ka.translate((0, 0, -d)))) > 1e-4]
    xs = C.radar_pin_xs(); t = kw.get('HDR_PIN_T', P.HDR_PIN_T)
    slot = min((xs[1] - t / 2) - P.KA_SLOT_X0, P.KA_SLOT_X1 - (xs[-1] + t / 2))
    print(f'{label:34s} header x {bb.xmin:5.2f}..{bb.xmax:5.2f} y {bb.ymin:5.2f}..{bb.ymax:5.2f} z {bb.zmin:6.2f}..{bb.zmax:6.2f} | '
          f'keeper A {res["keeper_a"]:.3f}  sleeve {res["sleeve"]:.3f}  insert {res["insert"]:.3f}  pin-to-slot {slot:.3f}  path hits {path or "none"}')
    return res


L, W, S, T = P.HDR_PLASTIC_L, P.HDR_PLASTIC_W, P.HDR_SPACER_T, P.HDR_PIN_T
run('nominal')
run('plastic length +0.3', HDR_PLASTIC_L=L + 0.3)
run('plastic width +0.3', HDR_PLASTIC_W=W + 0.3)
run('plastic length+width +0.3', HDR_PLASTIC_L=L + 0.3, HDR_PLASTIC_W=W + 0.3)
run('spacer thickness +0.3', HDR_SPACER_T=S + 0.3)
run('pin thickness +0.3', HDR_PIN_T=T + 0.3)
run('all +0.3', HDR_PLASTIC_L=L + 0.3, HDR_PLASTIC_W=W + 0.3, HDR_SPACER_T=S + 0.3, HDR_PIN_T=T + 0.3)
