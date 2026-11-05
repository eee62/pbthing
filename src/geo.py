"""Small CadQuery helpers (exact B-rep solids)."""
import math
import cadquery as cq


def box(x0, x1, y0, y1, z0, z1):
    assert x1 > x0 and y1 > y0 and z1 > z0, (x0, x1, y0, y1, z0, z1)
    return cq.Workplane().add(cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0)))


def cyl(cx, cy, z0, z1, d):
    return cq.Workplane().add(cq.Solid.makeCylinder(d / 2, z1 - z0, cq.Vector(cx, cy, z0)))


def cone(cx, cy, z0, z1, d0, d1):
    return cq.Workplane().add(cq.Solid.makeCone(d0 / 2, d1 / 2, z1 - z0, cq.Vector(cx, cy, z0)))


def rrect(x0, x1, y0, y1, z0, z1, r):
    w, h = x1 - x0, y1 - y0
    r = min(r, w / 2 - 1e-3, h / 2 - 1e-3)
    wp = (cq.Workplane('XY', origin=((x0 + x1) / 2, (y0 + y1) / 2, z0))
          .rect(w, h).extrude(z1 - z0))
    if r > 0.01:
        wp = wp.edges('|Z').fillet(r)
    return wp


def ring(cx, cy, z0, z1, d_in, d_out):
    return cyl(cx, cy, z0, z1, d_out).cut(cyl(cx, cy, z0 - 1, z1 + 1, d_in))


def solid_of(wp):
    """Return the single cq.Solid (or a compound if several) of a workplane."""
    v = wp.vals()
    if len(v) == 1:
        return v[0]
    return cq.Compound.makeCompound(v)


def union_all(items):
    it = [i for i in items if i is not None]
    r = it[0]
    for x in it[1:]:
        r = r.union(x)
    return r


def path_edges(pts, r):
    """Polyline through 3D points with every interior corner replaced by a circular arc of
    radius r (tangent). Returns (list of cq.Edge, list of actual radii)."""
    import numpy as np
    P = [np.array(p, float) for p in pts]
    edges, radii = [], []
    cur = P[0]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        u = (a - b) / np.linalg.norm(a - b)
        v = (c - b) / np.linalg.norm(c - b)
        ang = math.acos(max(-1.0, min(1.0, float(u @ v))))   # interior angle
        if abs(ang - math.pi) < 1e-6:
            continue
        t = r / math.tan(ang / 2)                             # tangent length
        used_prev = np.linalg.norm(cur - b)                   # length left on incoming segment
        assert t <= used_prev + 1e-6 and t <= np.linalg.norm(c - b) + 1e-6, \
            f'bend radius {r} too large at point {i}: needs {t:.2f}, have {used_prev:.2f}/{np.linalg.norm(c - b):.2f}'
        p1, p2 = b + u * t, b + v * t
        bis = (u + v) / np.linalg.norm(u + v)
        dc = r / math.sin(ang / 2)
        centre = b + bis * dc
        mid = centre - bis * r
        if np.linalg.norm(p1 - cur) > 1e-6:
            edges.append(cq.Edge.makeLine(cq.Vector(*cur), cq.Vector(*p1)))
        edges.append(cq.Edge.makeThreePointArc(cq.Vector(*p1), cq.Vector(*mid), cq.Vector(*p2)))
        radii.append(r)
        cur = p2
    if np.linalg.norm(P[-1] - cur) > 1e-6:
        edges.append(cq.Edge.makeLine(cq.Vector(*cur), cq.Vector(*P[-1])))
    return edges, radii


def sweep_circle(edges, d):
    path = cq.Wire.assembleEdges(edges)
    e0 = edges[0]
    p0 = e0.startPoint()
    t0 = e0.tangentAt(0)
    circ = cq.Wire.makeCircle(d / 2, p0, t0)
    return cq.Solid.sweep(circ, [], path, makeSolid=True, isFrenet=True)


def sweep_rect(edges, w, t, binormal=(1, 0, 0)):
    """Sweep a w x t rectangle (w along `binormal`) along the path. Used for the FPC whose
    bends are all about the x axis, so the width direction stays constant."""
    path = cq.Wire.assembleEdges(edges)
    e0 = edges[0]
    p0 = e0.startPoint()
    t0 = e0.tangentAt(0)
    bn = cq.Vector(*binormal)
    nrm = t0.cross(bn).normalized()
    c = [p0 + bn * (sx * w / 2) + nrm * (sy * t / 2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    rect = cq.Wire.makePolygon(c, close=True)
    return cq.Solid.sweep(rect, [], path, makeSolid=True, isFrenet=True)
