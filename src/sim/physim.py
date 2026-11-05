"""Small physics engine for the assembly simulation (mm, s, N units; device frame, +z = toward the front face).

Rigid bodies : real tessellated meshes, exact signed-distance fields (VTK), contact = surface sample points vs the SDF
               of every other body, resolved by position-level push-out (translation + rotation), frictionless.
               The assembler's hand is a compliant follower of a scripted path: if the part cannot follow, it jams.
Flexible     : XPBD particles. Wire = chain with bending compliance. Ribbon = 3-wide strip (rows rigid across the
               width), stretch + shear + bending. Particles collide with the SDF of every rigid body at its CURRENT pose.
Events       : jam, rigid penetration, over-bend (radius below limit), taut (stretch), pinch (unresolved penetration).
"""
import numpy as np
from scipy.spatial.transform import Rotation as Rot

G = np.array([0.0, 0.0, 9810.0])          # gravity: the front face is on the glass, so "down" is +z


def box_inertia(mass, size):
    sx, sy, sz = size
    return mass / 12.0 * np.diag([sy**2 + sz**2, sx**2 + sz**2, sx**2 + sy**2])


class Rigid:
    def __init__(self, name, mesh, sdf, nsamp=2500, mass=None, rng=0, sample=True):
        import trimesh
        self.name, self.mesh, self.sdf = name, mesh, sdf
        lo, hi = mesh.bounds
        self.com = (lo + hi) / 2.0
        size = hi - lo
        self.mass = mass if mass else max(0.2e-3, abs(mesh.volume) * 1.2e-3 * 1e-3)       # kg (resin 1.2 g/cc)
        self.I = box_inertia(self.mass, size) * 1e-0
        self.Iinv = np.linalg.inv(self.I)
        if sample:
            pts = mesh.sample(nsamp, return_index=False) if len(mesh.faces) else mesh.vertices
            self.pb = np.vstack([pts, mesh.vertices[::max(1, len(mesh.vertices) // 1500)]]) - self.com
        else:
            self.pb = np.zeros((0, 3))
        self.x = self.com.copy(); self.R = np.eye(3)       # pose (final pose = identity)
        self.active = True
        self.local_aabb = np.array([lo - self.com, hi - self.com])
        self._aabb = None

    # --- pose ---
    def set_pose(self, x, R):
        self.x = np.asarray(x, float).copy(); self.R = np.asarray(R, float).copy(); self._aabb = None

    def translate_from_final(self, t):
        self.set_pose(self.com + np.asarray(t, float), self.R)

    def world(self, local_dev):
        """device-frame (final-pose) point(s) fixed to this body -> world."""
        return self.x + (np.atleast_2d(local_dev) - self.com) @ self.R.T

    def aabb(self):
        if self._aabb is None:
            lo, hi = self.local_aabb
            c = np.array([[a, b, d] for a in (lo[0], hi[0]) for b in (lo[1], hi[1]) for d in (lo[2], hi[2])])
            w = self.x + c @ self.R.T
            self._aabb = (w.min(0), w.max(0))
        return self._aabb

    def query(self, P):
        """world points -> (signed distance, world gradient)."""
        pd = (P - self.x) @ self.R + self.com                 # R^T (P-x) + com, row-vector form
        d, g = self.sdf.query(pd)
        return d, g @ self.R.T


def env_query(P, bodies, exclude=None, pad=1.5):
    """min signed distance over bodies (None entries and `exclude` skipped). Returns d, g, body index."""
    d = np.full(len(P), 1e9); g = np.zeros_like(P); bid = np.full(len(P), -1)
    for k, b in enumerate(bodies):
        if b is exclude or not b.active:
            continue
        lo, hi = b.aabb()
        m = np.all((P > lo - pad) & (P < hi + pad), axis=1)
        if not m.any():
            continue
        dd, gg = b.query(P[m])
        idx = np.where(m)[0]
        better = dd < d[idx]
        sel = idx[better]
        d[sel] = dd[better]; g[sel] = gg[better]; bid[sel] = k
    return d, g, bid


class Hand:
    """Compliant follower of a scripted target. Reports jam when the part lags the target."""
    def __init__(self, body, x0, R0, jam_mm=1.2):
        self.b, self.jam_mm = body, jam_mm
        self.tx = np.asarray(x0, float).copy(); self.tR = np.asarray(R0, float)

    def substep(self, bodies, dt, gain=0.35, max_v=60.0, iters=8, pen_tol=0.02, rot_gain=0.25):
        b = self.b
        e = self.tx - b.x
        step = e * gain
        n = np.linalg.norm(step)
        if n > max_v * dt:
            step *= max_v * dt / n
        # orientation follower (soft)
        rv = Rot.from_matrix(self.tR @ b.R.T).as_rotvec() * rot_gain
        b.set_pose(b.x + step, Rot.from_rotvec(rv).as_matrix() @ b.R)
        depth = 0.0; ncont = 0; where = None; other = None
        for it in range(iters):
            P = b.x + b.pb @ b.R.T
            d, g, bid = env_query(P, self.bodies_for_contact, exclude=b)
            pen = np.where(d < -1e-4)[0]
            if len(pen) == 0:
                depth = 0.0; ncont = 0
                break
            pen = pen[np.argsort(d[pen])][:80]
            nrm = g[pen] / np.maximum(np.linalg.norm(g[pen], axis=1, keepdims=True), 1e-9)
            dep = -d[pen]
            r = b.pb[pen] @ b.R.T
            rxn = np.cross(r, nrm)
            Iw = b.R @ b.Iinv @ b.R.T
            w = 1.0 / b.mass + np.einsum('ij,jk,ik->i', rxn, Iw, rxn)
            lam = dep / w
            k = len(pen)
            dx = (lam[:, None] * nrm).sum(0) / b.mass / k * 1.5
            dth = (Iw @ np.cross(r, lam[:, None] * nrm).sum(0).T) / k * 1.5 if False else \
                  (np.cross(r, lam[:, None] * nrm) @ Iw.T).sum(0) / k * 1.5
            b.set_pose(b.x + dx, Rot.from_rotvec(dth).as_matrix() @ b.R)
            depth = dep.max(); ncont = k; where = P[pen[0]].copy(); other = int(bid[pen[0]])
        return dict(err=float(np.linalg.norm(self.tx - b.x)), depth=float(depth), ncont=ncont, where=where, other=other)

    bodies_for_contact = []


class Flex:
    """XPBD particle body. kind 'wire' (chain) or 'ribbon' (rows of 3)."""
    def __init__(self, name, kind, pts, radius, width=0.0, EI=1.0, mu=0.25, rest_slack=0.0, color=None, rmin=2.0, kb=None):
        self.name, self.kind, self.r, self.W, self.EI, self.mu, self.rmin = name, kind, radius, width, EI, mu, rmin
        self.color = color
        self.kb = kb if kb is not None else (0.15 if kind == 'ribbon' else 0.12)
        pts = np.asarray(pts, float)
        self.nr = len(pts)                              # rows (ribbon) or particles (wire)
        if kind == 'ribbon':
            self.nc = 3
            offs = np.array([-width / 2, 0.0, width / 2])
            self.pos = np.concatenate([pts + [o, 0, 0] for o in offs], 0).reshape(3, self.nr, 3).transpose(1, 0, 2).reshape(-1, 3)
        else:
            self.nc = 1; self.pos = pts.copy()
        self.N = len(self.pos)
        self.prev = self.pos.copy(); self.vel = np.zeros_like(self.pos)
        self.w = np.ones(self.N)                        # inverse mass (relative), 0 = anchored
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        self.L0 = seg * (1.0 + rest_slack)              # rest segment lengths along the chain
        self.anchors = []                               # (idx array, owner, local points device frame) owner: Rigid | ('fixed', pts) | ('hand', fn)
        self._build()
        self.pinch = np.zeros(self.N); self.maxpen = np.zeros(self.N)
        self.hitbody = np.full(self.N, -1); self.nocol = np.zeros(self.N, bool)

    def _id(self, r, c):
        return r * self.nc + c

    def _build(self):
        nr, nc = self.nr, self.nc
        S = []                                           # stretch constraint sets: (I, J, L)
        r = np.arange(nr - 1)
        for par in (0, 1):
            rr = r[r % 2 == par]
            I = np.concatenate([[self._id(q, c) for q in rr] for c in range(nc)]); J = I + nc
            L = np.concatenate([self.L0[rr] for _ in range(nc)])
            S.append((I, J, L))
        if self.kind == 'ribbon':
            rows = np.arange(nr)
            hw = self.W / 2
            S.append((rows * 3, rows * 3 + 1, np.full(nr, hw)))
            S.append((rows * 3 + 1, rows * 3 + 2, np.full(nr, hw)))
            S.append((rows * 3, rows * 3 + 2, np.full(nr, self.W)))
            for a, b in ((0, 1), (1, 0), (1, 2), (2, 1)):          # shear diagonals
                I = r * 3 + a; J = (r + 1) * 3 + b
                S.append((I, J, np.sqrt(self.L0[r] ** 2 + hw ** 2)))
        self.S = S
        # bending triples per column, 3 colour sets by row index
        self.B = []
        mid = np.arange(1, nr - 1)
        for col in range(3):
            m = mid[mid % 3 == col]
            if len(m) == 0:
                continue
            ids = []
            for c in range(nc):
                ids.append(np.stack([(m - 1) * nc + c, m * nc + c, (m + 1) * nc + c], 1))
            T = np.concatenate(ids, 0)
            Lm = np.concatenate([(self.L0[m - 1] + self.L0[m]) / 2 for _ in range(nc)])
            self.B.append((T, Lm))

    # ------------------------------------------------------------------
    def anchor(self, idx, owner, local_dev=None):
        idx = np.atleast_1d(idx)
        self.anchors.append((idx, owner, None if local_dev is None else np.atleast_2d(np.asarray(local_dev, float))))
        self.w[idx] = 0.0

    def apply_anchors(self):
        for idx, owner, loc in self.anchors:
            if isinstance(owner, Rigid):
                self.pos[idx] = owner.world(loc)
            elif owner[0] == 'fixed':
                self.pos[idx] = owner[1]
            elif owner[0] == 'hand':
                self.pos[idx] = owner[1]()

    def center(self):
        return self.pos.reshape(self.nr, self.nc, 3).mean(1)

    def stretch_strain(self):
        c = self.center()
        L = np.linalg.norm(np.diff(c, axis=0), axis=1)
        return L / self.L0 - 1.0

    def bend_radius(self):
        """centerline bend radius at interior rows (mm); large = straight."""
        c = self.center()
        e1 = c[1:-1] - c[:-2]; e2 = c[2:] - c[1:-1]
        l1 = np.linalg.norm(e1, axis=1); l2 = np.linalg.norm(e2, axis=1)
        cs = np.clip(np.einsum('ij,ij->i', e1, e2) / np.maximum(l1 * l2, 1e-9), -1, 1)
        th = np.arccos(cs)
        return np.where(th > 1e-6, (l1 + l2) / 2 / np.maximum(th, 1e-9), 1e6)

    # ------------------------------------------------------------------
    def step(self, dt, bodies, iters=8, grav=True, damp=0.985, pen_tol=0.03, gq=0.004):
        """Quasi-static position-based relaxation (no inertia): hard stretch, soft bending (stiffness kb),
        anchors, SDF collision. gq = small gravity bias per call (mm) for wires; the ribbon's own weight is
        negligible against its stiffness (EI 18 N mm^2: ~0.03 mm sag) so it uses gq=0."""
        free = self.w > 0
        self.prev = self.pos.copy()
        if grav and self.kind == 'wire':
            self.pos[free] += np.array([0.0, 0.0, gq])
        self.apply_anchors()
        self.pinch[:] = 0.0
        for it in range(iters):
            for I, J, L in self.S:
                d = self.pos[J] - self.pos[I]
                l = np.maximum(np.linalg.norm(d, axis=1), 1e-9)
                C = l - L
                if self.kind == 'wire':
                    # a wire is limp: it can go slack (down to 70 % of the rest length, then it bunches), it cannot stretch.
                    C = np.where(l > L, l - L, np.minimum(0.0, l - 0.7 * L))
                wi, wj = self.w[I], self.w[J]
                den = wi + wj
                ok = den > 0
                s = np.where(ok, C / np.where(ok, den, 1.0), 0.0)
                corr = (s / l)[:, None] * d
                np.add.at(self.pos, I, corr * wi[:, None])
                np.add.at(self.pos, J, -corr * wj[:, None])
            for T, Lm in self.B:
                a, b, c = self.pos[T[:, 0]], self.pos[T[:, 1]], self.pos[T[:, 2]]
                e1, e2 = b - a, c - b
                l1 = np.maximum(np.linalg.norm(e1, axis=1), 1e-9); l2 = np.maximum(np.linalg.norm(e2, axis=1), 1e-9)
                t1, t2 = e1 / l1[:, None], e2 / l2[:, None]
                cs = np.einsum('ij,ij->i', t1, t2)
                sn = np.linalg.norm(np.cross(t1, t2), axis=1)
                th = np.arctan2(sn, cs)
                live = sn > 1e-5                                    # straight triples carry no bending correction
                sn_ = np.where(live, sn, 1.0)
                de2 = -(t1 - cs[:, None] * t2) / (sn_ * l2)[:, None]
                de1 = -(t2 - cs[:, None] * t1) / (sn_ * l1)[:, None]
                ga, gc = -de1, de2
                gb = de1 - de2
                wa, wb, wc = self.w[T[:, 0]], self.w[T[:, 1]], self.w[T[:, 2]]
                den = wa * (ga ** 2).sum(1) + wb * (gb ** 2).sum(1) + wc * (gc ** 2).sum(1)
                lam = np.where(live, -self.kb * th / np.maximum(den, 1e-9), 0.0)
                np.add.at(self.pos, T[:, 0], (wa * lam)[:, None] * ga)
                np.add.at(self.pos, T[:, 1], (wb * lam)[:, None] * gb)
                np.add.at(self.pos, T[:, 2], (wc * lam)[:, None] * gc)
            self.apply_anchors()
            self._collide(bodies, pen_tol, last=(it == iters - 1))
        self.vel = np.zeros_like(self.pos)

    def _collide(self, bodies, pen_tol, last):
        d, g, bid = env_query(self.pos, bodies, pad=self.r + 1.0)
        pen = d - self.r
        hit = np.where((pen < 0) & (self.w > 0) & (~self.nocol))[0]
        if len(hit):
            n = g[hit] / np.maximum(np.linalg.norm(g[hit], axis=1, keepdims=True), 1e-9)
            push = n * (-pen[hit])[:, None]
            self.pos[hit] += push
            # friction: remove part of the tangential motion this substep
            dp = self.pos[hit] - self.prev[hit]
            dn = np.einsum('ij,ij->i', dp, n)[:, None] * n
            tang = dp - dn
            self.pos[hit] -= self.mu * tang * 0.5
        if last:
            d2, g2, bid2 = env_query(self.pos, bodies, pad=self.r + 1.0)
            p2 = -(d2 - self.r)
            self.maxpen = np.maximum(self.maxpen * 0.0, p2)
            self.pinch = np.where((p2 > pen_tol) & (~self.nocol), p2, 0.0)
            self.hitbody = bid2
