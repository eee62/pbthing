"""Build every part, export print STLs (+ STEP for insert, plug, keepers) and an assembly
folder for renders.  Run: python src/build.py"""
import os, json, time
import cadquery as cq
from params import *  # noqa
import parts as P
import components as C
import wires as W

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out')
TOLS = dict(tolerance=0.01, angularTolerance=0.1)


def export(wp, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    shape = wp.val() if hasattr(wp, 'val') else wp
    if path.endswith('.stl'):
        cq.exporters.export(cq.Workplane().add(shape), path, **TOLS)
    else:
        cq.exporters.export(cq.Workplane().add(shape), path)


def main():
    t0 = time.time()
    # ---- printed parts in print orientation (as designed; JLC chooses supports)
    printed = {
        'insert': P.insert(), 'plug': P.plug(), 'tray': P.tray(), 'coupon': P.coupon(),
    }
    for n, wp in printed.items():
        export(wp, os.path.join(OUT, 'stl', f'{n}.stl'))
    for n in ('insert', 'plug'):
        export(printed[n], os.path.join(OUT, 'step', f'{n}.step'))
    # individual small parts (reference; they are ordered on the tray)
    singles = {'keeper_a': P.keeper_a(), 'keeper_b': P.keeper_b(), 'keeper_c': P.keeper_c()}
    for h in SW_H_VARIANTS:
        singles[f'carrier_H{h:g}'] = P.carrier(h)
    for v, c in CAP_VARIANTS.items():
        singles[f'lens_cap_{v}'] = P.lens_cap(c)
        singles[f'usb_cover_{v}'] = P.usb_cover(c)
    for n, wp in singles.items():
        export(wp, os.path.join(OUT, 'stl', 'tray_parts', f'{n}.stl'))
    for n in ('keeper_a', 'keeper_b', 'keeper_c'):
        export(singles[n], os.path.join(OUT, 'step', f'{n}.step'))

    # ---- assembly (sleeve frame) for renders
    asm = os.path.join(OUT, 'assembly')
    export(C.sleeve(), os.path.join(asm, 'sleeve_rebuilt.stl'))
    for n in ('insert', 'plug'):
        export(printed[n], os.path.join(asm, f'{n}.stl'))
    for n in ('keeper_a', 'keeper_b', 'keeper_c'):
        export(singles[n], os.path.join(asm, f'{n}.stl'))
    export(P.carrier(SW_H_DEFAULT), os.path.join(asm, 'carrier.stl'))
    export(P.lens_cap(0.1, at_origin=False), os.path.join(asm, 'lens_cap.stl'))
    export(P.usb_cover(0.1, at_origin=False), os.path.join(asm, 'usb_cover.stl'))
    comps = {'radar': C.radar(), 'bms': C.bms(), 'camera': C.camera(), 'switch': C.main_switch(),
             'holder': C.holder(), 'antenna': C.antenna()}
    for n, wp in comps.items():
        export(wp, os.path.join(asm, f'cmp_{n}.stl'))
    xi = cq.Compound.makeCompound([s for _, s in C.xiao_parts()])
    export(xi, os.path.join(asm, 'cmp_xiao.stl'))
    fpc, info = W.fpc()
    export(fpc, os.path.join(asm, 'wire_fpc.stl'))
    for i, w in enumerate(W.all_wires()):
        export(w['solid'], os.path.join(asm, f"wire_{w['group']}_{i:02d}.stl"))
    with open(os.path.join(OUT, 'logs', 'build.json'), 'w') as f:
        json.dump(dict(fpc=info, time_s=round(time.time() - t0, 1)), f, indent=1, default=float)
    print('build done', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
