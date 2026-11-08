import sys, time, numpy as np
sys.path.insert(0, '/home/user/pbthing/src/sim'); sys.path.insert(0, '/home/user/pbthing/src')
import meshes, sdf
t0 = time.time()
for n in ['radar', 'camera', 'keeper_a', 'keeper_b', 'keeper_c', 'xiao', 'insert']:
    sdf.build(n, meshes.get(n), 0.1, margin=1.5)
m = meshes.get('sleeve')
lo, hi = m.bounds.copy(); lo[2] = 85.0
sdf.build('sleeve', m, 0.15, margin=1.0, bounds=(lo, hi), tag='_z85')
print('all sdfs built', round(time.time() - t0), 's', flush=True)
