"""Verification. Every check prints numbers and PASS/FAIL. Writes out/logs/verify.txt + verify.json.
Run after build.py:  python src/verify.py"""
import os, sys, json, math, time, itertools
import numpy as np
import cadquery as cq
import trimesh
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Vec

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa
import parts as P
import components as C
import wires as W
from geo import solid_of, box, cyl, rrect

ROOT = os.path.dirname(HERE)
LOG = []
RES = {}
FAILS = []


def out(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def check(name, ok, detail=''):
    out(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILS.append(name)
    return ok


def vol_common(a, b):
    ba, bb = a.BoundingBox(), b.BoundingBox()
    if (ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin
            or ba.zmax < bb.zmin or bb.zmax < ba.zmin):
        return 0.0
    return a.intersect(b).Volume()


def dist(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value()


def sweep(shape, vec):
    """Exact swept volume of a pure translation: shape U moved shape U prisms of all faces."""
    v = gp_Vec(*vec)
    pieces = [shape, shape.translate(cq.Vector(*vec))]
    for f in shape.Faces():
        pr = cq.Shape.cast(BRepPrimAPI_MakePrism(f.wrapped, v).Shape())
        vol = pr.Volume()
        if abs(vol) < 1e-9:
            continue
        if vol < 0:                        # reversed face orientation -> flip the prism
            pr = cq.Shape.cast(pr.wrapped.Reversed())
        pieces.append(pr)
    return cq.Compound.makeCompound(pieces)


def main():
    t0 = time.time()
    out('VERIFICATION REPORT  (all numbers in mm, mm3, degrees)')
    out('=' * 78)

    # ---------------------------------------------------------------- 0. sleeve model vs STL
    out('\n0. Sleeve: exact B-rep rebuild vs supplied STL')
    sl_mesh = trimesh.load(os.path.join(ROOT, 'inputs', 'zen_v7_sleeve.stl'))
    sleeve = solid_of(C.sleeve())
    vol_b = sleeve.Volume()
    out(f'  STL volume {sl_mesh.volume:.2f}  rebuilt volume {vol_b:.2f}  diff {vol_b - sl_mesh.volume:+.2f} '
        f'({100 * (vol_b - sl_mesh.volume) / sl_mesh.volume:+.3f} %)')
    pts = sl_mesh.vertices
    dmax = 0.0
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.gp import gp_Pnt
    for p_ in pts[::3]:
        vtx = cq.Vertex.makeVertex(*p_)
        dmax = max(dmax, dist(vtx, sleeve.Faces()[0]) if False else 0.0)
    # distance from STL vertices to the rebuilt surface (all vertices)
    shell = cq.Compound.makeCompound(sleeve.Faces())
    ds = [dist(cq.Vertex.makeVertex(*p_), shell) for p_ in pts]
    out(f'  max distance STL vertex -> rebuilt surface {max(ds):.4f} (n={len(ds)})')
    check('sleeve rebuild matches STL', max(ds) < 0.06 and abs(vol_b - sl_mesh.volume) / sl_mesh.volume < 0.002)
    RES['sleeve'] = dict(stl_vol=sl_mesh.volume, rebuilt_vol=vol_b, max_dev=max(ds))

    # ---------------------------------------------------------------- 1. printed parts are single solids
    out('\n1. Printed parts: single watertight solid (B-rep + exported STL)')
    printed = {'insert': P.insert(), 'plug': P.plug(), 'tray': P.tray(), 'coupon': P.coupon(),
               'keeper_a': P.keeper_a(), 'keeper_b': P.keeper_b(), 'keeper_c': P.keeper_c()}
    for h in SW_H_VARIANTS:
        printed[f'carrier_H{h:g}'] = P.carrier(h)
    for v, c in CAP_VARIANTS.items():
        printed[f'lens_cap_{v}'] = P.lens_cap(c)
        printed[f'usb_cover_{v}'] = P.usb_cover(c)
    RES['parts'] = {}
    for n, wp in printed.items():
        vals = wp.vals()
        valid = all(s.isValid() for s in vals)
        f = os.path.join(ROOT, 'out', 'stl', f'{n}.stl')
        if not os.path.exists(f):
            f = os.path.join(ROOT, 'out', 'stl', 'tray_parts', f'{n}.stl')
        m = trimesh.load(f) if os.path.exists(f) else None
        bodies = len(m.split(only_watertight=False)) if m is not None else -1
        wt = bool(m.is_watertight) if m is not None else False
        bb = vals[0].BoundingBox()
        ok = len(vals) == 1 and valid and wt and bodies == 1
        check(f'{n:16s}', ok, f'brep_solids={len(vals)} valid={valid} stl_watertight={wt} stl_bodies={bodies} '
              f'vol={sum(s.Volume() for s in vals):.1f} bbox={bb.xlen:.1f}x{bb.ylen:.1f}x{bb.zlen:.1f}')
        RES['parts'][n] = dict(volume=sum(s.Volume() for s in vals), bbox=[bb.xlen, bb.ylen, bb.zlen])
        mn = min(bb.xlen, bb.ylen, bb.zlen)
        if n in ('insert', 'plug', 'tray', 'coupon'):
            check(f'{n:16s} min build size >= 5 mm', mn >= 5.0, f'(smallest bbox side {mn:.1f})')

    # ---------------------------------------------------------------- 2. interference
    out('\n2. Interference, exact boolean volume, every pair of placed bodies (default switch H)')
    objs = {
        'sleeve': sleeve, 'insert': solid_of(printed['insert']), 'keeper_a': solid_of(printed['keeper_a']),
        'keeper_b': solid_of(printed['keeper_b']), 'keeper_c': solid_of(printed['keeper_c']),
        'plug': solid_of(printed['plug']), 'carrier': solid_of(P.carrier(SW_H_DEFAULT)),
        'radar': solid_of(C.radar()), 'tact': solid_of(C.tact()), 'camera': solid_of(C.camera()),
        'switch': solid_of(C.main_switch()), 'holder': solid_of(C.holder()), 'antenna': solid_of(C.antenna()),
        'lens_cap': solid_of(P.lens_cap(CAP_VARIANTS['A'], at_origin=False)),
        'usb_cover': solid_of(P.usb_cover(CAP_VARIANTS['A'], at_origin=False)),
    }
    fpc, finfo = W.fpc()
    objs['fpc'] = fpc
    wires = W.all_wires()
    for w in wires:
        objs['W:' + w['name']] = w['solid']
    xparts = C.xiao_parts()
    objs['xiao'] = cq.Compound.makeCompound([s for _, s in xparts])
    names = list(objs)
    worst = 0.0
    npairs = 0
    for a, b in itertools.combinations(names, 2):
        v = vol_common(objs[a], objs[b])
        npairs += 1
        if v > 1e-6:
            check(f'{a} x {b}', False, f'overlap {v:.4f} mm3')
        worst = max(worst, v)
    check(f'all {npairs} pairs of {len(names)} bodies', worst <= 1e-6, f'max overlap volume = {worst:.6f} mm3')
    RES['interference'] = dict(bodies=len(names), pairs=npairs, max_overlap=worst)
    # minimum gaps of the printed parts to their neighbours
    out('  minimum distance between neighbours (exact):')
    gaps = {}
    for a, b in [('insert', 'sleeve'), ('keeper_a', 'sleeve'), ('keeper_b', 'sleeve'), ('keeper_c', 'sleeve'),
                 ('plug', 'sleeve'), ('holder', 'sleeve'), ('insert', 'xiao'), ('keeper_c', 'xiao'), ('insert', 'radar'),
                 ('keeper_a', 'radar'), ('insert', 'camera'), ('keeper_b', 'camera'), ('insert', 'tact'),
                 ('fpc', 'xiao'), ('fpc', 'insert'), ('fpc', 'keeper_b'), ('fpc', 'camera'), ('fpc', 'holder'),
                 ('carrier', 'plug'), ('switch', 'carrier'), ('switch', 'plug'), ('holder', 'plug'),
                 ('lens_cap', 'insert'), ('usb_cover', 'insert'), ('lens_cap', 'camera'), ('usb_cover', 'xiao')]:
        d = dist(objs[a], objs[b])
        gaps[f'{a}-{b}'] = d
        out(f'    {a:10s} - {b:10s} {d:7.3f}')
    RES['gaps'] = gaps

    # ---------------------------------------------------------------- 3. assembly paths
    out('\n3. Assembly paths (exact swept volumes)')
    # 3a. everything of the top module below the lip top must be inside the lip opening
    lipprism = rrect(LIP_X0, LIP_X1, LIP_Y0, LIP_Y1, 50, LIP_Z1, LIP_R)
    below = box(-10, 40, -10, 90, 50, LIP_Z1)
    top_module = ['insert', 'keeper_a', 'keeper_b', 'keeper_c', 'radar', 'tact', 'camera', 'xiao', 'fpc', 'antenna',
                  'lens_cap', 'usb_cover'] + ['W:' + w['name'] for w in wires if w['group'] in ('signal', 'rf')]
    worst = 0.0
    for n in top_module:
        part = objs[n].intersect(below.val())
        if part.Volume() < 1e-9:
            continue
        outside = part.cut(lipprism.val()).Volume()
        worst = max(worst, outside)
        if outside > 1e-6:
            check(f'top module: {n} passes lip', False, f'{outside:.4f} mm3 outside lip opening')
    check('top module passes the 19.4 x 67.2 lip opening (all bodies below z=137 inside it)', worst <= 1e-6,
          f'max outside volume {worst:.6f}')
    # clearance of the top module to the lip edge
    lip_ring = sleeve.intersect(box(-1, 31, -1, 79, LIP_Z0, LIP_Z1).val())
    dmin = min(dist(objs[n], lip_ring) for n in top_module)
    out(f'  min clearance of the top module to the lip (final position) = {dmin:.3f}')
    # 3b. bottom module inside cavity prism
    cav = rrect(CAV_X0, CAV_X1, CAV_Y0, CAV_Y1, -5, LIP_Z0, CAV_R)
    bottom_module = ['plug', 'carrier', 'switch', 'holder'] + ['W:' + w['name'] for w in wires if w['group'] == 'power']
    worst = max(objs[n].cut(cav.val()).Volume() for n in bottom_module)
    check('bottom module (plug, carrier, switch, holder, power wires) inside cavity prism', worst <= 1e-6,
          f'max outside {worst:.6f}')
    # 3c. install sweeps in the face-down order
    out('  install order (insert face-down on glass): radar, tact -> keeper A -> camera -> keeper B -> XIAO -> keeper C')
    seq = [
        ('keeper_a', (0, 0, -40), ['insert', 'radar', 'tact']),
        ('keeper_b', (0, 0, -40), ['insert', 'radar', 'tact', 'keeper_a', 'camera']),
        ('keeper_c', (0, 0, -40), ['insert', 'radar', 'tact', 'keeper_a', 'camera', 'keeper_b', 'xiao', 'fpc', 'antenna']
         + ['W:' + w['name'] for w in wires if w['group'] in ('signal', 'rf')]),
        ('lens_cap', (0, 0, 10), ['insert', 'camera']),
        ('usb_cover', (0, 0, 10), ['insert', 'xiao']),
    ]
    for part, vec, obstacles in seq:
        sw = sweep(objs[part], vec)
        worst = 0.0
        hit = []
        for ob in obstacles:
            v = sum(vol_common(s, objs[ob]) for s in sw.Solids())
            # the part's own final position is allowed to touch nothing (already checked)
            if v > 1e-6:
                hit.append((ob, v))
            worst = max(worst, v)
        check(f'{part} install path {vec}', worst <= 1e-6, f'hits: {hit if hit else "none"}')
    # XIAO slides +z into the closed collar: sweep of its solids' bounding boxes (conservative)
    worst, hit = 0.0, []
    xb = []
    for nm, s in xparts:
        b = s.BoundingBox()
        if b.zmax > Z_PT - 1.0:            # parts that reach the collar: exact prism sweep
            xb += list(sweep(s, (0, 0, -40)).Solids())
        else:                              # the rest: conservative bounding-box sweep
            xb.append(box(b.xmin, b.xmax, b.ymin, b.ymax, b.zmin - 40, b.zmax).val())
    xsw = cq.Compound.makeCompound(xb)
    for ob in ['insert', 'radar', 'tact', 'keeper_a', 'camera', 'keeper_b']:
        v = vol_common(xsw, objs[ob])
        if v > 1e-6:
            hit.append((ob, v))
        worst = max(worst, v)
    check('XIAO stack install path +z (bounding boxes of all 90+ solids, conservative)', worst <= 1e-6,
          f'hits: {hit if hit else "none"}')
    # carrier + switch slide in along +x from outside the plug
    cs = objs['carrier'].fuse(objs['switch'])
    sw = sweep(cs, (-20, 0, 0))
    v = sum(vol_common(s, objs['plug']) for s in sw.Solids())
    check('carrier + switch slide into plug along +x (from -x side)', v <= 1e-6, f'overlap {v:.6f}')
    # plug sub-assembly enters the sleeve from the bottom (+z)
    plug_sub = cq.Compound.makeCompound([objs[n] for n in bottom_module])
    v = sum(vol_common(s, sleeve) for s in sweep(plug_sub, (0, 0, -150)).Solids())
    check('plug + holder + switch + power wires slide into the sleeve from below', v <= 1e-6, f'overlap {v:.6f}')
    # lowering from above: every point passes all sleeve bands above its final height. The lip
    # is the narrowest band (checked above); the bore band z 137..140.5 is checked here.
    bore = rrect(CAV_X0, CAV_X1, CAV_Y0, CAV_Y1, LIP_Z1, 200, CAV_R)
    band = box(-10, 40, -10, 90, LIP_Z1, 200)
    worst = 0.0
    for n in top_module:
        part = objs[n].intersect(band.val())
        if part.Volume() > 1e-9:
            worst = max(worst, part.cut(bore.val()).Volume())
    check('top module above the lip top stays inside the 24.4 x 72.2 bore (so it can be lowered in)', worst <= 1e-6,
          f'max outside {worst:.6f}')
    # captured parts: carrier is held in x by the sleeve wall, keepers by the seam glue
    d = dist(objs['carrier'], sleeve)
    check('switch carrier captured by sleeve wall (slide-out play)', d < 0.6, f'play {d:.3f} (< engagement 4.0)')

    # ---------------------------------------------------------------- 4. wall thickness / feature size
    out('\n4. Wall thickness and minimum features (ray casting on exported STL, opposite-face rays only)')
    RES['walls'] = {}
    for n in ['insert', 'plug', 'keeper_a', 'keeper_b', 'keeper_c', 'carrier_H13.5', 'lens_cap_A', 'usb_cover_A', 'coupon']:
        f = os.path.join(ROOT, 'out', 'stl', f'{n}.stl')
        if not os.path.exists(f):
            f = os.path.join(ROOT, 'out', 'stl', 'tray_parts', f'{n}.stl')
        m = trimesh.load(f)
        wall, gap = thickness(m)
        RES['walls'][n] = dict(min_wall=wall, min_gap=gap)
        check(f'{n:14s} min wall {wall:.3f} >= {MIN_WALL}', wall >= MIN_WALL - 0.02, '')
        g = gap if gap == gap else 99.0
        check(f'{n:14s} min internal gap/slot {g:.3f} >= {MIN_ENGRAVE} (no slot that could fuse shut)',
              g >= MIN_ENGRAVE - 0.02, '')

    # ---------------------------------------------------------------- 5. tolerance table
    out('\n5. Worst-case clearance per fit. Rule: worst = nominal - (tolA + tolB)/2 (- purchased-part tol)')
    tb = tolerance_table(gaps)
    RES['tolerances'] = tb
    for row in tb:
        if row.get('friction'):
            out(f"  [INFO] {row['fit']:58s} nominal {row['nominal']:.3f}  worst {row['worst']:+.3f}  "
                f"(friction option, see variant check below)")
            continue
        check(f"{row['fit']:58s}", row['worst'] >= -1e-9,
              f"nominal {row['nominal']:.3f}  tolA {row['tolA']}  tolB {row['tolB']}  worst {row['worst']:+.3f}")
    cs = sorted(CAP_VARIANTS.values())
    e = (TOL_HOLE + TOL) / 2
    loosest_worst = cs[-1] - e
    gaps_ok = all(b - a <= 0.101 for a, b in zip(cs, cs[1:]))
    check('cap/cover variant set: loosest variant always inserts (worst >= 0), steps <= 0.10',
          loosest_worst >= -1e-9 and gaps_ok,
          f"variants {cs}, combined per-side error +-{e:.2f}: actual clearance A {cs[0]-e:+.2f}..{cs[0]+e:+.2f}, "
          f"B {cs[1]-e:+.2f}..{cs[1]+e:+.2f}, C {cs[2]-e:+.2f}..{cs[2]+e:+.2f}")

    # ---------------------------------------------------------------- 6. wires
    out('\n6. Wires and ribbon: swept at real diameter, zero overlap with every body, minimum bend radius')
    RES['wires'] = []
    solids_all = {k: v for k, v in objs.items() if not k.startswith('W:') and k != 'fpc'}
    items = [dict(name=f'camera FPC {FPC_W:g} x {FPC_T:g}', solid=fpc, min_radius=finfo['min_radius'], length=finfo['length'],
                  d=FPC_T)] + wires
    for w in items:
        wb = w['solid'].BoundingBox()

        def near(s, m=3.0):
            b = s.BoundingBox()
            return not (wb.xmax + m < b.xmin or b.xmax + m < wb.xmin or wb.ymax + m < b.ymin or
                        b.ymax + m < wb.ymin or wb.zmax + m < b.zmin or b.zmax + m < wb.zmin)
        cand = [s for k, s in solids_all.items() if near(s)]
        clear = min(dist(w['solid'], s) for s in cand) if cand else 99.0
        others = [x for x in items if x is not w]
        clear_w = min(dist(w['solid'], x['solid']) for x in others)
        r = w['min_radius']
        ok = (r is None or r >= (FPC_R_MIN if 'FPC' in w['name'] else (2.5 if 'coax' in w['name'] else WIRE_R_MIN)) - 1e-6)
        check(f"{w['name']:42s}", ok and clear >= -1e-9,
              f"d={w['d']:.2f} len={w['length']:.1f} min_bend_r={r if r is None else round(r, 2)} "
              f"clear_to_solids={clear:.3f} clear_to_other_wires={clear_w:.3f}")
        RES['wires'].append(dict(name=w['name'], length=w['length'], min_radius=r, clear=clear, clear_wires=clear_w))
    out(f"  FPC: solved loop bottom z = {finfo['loop_bottom']:.2f} for length {FPC_LEN} "
        f"(holder top z = {HOLDER_Z0 + HOLDER_Z:.1f}, margin {finfo['loop_bottom'] - HOLDER_Z0 - HOLDER_Z:.1f})")
    for L in (40, 55, 75, 85):
        zb = W.solve_fpc_loop(L)
        out(f'     FPC length {L} mm -> loop bottom z {zb:.1f}')
    RES['fpc'] = finfo

    # ---------------------------------------------------------------- 7. main switch
    out('\n7. Latching switch: recess depths, travel, every height variant')
    RES['switch'] = []
    for h in SW_H_VARIANTS:
        car = solid_of(P.carrier(h))
        ok_all = True
        for state, tr in (('released', 0.0), ('latched', SW_LOCK_TRAVEL), ('full press', SW_FULL_TRAVEL)):
            swc = solid_of(C.main_switch(h, pressed=tr))
            # in the pressed state the body is held, knob moves into it: model knob only shortened
            v1 = vol_common(swc, objs['plug'])
            v2 = vol_common(swc, car)
            ok_all &= (v1 <= 1e-6 and v2 <= 1e-6)
        tip = SW_RECESS_OUT + h + SW_PIN_L
        top_room = HOLDER_Z0 - tip
        vcp = vol_common(car, objs['plug'])
        row = dict(H=h, recess_released=SW_RECESS_OUT, recess_latched=SW_RECESS_OUT + SW_LOCK_TRAVEL,
                   recess_full=SW_RECESS_OUT + SW_FULL_TRAVEL, pin_tip_z=tip, room_to_holder=top_room)
        RES['switch'].append(row)
        check(f'H={h:4.1f}: switch/carrier/plug no overlap in all 3 states, pins {top_room:.2f} below holder',
              ok_all and vcp <= 1e-6 and top_room >= 2.4,
              f'recess released {row["recess_released"]:.2f} | latched {row["recess_latched"]:.2f} | full {row["recess_full"]:.2f}')
    out(f'  knob travel: lock {SW_LOCK_TRAVEL} +-0.15, full {SW_FULL_TRAVEL} +-0.2 (datasheet); '
        f'knob tip never protrudes: released recess {SW_RECESS_OUT} - tolerance 0.4 = {SW_RECESS_OUT - 0.4:.2f} > 0')
    out(f'  finger dimple: cone D{P.DIMPLE_D2} -> D{P.KNOB_HOLE_D2} over {DIMPLE_DEPTH} mm; '
        f'fingertip (sphere R8) reach into D{P.DIMPLE_D2}: {8 - math.sqrt(64 - (P.DIMPLE_D2 / 2) ** 2):.2f} mm (rigid) '
        f'< full-press depth {SW_RECESS_OUT + SW_FULL_TRAVEL:.1f} -> use a pen tip / nail (finger NOT guaranteed)')

    # ---------------------------------------------------------------- 8. engraving + button flexure
    out('\n8. Front button: engraved icon and flexure')
    icon = P.power_icon()
    bb = icon.val().BoundingBox()
    depth = Z_FRONT - bb.zmin
    sec = section_polys(icon.val(), Z_FRONT - 0.4)
    width = min_feature_width(sec)
    pad_disk = Point(BTN_X, BTN_Y).buffer(BTN_D / 2, 256)
    land = pad_disk.difference(sec)
    land_w = min_feature_width(land, inner=True)
    edge_margin = BTN_D / 2 - max(Point(BTN_X, BTN_Y).distance(Point(c)) for g in getattr(sec, 'geoms', [sec])
                                  for c in g.exterior.coords)
    check('icon depth >= 0.8', depth >= MIN_ENGRAVE - 1e-6, f'depth {depth:.3f}')
    check('icon line width >= 0.8', width >= MIN_ENGRAVE - 0.01, f'min line width {width:.3f}')
    check('icon land (material between strokes) >= 0.8', land_w >= MIN_ENGRAVE - 0.01, f'min land {land_w:.3f}')
    check('icon inside pad', edge_margin >= 0.5, f'margin to pad edge {edge_margin:.3f}')
    L = BEAM_ROOT_X - BTN_X
    Lb = BEAM_ROOT_X - (BTN_X + BTN_D / 2)
    a = L - Lb
    delta = BTN_PRE + TACT_TRAVEL
    # cantilever of length Lb with rigid extension a: tip-load F at distance L from root
    I = BEAM_W * BEAM_T ** 3 / 12
    defl_per_F = (Lb ** 3 / 3 + Lb ** 2 * a / 2 * 2 + Lb * a ** 2) / (E_RESIN * I)   # deflection at load point per N
    F = delta / defl_per_F
    strain = (F * L) * (BEAM_T / 2) / I / E_RESIN
    check('button flexure strain at full travel < 1 %', strain < ELONG_SAFE,
          f'travel {delta:.2f} (pre {BTN_PRE} + switch {TACT_TRAVEL}), beam {Lb:.1f} x {BEAM_W} x {BEAM_T}, '
          f'lever {L:.1f}: force {F:.2f} N, root strain {100 * strain:.2f} %')
    RES['button'] = dict(icon_depth=depth, icon_width=width, land=land_w, flex_strain=strain, flex_force=F)

    # ---------------------------------------------------------------- 9. radar window, lens FOV
    out('\n9. Radar window and lens field of view')
    for er in (2.6, 3.0, 3.4, 3.8):
        l8 = 299.792458 / 24.125 / math.sqrt(er) / 8
        out(f'  er={er}: lambda/8 in resin = {l8:.2f} mm  -> window {WIN_T} {"<=" if WIN_T <= l8 else ">"} lambda/8')
    h_air = (Z_FRONT - WIN_T) - RAD_Z1
    out(f'  antenna plane to window inner surface H = {h_air:.2f} mm (Hi-Link guide prefers 6.2 / 12.4; '
        f'<6.2 needs testing) -> RISK, coupon includes the real window for a range test')
    a_cb = math.degrees(math.atan((CAP_POCKET_D / 2 - LENS_FRONT_D / 2) / (Z_FRONT - CAM_TOP)))
    a_op = math.degrees(math.atan((LENS_OPEN_D / 2 - LENS_FRONT_D / 2) / (Z_FRONT - CAP_T - CAM_TOP)))
    fov = 2 * min(a_cb, a_op)
    check(f'lens FOV not vignetted up to {LENS_FOV_DEG:.0f} deg (assumed lens)', fov >= LENS_FOV_DEG,
          f'unvignetted full angle {fov:.1f} deg (cap pocket limit {2 * a_cb:.1f}, opening limit {2 * a_op:.1f})')
    RES['optics'] = dict(radar_H=h_air, fov=fov)
    w_cap = (CAM_Y - CAP_POCKET_D / 2) - (USB_Y + OVM_H / 2)
    w_head = (CAM_Y0 - CAM_POCKET_CLR) - (USB_Y + OVM_H / 2)
    w_btn = (USB_Y - OVM_H / 2) - (BTN_Y + BTN_D / 2) if 'BTN_D' in globals() else None
    check('USB-C pocket %.1f x %.1f: wall to cap pocket >= 0.8 mm' % (OVM_W, OVM_H), w_cap >= 0.8, f'{w_cap:.2f} mm (cap pocket, y); to camera head pocket {w_head:.2f} mm')
    check('lens hole land ring (cap pocket minus lens hole) >= 1.5 mm', (CAP_POCKET_D - LENS_OPEN_D) / 2 >= 1.5, f'{(CAP_POCKET_D - LENS_OPEN_D) / 2:.2f} mm per side')

    # ---------------------------------------------------------------- summary
    out('\n' + '=' * 78)
    out(f'FAILED CHECKS: {len(FAILS)}' + ('' if not FAILS else ' -> ' + '; '.join(FAILS)))
    out(f'run time {time.time() - t0:.0f} s')
    with open(os.path.join(ROOT, 'out', 'logs', 'verify.txt'), 'w') as f:
        f.write('\n'.join(LOG) + '\n')
    with open(os.path.join(ROOT, 'out', 'logs', 'verify.json'), 'w') as f:
        json.dump(RES, f, indent=1, default=float)
    return len(FAILS)


# ------------------------------------------------------------------ helpers
def thickness(m, n=15000, seed=3):
    """Min wall (inward ray to an opposite face) and min internal gap (outward ray to an
    opposite face of the same part, < 3 mm)."""
    pts, fi = trimesh.sample.sample_surface_even(m, n, seed=seed)
    nrm = m.face_normals[fi]
    rmi = trimesh.ray.ray_triangle.RayMeshIntersector(m)
    walls, gaps = [], []
    for sign, store, eps in ((-1, walls, 1e-4), (1, gaps, 1e-4)):
        org = pts + sign * nrm * eps
        loc, ri, tri = rmi.intersects_location(org, sign * nrm, multiple_hits=True)
        best = {}
        for L, r, t in zip(loc, ri, tri):
            d = np.linalg.norm(L - org[r])
            if d < 1e-3:
                continue
            if r not in best or d < best[r][0]:
                best[r] = (d, t)
        for r, (d, t) in best.items():
            if np.dot(nrm[r], m.face_normals[t]) < -0.95:
                if sign < 0 or d < 3.0:
                    store.append(d)
    return (min(walls) if walls else float('nan')), (min(gaps) if gaps else float('nan'))


def section_polys(shape, z):
    sl = shape.intersect(cq.Solid.makeBox(100, 100, 0.001, cq.Vector(-20, -20, z)))
    polys = []
    for f in sl.Faces():
        if abs(f.normalAt().z) > 0.99 and abs(f.Center().z - z) < 0.01:
            polys.append(face_polygon(f))
    return unary_union(polys)


def wire_coords(w):
    """Ordered, discretised 2D coordinates of a wire (BRepTools_WireExplorer keeps order)."""
    from OCP.BRepTools import BRepTools_WireExplorer
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    ex = BRepTools_WireExplorer(w.wrapped)
    pts = []
    while ex.More():
        e = ex.Current()
        c = BRepAdaptor_Curve(e)
        t0, t1 = c.FirstParameter(), c.LastParameter()
        ts = np.linspace(t0, t1, 48)
        if e.Orientation().name == 'TopAbs_REVERSED':
            ts = ts[::-1]
        for t in ts:
            p = c.Value(t)
            pts.append((p.X(), p.Y()))
        ex.Next()
    return pts


def face_polygon(f):
    outer = Polygon(wire_coords(f.outerWire())).buffer(0)
    for iw in f.innerWires():
        outer = outer.difference(Polygon(wire_coords(iw)).buffer(0))
    return outer


def min_feature_width(geom, inner=False):
    """Smallest neck/stroke width: 2 * the largest erosion radius that keeps the same number
    of connected pieces, none vanishing (sharp corners do not count, unlike an area test)."""
    def npieces(g):
        return 0 if g.is_empty else len(getattr(g, 'geoms', [g]))
    n0 = npieces(geom)
    lo, hi = 0.0, 1.5
    for _ in range(40):
        mid = (lo + hi) / 2
        g2 = geom.buffer(-mid, 64)
        ok = (npieces(g2) == n0) and all(p.area > 1e-9 for p in getattr(g2, 'geoms', [g2]))
        if ok:
            lo = mid
        else:
            hi = mid
    return 2 * lo


def tolerance_table(g):
    T = TOL
    H = TOL_HOLE
    rows = []

    def r(fit, nominal, tolA, tolB, extra=0.0, note=''):
        rows.append(dict(fit=fit, nominal=nominal, tolA=tolA, tolB=tolB, extra=extra,
                         worst=nominal - (tolA + tolB) / 2 - extra, note=note))
    r('faceplate edge to sleeve bore (per side)', G_FACE, T, T)
    r('insert / keepers to lip opening (per side)', G_LIP, T, T)
    r('pads to lip top (glue line, z)', G_GLUE, T, T)
    r('keeper ears to lip top (z)', P.EAR_Z0 - LIP_Z1, T, T)
    r('keeper ears to faceplate rim (z, glue fills; foot/posts touch first)', HOVER, T, T, note='>=0 means the keeper rests on its part, not on the rim')
    r('radar PCB to radar pocket walls (per side)', RAD_POCKET_CLR, T, 0.2, note='radar 20.0 +-0.1 [GUESS tol]')
    r('radar PCB back to lip top (z, PCB overhangs lip 0.3)', RAD_Z0 - LIP_Z1, T, T, extra=RAD_T_TOL)
    r('radar front components to window (z)', RAD_FRONT_GAP, T, 0.0, note='component height is [GUESS]')
    r('tact switch to its pocket (per side)', 0.25, T, 0.2)
    r('button nub to tact actuator (pre-travel)', BTN_PRE, T, 0.2)
    r('button pad ring slot (single part, stays open)', BTN_SLOT, T, T, extra=0.0)
    r('hidden beam to skin gap (single part, stays open)', BEAM_TOP_GAP, T, T)
    r('USB-C shell to collar opening (hole, per side)', COLLAR_CLR, H, 0.2)
    r('XIAO bottom face to top rib (backup stop)', ys2y(-0.25) - (ys2y(-0.25) - 0.30), T, 0.2)
    r('XIAO bottom face to keeper C -y wall', 0.20, T, 0.2)
    r('XIAO connector housing to keeper C +y lip', P.LIP_Y0_ - ys2y(7.18), T, 0.2)
    r('camera head to pocket (per side)', CAM_POCKET_CLR, T, 0.2, note='head size [GUESS]')
    r('lens barrel to lens opening (hole Ø%.1f, per side)' % LENS_OPEN_D, (LENS_OPEN_D - CAM_BARREL_D) / 2, LENS_HOLE_TOL, 0.2, note='hole tol +-0.3 [USER], barrel +-0.2 [GUESS]')
    r('lens barrel top to cap underside (z)', CAP_UNDER_GAP, T, T, extra=0.1)
    for v, c in CAP_VARIANTS.items():
        r(f'lens cap {v} in cap pocket (hole, per side)', c, H, T, note='friction fit: pick the variant that holds')
        rows[-1]['friction'] = v != 'C'
        r(f'USB cover {v} in overmold pocket (per side)', c, H, T, note='friction fit')
        rows[-1]['friction'] = v != 'C'
    r(f'cable overmold {CABLE_W} x {CABLE_H} in pocket (per side, short side)', (OVM_H - CABLE_H) / 2, H, 0.0, note='largest spec-compliant overmold [USER]')
    _xs = C.radar_pin_xs()
    r('radar header plastic underside to keeper A plate (z)', (RAD_Z0 - HDR_SPACER_T) - P.KA_Z1, T, T, note='header dims [USER 8.3 / 1.35], plastic [GUESS]')
    r('radar header pins to keeper A slot (per side)', min((_xs[1] - HDR_PIN_T / 2) - KA_SLOT_X0, KA_SLOT_X1 - (_xs[-1] + HDR_PIN_T / 2)), T, T, note='pin 0.64 [GUESS]')
    r('radar header plastic (trimmed edge) to sleeve lip opening (x)', (_xs[1] - RAD_PIN_PITCH / 2) - LIP_X0, T, T, note='pin 1 clipped, plastic trimmed at pin 2 cell')
    r('radar header plastic to radar pocket wall (y)', RAD_POCKET_CLR + (RAD_PIN_EDGE - HDR_PLASTIC_W / 2), T, T, note='plastic width [GUESS]')
    r(f'cable overmold {CABLE_W} x {CABLE_H} in pocket (per side, long side)', (OVM_W - CABLE_W) / 2, H, 0.0, note='largest spec-compliant overmold [USER]')
    r('holder to plug cradle walls (per side)', HOLDER_CLR, T, T, note='holder tol [GUESS] +-0.2')
    r('plug to cavity wall (glue line, per side)', G_PLUG, T, T)
    r('switch carrier to plug pocket (per side, y)', P.POCKET_CLR, T, T)
    r('switch carrier to pocket roof (z)', P.POCKET_Z1 - P.CAR_Z1, T, T)
    r('switch body to carrier walls (per side)', P.SW_CLR, T, 0.2, note='datasheet: +-0.2 over 1.5 mm')
    r('switch body top to carrier bridge (z, lost motion)', P.SW_ZCLR, T, 0.1)
    r(f'knob (3.9 sq, diag 5.52) to knob hole D{P.KNOB_HOLE_D2} incl. 0.6 carrier play', (P.KNOB_HOLE_D2 - 3.9 * math.sqrt(2)) / 2 - 0.6, H, 0.2)
    r('knob to carrier shelf slot (per side)', (4.5 - SW_KNOB) / 2, T, 0.2)
    return rows


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
