"""Annotated close-ups of the frames where something happens (collision / pinch / over-bend), found automatically.
Usage: python src/sim/render_events.py run.pkl outdir [tag]
For every step it picks (a) the frame with the smallest ribbon bend radius in the free part, (b) the frame with the largest
squeeze (wire or ribbon vs a rigid part) and writes one PNG row per step with three views."""
import os, sys, pickle
import numpy as np, imageio.v2 as imageio
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import render_sim as RS


def steps_of(frames):
    out = []
    for i, f in enumerate(frames):
        if not out or out[-1][0] != f['step']:
            out.append([f['step'], i, i])
        else:
            out[-1][2] = i
    return out


def main(pkl, outdir, tag):
    os.makedirs(outdir, exist_ok=True)
    d = pickle.load(open(pkl, 'rb')); fr = d['frames']; meta = d['flex_meta']
    M = RS.load_meshes()
    rows = []
    for lab, i0, i1 in steps_of(fr):
        if lab == 'stage':
            continue
        rmin = []
        for k in range(i0, i1 + 1):
            R = fr[k]['bend']['ribbon']
            rmin.append(R[3:-3].min())
        kR = i0 + int(np.argmin(rmin))
        sq = [max(fr[k]['pinch'][n].max() for n in fr[k]['pinch']) for k in range(i0, i1 + 1)]
        kS = i0 + int(np.argmax(sq))
        tiles = [RS.render(fr[kR], M, meta, 'cam_obl', (520, 460), f"{lab}: tightest ribbon bend R={min(rmin):.2f} mm"),
                 RS.render(fr[kR], M, meta, 'xiao_close', (520, 460), f"{lab}: same frame, close-up"),
                 RS.render(fr[kS], M, meta, 'radar_close', (520, 460), f"{lab}: worst squeeze {max(sq):.2f} mm (red dots)")]
        img = np.hstack(tiles)
        name = f"{tag}_{lab.split()[0]}_{'_'.join(lab.split()[1:]).replace('+', '')}.png"
        imageio.imwrite(os.path.join(outdir, name), img)
        rows.append(img)
        print(lab, 'Rmin', round(min(rmin), 2), 'squeeze', round(max(sq), 2), flush=True)
    imageio.imwrite(os.path.join(outdir, f'{tag}_events_all_steps.png'), np.vstack(rows))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'run')
