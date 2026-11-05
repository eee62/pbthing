"""Tessellated meshes (device frame, mm) of every real part, cached as STL in out/sim/cache."""
import os, sys
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
CACHE = os.path.join(ROOT, 'out', 'sim', 'cache')
os.makedirs(CACHE, exist_ok=True)


def _tess(shape, tol=0.02, ang=0.2):
    vs, fs = shape.tessellate(tol, ang)
    v = np.array([[p.x, p.y, p.z] for p in vs]); f = np.array(fs)
    return trimesh.Trimesh(v, f, process=True)


def get(name):
    """Return a trimesh for 'insert','keeper_a','keeper_b','keeper_c','radar','tact','camera','xiao','sleeve','plug'."""
    path = os.path.join(CACHE, f'{name}.stl')
    if os.path.exists(path):
        return trimesh.load(path)
    import parts as P, components as C
    from geo import solid_of
    import cadquery as cq
    if name == 'sleeve':
        m = trimesh.load(os.path.join(ROOT, 'inputs', 'zen_v7_sleeve.stl'))
    elif name == 'xiao':
        ms = [_tess(s, 0.03) for _, s in C.xiao_parts()]
        m = trimesh.util.concatenate(ms)
    else:
        mk = {'insert': P.insert, 'keeper_a': P.keeper_a, 'keeper_b': P.keeper_b, 'keeper_b_slot': (lambda: P.keeper_b(slot=True)), 'keeper_b_noslot': (lambda: P.keeper_b(slot=False)), 'keeper_c': P.keeper_c,
              'radar': C.radar, 'tact': C.tact, 'camera': C.camera, 'plug': P.plug}[name]
        m = _tess(solid_of(mk()))
    m.export(path)
    return m
