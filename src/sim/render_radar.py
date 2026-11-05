"""Render the radar-behind-window study (frames recorded by radar_study.py) as section views through the sleeve.
Usage: python src/sim/render_radar.py  -> out/sim/render/radar_*.png"""
import os, sys, pickle, json
import numpy as np, pyvista as pv, imageio.v2 as imageio
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE); ROOT = os.path.dirname(SRC)
sys.path.insert(0, HERE); sys.path.insert(0, SRC)
import meshes
pv.global_theme.background = 'white'
OUT = os.path.join(ROOT, 'out', 'sim', 'render'); os.makedirs(OUT, exist_ok=True)


def posed(pm, com, x, R):
    q = pm.copy(); q.points = (np.asarray(pm.points) - com) @ R.T + x
    return q


def section_lines():
    sec = meshes.get('sleeve').section(plane_origin=(0, 38.6, 0), plane_normal=(0, 1, 0))
    out = pv.PolyData()
    for e in sec.entities:
        P = sec.vertices[e.points]
        out = out.merge(pv.lines_from_points(P), merge_points=False)
    return out


def frame(sleeve_half, radar_pm, rcom, x, R, title, plane='xz', size=(520, 520), zoom=2.5, mark=None):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.add_mesh(sleeve_half, color='#9aa5b1', opacity=0.35, smooth_shading=False)
    pl.add_mesh(SEC, color='black', line_width=3)
    pl.add_mesh(posed(radar_pm, rcom, x, R), color='#2a9d8f')
    if mark is not None:
        pl.add_mesh(pv.Line((-2, 38.6, mark), (32, 38.6, mark)), color='#d62828', line_width=2)
    if plane == 'xz':       # looking along +y at the half-sleeve y >= 38.6, z up
        pl.camera_position = [(14.7, -150, 133), (14.7, 38.6, 133), (0, 0, 1)]
    pl.enable_parallel_projection(); pl.camera.zoom(zoom)
    pl.add_text(title, font_size=9, color='black')
    img = pl.screenshot(return_img=True); pl.close()
    return img


def main():
    d = pickle.load(open(os.path.join(ROOT, 'out', 'sim', 'radar_study.pkl'), 'rb'))
    res = json.load(open(os.path.join(ROOT, 'out', 'sim', 'radar_study.json')))
    rcom = d['radar_com']
    sl = pv.wrap(meshes.get('sleeve'))
    global SEC
    SEC = section_lines()
    half = sl.clip(normal=(0, 1, 0), origin=(0, 38.6, 0), invert=False)       # keep y >= 38.6 (far half, seen from -y)
    half = half.clip(normal=(0, 0, 1), origin=(0, 0, 118.0), invert=False)      # only z >= 118 matters here
    rm = pv.wrap(meshes.get('radar'))
    rows = []
    for r in res:
        log = d['logs'][r['case']]
        n = len(log); sel = [0, n // 3, 2 * n // 3, n - 1]
        tiles = []
        for k in sel:
            x, R = log[k]
            tiles.append(frame(half, rm, rcom, x, R, f"{r['case'][:34]}", mark=139.7))
        verdict = ('JAM' if r['jam'] else 'passes') + f"  tilt {r['final_tilt_deg']}  H={r['H_at_centre_mm']} mm"
        t = np.hstack(tiles)
        rows.append(t)
        imageio.imwrite(os.path.join(OUT, 'radar_' + r['case'].split()[0] + '.png'), t)
        print(r['case'], verdict, flush=True)
    imageio.imwrite(os.path.join(OUT, 'radar_all_cases.png'), np.vstack(rows))


if __name__ == '__main__':
    main()
