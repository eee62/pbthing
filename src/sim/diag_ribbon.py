"""Where along the ribbon does the strain / tight bend occur?  python src/sim/diag_ribbon.py run.pkl
Prints, for the last frame of every step: worst segment strains (row index, position), bend radii, anchored-row positions."""
import sys, pickle
import numpy as np

d = pickle.load(open(sys.argv[1], 'rb'))
frames = d['frames']
meta = {m[0]: m for m in d['flex_meta']}
name, kind, r, W, nr, nc, color, rmin = meta['ribbon']
L0 = 65.0 / (nr - 1)
seen = []
for i, f in enumerate(frames):
    if not seen or seen[-1][0] != f['step']:
        seen.append([f['step'], i, i])
    else:
        seen[-1][2] = i
for step, i0, i1 in seen:
    smax = (-9, None, None)
    for k in range(i0, i1 + 1):
        P = frames[k]['flex']['ribbon'].reshape(nr, nc, 3).mean(1)
        s = np.linalg.norm(np.diff(P, axis=0), axis=1) / L0 - 1
        j = int(s.argmax())
        if s[j] > smax[0]:
            smax = (s[j], j, k)
    P = frames[smax[2]]['flex']['ribbon'].reshape(nr, nc, 3).mean(1) if smax[1] is not None else None
    Pl = frames[i1]['flex']['ribbon'].reshape(nr, nc, 3).mean(1)
    sl = np.linalg.norm(np.diff(Pl, axis=0), axis=1) / L0 - 1
    R = frames[i1]['bend']['ribbon']
    print(f"{step:22s} worst strain {100*smax[0]:5.1f}% at segment {smax[1]} of {nr-1} (frame {smax[2]}, y,z = {None if P is None else P[smax[1]][1:].round(1).tolist()})"
          f" | end of step: max strain {100*sl.max():5.1f}% (seg {int(sl.argmax())}), min R {R[3:-3].min():.2f} at row {3+int(R[3:-3].argmin())}, total length {np.linalg.norm(np.diff(Pl,axis=0),axis=1).sum():.1f} mm")
