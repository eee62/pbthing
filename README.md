# pbthing — insert, plug and helpers for the zen_v7 sleeve

Hidden-sensor "power bank" (XIAO ESP32-S3 Sense + OV5640 + HLK-LD2410S + 3x18650) designed
around the already-printed `inputs/zen_v7_sleeve.stl`. Printed in JLC3DP 9000HE resin.

* **REPORT.md** — decisions, parts to order, tolerance table, assumptions, risks.
* **ASSEMBLY.md** — order of assembly, wiring, tests, glue points.
* **SIMULATION.md** — physical assembly simulation (rigid parts + flexible ribbon/wires), where things jam, pinch or over-bend, and the radar-at-6.2 mm study. Frames/video: `out/sim/render/`.
* `out/stl/` print files (`insert`, `plug`, `tray`, `coupon`), `out/step/` STEP,
  `out/img/` renders, `out/logs/verify.txt` the verification log.

Rebuild everything (Python 3.11+):

```
pip install -r requirements.txt
python src/measure.py    # measurements of the supplied STL and STEP
python src/build.py      # parts -> out/stl, out/step, out/assembly
python src/verify.py     # numeric checks -> out/logs/verify.txt (exit code = number of failures > 0)
python src/render.py     # images -> out/img (needs OSMesa/EGL for off-screen VTK)
python src/report_tables.py
python src/sim/scenario.py --slack 16 --xiao-stage 14 --speed 3 --dress   # assembly simulation (see SIMULATION.md §5)
```
