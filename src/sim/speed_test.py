"""Is the transient ribbon strain real or solver lag?  Repeat S4 (camera) and S6 (XIAO) at different hand speeds.
If the peak scales with speed it is lag of the quasi-static solver; if it does not, the geometry forces it.
Usage: python src/sim/speed_test.py S4|S6 speed [speed ...]"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import scenario as S
from physim import Hand


def run(which, speed, slack=30.0, xiao_stage=25.0):
    B, flex, stage = S.build_world(slack, False, xiao_stage, 'keeper_b')
    env = S.env_list(B); Hand.bodies_for_contact = env
    rec = S.Recorder(B, flex); t = 0.0
    for n in ('radar', 'tact', 'keeper_a'):                      # earlier steps assumed done (final poses)
        B[n].set_pose(B[n].com.copy(), np.eye(3)); B[n].active = True
    for f in flex: f.apply_anchors()
    for k in range(400):
        for f in flex: f.step(S.DT, [b for b in env if b.active], iters=(30 if f.kind == 'ribbon' else 12), gq=getattr(f, 'gq', 0.0))
    seq = [('S4 camera', 'camera', 12.0 if which == 'S4' else 12.0)]
    if which == 'S6':
        seq += [('S5 keeper B', 'keeper_b', 12.0), ('S6 XIAO', 'xiao', speed)]
    else:
        seq = [('S4 camera', 'camera', speed)]
    for label, name, sp in seq:
        b = B[name]; b.active = True
        t = S.do_step(label, b, B, flex, env, rec, t, b.x.copy(), b.com.copy(), sp, 150, False)


if __name__ == '__main__':
    which = sys.argv[1]
    for sp in map(float, sys.argv[2:]):
        print(f'--- {which} at {sp} mm/s', flush=True)
        run(which, sp)
