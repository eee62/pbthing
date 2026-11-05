"""Render the simulation: per-step key frames (PNG), an MP4 of the whole assembly, and event close-ups.
Usage: python src/sim/render_sim.py [run.pkl] [outdir]"""
import os, sys, pickle, glob
import numpy as np, pyvista as pv, imageio.v2 as imageio
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE); ROOT = os.path.dirname(SRC)
sys.path.insert(0, HERE); sys.path.insert(0, SRC)
import meshes
pv.global_theme.background = 'white'

COL = {'insert': ('#6c8ebf', 0.28), 'radar': ('#2a9d8f', 1.0), 'tact': ('#444444', 1.0), 'keeper_a': ('#e07b39', 0.55),
       'camera': ('#222222', 1.0), 'keeper_b': ('#e0b339', 0.45), 'xiao': ('#2e8b57', 1.0), 'keeper_c': ('#b5412f', 0.45),
       'sleeve': ('#b0b0b0', 0.12)}
WIRE_COL = {'radar': '#d62828', 'button': '#f77f00', 'coax': '#ffbe0b', 'BAT': '#ff006e'}


def load_meshes():
    out = {}
    for n in COL:
        m = meshes.get(n)
        pm = pv.wrap(m)
        out[n] = (pm, (m.bounds[0] + m.bounds[1]) / 2.0)
    return out


def posed(pm, com, x, R):
    P = (np.asarray(pm.points) - com) @ R.T + x
    q = pm.copy(); q.points = P
    return q


def ribbon_mesh(pos, nr, nc, bend):
    P = pos.reshape(nr, nc, 3)
    pts = P.reshape(-1, 3)
    faces = []
    for r in range(nr - 1):
        for c in range(nc - 1):
            a, b = r * nc + c, r * nc + c + 1
            d, e = (r + 1) * nc + c, (r + 1) * nc + c + 1
            faces += [4, a, b, e, d]
    m = pv.PolyData(pts, np.array(faces))
    R = np.full(nr, 99.0)
    R[1:-1] = bend
    m['R'] = np.repeat(R, nc)
    return m


def wire_tube(pos, r):
    if len(pos) < 2:
        return None
    line = pv.lines_from_points(pos)
    return line.tube(radius=r, n_sides=8)


def draw_frame(pl, fr, M, meta, show_sleeve=True, hide=()):
    for n, (pm, com) in M.items():
        if n in hide or (n == 'sleeve' and not show_sleeve):
            continue
        x, R, act = fr['rigid'][n]
        # parts that are not yet in play sit on the bench: draw them faint at their staged pose
        colr, op = COL[n]
        if not act and n not in ('sleeve',):
            op = 0.18
        if n == 'sleeve' and not act:
            continue
        pl.add_mesh(posed(pm, com, x, R), color=colr, opacity=op, smooth_shading=False)
    for (name, kind, r, W, nr, nc, color, rmin) in meta:
        pos = fr['flex'][name]
        if kind == 'ribbon':
            rm = ribbon_mesh(pos, nr, nc, fr['bend'][name])
            pl.add_mesh(rm, scalars='R', cmap=['#d62828', '#f4d03f', '#2ca02c'], clim=[0, 4.0], show_scalar_bar=False,
                        opacity=1.0, smooth_shading=False, show_edges=False)
            pl.add_mesh(rm.extract_feature_edges(), color='black', line_width=1)
        else:
            t = wire_tube(pos, r)
            if t is not None:
                key = 'BAT' if name.startswith('BAT') else ('coax' if 'coax' in name else ('button' if name.startswith('button') else 'radar'))
                pl.add_mesh(t, color=WIRE_COL[key])
        pin = fr['pinch'][name]
        hit = np.where(pin > 0.03)[0]
        if len(hit):
            pl.add_mesh(pv.PolyData(pos[hit]), color='red', point_size=14, render_points_as_spheres=True)


VIEWS = {   # scale = half the visible height in mm (parallel projection); up = -z so the front face (z 140.5) is at the bottom, like the glass plate
    'side': dict(pos=(260, 40, 120), focal=(15, 40, 120), up=(0, 0, -1), scale=42),
    'oblique': dict(pos=(120, -90, 95), focal=(15, 36, 120), up=(0, 0, -1), scale=42),
    'xiao_close': dict(pos=(220, 42, 125), focal=(15, 42, 125), up=(0, 0, -1), scale=17),
    'radar_close': dict(pos=(220, 20, 131), focal=(15, 20, 131), up=(0, 0, -1), scale=12),
    'cam_close': dict(pos=(220, 50, 124), focal=(15, 50, 124), up=(0, 0, -1), scale=15),
    'cam_obl': dict(pos=(150, -20, 100), focal=(15, 50, 120), up=(0, 0, -1), scale=26),
}


def render(fr, M, meta, view='side', size=(900, 700), title='', zoom=None, hide=(), parallel=True, sleeve=True):
    pl = pv.Plotter(off_screen=True, window_size=size)
    draw_frame(pl, fr, M, meta, show_sleeve=sleeve, hide=hide)
    v = VIEWS[view]
    pl.camera_position = [v['pos'], v['focal'], v['up']]
    pl.enable_parallel_projection()
    pl.camera.parallel_scale = v['scale'] / (zoom or 1.0)
    if title:
        pl.add_text(title, font_size=10, color='black')
    img = pl.screenshot(return_img=True)
    pl.close()
    return img


def summarize(frames):
    steps = []
    for i, f in enumerate(frames):
        if not steps or steps[-1][0] != f['step']:
            steps.append([f['step'], i, i])
        else:
            steps[-1][2] = i
    return steps


def main(pkl, outdir):
    os.makedirs(outdir, exist_ok=True)
    d = pickle.load(open(pkl, 'rb')); frames = d['frames']; meta = d['flex_meta']
    M = load_meshes()
    steps = summarize(frames)
    # ---- key frames per step: start, 1/3, 2/3, end, + worst frame (max pinch or min ribbon radius)
    for label, i0, i1 in steps:
        sel = [i0, i0 + (i1 - i0) // 3, i0 + 2 * (i1 - i0) // 3, i1]
        worst = max(range(i0, i1 + 1), key=lambda k: max(frames[k]['pinch'][n].max() for n in frames[k]['pinch']))
        tiles = []
        for k in sel:
            tiles.append(render(frames[k], M, meta, 'side', (640, 520), f"{label}  t={frames[k]['t']:.2f}s"))
        tiles.append(render(frames[worst], M, meta, 'xiao_close', (640, 520), f"{label}: most-squeezed frame (red dots = squeezed wire/ribbon)"))
        tiles.append(render(frames[i1], M, meta, 'oblique', (640, 520), f"{label}: end state, oblique"))
        row1 = np.hstack(tiles[:3]); row2 = np.hstack(tiles[3:])
        imageio.imwrite(os.path.join(outdir, f"step_{label.split()[0]}_{label.split(' ', 1)[1].replace(' ', '_').replace('+', '')}.png"), np.vstack([row1, row2]))
        print('key frames', label, flush=True)
    # ---- movie: every k-th frame, side + close-up
    vid = os.path.join(outdir, 'assembly_simulation.mp4')
    w = imageio.get_writer(vid, fps=14, codec='libx264', quality=7, macro_block_size=None)
    stride = max(1, len(frames) // 220)
    for k in range(0, len(frames), stride):
        fr = frames[k]
        a = render(fr, M, meta, 'side', (800, 640), f"{fr['step']}   t={fr['t']:.2f} s")
        b = render(fr, M, meta, 'xiao_close', (800, 640), 'close-up: ribbon (colour = bend radius: red < 2 mm), wires, red dots = squeezed')
        w.append_data(np.hstack([a, b]))
    w.close()
    print('video', vid, flush=True)


if __name__ == '__main__':
    pkl = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'sim', 'run.pkl')
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'out', 'sim', 'render')
    main(pkl, out)
