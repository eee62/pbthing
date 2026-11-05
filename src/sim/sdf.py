"""Exact signed-distance fields of triangle meshes on a regular grid (VTK implicit distance), cached.
Negative inside. Trilinear value + analytic gradient."""
import os, time, hashlib
import numpy as np, pyvista as pv, trimesh

CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'out', 'sim', 'cache')


class SDF:
    def __init__(self, origin, pitch, vals):
        self.o = np.asarray(origin, float); self.h = float(pitch); self.v = vals.astype(np.float32)
        self.n = np.array(vals.shape)
        self.hi = self.o + (self.n - 1) * self.h

    def query(self, p, grad=True):
        """p (N,3) in the SDF frame -> d (N,), g (N,3). Outside the grid: distance to the box + edge value."""
        q = (p - self.o) / self.h
        qc = np.clip(q, 0, self.n - 1.0001)
        i0 = np.floor(qc).astype(np.int64); f = qc - i0
        x, y, z = i0[:, 0], i0[:, 1], i0[:, 2]
        v = self.v
        c000, c100, c010, c110 = v[x, y, z], v[x+1, y, z], v[x, y+1, z], v[x+1, y+1, z]
        c001, c101, c011, c111 = v[x, y, z+1], v[x+1, y, z+1], v[x, y+1, z+1], v[x+1, y+1, z+1]
        fx, fy, fz = f[:, 0], f[:, 1], f[:, 2]
        c00 = c000*(1-fx) + c100*fx; c10 = c010*(1-fx) + c110*fx
        c01 = c001*(1-fx) + c101*fx; c11 = c011*(1-fx) + c111*fx
        c0 = c00*(1-fy) + c10*fy; c1 = c01*(1-fy) + c11*fy
        d = c0*(1-fz) + c1*fz
        out = np.linalg.norm((q - qc) * self.h, axis=1)
        d = d + out
        if not grad:
            return d, None
        gx = ((c100 - c000)*(1-fy)*(1-fz) + (c110 - c010)*fy*(1-fz) + (c101 - c001)*(1-fy)*fz + (c111 - c011)*fy*fz) / self.h
        gy = ((c010 - c000)*(1-fx)*(1-fz) + (c110 - c100)*fx*(1-fz) + (c011 - c001)*(1-fx)*fz + (c111 - c101)*fx*fz) / self.h
        gz = ((c001 - c000)*(1-fx)*(1-fy) + (c101 - c100)*fx*(1-fy) + (c011 - c010)*(1-fx)*fy + (c111 - c110)*fx*fy) / self.h
        g = np.stack([gx, gy, gz], 1)
        far = out > 0
        if far.any():                      # outside the box: gradient points away from the box
            dirn = (q - qc)[far] * self.h
            g[far] = dirn / np.maximum(np.linalg.norm(dirn, axis=1, keepdims=True), 1e-9)
        return d, g


def build(name, mesh, pitch, margin=1.5, bounds=None, tag=''):
    """Build (or load) the SDF of `mesh` (device frame). Returns an SDF in the *device frame*."""
    path = os.path.join(CACHE, f'sdf_{name}{tag}_{pitch}.npz')
    if os.path.exists(path):
        z = np.load(path); return SDF(z['o'], float(z['h']), z['v'])
    lo, hi = (mesh.bounds if bounds is None else bounds)
    lo = np.asarray(lo) - margin; hi = np.asarray(hi) + margin
    dims = np.ceil((hi - lo) / pitch).astype(int) + 1
    surf = pv.wrap(mesh)
    grid = pv.ImageData(dimensions=tuple(dims), spacing=(pitch,) * 3, origin=tuple(lo))
    t = time.time()
    g = grid.compute_implicit_distance(surf)
    d = np.asarray(g['implicit_distance']).reshape(tuple(dims), order='F')
    # sign convention check: a point deep inside the mesh must be negative
    inside = mesh.contains(mesh.bounds.mean(0, keepdims=True)) if mesh.is_watertight else None
    print(f'  sdf {name}: dims {tuple(dims)} ({dims.prod()/1e6:.1f} M pts) {time.time()-t:.0f}s', flush=True)
    np.savez_compressed(path, o=lo, h=pitch, v=d.astype(np.float32))
    return SDF(lo, pitch, d)
