"""Render the assembly (needs out/assembly from build.py). Writes out/img/*.png"""
import os, glob
import numpy as np
import pyvista as pv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, 'out', 'assembly')
IMG = os.path.join(ROOT, 'out', 'img')
os.makedirs(IMG, exist_ok=True)
pv.global_theme.background = 'white'

COL = {
    'sleeve_rebuilt': ('#b9bcc2', 1.0), 'insert': ('#3d6fb6', 1.0), 'plug': ('#3d6fb6', 1.0),
    'keeper_a': ('#e07b39', 1.0), 'keeper_b': ('#e0b339', 1.0), 'keeper_c': ('#c2493d', 1.0),
    'carrier': ('#8e5bb5', 1.0), 'lens_cap': ('#222222', 1.0), 'usb_cover': ('#222222', 1.0),
    'cmp_radar': ('#2a9d8f', 1.0), 'cmp_bms': ('#555555', 1.0), 'cmp_camera': ('#111111', 1.0),
    'cmp_switch': ('#4a7fd4', 1.0), 'cmp_holder': ('#333333', 1.0), 'cmp_antenna': ('#d4af37', 1.0),
    'cmp_xiao': ('#1f6b3a', 1.0), 'wire_fpc': ('#d98c1f', 1.0),
}
WIRECOL = {'signal': '#e63946', 'power': '#ff006e', 'rf': '#ffbe0b'}


def load(names=None, skip=()):
    meshes = {}
    for f in sorted(glob.glob(os.path.join(A, '*.stl'))):
        n = os.path.basename(f)[:-4]
        if (names and n not in names) or n in skip:
            continue
        meshes[n] = pv.read(f)
    return meshes


def colour(n):
    if n in COL:
        return COL[n]
    for g, c in WIRECOL.items():
        if n.startswith(f'wire_{g}'):
            return (c, 1.0)
    return ('#999999', 1.0)


def shot(meshes, fname, cam, clip=None, size=(1600, 1200), offsets=None, title=None, opac=None, parallel=True,
         zoom=1.0, labels=None, fit=False):
    p = pv.Plotter(off_screen=True, window_size=size)
    for n, m in meshes.items():
        mm = m.copy()
        if offsets and n in offsets:
            mm = mm.translate(offsets[n], inplace=False)
        if clip is not None:
            mm = mm.clip(normal=clip[0], origin=clip[1], invert=True)
            if mm.n_points == 0:
                continue
        c, o = colour(n)
        if opac and n in opac:
            o = opac[n]
        p.add_mesh(mm, color=c, opacity=o, smooth_shading=False, specular=0.2)
    p.camera_position = cam
    if parallel:
        p.enable_parallel_projection()
    if fit:
        p.reset_camera()
    p.camera.zoom(zoom)
    if title:
        p.add_text(title, font_size=12, color='black')
    if labels:
        pts = np.array([l[0] for l in labels])
        p.add_point_labels(pts, [l[1] for l in labels], font_size=14, point_size=6, shape_opacity=0.8,
                           always_visible=True)
    p.screenshot(os.path.join(IMG, fname))
    p.close()


def main():
    m = load()
    full = dict(m)
    c = (14.7, 38.6, 70)
    # 1 front face
    shot({k: v for k, v in full.items() if k in ('sleeve_rebuilt', 'insert', 'lens_cap', 'usb_cover')},
         'front.png', [(14.7, 38.6, 400), (14.7, 38.6, 140), (1, 0, 0)], title='Front face (z = 140.5)', zoom=1.6)
    # 1b front, caps removed, perspective
    shot({k: v for k, v in full.items() if k in ('sleeve_rebuilt', 'insert', 'cmp_camera', 'cmp_xiao')},
         'front_caps_off.png', [(80, -40, 230), (14.7, 38.6, 135), (0, 0, 1)], parallel=False,
         title='Front, caps removed (USB-C and lens visible)', zoom=2.2)
    # 2 bottom face
    shot({k: v for k, v in full.items() if k in ('sleeve_rebuilt', 'plug', 'cmp_switch', 'carrier')},
         'bottom.png', [(14.7, 38.6, -300), (14.7, 38.6, 0), (1, 0, 0)], title='Bottom face (z = 0): latching switch in dimple', zoom=1.6)
    # 3 exploded
    off = {'insert': (0, 0, 60), 'keeper_a': (0, 0, 30), 'keeper_b': (0, 0, 30), 'keeper_c': (0, 0, 22),
           'lens_cap': (0, 0, 80), 'usb_cover': (0, 0, 80), 'cmp_radar': (0, 0, 45), 'cmp_bms': (0, 0, 45),
           'cmp_camera': (0, 0, 45), 'cmp_xiao': (0, 0, 38), 'wire_fpc': (0, 0, 38), 'cmp_antenna': (0, 0, 38),
           'plug': (0, 0, -70), 'carrier': (-25, 0, -70), 'cmp_switch': (-25, 0, -70), 'cmp_holder': (0, 0, -35)}
    ex = {k: v for k, v in full.items() if not k.startswith('wire_') or k == 'wire_fpc'}
    shot(ex, 'exploded.png', [(260, -220, 160), (14.7, 38.6, 75), (0, 0, 1)], offsets=off,
         opac={'sleeve_rebuilt': 0.18}, parallel=True, title='Exploded (sleeve translucent)', zoom=1.1, fit=True,
         size=(1400, 1800))
    # 4 cross-section x = 14.7 through radar, button, USB, camera, switch
    sec = {k: v for k, v in full.items()}
    shot(sec, 'section_top_x14.7.png', [(300, 38.6, 128), (14.7, 38.6, 128), (0, 0, 1)], clip=((1, 0, 0), (14.7, 0, 0)),
         title='Section x = 14.7: radar | USB-C | camera | FPC', zoom=2.4)
    shot(sec, 'section_bottom_x14.7.png', [(300, 38.6, 18), (14.7, 38.6, 18), (0, 0, 1)], clip=((1, 0, 0), (14.7, 0, 0)),
         title='Section x = 14.7: plug, carrier, latching switch, holder', zoom=2.4)
    shot(sec, 'section_full_x14.7.png', [(400, 38.6, 70), (14.7, 38.6, 70), (0, 0, 1)], clip=((1, 0, 0), (14.7, 0, 0)),
         title='Section x = 14.7 (whole device)', zoom=0.9, size=(1000, 1700))
    shot(sec, 'section_y38.6_switch.png', [(14.7, -300, 15), (14.7, 38.6, 15), (0, 0, 1)], clip=((0, -1, 0), (0, 38.6, 0)),
         title='Section y = 38.6 through the switch (carrier slides in from -x)', zoom=3.0)
    # 5 wire routes (sleeve and holder translucent)
    wires = {k: v for k, v in full.items() if k.startswith('wire_') or k in ('cmp_xiao', 'cmp_radar', 'cmp_bms',
             'cmp_camera', 'cmp_switch', 'cmp_holder', 'cmp_antenna', 'keeper_c', 'sleeve_rebuilt')}
    shot(wires, 'wires_all.png', [(200, -160, 120), (14.7, 38.6, 70), (0, 0, 1)], opac={'sleeve_rebuilt': 0.12, 'cmp_holder': 0.35},
         parallel=True, title='Wire routes: red = signal, pink = battery/switch, yellow = coax, orange = camera FPC', zoom=1.1,
         fit=True, size=(1400, 1800))
    top = {k: v for k, v in full.items() if k.startswith('wire_') or k in ('cmp_xiao', 'cmp_radar', 'cmp_bms', 'cmp_camera',
           'cmp_antenna', 'keeper_a', 'keeper_c', 'keeper_b')}
    shot(top, 'wires_top.png', [(-70, -40, 100), (14.7, 40, 125), (0, 0, 1)], clip=((0, 0, -1), (0, 0, 104)),
         parallel=False, title='Top module wiring (insert hidden)', zoom=1.2, fit=True)
    shot(top, 'wires_top_side.png', [(300, 40, 125), (14.7, 40, 125), (0, 0, 1)], clip=((0, 0, -1), (0, 0, 104)),
         title='Top module, side view (insert hidden)', zoom=1.3, fit=True)
    # 6 coupon and tray (print files)
    for nm, cam in (('coupon', [(90, -60, 200), (14.7, 40, 135), (0, 0, 1)]), ('tray', [(50, -80, 120), (50, 31, 10), (0, 0, 1)])):
        mm = pv.read(os.path.join(ROOT, 'out', 'stl', f'{nm}.stl'))
        p = pv.Plotter(off_screen=True, window_size=(1600, 1200))
        p.add_mesh(mm, color='#3d6fb6' if nm == 'coupon' else '#8e5bb5', specular=0.3)
        p.camera_position = cam
        p.camera.zoom(1.3)
        p.add_text(f'{nm}.stl (print file)', font_size=12, color='black')
        p.screenshot(os.path.join(IMG, f'print_{nm}.png'))
        p.close()
    # 7 insert alone from below (structure)
    shot({k: v for k, v in full.items() if k in ('insert',)}, 'insert_from_below.png',
         [(120, -90, 60), (14.7, 38.6, 128), (0, 0, 1)], parallel=False, title='insert.stl from below', zoom=1.8)
    print('renders written to', IMG)


if __name__ == '__main__':
    main()
