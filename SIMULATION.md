# Assembly simulation (rigid bodies + flexible ribbon/wires) and the radar-at-6.2 mm study

Camera as modelled now: lens Ø3.8 mm, base 8.65 × 8.65 mm, base-to-lens 5.6 mm (base bottom to lens top), heatsink
**7.0 mm (x) × 7.1 mm (y) × 6.0 mm high**, centred on the base (offset 0 in x and y: base centre x 14.70, y 50.725; heatsink x 11.20–18.20,
y 47.175–54.275), glued behind the base with a **0.1 mm pad** (same footprint as the heatsink, footprint assumed). Total
5.6 + 0.1 + 6.0 = **11.7 mm**, z 127.2–138.9 (unchanged). Fins are not modelled (solid envelope).

**Latest (front tact switch, keeper A cup/bridge and D9/D10 wires removed; holder 62 × 76 × 20; 24 AWG battery path; protection board):** runs `out/sim/notact_final_h14_s16_dress.*` (dressed) and `notact_final_nodress.*`
(XIAO 14 mm aside, slack 16, 3 mm/s). Step S2 (tact switch) no longer exists, the other step names are unchanged. **Nothing fails:** no rigid jam or collision, **every wire squeeze is 0.00 mm, dressed and undressed** (the persistent 0.30 mm / 1.10 mm GND-wire pinches
of the earlier runs came from keeper A's tact bridge and cup, which are gone), wire strain ≤ 0.8 %, ribbon S4 2.30, S5 2.29, S8 1.97 mm. **The S6 ribbon dip is unchanged: 1.55 mm** (limit 2.0), recovering to 1.97 mm. Not in the simulation: the holder, protection board, plug and the 24 AWG wires
(they sit in the lower module, z < 100, and are checked numerically in verify: 0 overlaps, 0.85 mm board-to-wall, 1.85 mm board-to-holder, wire lane 1.05 mm from the wall); the sim's BAT wires are the 28–30 AWG pigtails.

**Latest (radar header kept, wires soldered to the pin tips):** run `out/sim/header_final_h14_s16_dress.*` (XIAO 14 mm aside, slack 16, dressed) and `header_final_nodress.*`.
No rigid jam or collision; ribbon identical (S4 2.35, S5 2.31, S6 **1.56**, S8 1.97 mm; hold-off 12.5 mm unchanged: the header is on the radar, far from the ribbon). Wires:
* **Dressed:** S4–S8 clean (squeeze 0.00, wire strain ≤ 3.8 %, S3 end 0.1 %), better than before the header (a 0.30 mm squeeze of the GND wire persisted S3–S8). But during keeper A's descent (S3)
  the GND and 3V3 wires are **momentarily squeezed 1.34 / 1.27 mm** at y ≈ 30–31: keeper A's tact bridge (x 12.2–22.6, y 29.2–32.4, z 131.6–132.4) comes from −z and sweeps through the
  wire level (GND run z 130.9, 3V3 z 130.2) before it reaches its seat above them. They are pushed aside and recover; in practice guide them clear of the bridge while keeper A goes down.
  (The GND wire already ran at this level before the header; the header does not cause it.)
* **Undressed:** the GND wire stays caught between the tact switch and keeper A from S3 to S8 (1.10 mm squeeze, 14 % strain); 3V3 0.30 mm.
* The radar wires are now 19–27 mm long (7.3 mm shorter than from the J2 holes) and no longer pass between the radar back components and keeper A's plate.

**Latest (lens hole Ø8.0, USB-C pocket 13.3 × 7.4):** re-run `out/sim/lens8_*`: identical to the Ø7.6 run (S4 2.35, S5 2.31, S6 1.56, S8 1.97 mm; no rigid jam/collision; wire numbers
identical; 12.5 mm hold-off clean 2.17 mm, S6 1.54 mm). Neither the hole nor the pocket touches anything that moves in the simulation. The radar header is not simulated (`HEADER_STUDY.md`).

**Latest camera update:** lens barrel Ø7 × 3.45 mm (was Ø3.8 × 1.0), lens-holder block 8.65 × 8.65 × 1.75 mm (was 4.2), front glass Ø3.5, ribbon
6 mm wide (was 13), faceplate lens hole Ø7.6 (0.3 mm per side, hole tolerance ±0.3). Re-run (`out/sim/barrel7_*`): rigid parts still never jam or collide;
ribbon and wire results match the table below to within 0.1 mm (S4 2.35, S5 2.31, S6 **1.56**, S8 1.97 mm; wire strain and squeeze identical); hold-off scan:
11 mm still fails at S5 (0.52 mm), 12.5 mm clean (2.17 mm, S6 1.54 mm), so **12.5 mm hold-off and the S6 dip are unchanged**. (`out/sim/hold_*.json` now hold this run; the
previous scan is in git history.) The narrower ribbon changes nothing because the route and its minimum radius are the same.

Ribbon exit: out of the head's +y edge, 65 mm, minimum bend radius 2.0 mm, route in
`src/wires.py` (verified numerically: no pinch, radius ≥ 2.0 mm, 111 PASS / 0 FAIL in `out/logs/verify.txt`).

## 1. Bottom line

**Observed (slow quasi-static runs, 3 mm/s, `out/sim/*.log`):**
* **No rigid jam and no rigid collision at any step** (radar, tact, keepers A/B/C, camera + heatsink, XIAO stack, sleeve):
  contact depth 0.000 mm, hand lag ≤ 0.02 mm, every part goes in with a pure +z move.
* **The ribbon over-bends and is pinched if the XIAO is held only 6 mm aside** while the camera and keeper B go in: the
  heatsink (S4) and then keeper B (S5) drive through the pre-dressed ribbon loop: radius **0.72 mm**, strain 51 % with the
  7.0 × 7.1 × 6.0 heatsink (0.70 mm / 74 % with the earlier assumed 8 × 8 × 6.1; images and video `fail_hold6_*` were rendered with that
  earlier heatsink).
  Cause (geometry): the ribbon's down-run (y = 47.85, top at z = 124.52 − hold-off) lies inside the drop path of the camera
  (y 46.4–55.05) and of keeper B's floor (y 46.2–54.75). **Hold the XIAO ≥ 12.5 mm above the seat until keeper B is in**
  (analytic minimum 12.1 mm, set by keeper B's floor underside, see §3b; simulated: 11 mm fails, 12.5, 14 and 25 mm clean).
* **The ribbon still dips to 1.56 mm (limit 2.0 mm) at the connector exit during the last part of the XIAO descent (S6)**,
  with 14 mm and with 25 mm hold-off (1.54 mm at 12.5 mm), unchanged by the new heatsink, and recovers to 1.96 mm when the XIAO is seated. This is an over-bend event. It is
  not fixed: the route has no margin (the two first corners use 4.0 of the 4.06 mm between the connector and the downward
  run). Guide the ribbon by hand during that step; a larger radius needs about 0.6 mm more room in y.
* **Loose wires get pinched.** With the 30 mm service slack of ASSEMBLY.md the four radar wires end up under keeper A's plate and are
  squeezed 0.40 mm (the lane between the plate top face z 135.7 and the radar back components z 136.4 is 0.7 mm, the wire is
  1.1 mm), and one button wire is caught at the sleeve rim in S8 (squeeze 0.85 mm, strain 33 %). Laying the radar wires
  straight into keeper A's slot before it is lowered removes both; what is left is one 0.30 mm contact of the radar GND wire with
  the tact switch / keeper A cup (17.7, 30.0, 132.9). Slack of 8 and 12 mm is too short with the XIAO held aside (wire strain 33–66 %).
  **No slack value was clean on its own:** with 22 mm slack and the same dressing (`final_h14_s22_dress`) keeper C caught a radar wire
  (S7: 0.18 mm squeeze, 51 % strain) while S4–S6 and the sleeve (S8) were clean. Wires have to be dressed before every part that comes
  down on them (keeper A, keeper C, sleeve); a slack of 16–22 mm is the working range.

**Theory / interpretation:** the design's lanes are clear on paper (CAD centre-line clearance ≥ 1.7 mm to the insert, ≥ 3.5 mm to the
sleeve); every wire event comes from slack wire that nobody dressed, so the fix is procedure, not geometry. The ribbon-dip at S6 is a
real geometric tightness of the route.

**Radar at 6.2 mm:** impossible above the lip (bore depth 2.7 mm vs 6.2 mm + 1.2 mm PCB); possible behind the lip (H = 5.2–6.2 mm)
but needs a new retainer. Details in §4.

## 2. What was simulated, and how far to trust it

**Frame and order.** The module is assembled face down on glass (front face down, gravity toward +z). Parts are lowered
by +z moves in the documented order: radar → tact → keeper A → camera + heatsink → keeper B → XIAO stack → keeper C →
sleeve over the whole module. The XIAO is held above the work from the start (it carries the soldered wires and the
plugged ribbon), every other part starts 8–14 mm above its seat.

**Rigid bodies** are the real tessellated parts (insert, keepers A/B/C, radar, tact, camera + heatsink, XIAO stack with
expansion board, the sleeve STL). Each part has an exact signed-distance field on a 0.1 mm grid (0.15 mm for the sleeve);
contact = surface sample points against the other parts' fields, resolved by position-level push-out (translation + rotation),
frictionless. A compliant "hand" follows the scripted path; **jam = the part lags the hand by > 1.2 mm after the move.**

**Flexible bodies.**
* **Camera ribbon:** 3-wide strip, rows 0.8 mm apart, 65 mm long (59.1 mm visible), inextensible (hard stretch, cross and
  shear links), soft bending (EI ≈ 18 N·mm²), 13 mm wide, both ends anchored to their rigid owner (XIAO connector, camera head),
  collides with every active part at its current pose, Coulomb friction μ = 0.2. Bend radius is measured on the centre line
  of the free part.
* **Wires** (4 radar, 2 button, U.FL coax, 2 × 150 mm battery leads): limp chains (1.5 mm particles, Ø1.1 mm), cannot stretch,
  can go slack, same collision and friction. Anchored at both ends or, for the coax and battery leads, fed from a fixed far end.
* Events: **over-bend** (ribbon radius < 2.0 mm), **taut** (stretch strain), **squeeze/pinch** (residual penetration of a
  flexible body into a rigid part after the solver > 0.03 mm), rigid penetration, jam.

**Validation done:** SDF value and gradient exact (-0.200 at 0.2 mm inside); dense 200 k-point re-check of the rigid contacts (true
penetration ≤ 0.008 mm); the S4 ribbon strain peak scales with hand speed (18.7 % at 12 mm/s, 6.6 % at 4, 2.4 % at 1.5 mm/s),
so it is solver lag, not geometry. **All results below are therefore from quasi-static runs at 3 mm/s** (hand lag ≤ 0.02 mm).

**Limits (read before trusting a number).**
* Quasi-static position-based relaxation with *qualitative* stiffness; it finds conflicts and tight bends, it does not predict forces.
* Frictionless rigid contacts; 0.1 mm field resolution; thin walls can be tunnelled by a flexible body after a large squeeze
  (one S8 event ends with a wire beyond the front face: treat squeezes ≥ 0.8 mm as "something is caught", not as a shape).
* Assumed inputs: pad footprint = heatsink footprint, fins not modelled, base thickness 0.4 mm, radar component heights (front 0.85 / back 1.1 mm), wire Ø1.1 mm,
  ribbon EI, starting loop shape, the staging offsets and the wire slack.
* Wires are not tucked or dressed by the "assembler"; where a result says "caught", a person would lay the wire in its lane.
* The plug sub-assembly is not simulated.
* The ribbon radius is measured on the centre line with 0.8 mm row spacing, starting 2.4 mm from the anchored rows: the designed 2.0 mm corner itself reads 1.8–2.4 mm depending on the state, so treat ±0.3 mm as noise. The 1.56 mm dip is 0.3–0.8 mm below those readings.
* Squeeze partners printed for runs made before the tracker fix (`fail_hold6`, `final_s30`, `final_h14_s12`, `final_h14_s20`, `runA…runH22`) can be wrong for S1–S5; the squeeze and radius values themselves are right.

## 3. Results per step

Final procedure simulated (`out/sim/hs7_final_h14_s16_dress.*`, new heatsink; identical to the earlier `final_h14_s16_dress` with the 8 × 8 × 6.1 heatsink): XIAO held 14 mm up and aside through S1–S5, wire slack 16 mm, the four
radar wires laid straight into keeper A's slot before S3, hand speed 3 mm/s. Values are the worst over the step.

| step | rigid contact depth (mm) | hand lag (mm) | jam | ribbon min radius (mm) | ribbon max strain | worst wire strain | worst squeeze (mm) |
|---|---|---|---|---|---|---|---|
| S1 radar | 0.000 | 0.02 | no | 1.83 | 0.2 % | 0.5 % (radar OT1 -> XIAO D7) | 0.00 (ribbon, vs None) |
| S2 tact switch | 0.000 | 0.02 | no | 2.12 | 0.1 % | 0.1 % (button leg B -> XIAO D9 (driven LOW)) | 0.00 (ribbon, vs None) |
| S3 keeper A | 0.000 | 0.02 | no | 2.28 | 0.1 % | 40.9 % (radar 3V3 -> XIAO 3V3) | 0.30 (radar GND -> XIAO GND, vs tact) |
| S4 camera + heatsink | 0.000 | 0.02 | no | 2.37 | 4.2 % | 14.2 % (radar GND -> XIAO GND) | 0.30 (radar GND -> XIAO GND, vs tact) |
| S5 keeper B | 0.000 | 0.02 | no | 2.38 | 0.3 % | 11.5 % (radar GND -> XIAO GND) | 0.30 (radar GND -> XIAO GND, vs tact) |
| S6 XIAO stack | 0.000 | 0.02 | no | 1.56 | 2.5 % | 11.5 % (radar GND -> XIAO GND) | 0.30 (radar GND -> XIAO GND, vs tact) |
| S7 keeper C | 0.000 | 0.02 | no | 1.56 | 0.9 % | 2.2 % (radar 3V3 -> XIAO 3V3) | 0.30 (radar GND -> XIAO GND, vs keeper_a) |
| S8 sleeve over module | 0.000 | 0.02 | no | 1.96 | 0.2 % | 2.2 % (radar 3V3 -> XIAO 3V3) | 0.30 (radar GND -> XIAO GND, vs keeper_a) |

Same run without dressing (slack 20, `final_h14_s20`): ribbon identical; radar wires squeezed 0.40 mm from S3 to S8; wire strain
5.9–8.7 %.

Failure case, XIAO held only 6 mm aside (`fail_hold6`, slack 30):

| step | rigid contact depth (mm) | hand lag (mm) | jam | ribbon min radius (mm) | ribbon max strain | worst wire strain | worst squeeze (mm) |
|---|---|---|---|---|---|---|---|
| S1 radar | 0.000 | 0.02 | no | 1.82 | 0.3 % | 0.3 % (radar OT1 -> XIAO D7) | 0.00 (ribbon, vs None) |
| S2 tact switch | 0.000 | 0.02 | no | 2.09 | 0.1 % | 0.0 % (button leg A -> XIAO D10 (input, pull-up)) | 0.00 (ribbon, vs None) |
| S3 keeper A | 0.000 | 0.02 | no | 2.22 | 0.1 % | 1.2 % (radar OT1 -> XIAO D7) | 0.40 (radar OT1 -> XIAO D7, vs radar) |
| S4 camera + heatsink | 0.000 | 0.02 | no | 0.96 | 27.7 % | 1.0 % (radar GND -> XIAO GND) | 0.40 (radar OT1 -> XIAO D7, vs radar) |
| S5 keeper B | 0.000 | 0.02 | no | 0.70 | 74.2 % | 1.0 % (radar GND -> XIAO GND) | 0.40 (radar OT1 -> XIAO D7, vs radar) |
| S6 XIAO stack | 0.000 | 0.02 | no | 0.70 | 74.2 % | 1.1 % (radar GND -> XIAO GND) | 0.40 (radar OT1 -> XIAO D7, vs radar) |
| S7 keeper C | 0.000 | 0.02 | no | 0.77 | 29.5 % | 19.2 % (radar GND -> XIAO GND) | 0.90 (radar 3V3 -> XIAO 3V3, vs keeper_c) |
| S8 sleeve over module | 0.000 | 0.02 | no | 0.77 | 29.5 % | 51.0 % (U.FL coax) | 0.90 (radar 3V3 -> XIAO 3V3, vs keeper_c) |

Confirmatory run with 22 mm slack (`final_h14_s22_dress`): ribbon identical to the table above (S6 1.56 mm, S8 1.96 mm); wires clean in S4–S6 and S8; S3 and S7 show
transient wire tension (47 % / 51 %), S7 with a 0.18 mm squeeze against keeper C.

Other runs kept in `out/sim/` for the record: `final_s30` (hold-off 25 mm, slack 30: S8 button wire caught, 0.85 mm), `final_s8`
(slack 8: wires taut 66 %, squeeze 1.10 mm), `final_h14_s12` (slack 12: button wire taut 33 %, squeeze 1.10 mm), `runA…runH22`
(faster 6–20 mm/s runs from before the speed check; their ribbon-strain peaks are partly solver lag, see §2).

**Images and video** (frames: ribbon coloured by bend radius, red < 2 mm; wires coloured by role; red dots = squeezed):
* per-step key frames: `out/sim/render/final/step_S*.png`; whole assembly: `out/sim/render/final/assembly_simulation.mp4`
* tightest-bend / worst-squeeze close-ups per step: `out/sim/render/final_dress_S*.png`, `…_events_all_steps.png`
* failure case (rendered with the earlier 8 × 8 × 6.1 heatsink; numbers for the new one are in §3b): `out/sim/render/fail_hold6_S*.png` and `render/fail_hold6_video/assembly_simulation.mp4`
* radar study: `out/sim/render/radar_R*.png`, `radar_all_cases.png`

### 3b. Heatsink changed to 7.0 × 7.1 × 6.0 (+ 0.1 mm pad): what moved

Re-run with the same engine, 3 mm/s. **Final procedure (14 mm hold-off, dressed wires, 16 mm slack): every number in the table above is
identical to three digits** (ribbon radius per step, strain, wire strain, squeeze, S6 dip 1.56 mm at (15.3, 45.3, 124.0)). Reason: at 14 mm hold-off
nothing flexible comes near the heatsink (closest ribbon centre line 2.43 mm from the camera/heatsink surface, wires > 9.5 mm), so its size cannot matter.

**Hold-off scan** (S1–S3 assumed done; S4 camera, S5 keeper B, S6 XIAO descent; parts start 14 mm above their seats; `out/sim/hold_*.json`):

| XIAO hold-off | S4 ribbon R / strain | S5 ribbon R / strain | S6 ribbon R | verdict |
|---|---|---|---|---|
| 6 mm | 1.46 mm / 3.7 % (was 0.96 / 27.7 % with 8 × 8 × 6.1) | **0.72 mm / 51 %**, squeeze 0.21 | 0.71 mm | fails (S5, keeper B) |
| 10 mm | 1.67 mm / 4.0 % | **0.59 mm / 96 %** | 1.76 mm | fails (S5) |
| 11 mm | 1.83 mm / 4.0 % | **0.52 mm / 76 %** | 1.59 mm | fails (S5) |
| 12.5 mm | 1.83 mm / 4.1 % | 2.14 mm / 0.3 % | 1.54 mm | clean |
| 14 mm (full run) | 2.37 mm / 4.2 % | 2.38 mm / 0.3 % | 1.56 mm | clean |

* **The 11.7 mm hold-off was wrong, but not because of the heatsink.** It came from the heatsink bottom (z 127.2, staged z 113.2, needs hold-off
  > 124.52 − 113.2 = 11.3 mm). Keeper B's floor underside is 0.8 mm lower (z 126.4, staged 112.4) and needs > 124.52 − 112.4 = **12.1 mm**.
  The new heatsink has the same bottom z, so the heatsink-only threshold stays 11.3 mm; the simulation shows keeper B failing at 11 mm.
  **Use ≥ 12.5 mm** (valid when parts start 14 mm above their seats; the rule is that the ribbon's down-run must stay behind the underside of
  the part being lowered).
* **What the heatsink change did change:** with the XIAO held 6 mm aside the S4 camera drop is much gentler (R 0.96 → 1.46 mm, strain 28 → 3.7 %)
  because the narrower, shorter heatsink covers less of the ribbon's down-run (y 47.85 is now 0.68 mm inside the heatsink's y edge at 47.175,
  was 1.1 mm). The S5 keeper-B failure is the same as before (0.72 vs 0.70 mm).
* **The S6 dip does not change:** 1.56 mm (14 mm hold-off), 1.54 mm (12.5), 1.59 mm (11); same place, the first bend below the connector. The ribbon is
  nowhere near the heatsink during S6.

## 4. Can the radar sit ~6.2 mm behind the window?

**Answer: not in the current architecture. Yes geometrically if the board moves behind the lip, but then nothing holds it.**

Hi-Link's radome guide asks for an antenna-to-radome distance of an integer multiple of the half-wavelength in air
(λ/2 = 6.2 mm at 24.125 GHz), tolerance ±1.2 mm, so the antenna plane (PCB front face) must be at z = 133.5 (132.3–134.7).
Window inner face z = 139.7 (0.8 mm window, front face z = 140.5). Lip slab z 134.5–137.0, opening 19.4 × 67.2.

| Option | Antenna to window H | Verdict | What blocks it (dimension) |
|---|---|---|---|
| **A. Current: board on top of the lip, in the bore** | 1.0 mm (max 1.5 mm with the board touching the lip top) | does not reach 6.2 | bore depth between lip top (z 137.0) and window inner face (z 139.7) is **2.7 mm**; the 1.2 mm PCB takes 1.2 of it, so H ≤ 1.5 mm. 4.7 mm short. The sleeve STL is fixed. |
| B. Recessed window | ≤ 1.0 mm | no gain | the window already sits at the front face (z 139.7–140.5). A recess can only move it *inward*, which reduces H. A thinner window gains 0.4 mm at most (0.8 → 0.4 mm), and costs RF margin. |
| C. Different orientation (45°, on edge) in the bore | n/a | does not fit | the board is 20 mm in both directions; the bore is 2.7 mm deep. Any tilt that raises a board edge to H = 6.2 mm puts that edge inside the 2.5 mm lip slab. |
| D. Different board position in x/y | unchanged | no effect | H depends only on z. x/y only changes which part of the opening the board covers. |
| **E. Board behind the lip (below z 134.5), antenna plane z 133.5 … 134.5** | **5.2 – 6.2 mm** (6.05 with the front components touching the lip underside) | **geometrically possible** | the 20.0 mm board is wider than the 19.4 mm opening, so it only overlaps the lip by 0.3 mm per side (long edges). It can be loaded **from the bottom** (the open end). Nothing in the current insert retains it there, so a retainer must be added (below). |

### Physical simulation of option E (same engine, real sleeve mesh)

| Case | Result |
|---|---|
| R1 flat, pushed in from the front through the opening (board free to rock) | passes, rocks ~4°, ends flat at z_ant = 133.5 (H = 6.2) |
| Tilt locked at 0° / 2° | **jams** at z_ant = 137.7 / 137.2 (the 20.0 mm edge hits the 19.4 mm opening); hand lag 4.2 / 3.7 mm |
| Tilt locked at ≥ 4° | passes (analytic threshold 20·sinθ + 1.2·cosθ ≥ 2.5 → θ ≈ 3.3°) |
| R2/R2b tilted 20°/15° from the front | passes, reaches H = 6.2 |
| R4 on edge (90°) | passes, reaches H = 6.2 |
| R3 flat from the bottom, pushed up | stops against the lip underside; the hand-guided board ends tilted 7.5° (H = 4.0 mm at the centre); flat against the underside would be H = 5.2 mm (geometry, not simulated flat) |

Penetration after contact resolution ≤ 0.08 mm; 200 k-point re-check ≤ 0.008 mm.

**Field of view cost** (ray trace through the lip opening, window transparent): at H = 6.2 the board centre sees ±60° in
x–z and ±79° in y–z (current design: ±81° / ±85°). A patch edge at x = ±8 mm sees −26° … +71° (current: −67° … +85°). The
x-direction cone narrows by about a quarter; for a presence sensor at 24 GHz that is the price.

### What would have to be designed for option E (not designed, not verified)
* A bottom-loaded retainer, glued to the sleeve walls, that presses the board against the lip underside along the two
  0.3 mm long-edge strips (or a 0.5 mm-thick frame that spans it). Everything below the lip belongs to the sleeve, which cannot change.
* The keepers and the insert faceplate would no longer carry the radar pocket; the radar harness would exit toward the XIAO
  through the bottom instead of through keeper A's wire slot.
* This changes the face-down assembly order (the radar becomes the last part inserted, from the bottom).

Recommendation: keep option A unless a range test on the coupon shows the 1 mm configuration is too weak; option E is the
only route to 6.2 mm and needs its own design round.

## 5. Re-run

```
python src/sim/build_sdfs.py                      # signed-distance fields (cached in out/sim/cache, ~6 min)
python src/sim/scenario.py --slack 16 --xiao-stage 14 --speed 3 --dress --out out/sim/run.pkl   # ~25 min
python src/sim/report_sim.py out/sim/run_events.json
python src/sim/render_sim.py out/sim/run.pkl out/sim/render/run       # key frames + mp4
python src/sim/render_events.py out/sim/run.pkl out/sim/render run    # tightest-bend / worst-squeeze close-ups
python src/sim/radar_study.py ; python src/sim/radar_study.py extra ; python src/sim/render_radar.py
python src/sim/speed_test.py S4 12 4 1.5          # solver-lag check
python src/sim/speed_test.py hold 12.5 3          # S4-S6 at one hold-off (-> out/sim/hold_12.5.json)
```
Files: `src/sim/{meshes,sdf,physim,scenario,render_sim,render_events,render_radar,radar_study,report_sim,diag_ribbon,speed_test}.py`.
