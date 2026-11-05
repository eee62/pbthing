"""Turn out/logs/verify.json into markdown tables (pasted into REPORT.md)."""
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(ROOT, 'out', 'logs', 'verify.json')))
L = []
L.append('| Fit | Nominal | tol A | tol B | extra | Worst case | Note |')
L.append('|---|---:|---:|---:|---:|---:|---|')
for r in R['tolerances']:
    flag = ' (friction option)' if r.get('friction') else ''
    L.append(f"| {r['fit']}{flag} | {r['nominal']:.3f} | {r['tolA']} | {r['tolB']} | {r['extra']} | "
             f"**{r['worst']:+.3f}** | {r.get('note', '')} |")
L.append('')
L.append('| Wire / ribbon | Length mm | Min bend r | Clearance to solids | Clearance to other wires |')
L.append('|---|---:|---:|---:|---:|')
for w in R['wires']:
    L.append(f"| {w['name']} | {w['length']:.1f} | {w['min_radius'] if w['min_radius'] is None else round(w['min_radius'], 2)} | "
             f"{w['clear']:.3f} | {w['clear_wires']:.3f} |")
L.append('')
L.append('| Part | Volume mm3 | Bounding box mm | Min wall | Min internal gap |')
L.append('|---|---:|---|---:|---:|')
for n, p in R['parts'].items():
    w = R['walls'].get(n, {})
    L.append(f"| {n} | {p['volume']:.0f} | {p['bbox'][0]:.1f} x {p['bbox'][1]:.1f} x {p['bbox'][2]:.1f} | "
             f"{w.get('min_wall', float('nan')):.2f} | {w.get('min_gap', float('nan')):.2f} |")
L.append('')
L.append('| Switch H (body+knob) | Recess released | Recess latched | Recess full press | Pin tip z | Room to holder |')
L.append('|---:|---:|---:|---:|---:|---:|')
for s in R['switch']:
    L.append(f"| {s['H']:.1f} | {s['recess_released']:.2f} | {s['recess_latched']:.2f} | {s['recess_full']:.2f} | "
             f"{s['pin_tip_z']:.2f} | {s['room_to_holder']:.2f} |")
open(os.path.join(ROOT, 'out', 'logs', 'tables.md'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))

def refresh_report():
    rp = os.path.join(ROOT, 'REPORT.md')
    rep = open(rp).read()
    a = rep.index('| Fit | Nominal |')
    b = rep.index('\n---', a)
    rep = rep[:a] + '\n'.join(L) + '\n' + rep[b:]
    open(rp, 'w').write(rep)


refresh_report()
