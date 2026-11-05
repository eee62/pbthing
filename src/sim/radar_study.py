"""Radar-behind-window study, run with the same rigid-body engine against the real sleeve mesh.
Window inner surface z = 139.7 (0.8 mm window). Target antenna-to-window distance H = 6.2 mm (+-1.2 per the Hi-Link radome guide)
=> antenna plane (radar PCB front face) at z = 133.5 (132.3..134.7). Lip slab z 134.5..137.0, opening 19.4 x 67.2.
Scenarios (rigid radar + sleeve, hand-guided):
  R1  flat, loaded from the front through the lip opening           -> expect jam (board 20.0 > opening 19.4)
  R2  tilted 20 deg about y, loaded from the front                  -> passes the lip; ends tilted
  R3  flat, loaded from the bottom (open end), pushed up            -> stops against the lip underside
  R4  on edge (rotated 90 deg about y), loaded from the front       -> passes the lip
  R5  flat, loaded from the front in the current design             -> rests on the lip top (reference)
Run: python src/sim/radar_study.py  -> out/sim/radar_study.json + frames (pickle) for rendering."""
import os, sys, json, pickle
import numpy as np
from scipy.spatial.transform import Rotation as Rot
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE); ROOT = os.path.dirname(SRC)
sys.path.insert(0, HERE); sys.path.insert(0, SRC)
import meshes, sdf
from physim import Rigid, Hand

DT = 1 / 240.0
WIN_IN = 139.7


def make_world():
    ms = meshes.get('sleeve'); lo, hi = ms.bounds.copy(); lo[2] = 85.0
    S = sdf.build('sleeve', ms, 0.15, margin=1.0, bounds=(lo, hi), tag='_z85')
    sleeve = Rigid('sleeve', ms, S, sample=False)
    rm = meshes.get('radar'); rs = sdf.build('radar', rm, 0.1, margin=1.5)
    radar = Rigid('radar', rm, rs, nsamp=6000)
    return sleeve, radar


def run_case(name, sleeve, radar, start_z_ant, end_z_ant, tilt_deg=0.0, edge_on=False, cx=14.7, cy=38.6, speed=8.0, hold_tilt=True):
    """Move the radar so that its PCB front-face centre goes from z=start to z=end (mm), x,y centred on the lip opening."""
    # radar mesh frame: PCB front face is at RAD_Z1 = 138.7 in the current design pose; centre of mesh (com) known
    import params as PR
    com = radar.com.copy()
    front_c = np.array([PR.RAD_X0 + PR.RAD_W / 2, PR.RAD_Y0 + PR.RAD_W / 2, PR.RAD_Z1])      # front-face centre in the design frame
    R = Rot.from_euler('y', 90.0 if edge_on else tilt_deg, degrees=True).as_matrix()
    def pose_for(z_ant):
        # place so that the (rotated) front-face centre is at (cx, cy, z_ant)
        x = np.array([cx, cy, z_ant]) - R @ (front_c - com)
        return x
    radar.set_pose(pose_for(start_z_ant), R)
    sleeve.active = True
    Hand.bodies_for_contact = [sleeve]
    hand = Hand(radar, radar.x, R, jam_mm=1.0)
    x0, x1 = pose_for(start_z_ant), pose_for(end_z_ant)
    dist = np.linalg.norm(x1 - x0); n = int(dist / speed / DT) + 1
    log = []; worst_depth = 0; jam_at = None
    for k in range(n + 120):
        s = min(1.0, k / n); hand.tx = x0 + (x1 - x0) * s
        info = hand.substep([sleeve], DT, iters=10)
        if not hold_tilt:
            pass
        worst_depth = max(worst_depth, info['depth'])
        if k % 4 == 0:
            log.append((radar.x.copy(), radar.R.copy()))
        if info['err'] > 1.0 and jam_at is None:
            jam_at = dict(step=k, err=info['err'], where=None if info['where'] is None else info['where'].tolist(), target_z_ant=float(x0[2] + (x1[2] - x0[2]) * s))
    # final state
    zc = radar.world(front_c)[0]
    lag = float(np.linalg.norm(hand.tx - radar.x))
    P = radar.x + radar.pb @ radar.R.T
    res = dict(case=name, requested_end_z_ant=end_z_ant, final_front_centre=[round(float(v), 2) for v in zc], hand_lag_mm=round(lag, 2),
               jam=bool(lag > 1.0), jam_at=jam_at, worst_penetration_mm=round(float(worst_depth), 3),
               final_tilt_deg=round(float(np.degrees(np.arccos(np.clip(radar.R[:, 2] @ np.array([0, 0, 1.0]), -1, 1)))), 1) if not edge_on else 'edge-on',
               H_at_centre_mm=round(float(WIN_IN - zc[2]), 2))
    return res, log


def main():
    sleeve, radar = make_world()
    out = []; logs = {}
    # R1: flat, from the front: start with the PCB front face 2 mm above the lip top (z 139.0), push to z_ant = 133.5
    cases = [('R1 flat, loaded from the front', dict(start_z_ant=139.0, end_z_ant=133.5)),
             ('R2 tilted 20 deg, loaded from the front', dict(start_z_ant=141.0, end_z_ant=133.5, tilt_deg=20.0)),
             ('R2b tilted 15 deg, loaded from the front', dict(start_z_ant=141.0, end_z_ant=133.5, tilt_deg=15.0)),
             ('R3 flat, loaded from the bottom', dict(start_z_ant=125.0, end_z_ant=136.0)),
             ('R4 on edge (90 deg), loaded from the front', dict(start_z_ant=141.0, end_z_ant=133.5, edge_on=True)),
             ('R5 flat, current design (rests above the lip)', dict(start_z_ant=141.5, end_z_ant=137.0))]
    for nm, kw in cases:
        res, log = run_case(nm, sleeve, radar, **kw)
        out.append(res); logs[nm] = log
        print(json.dumps(res), flush=True)
    json.dump(out, open(os.path.join(ROOT, 'out', 'sim', 'radar_study.json'), 'w'), indent=1)
    pickle.dump(dict(logs=logs, radar_com=radar.com), open(os.path.join(ROOT, 'out', 'sim', 'radar_study.pkl'), 'wb'))


if __name__ == '__main__' and not (len(sys.argv) > 1 and sys.argv[1] == 'extra'):
    main()


def tilt_sweep(sleeve, radar):
    """Orientation LOCKED (stiff hold) at a fixed tilt about y; load from the front down to z_ant = 133.5. Pass = no jam."""
    import params as PR
    front_c = np.array([PR.RAD_X0 + PR.RAD_W / 2, PR.RAD_Y0 + PR.RAD_W / 2, PR.RAD_Z1])
    res = []
    for tilt in (0, 2, 4, 6, 8, 10, 12, 14):
        R = Rot.from_euler('y', tilt, degrees=True).as_matrix()
        def pose_for(z):
            return np.array([14.7, 38.6, z]) - R @ (front_c - radar.com)
        radar.set_pose(pose_for(141.0), R); sleeve.active = True
        Hand.bodies_for_contact = [sleeve]
        hand = Hand(radar, radar.x, R, jam_mm=1.0)
        x0, x1 = pose_for(141.0), pose_for(133.5); n = int(np.linalg.norm(x1 - x0) / 6.0 / DT) + 1
        jam = False; blocked_z = None; maxpen = 0.0
        for k in range(n + 100):
            s = min(1.0, k / n); hand.tx = x0 + (x1 - x0) * s
            info = hand.substep([sleeve], DT, iters=12, rot_gain=1.0)
            maxpen = max(maxpen, info['depth'])
            if k > n and info['err'] > 1.0:
                jam = True
        zc = radar.world(front_c)[0][2]
        res.append(dict(tilt_deg=tilt, passed=not jam, reached_z_ant=round(float(zc), 2), hand_lag=round(float(np.linalg.norm(hand.tx - radar.x)), 2),
                        stuck_penetration=round(float(maxpen), 3)))
        print(res[-1], flush=True)
    return res


def fov(z_ant=133.5):
    """Unobstructed angular range through the lip aperture for points on the antenna plane (sleeve mesh only; the thin
    window is treated as transparent). Angles are measured from the board normal in the x-z and y-z planes."""
    import trimesh
    ms = meshes.get('sleeve')
    out = {}
    for name, (dx, dy) in {'centre': (0, 0), 'patch edge -x (x=-8)': (-8, 0), 'patch edge +x (x=+8)': (8, 0), 'patch y=-8': (0, -8), 'patch y=+8': (0, 8)}.items():
        P = np.array([14.7 + dx, 38.6 + dy, z_ant + 0.05])
        res = {}
        for plane in ('x', 'y'):
            ang = np.radians(np.arange(-85, 86, 1.0))
            d = np.stack([np.sin(ang), np.zeros_like(ang), np.cos(ang)], 1) if plane == 'x' else np.stack([np.zeros_like(ang), np.sin(ang), np.cos(ang)], 1)
            hits = ms.ray.intersects_any(np.tile(P, (len(ang), 1)), d)
            free = ~hits
            # contiguous free interval around 0 deg
            c = len(ang) // 2
            lo = c
            while lo > 0 and free[lo - 1]: lo -= 1
            hi = c
            while hi < len(ang) - 1 and free[hi + 1]: hi += 1
            res[plane] = (round(float(np.degrees(ang[lo])), 0), round(float(np.degrees(ang[hi])), 0))
        out[name] = res
    return out


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'extra':
    sl, rd = make_world()
    sw = tilt_sweep(sl, rd)
    f6 = {'below lip, H=6.2 (z_ant 133.5)': fov(133.5), 'below lip touching underside (z_ant 134.5, H=5.2)': fov(134.5), 'current design above the lip (z_ant 138.7, H=1.0)': fov(138.7)}
    for k, v in f6.items():
        print(k); [print('   ', n, r) for n, r in v.items()]
    json.dump(dict(tilt_sweep=sw, fov=f6), open(os.path.join(ROOT, 'out', 'sim', 'radar_study_extra.json'), 'w'), indent=1)
