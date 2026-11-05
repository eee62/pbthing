# pbthing — insert, plug and helpers for the zen_v7 sleeve

Hidden-sensor "power bank" (XIAO ESP32-S3 Sense + OV5640 + HLK-LD2410S + 3×18650) designed
around the already-printed `inputs/zen_v7_sleeve.stl`. Printed in JLC3DP 9000HE resin.
**Nothing here has been printed or tested on hardware.**

## Read in this order

1. **REVIEW_CONNECTORS_WIFI_SEAL.md** — JST-PH vs RCY, Wi-Fi antenna review + range test, permanent-build review
   (adhesives, heat, strain relief, cell swelling, what fails after sealing).
2. **REPORT.md** — decisions, parts to order, tolerance tables, assumptions, risks.
3. **ASSEMBLY.md** — order of assembly, wiring, tests, glue points.

## Latest update (connectors / Wi-Fi / permanent build)

* No board here has a JST-PH socket (XIAO = solder pads, radar = 2.54 mm holes, expansion board = FPC + U.FL). One PH pair was added
  where a disconnect is useful: the battery line between the plug module and the top module (plug zone P1, real size 5.9 × 4.5 × 11.4 mm).
  The red RCY pairs do not mate with PH (2.5 vs 2.0 mm pitch) and are not used. An optional RCY splice (23.3 × 4.0 mm) is modelled:
  `PB_RCY=1 python src/verify.py`.
* **Length** (sleeve is fixed at 140.5 mm): battery conductors B+/B− are 173.0 / 142.0 mm with PH (was 168.5 / 138.1, direct solder);
  with the RCY splice 181.0 / 150.0 mm. The splice uses 23.3 mm (31.3 with allowances) of a 71.6 mm straight run.
* Antenna moved to a new +y end wall: 13.3 mm from the camera ribbon (was 1.8), 15.4 mm from the camera head (was 3.9), 11.1 mm above the cell tops (was 9.5).
* Verification: **123 checks, 0 failures** (125 / 0 with the RCY splice). Log: `out/logs/verify.txt`, `out/logs/verify_rcy.txt`.
* Biggest open risk: heat. A XIAO with a camera is reported at 80–95 °C while the resin's HDT/Tg is 60 / 61–68 °C (see the review, §3.2).

## Layout

* `out/stl`, `out/step` print files (`insert`, `plug`, `tray`, `coupon`) · `out/img` renders · `out/logs` logs
* `src/` parametric source (`params.py` holds every number, tagged) · `inputs/` supplied files + datasheets used

## Rebuild (Python 3.11+)

```
pip install -r requirements.txt
python src/measure.py    # measurements of the supplied STL and STEP
python src/build.py      # parts -> out/stl, out/step, out/assembly
python src/verify.py     # numeric checks -> out/logs/verify.txt (exit code = number of failures)
PB_RCY=1 python src/verify.py   # same with the optional RCY splice -> out/logs/verify_rcy.txt
python src/render.py     # images -> out/img (needs OSMesa/EGL for off-screen VTK)
python src/report_tables.py     # refresh the tables in REPORT.md
```
