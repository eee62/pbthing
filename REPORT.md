# REPORT — insert, plug and helpers for the zen_v7 sleeve

## Bottom line

* **Design is complete and passes every numeric check I wrote** (`out/logs/verify.txt`,
  111 checks, 0 failures). Checks use exact B-rep booleans (CadQuery/OCCT), not sampled points,
  except wall thickness (ray casting on the exported STL).
* **Nothing has been printed or physically tested.** The biggest unknowns are the camera module,
  the radar's component heights and its RF behaviour behind a 1 mm air gap, and the cable
  overmold. All of them are on the fit coupon, which should be ordered first.
* **Three things differ from the brief**, each forced by the measured geometry (details below):
  1. The XIAO, camera, radar and button go in **with the insert from the top** (the module is
     assembled face-down on glass, then the sleeve is lowered over it). Only the holder and plug
     enter from the bottom.
  2. Three small **keepers** (on the tray) hold the radar/button, camera and XIAO; they are glued
     only in the insert seam. One more glue point is listed: holder base to plug (G3).
  3. The XIAO ESP32-S3 has **no on-board antenna** (U.FL only). The facts file does not mention
     it; I added a mounting face for the supplied FPC antenna.
* Order: **(1) coupon + tray** → test → **(2) insert + plug** (+ tray again only if a
  parameter changed). Three print files in the big order.

---------------------------------------------------------------------------------------
## 1. Measured inputs (trust these over the facts file)

| Item | Facts file | Measured / datasheet | Source |
|---|---|---|---|
| Sleeve outer | 29.4 x 77.2 x 140.5 | same, outer corner r 7.0 | STL |
| Cavity | 24.4 x 72.2, r~4 | same, r 4.0 | STL |
| Lip | z 134.5–137.0, opening ~19.4 x 67.2 | same, opening corner r 1.5 | STL |
| Bore | z 137–140.5 | same (3.5 deep, 24.4 x 72.2 r4) | STL |
| Ends | open both ends | confirmed: vertices only at z 0, 134.5, 137, 140.5 | STL |
| Free space beside holder at each y end | ~4.9 | **5.6** ((72.2 − 61)/2) | STL |
| Switch pin pitch / row spacing | 2.54 / 5.0 [GUESS] | **2.5 / 6.0** | G-Switch PB-22E08-LC drawing |
| Switch size | 8x8 (8.5), 8x8x13 | body **8.0 x 8.0 x 8.0**, knob 5.5 above body (H = 13.5), pins 3.5 | datasheet |
| Switch travel | 2–2.5 | lock 1.5 ±0.15, full 2.5 ±0.2 | datasheet |
| Switch rating | 0.3–0.5 A, 30 V | 1 A 12 V DC (drawing); 0.5 A 30 V (LCSC) | datasheet / LCSC |
| Radar | — | 20.0 x 20.0, PCB 1.2 ±10 %, J2 5 holes 2.54 pitch from 1.62 | HLK manual §9 |
| Radar housing | thin ~0.8 | λ/2 in medium or ≤ λ/8; antenna-to-cover ideal 6.2 mm | Hi-Link/Waveshare radome guide |
| XIAO stack | — | 22.8 (with USB-C) x 17.8 x 8.0; USB-C tip 1.53 beyond PCB edge | STEP |
| STEP "MicroSD v2" | — | is the **inserted card** (protrudes past the USB-C); excluded | STEP |
| Stock camera FPC | ~13 wide | 12.5 wide tail, leaves the connector **toward the USB end** | STEP |
| XIAO antenna | not mentioned | **U.FL only**, no PCB antenna | STEP (U.FL part), Seeed docs |
| XIAO BAT pads | — | two 0.76 x 1.78 pads on the bottom; BAT− nearer the USB-C | STEP + OpenELAB wiki [verify silkscreen] |

The sleeve was rebuilt as an exact B-rep from these numbers; all 352 STL vertices lie on it
(max deviation 0.0000 mm; volume differs +0.09 % because the STL facets the corner radii).

---------------------------------------------------------------------------------------
## 2. Design decisions (and why)

**Top module enters from the top, not "boards from the bottom".** The camera FPC must be
latched into the expansion-board connector on the bench, so board and camera are one harness;
the radar and button are wired to the same board. The 19.4 mm lip opening passes the 17.8 mm
XIAO stack (0.55 mm per side after 0.25 clearance) — verified as a swept volume. Docking the
XIAO blind 115 mm deep from the bottom could not be guided or checked.

**Face-down assembly on glass.** The insert lies face-down; every part drops into its pocket by
gravity; three keepers are laid on from the inside; the sleeve is lowered over everything
until its front face touches the glass. This makes the faceplate flush by construction (the
pads float 0.25 mm under the lip in epoxy) instead of relying on the ±0.2 mm print tolerance.

**Radar sits above the lip.** It is 20.0 wide and the lip opening is 19.4, so it overhangs the
lip by 0.3 per side and must stay in the 3.5 mm bore zone: PCB back at z 137.5 (0.5 above the
lip top), window 0.8 mm, front components assumed ≤ 0.85 mm. The factory 5-pin header must be
removed (its plastic would hit the lip and the keeper).

**XIAO orientation.** Board width (17.8) across x, stack thickness along y, USB-C up. This puts
USB-C and lens on the centre line and lets the 12.5–13 mm FPC run with all bends about one
axis (no twist): out of the connector toward +y under the SD socket (r 2), up (r 2), 180° fold
under the camera (r 2), down, U-loop (r 2.35, bottom z 112.2 for a 65 mm FPC), up and 90°
into the head (r 2). The loop depth is solved from the FPC length; 40–85 mm all fit
(loop bottom z 124.8 … 102.3, holder top z 97).

**Front layout** (y along the face): radar window (blank) 5.3–25.3 · button Ø7 at 30.75 ·
USB-C pocket 12.9 x 7.0 at 40.63 · lens cap Ø11 at 50.8 · FPC guide wall + antenna. The three
visible features cluster around the face centre (38.6).

**Button.** Flush Ø7 pad in a 0.8 mm visible ring seam, on a hidden cantilever beam
(4.8 x 2.0 x 0.8, lever 8.3 mm) under a 0.8 mm skin with a 0.8 mm gap. Full travel 0.45 mm
(0.2 pre-travel + 0.25 switch) gives 0.85 % root strain and 0.54 N beam force; the tact switch
body is the hard stop. Engraved power icon: 0.8 lines, 0.8 deep, ≥ 0.83 land.

**XIAO retention.** USB-C shell in a closed collar (0.30 per side), collar underside is the
stop for the PCB edge (takes cable pull-out), keeper C's U-foot takes cable insertion and
holds the bottom end in y. No snaps, no flexing.

**Main switch: under the holder, in the bottom plug.** Beside the holder there is 5.6 mm, not
enough for an 8 mm body. The holder is raised to z 21–97. The switch rides in a printed
carrier that slides into the plug from its −x side face (knob in a hidden channel above a
0.8 mm skin); after the plug goes into the sleeve, the sleeve wall closes that opening
(carrier play 0.35). Six carrier variants (H = 10, 11, 12, 13, 13.5, 14) keep the knob tip at
the same depth whatever knob length you buy: **released 1.00 mm recessed, latched 2.50,
full press 3.50**, in a Ø10 → Ø7.4 conical dimple. A pen tip or fingernail is required; a
fingertip only reaches ~1.8 mm (rigid-sphere estimate), so finger operation is not claimed.
Both poles are paralleled with jumpers 2–5 and 3–6 in the battery-positive line.

---------------------------------------------------------------------------------------
## 3. Parts to order

| File | What it is | Qty | Order |
|---|---|---|---|
| `out/stl/coupon.stl` | fit coupon: exact crops of the insert front end and plug switch area | 1 | 1st |
| `out/stl/tray.stl` | keepers A, B, C; switch carriers H10/11/12/13/13.5/14; lens caps A/B/C; USB covers A/B/C, on one frame with Ø1.0 snap-off posts | 1 | 1st (re-order with order 2 only if parameters change) |
| `out/stl/insert.stl` (+ `out/step/insert.step`) | one-piece faceplate + tray: radar pocket and window, button flexure, USB-C collar and overmold pocket, camera pocket, cap pocket, backbone, FPC guide wall, antenna face | 1 | 2nd |
| `out/stl/plug.stl` (+ `out/step/plug.step`) | flush bottom plug: dimple + knob hole, carrier pocket, holder cradle | 1 | 2nd |
| `out/stl/tray_parts/*.stl`, `out/step/keeper_*.step` | the tray parts individually (reference only, do not order separately) | – | – |

Printed volumes (cost driver) are in the table in §5. No fasteners. Purchased parts: see
ASSEMBLY §0.

---------------------------------------------------------------------------------------
## 4. Verification summary (numbers from `out/logs/verify.txt`)

| Check | Result |
|---|---|
| Sleeve rebuilt as exact B-rep vs STL | 352/352 vertices on surface (max dev 0.0000 mm), volume +0.09 % |
| Every printed part one valid watertight solid (B-rep and STL) | 4 print files + 19 tray parts: all 1 body |
| Interference, exact boolean volume | 406 pairs of 29 bodies (sleeve, insert, 3 keepers, plug, carrier, XIAO from STEP, radar, tact, camera, switch, holder, antenna, caps, FPC, 12 wires): max overlap 0.000000 mm3 |
| Top module passes the 19.4 x 67.2 lip | 0.000 mm3 outside; min clearance to lip 0.250 |
| Top module above the lip inside the bore | 0.000 mm3 outside |
| Install sweeps (exact prisms): keeper A, keeper B, keeper C, caps; XIAO (+z, boxes/prisms); carrier along +x; plug sub-assembly from below | all 0.000 mm3 |
| Carrier captured by sleeve wall | 0.35 mm play, 4 mm engagement |
| Min wall (ray casting, opposite faces) | insert 0.80, plug 0.80, keepers 0.80, carrier 0.95, caps 1.20, coupon 0.80 (rule 0.8) |
| Min internal slot/gap that must stay open | insert 0.80 (button ring seam, beam gap), coupon 0.80 (rule 0.8) |
| Worst-case clearances | all fits ≥ 0 (table 5.1); caps: variant C always fits |
| Wires: 12 wires + FPC swept at real size | 0 overlaps; min bend r 2.0 (wires, FPC), 2.5 (coax) |
| FPC 65 mm | loop bottom z 112.2, 15.2 above holder; 40–85 mm lengths also fit |
| Main switch, H = 10…14 | no overlap in released/latched/full states; recess 1.00 / 2.50 / 3.50 for every H |
| Front button | icon depth 0.80, line 0.80, land 0.83; flexure strain 0.85 % at 0.45 mm, force 0.54 N |
| Radar window | 0.8 mm ≤ λ/8 for εr ≤ 3.8; antenna-to-window H = 1.00 mm (risk) |
| Lens field of view | 123.9° unvignetted (assumed Ø5 front glass) |

---------------------------------------------------------------------------------------
## 5. Tables (generated from `out/logs/verify.json`)

### 5.1 Worst-case clearance per fit
Rule used: worst = nominal − (tolA + tolB)/2 − (purchased-part tolerance where stated). Printed
parts ±0.2 (holes ±0.3). Purchased parts assumed ±0.1–0.2 where no data. Rows marked
"friction option" are the tighter cap/cover variants A and B: they are meant to be tight and
may not go in at the worst case; variant C always fits (worst ≥ 0).

| Fit | Nominal | tol A | tol B | extra | Worst case | Note |
|---|---:|---:|---:|---:|---:|---|
| faceplate edge to sleeve bore (per side) | 0.250 | 0.2 | 0.2 | 0.0 | **+0.050** |  |
| insert / keepers to lip opening (per side) | 0.250 | 0.2 | 0.2 | 0.0 | **+0.050** |  |
| pads to lip top (glue line, z) | 0.250 | 0.2 | 0.2 | 0.0 | **+0.050** |  |
| keeper ears to lip top (z) | 0.500 | 0.2 | 0.2 | 0.0 | **+0.300** |  |
| keeper ears to faceplate rim (z, glue fills; foot/posts touch first) | 0.200 | 0.2 | 0.2 | 0.0 | **+0.000** | >=0 means the keeper rests on its part, not on the rim |
| radar PCB to radar pocket walls (per side) | 0.300 | 0.2 | 0.2 | 0.0 | **+0.100** | radar 20.0 +-0.1 [GUESS tol] |
| radar PCB back to lip top (z, PCB overhangs lip 0.3) | 0.500 | 0.2 | 0.2 | 0.12 | **+0.180** |  |
| radar front components to window (z) | 0.150 | 0.2 | 0.0 | 0.0 | **+0.050** | component height is [GUESS] |
| tact switch to its pocket (per side) | 0.250 | 0.2 | 0.2 | 0.0 | **+0.050** |  |
| button nub to tact actuator (pre-travel) | 0.200 | 0.2 | 0.2 | 0.0 | **+0.000** |  |
| button pad ring slot (single part, stays open) | 0.800 | 0.2 | 0.2 | 0.0 | **+0.600** |  |
| hidden beam to skin gap (single part, stays open) | 0.800 | 0.2 | 0.2 | 0.0 | **+0.600** |  |
| USB-C shell to collar opening (hole, per side) | 0.300 | 0.3 | 0.2 | 0.0 | **+0.050** |  |
| XIAO bottom face to top rib (backup stop) | 0.300 | 0.2 | 0.2 | 0.0 | **+0.100** |  |
| XIAO bottom face to keeper C -y wall | 0.200 | 0.2 | 0.2 | 0.0 | **+0.000** |  |
| XIAO connector housing to keeper C +y lip | 0.220 | 0.2 | 0.2 | 0.0 | **+0.020** |  |
| camera head to pocket (per side) | 0.250 | 0.2 | 0.2 | 0.0 | **+0.050** | head size [GUESS] |
| lens barrel to lens opening (hole, per side) | 0.250 | 0.3 | 0.2 | 0.0 | **+0.000** |  |
| lens barrel top to cap underside (z) | 0.400 | 0.2 | 0.2 | 0.1 | **+0.100** |  |
| lens cap A in cap pocket (hole, per side) (friction option) | 0.050 | 0.3 | 0.2 | 0.0 | **-0.200** | friction fit: pick the variant that holds |
| USB cover A in overmold pocket (per side) (friction option) | 0.050 | 0.3 | 0.2 | 0.0 | **-0.200** | friction fit |
| lens cap B in cap pocket (hole, per side) (friction option) | 0.150 | 0.3 | 0.2 | 0.0 | **-0.100** | friction fit: pick the variant that holds |
| USB cover B in overmold pocket (per side) (friction option) | 0.150 | 0.3 | 0.2 | 0.0 | **-0.100** | friction fit |
| lens cap C in cap pocket (hole, per side) | 0.250 | 0.3 | 0.2 | 0.0 | **+0.000** | friction fit: pick the variant that holds |
| USB cover C in overmold pocket (per side) | 0.250 | 0.3 | 0.2 | 0.0 | **+0.000** | friction fit |
| cable overmold 12.35 x 6.5 [GUESS] in pocket (per side, short side) | 0.250 | 0.3 | 0.0 | 0.0 | **+0.100** |  |
| holder to plug cradle walls (per side) | 0.250 | 0.2 | 0.2 | 0.0 | **+0.050** | holder tol [GUESS] +-0.2 |
| plug to cavity wall (glue line, per side) | 0.250 | 0.2 | 0.2 | 0.0 | **+0.050** |  |
| switch carrier to plug pocket (per side, y) | 0.250 | 0.2 | 0.2 | 0.0 | **+0.050** |  |
| switch carrier to pocket roof (z) | 0.250 | 0.2 | 0.2 | 0.0 | **+0.050** |  |
| switch body to carrier walls (per side) | 0.250 | 0.2 | 0.2 | 0.0 | **+0.050** | datasheet: +-0.2 over 1.5 mm |
| switch body top to carrier bridge (z, lost motion) | 0.150 | 0.2 | 0.1 | 0.0 | **-0.000** |  |
| knob (3.9 sq, diag 5.52) to knob hole D7.4 incl. 0.6 carrier play | 0.342 | 0.3 | 0.2 | 0.0 | **+0.092** |  |
| knob to carrier shelf slot (per side) | 0.300 | 0.2 | 0.2 | 0.0 | **+0.100** |  |

| Wire / ribbon | Length mm | Min bend r | Clearance to solids | Clearance to other wires |
|---|---:|---:|---:|---:|
| camera FPC 13.0 x 0.15 | 65.0 | 2.0 | 0.000 | 6.165 |
| radar RX -> XIAO D8 | 28.5 | 2.0 | 0.000 | 1.440 |
| radar OT1 -> XIAO D7 | 33.6 | 2.0 | 0.000 | 1.440 |
| radar GND -> XIAO GND | 24.1 | 2.0 | 0.000 | 0.850 |
| radar 3V3 -> XIAO 3V3 | 28.5 | 2.0 | 0.000 | 0.420 |
| button leg A -> XIAO D10 (input, pull-up) | 14.4 | 2.0 | 0.250 | 1.440 |
| button leg B -> XIAO D9 (driven LOW) | 19.1 | 2.0 | 0.250 | 0.180 |
| jumper pin2-pin5 | 4.8 | None | 0.453 | 1.200 |
| jumper pin3-pin6 | 4.8 | None | 0.453 | 1.200 |
| holder B+ (red) -> switch pin 2 | 38.7 | 2.0 | 0.050 | 0.100 |
| switch pin 3 -> XIAO BAT+ | 168.5 | 2.0 | 0.100 | 0.100 |
| holder B- (black) -> XIAO BAT- | 138.1 | 2.0 | 0.050 | 0.100 |
| U.FL coax -> antenna | 37.8 | 2.5 | 0.498 | 2.358 |

| Part | Volume mm3 | Bounding box mm | Min wall | Min internal gap |
|---|---:|---|---:|---:|
| insert | 4062 | 23.9 x 71.7 x 34.5 | 0.80 | 0.80 |
| plug | 7412 | 23.9 x 71.7 x 27.0 | 0.80 | 2.62 |
| tray | 10375 | 100.3 x 63.2 x 27.8 | nan | nan |
| coupon | 4284 | 23.9 x 74.1 x 18.0 | 0.80 | 0.80 |
| keeper_a | 444 | 23.6 x 27.2 x 6.7 | 0.80 | 2.10 |
| keeper_b | 216 | 23.6 x 8.4 x 6.2 | 0.80 | nan |
| keeper_c | 749 | 23.6 x 13.7 x 24.8 | 0.80 | nan |
| carrier_H10 | 875 | 17.2 x 10.4 x 15.7 | nan | nan |
| carrier_H11 | 875 | 17.2 x 10.4 x 15.7 | nan | nan |
| carrier_H12 | 875 | 17.2 x 10.4 x 15.7 | nan | nan |
| carrier_H13 | 875 | 17.2 x 10.4 x 15.7 | nan | nan |
| carrier_H13.5 | 875 | 17.2 x 10.4 x 15.7 | 0.95 | nan |
| carrier_H14 | 875 | 17.2 x 10.4 x 15.7 | nan | nan |
| lens_cap_A | 111 | 10.9 x 10.9 x 1.2 | 1.20 | 1.20 |
| usb_cover_A | 123 | 12.8 x 6.9 x 1.5 | 1.50 | 1.20 |
| lens_cap_B | 107 | 10.7 x 10.7 x 1.2 | nan | nan |
| usb_cover_B | 118 | 12.6 x 6.7 x 1.5 | nan | nan |
| lens_cap_C | 103 | 10.5 x 10.5 x 1.2 | nan | nan |
| usb_cover_C | 113 | 12.4 x 6.5 x 1.5 | nan | nan |

| Switch H (body+knob) | Recess released | Recess latched | Recess full press | Pin tip z | Room to holder |
|---:|---:|---:|---:|---:|---:|
| 10.0 | 1.00 | 2.50 | 3.50 | 14.50 | 6.50 |
| 11.0 | 1.00 | 2.50 | 3.50 | 15.50 | 5.50 |
| 12.0 | 1.00 | 2.50 | 3.50 | 16.50 | 4.50 |
| 13.0 | 1.00 | 2.50 | 3.50 | 17.50 | 3.50 |
| 13.5 | 1.00 | 2.50 | 3.50 | 18.00 | 3.00 |
| 14.0 | 1.00 | 2.50 | 3.50 | 18.50 | 2.50 |

---------------------------------------------------------------------------------------
## 6. Assumptions [GUESS] and how they get confirmed

| # | Assumption [GUESS] | Value used (param) | Confirmed by |
|---|---|---|---|
| G1 | OV5640 head 8.5 x 8.5, base 0.3 + body 4.7 + barrel Ø7.9 x 1.0 (total 6.0) | `CAM_*` | coupon step 4; calipers |
| G2 | Camera FPC 13.0 x 0.15 x 65 mm, leaves the head edge in-plane toward +y, bendable at r 2 | `FPC_*` | measure; loop auto-solves for 30–85 mm |
| G3 | Lens front glass Ø5, FOV 120° | `LENS_*` | coupon; unvignetted limit computed |
| G4 | Radar front components ≤ 0.85 mm; back components ≤ 1.1 mm and ≥ 1.5 mm from the edge at the 3 keeper posts | `RAD_FRONT_H`, posts | coupon step 1; calipers |
| G5 | Radar J2 hole 1.27 from the edge, pin order OT2-RX-OT1-GND-3V3 from the −x end | `RAD_PIN_*` | look at the board |
| G6 | 9000HE relative permittivity 2.6–3.8 at 24 GHz | window 0.8 | radar range test on the coupon |
| G7 | Tact switch: body 3.5 + Ø3.5 actuator, legs 6.5 x 4.5, travel 0.25 | `TACT_*` | coupon step 2 |
| G8 | Your switch knob height H; latched-closed contacts 2-3 / 5-6 | carrier variants | calipers, multimeter |
| G9 | Holder 76 x 61 x 20 ±0.2; leads leave its −y end face near the bottom (z 25) | `HOLDER_*` | look at the holder; re-route if not |
| G10 | USB-C cable overmold ≤ 12.35 x 6.5 mm (spec maximum, not verified) | `OVM_*` | coupon step 3 with your cables |
| G11 | Antenna FPC 30 x 8 x 0.3 with Ø1.13 coax, ≥ 40 mm | `ANT_*` | the antenna in the box |
| G12 | XIAO BAT+ / BAT− pads = the two 0.76 x 1.78 pads (BAT− nearer the USB-C) | wires | silkscreen / meter |
| G13 | Wire OD 1.1 (28–30 AWG silicone, max) | `WIRE_D` | — |
| G14 | Resin flexural modulus 2.5 GPa; < 1 % strain is safe | flexure | coupon button test |
| G15 | Purchased-part tolerances ±0.1–0.2 where no datasheet | tolerance table | — |
| G16 | D8/D9/D10 free without an SD card (pull-ups harmless) | wiring | firmware test |

---------------------------------------------------------------------------------------
## 7. Not verified numerically

* RF: radar detection through the 0.8 mm window with only 1.0 mm antenna-to-window distance
  (Hi-Link prefers 6.2); WiFi range with the antenna 30 mm from three steel cells.
* Friction of the caps/covers (resin-on-resin friction, creep, the 0.15–0.2 mm post-delivery
  drift).
* Real shape of the FPC and wires. They are modelled as ideal swept paths through open channels;
  the battery-lead slack and the two splices (stored above the holder) are not modelled.
* Solder-joint sizes on the castellations (only 0.55 mm per side to the lip opening).
* Heat (charging, WiFi, camera) against the 60 °C deflection temperature.
* Drop / shock; brittleness of the 0.8 mm features.
* Resin drainage from the 0.8 mm gap under the button skin.
* No acoustic path for the microphone was designed (the seams are the only openings).
* That a fingertip can operate the main switch (pen tip / nail assumed).

---------------------------------------------------------------------------------------
## 8. Highest risks (ranked)

1. **Radar performance behind the window.** 1.0 mm air gap instead of the recommended 6.2 mm
   cannot be changed: the lip at 3.5 mm depth forces the 20 mm board into the bore zone. Test on
   the coupon before ordering the insert. If range is poor there is no geometric fix inside this
   sleeve; the alternative is a radar ≤ 19 mm wide that can sit below the lip.
2. **Camera module geometry and FPC behaviour** (G1–G3). The fold under keeper B has 0.25 mm
   clearance above it and 0.25 mm to keeper B. A thicker stiffener, wider FPC or different exit
   edge breaks the route. Measure the module first.
3. **USB-C cable fit and retention.** Receptacle 1.97 mm below the face in a 12.9 x 7.0 pocket;
   large overmolds will not seat. Pull-out force goes into the insert seam glue (G1).
4. **Cap/cover friction fit.** Brittle resin, ±0.25 per-side combined error, drift after delivery:
   one of A/B/C should hold, but it may need a drop of paint/varnish to tighten later.
5. **Assembly difficulty.** Wiring the XIAO bottom pads with joints kept inside the board
   outline (0.55 mm margin), dressing the FPC fold, gluing three keepers face-down, and splicing
   the battery leads inside the 24 x 72 mm cavity.

Further risks: holder lead exit position (G9); radar rattle ≤ 0.3 mm if keeper A ends up
resting on the rim instead of the radar (glue fills it); ±0.45 mm lost motion of the main
switch body between shelf and bridge.

---------------------------------------------------------------------------------------
## 9. If the printed result does not fit

Every number is in `src/params.py` (or the top of `src/parts.py`). After a change run
`python src/build.py && python src/verify.py && python src/render.py`.

| Symptom | Change |
|---|---|
| Faceplate proud of the sleeve (sleeve does not reach the glass) | sand the 5 pads + radar skirt bottom (up to 1.25 mm available), or lower `PAD_H` |
| Faceplate seam uneven | centre with 0.2 mm paper strips during cure; if > 0.45 mm total, reduce `G_FACE` |
| Insert body will not pass the lip | `G_LIP` 0.25 → 0.35 |
| Radar does not seat / touches window | measure front height → `RAD_FRONT_H`; pocket → `RAD_POCKET_CLR` |
| Radar range poor | see risk 1 (no fix inside this sleeve) |
| Button too stiff / cracks | `BEAM_W` 2.0 → 1.5; too soft: `BEAM_W` 2.5 |
| USB-C shell tight in collar | `COLLAR_CLR` 0.30 → 0.40 |
| Cable overmold does not seat | `OVM_W`, `OVM_H` (wall to lens pocket is 1.2 mm on +y) |
| Camera head tight / loose | `CAM_W`, `CAM_POCKET_CLR`; barrel `CAM_BARREL_D`, `LENS_OPEN_D`; height `CAM_BODY_H` |
| FPC length or width differs | `FPC_LEN` (loop re-solves), `FPC_W` |
| Caps all loose / all tight | shift `CAP_VARIANTS` by the measured error (keep 0.10 steps) |
| Switch knob too deep / proud | pick another carrier; or `SW_RECESS_OUT` |
| Switch body tight in carrier | `SW_CLR` 0.25 → 0.35 |
| Holder does not drop into cradle | `HOLDER_CLR` 0.25 → 0.4 |
| Plug tight in sleeve | `G_PLUG` 0.25 → 0.35 |
| Parts grew/shrank after a week | re-measure, update `TOL`, rebuild |

---------------------------------------------------------------------------------------
## 10. Files

* `src/params.py` all parameters (tagged) · `src/components.py` purchased parts (XIAO from STEP)
* `src/parts.py` printed parts · `src/wires.py` FPC, wires, coax · `src/build.py` export
* `src/verify.py` verification · `src/render.py` images · `src/measure.py` input measurements
* `out/stl`, `out/step` print files · `out/img` renders · `out/logs` measure/verify logs
* `inputs/` the supplied files plus the switch datasheet and radome guide that were used

Renders: `out/img/front.png`, `front_caps_off.png`, `bottom.png`, `exploded.png`,
`section_top_x14.7.png` (radar, button, USB-C, camera, FPC), `section_bottom_x14.7.png`
(switch, carrier, plug, holder), `section_y38.6_switch.png`, `section_y30.45_button.png`,
`section_full_x14.7.png`, `wires_all.png`, `wires_top.png`, `wires_top_side.png`,
`print_coupon.png`, `print_tray.png`, `insert_from_below.png`.
