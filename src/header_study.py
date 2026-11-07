import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from params import *
import params as P, parts as PT, components as C, wires as W
from geo import box, cyl, solid_of
import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

HDR_H, SPACER = 8.3, 1.35
xs = C.radar_pin_xs(); yp = C.radar_pin_y()
def header():
    pitch = RAD_PIN_PITCH
    body = box(xs[0] - pitch/2, xs[-1] + pitch/2, yp - pitch/2, yp + pitch/2, RAD_Z0 - SPACER, RAD_Z0)      # plastic spacer 5 x 2.54 x 1.35
    pins = [box(x - 0.32, x + 0.32, yp - 0.32, yp + 0.32, RAD_Z0 - HDR_H, RAD_Z0 + 0.0) for x in xs]
    h = body
    for p in pins: h = h.union(p)
    return h
H = solid_of(header())
bb = H.BoundingBox()
print('header x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f' % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
print('lip opening x %.1f..%.1f y %.1f..%.1f ; lip slab z %.1f..%.1f ; PCB back z %.2f' % (LIP_X0, LIP_X1, LIP_Y0, LIP_Y1, LIP_Z0, LIP_Z1, RAD_Z0))
def dmin(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped); d.Perform(); return d.Value()
def vol(a, b):
    try: return a.intersect(b).Volume()
    except Exception: return -1
parts = {'insert': PT.insert(), 'keeper_a': PT.keeper_a(), 'keeper_b': PT.keeper_b(), 'keeper_c': PT.keeper_c(), 'tact': C.tact(), 'sleeve': C.sleeve()}
sol = {k: solid_of(v) for k, v in parts.items()}
for k, s in sol.items():
    print(f'  header vs {k:9s}: overlap volume {vol(H, s):7.3f} mm3, min distance {dmin(H, s):6.3f} mm')
# keeper A install path: lowered from -z (toward +z) with the header already on the radar
ka = parts['keeper_a']
hits = []
for d in np.arange(0, 41, 1.0):
    k = solid_of(ka.translate((0, 0, -d)))
    v = vol(H, k)
    if v > 1e-4: hits.append((d, round(v, 3)))
print('keeper A path (offset above seat -> overlap mm3):', hits[:12], '... n hits', len(hits))
# which keeper A features touch: header footprint vs slot
print('slot x 7.6..17.6, slot starts y = %.2f; header y %.2f..%.2f, x %.2f..%.2f' % (yp - 1.0, yp - 1.27, yp + 1.27, xs[0] - 1.27, xs[-1] + 1.27))
# pins vs the 4 wire lanes and GND run under the tact bridge

import parts as PT
print('keeper A: plate z %.2f..%.2f, KA_Z0 %.2f, KA_Z1 %.2f, KA_LOW_Z0 %.2f, GND run level %.2f, tact Z0 %.2f' % (PT.KA_Z0, PT.KA_Z1, PT.KA_Z0, PT.KA_Z1, PT.KA_LOW_Z0, W.KA_LOW_Z0_W, P.TACT_Z0))
print('XIAO pad levels z:', {k: round(v[1], 2) for k, v in W.PADS.items()}, 'Y_WIRE', round(W.Y_WIRE, 2))
# trimmed header: pin 1 (OT2, unused) removed, spacer trimmed to start at pin 2's cell
def header2():
    body = box(xs[1] - RAD_PIN_PITCH/2, xs[-1] + RAD_PIN_PITCH/2, yp - RAD_PIN_PITCH/2, yp + RAD_PIN_PITCH/2, RAD_Z0 - SPACER, RAD_Z0)
    for x in xs[1:]: body = body.union(box(x - 0.32, x + 0.32, yp - 0.32, yp + 0.32, RAD_Z0 - HDR_H, RAD_Z0))
    return body
H2 = solid_of(header2()); b2 = H2.BoundingBox()
print('trimmed header x %.2f..%.2f' % (b2.xmin, b2.xmax))
for k, s_ in sol.items():
    print(f'  trimmed header vs {k:9s}: overlap {vol(H2, s_):7.3f} mm3, min distance {dmin(H2, s_):6.3f} mm')
hits = []
for d in np.arange(0, 41, 1.0):
    if vol(H2, solid_of(ka.translate((0, 0, -d)))) > 1e-4: hits.append(d)
print('keeper A path hits with trimmed header:', hits)
# pins only (no spacer) distance to the slot edges
print('pin 2 left edge to slot start: %.2f ; pin 5 right edge to slot end: %.2f' % ((xs[1] - 0.32) - 7.6, 17.6 - (xs[-1] + 0.32)))
# wire length saved: lane currently starts at z0 = RAD_Z0 - 1.0
print('lane start now z %.2f, pin tip z %.2f -> %.2f mm shorter per wire' % (RAD_Z0 - 1.0, RAD_Z0 - HDR_H, (RAD_Z0 - 1.0) - (RAD_Z0 - HDR_H)))
