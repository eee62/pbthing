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
    x = FPC_X
    y0, y1, y2, y3 = FPC_Y_SLOT, FPC_Y_UP, FPC_Y_DOWN, FPC_Y_UP2
    zb = FPC_Z_STIFF + FPC_R1        # horizontal hop under the SD socket (centre line)
    return [
        (x, y0, FPC_Z_MOUTH),        # connector front
        (x, y0, zb),                 # corner -> bend toward +y (r FPC_R1)
        (x, y1, zb),                 # corner -> bend up (r FPC_R2)
        (x, y1, FPC_Z_APEX),         # corner \ 180 deg fold
        (x, y2, FPC_Z_APEX),         # corner /
        (x, y2, z_loop),             # corner \ U loop (r FPC_R_LOOP)
        (x, y3, z_loop),             # corner /
        (x, y3, FPC_Z_HEAD),         # corner -> 90 deg into head
        (x, CAM_Y1, FPC_Z_HEAD),   # head edge; FPC_HEAD_IN more is inside the head
    ]


FPC_RADII = [FPC_R1, FPC_R2, FPC_RFOLD, FPC_RFOLD, None, None, FPC_RHEAD]


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
    lo, hi = 60.0, FPC_Z_HEAD - FPC_R_LOOP - 3
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
                length=sum(e.Length() for e in edges), pts=pts, d=d, group=group)


def _lane(name, x_lane, start, z_run, dest):
    """start (x,y,z) -> vertical drop to z_run -> +y to the bay -> -x onto the pad."""
    px, pz = PADS[dest]
    assert abs(pz - z_run) < 1e-6
    sx, sy, sz = start
    pts = [start, (x_lane, sy, z_run), (x_lane, Y_WIRE, z_run), (px, Y_WIRE, z_run)]
    return _wire(name, pts)


def radar_wires():
    xs = C.radar_pin_xs()
    yp = C.radar_pin_y()
    z0 = RAD_Z0 - 1.0                      # below the J2 solder joint
    plan = {'RX': 'D8', 'OT1': 'D7', 'GND': 'GND', '3V3': '3V3'}   # OT2 not used
    out = []
    for i, pin in enumerate(RAD_PINS):
        if pin not in plan:
            continue
        dest = plan[pin]
        if pin == 'GND':
            # runs 1.2 mm under keeper A's tact bridge, then climbs gently onto the GND pad
            px, pz = PADS[dest]
            zr = KA_LOW_Z0_W
            pts = [(xs[i], yp, z0), (xs[i], yp, zr), (xs[i], Y_WIRE, zr), (xs[i] - 2.6, Y_WIRE, zr), (px, Y_WIRE, pz)]
            out.append(_wire(f'radar {pin} -> XIAO {dest}', pts))
        else:
            out.append(_lane(f'radar {pin} -> XIAO {dest}', xs[i], (xs[i], yp, z0), PADS[dest][1], dest))
    return out


KA_LOW_Z0_W = TACT_Z0 - 1.6 - 0.15 - WIRE_D / 2   # GND run level under keeper A bridge


def button_wires():
    z0 = TACT_Z0 - TACT_LEG_L - 0.3       # just below the leg tip
    (xa, ya), _, _, (xb, yb) = C.tact_leg_points()
    return [_lane('button leg A -> XIAO D10 (input, pull-up)', xa, (xa, ya, z0), PADS['D10'][1], 'D10'),
            _lane('button leg B -> XIAO D9 (driven LOW)', xb, (xb, yb, z0), PADS['D9'][1], 'D9')]


# battery / switch harness ---------------------------------------------------
HOLDER_RED = (16.0, CY - HOLDER_Y / 2 - 0.05, 25.0)    # [GUESS] lead exits on the -y end face
HOLDER_BLK = (12.0, CY - HOLDER_Y / 2 - 0.05, 25.0)
Y_RISER = 4.6                                           # wires run up the -y end gap
Z_SW_WIRE = None                                        # set per switch height


def switch_wires(h=SW_H_DEFAULT):
    pins = C.switch_pin_xy()
    tip = SW_RECESS_OUT + h + SW_PIN_L
    zw = max(tip + 0.45, 18.6)            # wire level above the pocket roof (17.95)
    out = []
    # jumpers: commons 2-5, and 3-6 (the pair that closes when latched; verify with a meter)
    for a, b in ((2, 5), (3, 6)):
        (xa, ya), (xb, yb) = pins[a], pins[b]
        out.append(_wire(f'jumper pin{a}-pin{b}', [(xa, ya + 0.6, zw), (xb, yb - 0.6, zw)], group='power'))
    x2, y2 = pins[2]
    x3, y3 = pins[3]
    # holder red (+) -> pin 2
    rx, ry, rz = HOLDER_RED
    out.append(_wire('holder B+ (red) -> switch pin 2',
                     [(rx, ry, rz), (rx, Y_RISER, rz), (rx, Y_RISER, zw), (x2, Y_RISER + 6.0, zw), (x2, y2 - 0.6, zw)],
                     group='power'))
    # pin 3 -> XIAO BAT+
    bx, bz = PADS['BAT+']
    out.append(_wire('switch pin 3 -> XIAO BAT+',
                     [(x3, y3 - 0.6, zw), (x3, Y_RISER, zw), (x3, Y_RISER, 110.0), (bx, Y_WIRE - 6.0, 110.0),
                      (bx, Y_WIRE, 110.0), (bx, Y_WIRE, bz)], group='power'))
    # holder black (-) -> XIAO BAT-
    kx, ky, kz = HOLDER_BLK
    nx, nz = PADS['BAT-']
    out.append(_wire('holder B- (black) -> XIAO BAT-',
                     [(kx, ky, kz), (kx, Y_RISER, kz), (kx, Y_RISER, 107.8), (nx, Y_WIRE - 6.0, 107.8),
                      (nx, Y_WIRE, 107.8), (nx, Y_WIRE, nz)], group='power'))
    return out


def coax():
    x = 19.4
    start = (x, ys2y(2.4), xs2z(-8.45) + XIAO_DZ)
    yy = ANT_Y0 + ANT_T + 1.1
    pts = [start, (x, ys2y(2.4), 102.0), (x, yy - 4.4, 102.0), (CX, yy, 102.0), (CX, yy, ANT_Z0 - 0.5)]
    return _wire('U.FL coax -> antenna', pts, r=2.5, d=COAX_D, group='rf')


def all_wires(h=SW_H_DEFAULT):
    return radar_wires() + button_wires() + switch_wires(h) + [coax()]


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
