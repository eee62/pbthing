"""Camera FPC, signal wires, battery/switch wires and antenna coax as swept solids.
Every path is a polyline whose corners are replaced by tangent arcs of a stated radius,
so the minimum bend radius is known exactly."""
import math
import numpy as np
from params import *  # noqa
from geo import path_edges, sweep_circle, sweep_rect
import components as C


# ---------------- camera FPC ----------------------------------------------
def fpc_points(z_loop):
    """Ribbon route (exit direction is free; chosen: out of the head's +y edge in the base plane).
    mouth -> up -> bend +y under the SD socket -> bend down past keeper C -> U-loop -> up -> bend into the head."""
    x = FPC_X
    y0, yd, yu = FPC_Y_SLOT, FPC_Y_DOWN, FPC_Y_UP2
    zb = FPC_Z_STIFF + FPC_R1
    return [
        (x, y0, FPC_Z_MOUTH),        # connector front
        (x, y0, zb),                 # corner: bend toward +y (r FPC_R1)
        (x, yd, zb),                 # corner: bend down (r FPC_R2)
        (x, yd, z_loop),             # corner: U loop (r FPC_R_LOOP)
        (x, yu, z_loop),             # corner: U loop
        (x, yu, FPC_Z_HEAD),         # corner: 90 deg into the head (r FPC_RHEAD)
        (x, CAM_Y1, FPC_Z_HEAD),     # head edge; FPC_HEAD_IN more is inside the head
    ]


FPC_RADII = [FPC_R1, FPC_R2, None, None, FPC_RHEAD]


def _path_with_radii(pts, radii, default):
    """path_edges with an individual radius per corner."""
    import cadquery as cq
    P = [np.array(p, float) for p in pts]
    edges, used = [], []
    cur = P[0]
    for i in range(1, len(P) - 1):
        r = radii[i - 1] if radii[i - 1] is not None else default
        a, b, c = P[i - 1], P[i], P[i + 1]
        u = (a - b) / np.linalg.norm(a - b)
        v = (c - b) / np.linalg.norm(c - b)
        ang = math.acos(max(-1.0, min(1.0, float(u @ v))))
        t = r / math.tan(ang / 2)
        assert t <= np.linalg.norm(a - b) + 1e-6 and t <= np.linalg.norm(c - b) + 1e-6, (i, r, t)
        p1, p2 = b + u * t, b + v * t
        bis = (u + v) / np.linalg.norm(u + v)
        centre = b + bis * (r / math.sin(ang / 2))
        mid = centre - bis * r
        if np.linalg.norm(p1 - cur) > 1e-6:
            edges.append(cq.Edge.makeLine(cq.Vector(*cur), cq.Vector(*p1)))
        edges.append(cq.Edge.makeThreePointArc(cq.Vector(*p1), cq.Vector(*mid), cq.Vector(*p2)))
        used.append(r)
        cur = p2
    if np.linalg.norm(P[-1] - cur) > 1e-6:
        edges.append(cq.Edge.makeLine(cq.Vector(*cur), cq.Vector(*P[-1])))
    return edges, used


def fpc_length(z_loop):
    edges, _ = _path_with_radii(fpc_points(z_loop), FPC_RADII, FPC_R_LOOP)
    return sum(e.Length() for e in edges) + FPC_TAIL_IN + FPC_HEAD_IN


def solve_fpc_loop(length=FPC_LEN):
    lo, hi = 60.0, FPC_Z_STIFF + FPC_R1 - FPC_R2 - FPC_R_LOOP - 0.01
    f = lambda z: fpc_length(z) - length
    if f(hi) > 0:
        pass
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def fpc(length=FPC_LEN):
    z = solve_fpc_loop(length)
    edges, radii = _path_with_radii(fpc_points(z), FPC_RADII, FPC_R_LOOP)
    sol = sweep_rect(edges, FPC_W, FPC_T, binormal=(1, 0, 0))
    return sol, dict(z_loop=z, loop_bottom=z - FPC_T / 2, min_radius=min(radii),
                     radii=radii, length=sum(e.Length() for e in edges) + FPC_TAIL_IN + FPC_HEAD_IN)


# ---------------- discrete wires -------------------------------------------
# XIAO bottom-side pads in the sleeve frame (x, z); the wire lies in the bay at y = Y_WIRE.
def pad(xs, zs):
    return (zs2x(zs), xs2z(xs) + XIAO_DZ)


PADS = {
    'BAT+': (18.6, xs2z(2.12) + XIAO_DZ), 'BAT-': (19.8, xs2z(4.03) + XIAO_DZ),   # pad spans x 18.26..20.04
    '3V3': pad(4.28, 1.84), 'GND': pad(6.82, 1.84), 'D10': pad(1.74, 1.84), 'D9': pad(-0.80, 1.84),
    'D8': pad(-3.34, 1.84), 'D7': pad(-5.88, 1.84),
}
Y_BOT = ys2y(-0.25)                 # XIAO bottom face
Y_WIRE = Y_BOT - WIRE_D / 2 - 0.25  # wire centre line in the bay
WR = WIRE_R_MIN


def _wire(name, pts, r=WR, d=WIRE_D, group='signal'):
    pts = _dedupe(pts)
    edges, radii = path_edges(pts, r)
    return dict(name=name, solid=sweep_circle(edges, d), min_radius=min(radii) if radii else None,
                length=sum(e.Length() for e in edges), pts=pts, d=d, group=group, r_req=r)


def _lane(name, x_lane, start, z_run, dest):
    """start (x,y,z) -> vertical drop to z_run -> +y to the bay -> -x onto the pad."""
    px, pz = PADS[dest]
    assert abs(pz - z_run) < 1e-6
    sx, sy, sz = start
    pts = [start, (x_lane, sy, z_run), (x_lane, Y_WIRE, z_run), (px, Y_WIRE, z_run)]
    return _wire(name, pts)


def radar_wires():
    """Wires soldered to the tips of header pins 2-5 (RX, OT1, GND, 3V3), HDR_SOLDER_Z above the tip."""
    xs = C.radar_pin_xs()
    yp = C.radar_pin_y() + HDR_PIN_T / 2 + WIRE_D / 2 + 0.05     # wire lies against the +y face of the pin (solder joint), 0.05 gap
    zs = RAD_Z0 - HDR_H + HDR_SOLDER_Z      # solder point on the pin
    plan = {'RX': 'D8', 'OT1': 'D7', 'GND': 'GND', '3V3': '3V3'}   # OT2 pin clipped
    out = []
    for i, pin in enumerate(RAD_PINS):
        if pin not in plan:
            continue
        dest = plan[pin]
        px, pz = PADS[dest]
        zl = zs + (1.2 if pin == 'GND' else 0.0)      # GND solders 1.2 mm higher on its pin so its route stays above the 3V3 wire
        if pz > zl - WR:
            # pad too close below the pin: leave toward +y at the solder level, slope onto the pad
            out.append(_wire(f'radar {pin} -> XIAO {dest}', [(xs[i], yp, zl), (xs[i], Y_WIRE, zl), (px, Y_WIRE, pz)]))
        else:
            out.append(_lane(f'radar {pin} -> XIAO {dest}', xs[i], (xs[i], yp, zl), pz, dest))
    return out


# battery / switch harness ---------------------------------------------------
# 24 AWG (OD WIRE_BAT_D, bend radius WIRE_BAT_R) from the holder through the protection board and the PB-22E08 to a solder splice
# above the holder; 28-30 AWG pigtails (WIRE_D) from the splice to the XIAO BAT pads (pad pitch 1.2 x 1.9 mm cannot take 2.0 mm wires).
_XC = BMS_X0 + BMS_W / 2
HOLDER_BLK = (_XC - 1.05, CY - HOLDER_Y / 2 - 0.05, 25.0)   # [GUESS] holder leads exit the -y end face at z 25, lined up with the board's B- / B+ pads
HOLDER_RED = (_XC + 1.05, CY - HOLDER_Y / 2 - 0.05, 25.0)
SPLICE_Z = {'BAT+': 110.0, 'BAT-': 107.8}


def _pw(name, pts):
    return _wire(name, pts, r=WIRE_BAT_R, d=WIRE_BAT_D, group='power')


def switch_wires(h=SW_H_DEFAULT):
    pins = C.switch_pin_xy()
    tip = SW_RECESS_OUT + h + SW_PIN_L
    zw = max(tip + WIRE_BAT_D / 2, 19.0)  # 24 AWG lies on the pin tips; >= 19.0 keeps it in the plug's thin-wall passage (z 16.9..20.9)
    R, Yr = WIRE_BAT_R, Y_RISER
    pad = C.bms_pads()
    out = []
    # jumpers: commons 2-5, and 3-6 (the pair that closes when latched; verify with a meter)
    for a, b in ((2, 5), (3, 6)):
        (xa, ya), (xb, yb) = pins[a], pins[b]
        out.append(_pw(f'jumper pin{a}-pin{b}', [(xa, ya + 0.6, zw), (xb, yb - 0.6, zw)]))
    x2, y2 = pins[2]
    x3, y3 = pins[3]
    # holder black (-) and red (+) leads straight up the end gap to the board's lower end (B-, B+)
    for nm, (lx, ly, lz), key in (('holder black (B-)', HOLDER_BLK, 'B-'), ('holder red (B+)', HOLDER_RED, 'B+')):
        px, py, pz = pad[key]
        out.append(_pw(f'{nm} -> board {key}', [(lx, ly, lz), (lx, Yr, lz), (px, Yr, pz - 0.05)]))
    # board P+ (upper end) -> up 3, over to the switch lane, down to the pin 2 level, along +y to pin 2
    px, py, pz = pad['P+']
    out.append(_pw('board P+ -> switch pin 2', [(px, Yr, pz + 0.05), (px, Yr, pz + 0.05 + R), (x2, Yr, pz + 0.05 + R), (x2, Yr, zw), (x2, y2 - 0.6, zw)]))
    # switch pin 3 -> splice -> 28-30 AWG pigtail to XIAO BAT+
    bx, bz = PADS['BAT+']
    zs = SPLICE_Z['BAT+']
    out.append(_pw('switch pin 3 -> BAT+ splice', [(x3, y3 - 0.6, zw), (x3, Yr, zw), (x3, Yr, zs), (bx, Y_WIRE - 6.0, zs)]))
    out.append(_wire('BAT+ splice -> XIAO BAT+ (28-30 AWG)', [(bx, Y_WIRE - 6.0, zs), (bx, Y_WIRE, zs), (bx, Y_WIRE, bz)], group='power'))
    # board P- (upper end) straight up the gap to the splice level, then to the BAT- splice and pigtail
    px, py, pz = pad['P-']
    nx, nz = PADS['BAT-']
    zs = SPLICE_Z['BAT-']
    out.append(_pw('board P- -> BAT- splice', [(px, Yr, pz + 0.05), (px, Yr, zs), (nx, Y_WIRE - 6.0, zs)]))
    out.append(_wire('BAT- splice -> XIAO BAT- (28-30 AWG)', [(nx, Y_WIRE - 6.0, zs), (nx, Y_WIRE, zs), (nx, Y_WIRE, nz)], group='power'))
    return out


def coax():
    x = 19.4
    start = (x, ys2y(2.4), xs2z(-8.45) + XIAO_DZ)
    yy = ANT_Y0 + ANT_T + 1.1
    pts = [start, (x, ys2y(2.4), 102.0), (x, yy - 4.4, 102.0), (CX, yy, 102.0), (CX, yy, ANT_Z0 - 0.5)]
    return _wire('U.FL coax -> antenna', pts, r=2.5, d=COAX_D, group='rf')


def all_wires(h=SW_H_DEFAULT):
    return radar_wires() + switch_wires(h) + [coax()]


def _dedupe(pts):
    res = [tuple(map(float, pts[0]))]
    for p in pts[1:]:
        if np.linalg.norm(np.array(p) - np.array(res[-1])) > 1e-6:
            res.append(tuple(map(float, p)))
    out = [res[0]]
    for i in range(1, len(res) - 1):
        a, b, c = map(np.array, (out[-1], res[i], res[i + 1]))
        if np.linalg.norm(np.cross(b - a, c - b)) > 1e-9:
            out.append(res[i])
    out.append(res[-1])
    return out
