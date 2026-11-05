"""Assembly scenario: face-down on the glass (front face down, gravity toward +z), parts lowered in the documented order
into the insert, with ribbon / wires / coax as flexible bodies, then the sleeve lowered over the module.
Run:  python src/sim/scenario.py [--quick] [--slack 6]    -> out/sim/run.pkl"""
import os, sys, time, pickle, argparse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE); ROOT = os.path.dirname(SRC)
sys.path.insert(0, HERE); sys.path.insert(0, SRC)
import meshes, sdf
from physim import Rigid, Flex, Hand, env_query
import params as PR
import wires as W, components as C
from geo import path_edges

DT = 1.0 / 240.0


def sample_edges(edges, ds):
    L = np.array([e.Length() for e in edges]); tot = L.sum(); n = max(2, int(round(tot / ds)) + 1)
    s = np.linspace(0, tot, n); cum = np.concatenate([[0], np.cumsum(L)])
    pts = []
    for sk in s:
        k = min(np.searchsorted(cum, sk, side='right') - 1, len(edges) - 1)
        t = (sk - cum[k]) / L[k]
        v = edges[k].positionAt(min(max(t, 0), 1)); pts.append([v.x, v.y, v.z])
    return np.array(pts), tot


def sample_poly(pts, ds):
    pts = np.asarray(pts, float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)]); tot = cum[-1]
    n = max(2, int(round(tot / ds)) + 1); s = np.linspace(0, tot, n)
    out = np.stack([np.interp(s, cum, pts[:, k]) for k in range(3)], 1)
    return out, tot


def build_world(slack_signal=6.0, quick=False, xiao_stage=6.0, kb='keeper_b'):
    t0 = time.time()
    names = ['insert', 'radar', 'tact', 'keeper_a', 'camera', 'keeper_b', 'xiao', 'keeper_c']
    B = {}
    for n in names:
        mn = kb if n == 'keeper_b' else n
        m = meshes.get(mn)
        S = sdf.build(mn, m, 0.1, margin=1.5)
        ns = {'xiao': 5000, 'insert': 10, 'radar': 2500, 'tact': 800, 'camera': 2000}.get(n, 2000)
        B[n] = Rigid(n, m, S, nsamp=ns if n != 'insert' else 10, sample=(n != 'insert'))
    ms = meshes.get('sleeve'); lo, hi = ms.bounds.copy(); lo[2] = 85.0
    S = sdf.build('sleeve', ms, 0.15, margin=1.0, bounds=(lo, hi), tag='_z85')
    B['sleeve'] = Rigid('sleeve', ms, S, sample=False)
    # sleeve contact samples: inner surface region only
    pts = ms.sample(40000); pts = pts[pts[:, 2] > 100.0]
    B['sleeve'].pb = pts[::4] - B['sleeve'].com
    # staging offsets (mm toward -z = "above" in the face-down world)
    stage = {'radar': 10, 'tact': 8, 'keeper_a': 12, 'camera': 14, 'keeper_b': 14, 'xiao': xiao_stage, 'keeper_c': 14}
    for n, d in stage.items():
        B[n].translate_from_final((0, 0, -d))
        B[n].active = (n == 'xiao')                   # XIAO is held beside the work from the start; others sit on the bench
    B['sleeve'].active = False
    print(f'bodies ready {time.time()-t0:.0f}s', flush=True)

    X = B['xiao']
    flex = []
    # ---------------- ribbon -----------------------------------------------------------
    zl = W.solve_fpc_loop(PR.FPC_LEN)
    pts_route = np.array(W.fpc_points(zl))
    # staged anchors: connector end follows the staged XIAO (-6), camera end the staged camera (-14); loop re-solved deeper
    dX, dC = stage['xiao'], stage['camera']
    pts_st = pts_route.copy(); pts_st[:3, 2] -= dX; pts_st[5:, 2] -= dC
    def staged_len(zz):
        q = pts_st.copy(); q[3:5, 2] = zz
        e, _ = W._path_with_radii(q, W.FPC_RADII, PR.FPC_R_LOOP)
        return sum(x.Length() for x in e) + PR.FPC_TAIL_IN + PR.FPC_HEAD_IN
    lo_, hi_ = 40.0, pts_st[2, 2] - PR.FPC_R2 - PR.FPC_R_LOOP - 0.01
    for _ in range(60):                                  # exact loop depth so the staged ribbon has its full 65 mm
        mid_ = (lo_ + hi_) / 2
        if staged_len(mid_) > PR.FPC_LEN: lo_ = mid_
        else: hi_ = mid_
    zl2 = (lo_ + hi_) / 2
    pts_st[3:5, 2] = zl2
    edges, radii = W._path_with_radii(pts_st, W.FPC_RADII, PR.FPC_R_LOOP)
    rp, rlen = sample_edges(edges, 0.8)
    rib = Flex('ribbon', 'ribbon', rp, radius=PR.FPC_T / 2 + 0.03, width=PR.FPC_W, EI=18.0, mu=0.2, rmin=PR.FPC_R_MIN, color='#e8a317')
    rib.L0 = np.full(len(rp) - 1, (rlen) / (len(rp) - 1)); rib._build()       # rest length = staged arc length (= 65 mm incl. in-connector tail)
    ka = 2
    def loc_final(owner, world_pts, shift):                   # world (staged) points -> device-frame fixed to the owner
        return np.asarray(world_pts) + np.array([0, 0, shift])
    for rows, owner, sh in ((range(0, ka), X, dX), (range(len(rp) - ka, len(rp)), B['camera'], dC)):
        idx = np.array([r * 3 + c for r in rows for c in range(3)])
        rib.anchor(idx, owner, loc_final(owner, rib.pos[idx], sh))
    flex.append(rib)
    # ---------------- wires ------------------------------------------------------------
    def wire(name, pts, owner0, shift0, owner1, shift1, slack, color, hand_end=None, r=0.55):
        n_pts = np.array(pts)
        ptsd = n_pts.copy()
        k = len(ptsd)
        for j in range(k):                                   # blend staged shift along the route
            sh = shift0 + (shift1 - shift0) * j / max(k - 1, 1)
            ptsd[j, 2] -= sh
        p, L = sample_poly(ptsd, 3.0 if 'lead' in name else 1.5)
        f = Flex(name, 'wire', p, radius=r, EI=1.0, mu=0.3, color=color, rest_slack=0.0)
        f.gq = 0.0 if 'lead' in name else 0.002
        f.L0 = np.full(len(p) - 1, (L + slack) / (len(p) - 1)); f._build()
        if owner0 is not None:
            f.anchor([0], owner0, loc_final(owner0, f.pos[[0]], shift0))
        if owner1 is not None:
            f.anchor([len(p) - 1], owner1, loc_final(owner1, f.pos[[-1]], shift1))
        if hand_end is not None:
            f.anchor([len(p) - 1], ('fixed', np.array([hand_end])), None)
        return f
    for w in W.radar_wires():
        flex.append(wire(w['name'], w['pts'], B['radar'], stage['radar'], X, dX, slack_signal, '#d62828'))
    for w in W.button_wires():
        flex.append(wire(w['name'], w['pts'], B['tact'], stage['tact'], X, dX, slack_signal, '#f77f00'))
    cx = W.coax()
    flex.append(wire('U.FL coax', cx['pts'], X, dX, None, 0, 4.0, '#ffbe0b', hand_end=cx['pts'][-1], r=0.57))
    for nm, (px, pz) in (('BAT+', W.PADS['BAT+']), ('BAT-', W.PADS['BAT-'])):
        pts = [(px, W.Y_WIRE, pz), (px, W.Y_WIRE, pz - 75.0), (px, W.Y_WIRE, pz - 150.0)]
        f = wire(nm + ' lead', pts, X, dX, None, 0, 0.0, '#ff006e', hand_end=(px, W.Y_WIRE, pz - 150.0))
        flex.append(f)
    # ignore collisions within 2.5 mm of anchors (they sit inside connectors / on pads)
    for f in flex:
        f.nocol = np.zeros(f.N, bool)
        for idx, owner, loc in f.anchors:
            for i in idx:
                f.nocol |= np.linalg.norm(f.pos - f.pos[i], axis=1) < 2.5
    print(f'flex bodies: {len(flex)}, particles {sum(f.N for f in flex)}  {time.time()-t0:.0f}s', flush=True)
    return B, flex, stage


def env_list(B):
    return [B[k] for k in ['insert', 'radar', 'tact', 'keeper_a', 'camera', 'keeper_b', 'xiao', 'keeper_c', 'sleeve']]


class Recorder:
    def __init__(self, B, flex):
        self.B, self.flex = B, flex
        self.frames = []; self.events = []; self.step_summary = []

    def snap(self, step, t, info, extra=None):
        self.frames.append(dict(step=step, t=t,
                                rigid={k: (b.x.copy(), b.R.copy(), b.active) for k, b in self.B.items()},
                                flex={f.name: f.pos.copy() for f in self.flex},
                                bend={f.name: f.bend_radius().copy() for f in self.flex},
                                pinch={f.name: f.pinch.copy() for f in self.flex},
                                info=info))


def track(worst, flex, env, t):
    """Update per-flexible-body worst values: stretch, bend radius (free part), squeeze (+ where, which part)."""
    pf = worst.setdefault('per', {})
    for f in flex:
        e = pf.setdefault(f.name, dict(strain=0.0, R=1e9, R_pos=None, pinch=0.0, pinch_pos=None, pinch_body=None, t_pinch=None, t_R=None))
        R = f.bend_radius(); off = 3 if f.kind == 'ribbon' else 0
        Rr = R[off:len(R) - off] if off else R
        if len(Rr) and Rr.min() < e['R']:
            e['R'] = float(Rr.min()); e['t_R'] = t
            e['R_pos'] = f.center()[1:-1][off + int(Rr.argmin())].round(1).tolist()
        e['strain'] = max(e['strain'], float(f.stretch_strain().max()))
        pm = float(f.pinch.max())
        if pm > e['pinch']:
            i = int(f.pinch.argmax()); e['pinch'] = pm; e['t_pinch'] = t
            e['pinch_pos'] = f.pos[i].round(1).tolist()
            e['pinch_body'] = env[int(f.hitbody[i])].name if f.hitbody[i] >= 0 else '?'


def do_step(label, body, B, flex, env, rec, t, x0, xf, speed, n_settle, quick, hand_lag_jam=1.2):
    hand = Hand(body, x0, np.eye(3), jam_mm=hand_lag_jam)
    dist = float(np.linalg.norm(xf - x0)); n_move = max(1, int(round(dist / speed / DT)))
    worst = dict(depth=0.0, err=0.0, jam=False, first_depth=None)
    t_wall = time.time()
    for k in range(n_move + n_settle):
        s = min(1.0, k / n_move); hand.tx = x0 + (xf - x0) * s
        info = hand.substep(env, DT)
        active = [e for e in env if e.active]
        for f in flex:
            f.step(DT, active, iters=(30 if f.kind == 'ribbon' else 12), gq=getattr(f, 'gq', 0.0))
        t += DT
        if info['depth'] > worst['depth']:
            worst['depth'] = info['depth']
            if info['depth'] > 0.1 and worst['first_depth'] is None:
                worst['first_depth'] = (t, None if info['where'] is None else info['where'].round(1).tolist(), env[info['other']].name if info['other'] is not None and info['other'] >= 0 else '?')
        worst['err'] = max(worst['err'], info['err'])
        if k >= n_move and info['err'] > hand.jam_mm:
            worst['jam'] = True
        if k % 3 == 0:
            track(worst, flex, env, t)
        if k % 6 == 0 or k == n_move + n_settle - 1:
            i2 = dict(info); i2['label'] = label; rec.snap(label, t, i2)
    worst['wall_s'] = time.time() - t_wall
    rec.step_summary.append((label, worst))
    per = worst['per']
    ribR = min(v['R'] for n, v in per.items() if n == 'ribbon'); wR = min(v['R'] for n, v in per.items() if n != 'ribbon')
    tautw = max(((v['strain'], n) for n, v in per.items()))
    pinw = max(((v['pinch'], n) for n, v in per.items()))
    print(f"{label:24s} rigid depth {worst['depth']:.3f} lag {worst['err']:.2f} jam {worst['jam']} | ribbon Rmin {ribR:.2f} | wire Rmin {wR:.2f} | "
          f"max strain {100*tautw[0]:.1f}% ({tautw[1]}) | max squeeze {pinw[0]:.2f} ({pinw[1]}) [{worst['wall_s']:.0f}s]", flush=True)
    return t


def run(slack=6.0, quick=False, out=None, xiao_stage=6.0, kb='keeper_b'):
    B, flex, stage = build_world(slack, quick, xiao_stage, kb)
    env = env_list(B)
    Hand.bodies_for_contact = env
    rec = Recorder(B, flex)
    t = 0.0
    for f in flex:
        f.apply_anchors()
    for k in range(120 if quick else 400):            # pre-roll: relax the staged harness (rigid bodies held)
        for f in flex:
            f.step(DT, [b for b in env if b.active], iters=(30 if f.kind == 'ribbon' else 12), gq=getattr(f, 'gq', 0.0))
        t += DT
    rec.snap('stage', t, {})
    order = [('S1 radar', 'radar', 10, 12.0), ('S2 tact switch', 'tact', 8, 12.0), ('S3 keeper A', 'keeper_a', 12, 12.0),
             ('S4 camera + heatsink', 'camera', 14, 10.0), ('S5 keeper B', 'keeper_b', 14, 12.0),
             ('S6 XIAO stack', 'xiao', xiao_stage, 6.0), ('S7 keeper C', 'keeper_c', 14, 12.0)]
    settle = 60 if quick else 150
    for label, name, dist, speed in order:
        b = B[name]; b.active = True
        t = do_step(label, b, B, flex, env, rec, t, b.x.copy(), b.com.copy(), speed, settle, quick)
    b = B['sleeve']; b.active = True
    b.translate_from_final((0, 0, -50.0))
    t = do_step('S8 sleeve over module', b, B, flex, env, rec, t, b.x.copy(), b.com.copy(), 20.0, settle, quick)
    out = out or os.path.join(ROOT, 'out', 'sim', 'run.pkl')
    with open(out, 'wb') as fh:
        pickle.dump(dict(frames=rec.frames, summary=rec.step_summary, flex_meta=[(f.name, f.kind, f.r, f.W, f.nr, f.nc, f.color, f.rmin) for f in flex],
                         slack=slack), fh)
    import json
    with open(out.replace('.pkl', '_events.json'), 'w') as fh:
        json.dump([(l, {k: v for k, v in w.items() if k != 'ev_first'}) for l, w in rec.step_summary], fh, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    print('saved', out, len(rec.frames), 'frames', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--quick', action='store_true'); ap.add_argument('--slack', type=float, default=6.0)
    ap.add_argument('--out', default=None)
    ap.add_argument('--xiao-stage', type=float, default=6.0)
    ap.add_argument('--kb', default='keeper_b')
    a = ap.parse_args()
    run(a.slack, a.quick, a.out, a.xiao_stage, a.kb)
