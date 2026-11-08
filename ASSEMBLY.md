# ASSEMBLY — hidden-sensor "power bank" (zen_v7 sleeve)

Nothing here has been built or tested physically. Every dimension comes from the model
(`src/*.py`) and was checked by `src/verify.py` (log: `out/logs/verify.txt`). Read
`REPORT.md` first for what is assumed.

Frame used everywhere: x = 29.4 width, y = 77.2 length, z = height; front face z = 140.5,
bottom face z = 0. "−y end" = the end where the radar sits.

---------------------------------------------------------------------------------------
## 0. What you need

| Item | Qty | Note |
|---|---|---|
| Printed: `insert.stl`, `plug.stl`, `tray.stl` (keepers A/B/C, 6 switch carriers, caps A/B/C, covers A/B/C) | 1 each | JLC3DP 9000HE |
| Printed first: `coupon.stl` + `tray.stl` | 1 each | fit test before the big order (section 1) |
| XIAO ESP32-S3 Sense + its U.FL FPC antenna | 1 | stock camera removed |
| OV5640 AF camera, 24-pin 0.5 mm FPC (~65 mm) | 1 | |
| HLK-LD2410S | 1 | keep the factory 5-pin header: clip pin 1 (OT2), trim the plastic (step 3.2) |
| G-Switch PB-22E08-LC (8x8 self-locking DPDT) | 1 (buy 3) | |
| 1S protection board, DW01A + FS8205A style, about 30 x 4 x 2 mm (pads B-, B+, P-, P+) | 1 | **cells are UNPROTECTED**: check the board's cut-off current against 3 parallel cells |
| 3x18650 parallel holder 62x76x20 with leads + 3 UNPROTECTED cells | 1 | |
| 24 AWG silicone wire (OD about 2.0 mm), 1 m: battery path (holder, board, switch, splice) | | |
| 28–30 AWG silicone wire, heat-shrink 1.5–2 mm | | signal wires and the two pigtails to the XIAO BAT pads |
| Slow epoxy (gap-filling, 30 min), CA (optional), flat glass plate, 0.2 mm paper strips | | |

---------------------------------------------------------------------------------------
## 1. Order 1: coupon + tray (cheap), and what to test on it

`coupon.stl` is cut directly out of the production insert and plug, so every pocket is
the real geometry.

1. **Radar**: drop the radar (header kept, pin 1 clipped, plastic trimmed) face-down into the 20.6 mm pocket. It must
   lie flat on the 4 ledges; nothing on the front may touch the 0.8 mm window
   (front components are assumed ≤ 0.85 mm tall). Power it and compare detection range
   through the coupon window with open air (the antenna-to-window distance is only 1 mm;
   see REPORT risk 1).
2. **Front face**: it must show only the radar window, the lens opening and the USB-C pocket (no button, seam or icon: the front tact switch was removed).
3. **USB-C**: push the XIAO USB-C shell into the collar from below (it must slide in with
   0.3 mm per side), then plug your real cable into the overmold pocket (13.3 x 7.4, 1.97 deep
   above the receptacle). If the cable's overmold does not reach the receptacle, the pocket
   is too small for that cable (REPORT risk 3).
4. **Camera**: drop the camera head (8.65 x 8.65 base, 1.75 mm lens-holder block, Ø7 x 3.45 mm barrel, Ø3.5 front glass, heatsink
   7.0 x 7.1 x 6.0) into its 9.15 x 9.15 pocket (8.65 + 0.25 clearance per side) with the barrel in the Ø8.0 lens hole (0.5 mm per side;
   hole tolerance ±0.3). The cap pocket above is Ø11 x 1.2 (1.5 mm land beside the hole). Measure the barrel top: it must sit 1.6 mm below
   the face (cap depth 1.2 + 0.4 gap). The ribbon is 6 mm wide.
5. **Caps / covers**: try lens caps A, B, C and USB covers A, B, C (nominal clearance per side
   0.05 / 0.15 / 0.25). Keep the tightest one that still goes in fully by thumb pressure
   without cracking. C always fits; A may not.
6. **Main switch**: measure your switch: body (should be 8.0 x 8.0 x 8.0), body+knob height
   H (datasheet 13.5), pin rows 6.0 apart, pitch 2.5. Pick the carrier `carrier_H<H>` closest
   to your H (10, 11, 12, 13, 13.5, 14). Slide the switch into the carrier along +y (knob
   through the shelf slot), slide the carrier into the coupon's plug section from the −x
   side. Released, the knob tip must be 1.0 mm inside the bottom face; latched 2.5 mm; full
   press 3.5 mm. Press it with a pen tip.
7. Leave all printed parts 7 days (they drift 0.15–0.2 mm), then re-check 5 and 6.

If any of these fails, change the parameter named in REPORT §"If it does not fit",
re-run `python src/build.py && python src/verify.py`, and only then order the insert and
plug.

---------------------------------------------------------------------------------------
## 2. Wiring (text diagram)

```
                  3 x 18650 holder (cells in PARALLEL, 3.0-4.2 V, UNPROTECTED), 24 AWG leads
                 red (+) |                         | black (-)
                         |                         |
              B+ pad     |                         |  B- pad
            +------------+-------------------------+----------------+
            |  1S PROTECTION BOARD (DW01A + FS8205A style, 30x4x2)   |
            |  P+ pad (upper end)                    P- pad          |
            +------------+-------------------------+----------------+
                         | P+                      | P-  (24 AWG straight up the end gap)
            +------------+--------- MAIN SWITCH PB-22E08 (DPDT latching) ---+
            |   pin 2 (common A) ====== jumper ====== pin 5 (common B)      |
            |   pin 3 (NO A)     ====== jumper ====== pin 6 (NO B)          |
            |   (both poles in parallel: 2+5 in, 3+6 out)                   |
            +------------+--------------------------+-----------------------+
                         | switched P+                |
                splice (24 AWG -> 28-30 AWG)    splice (24 AWG -> 28-30 AWG)
                         |                             |
                 XIAO bottom pad BAT+          XIAO bottom pad BAT-
                 (pad nearer the board end     (pad nearer the USB-C)
                  away from USB-C)

 HLK-LD2410S J2 header (back side, wires soldered to the pin TIPS of pins 2-5; pin 1 / OT2 clipped)
   3V3  ---------------------------------  XIAO 3V3   (castellation, 5V/GND/3V3 side)
   GND  ---------------------------------  XIAO GND
   OT1 (UART TX)  -----------------------  XIAO D7  = GPIO44 (UART RX)
   RX  (UART RX)  -----------------------  XIAO D8  = GPIO7  (used as UART TX)
   OT2  (not used)

 (No front button: the only button is the latching PB-22E08 on the bottom plug; D9 and D10 are unused.)

 Camera FPC -> expansion-board 24-pin connector (contacts as for the stock camera)
 Antenna U.FL -> XIAO U.FL (under the expansion board), FPC antenna on the insert guide wall
```

Notes
* The latched state must be the ON state. Before soldering, check with a meter which
  outer pins close to the middle pins when the knob is **latched in** (datasheet diagram:
  commons are pins 2 and 5). If it is 1/4 instead of 3/6, use 1/4 for the jumper and the
  output wire.
* D7/D8 are the radar UART. Firmware: `Serial1.begin(115200, SERIAL_8N1, 44, 7);` (the Sense's SD-card SPI pins D9/D10 are unused).
* Battery path = 24 AWG (OD 2.0, bend radius 3.0 mm assumed, static): holder -> board B+/B-, board P+ -> switch pin 2, switch pin 3 and board P- each continue in 24 AWG to a solder splice above the holder (z 110 / 107.8),
  then 28-30 AWG pigtails (22 / 26 mm) to the XIAO BAT pads: the pads are only 1.2 x 1.9 mm apart and cannot take 2.0 mm wires. The board is 4 mm wide: the B pair (lower end) and the P pair (upper end) each take two 2.0 mm wires side by side (2.1 mm pitch).
* Board position: standing in the -y end gap beside the holder, x 5.65-9.65, y 3.55-5.55, z 33-63, held by 2 dabs of epoxy to the sleeve wall (0.85 mm from the wall, 1.85 mm from the holder end face).
* Every signal wire lands on the **bottom-side** half of a castellated pad (the side that
  faces the backbone). Keep each joint inside the board outline: there is only 0.55 mm
  per side between the XIAO edge and the lip opening.
* Switch OFF = battery fully disconnected; USB still powers the XIAO; no charging while OFF.

Wire lengths in the model: see `out/logs/verify.txt` §6. Add **16–22 mm** service slack to each signal wire (not 30 mm and not below ~14 mm):
the assembly simulation (`SIMULATION.md`) shows 8–12 mm too short with the XIAO held aside (wires taut, 33–66 % strain, 1.1 mm squeeze) and 30 mm
leaves loops that the next part catches. Every wire loop must be moved out of the next part's path before that part goes in (steps 4.4, 4.8, 6.3).

---------------------------------------------------------------------------------------
## 3. Bench preparation (before anything goes into a printed part)

1. Flash the firmware over USB-C. Test camera, radar UART (115200 baud), WiFi.
   BOOT/RESET will not be reachable later.
2. Radar: keep the factory 5-pin header (8.3 mm from the PCB back, plastic spacer 1.35 mm). **Clip pin 1 (OT2, unused) flush at the plastic, then
   trim the plastic spacer with a flush cutter so it starts at pin 2's cell (cut 2.54 mm from the end, x 7.59 on the module).** Untrimmed, the plastic end is 0.05 mm from
   the sleeve opening and pin 1 cuts through keeper A's plate. Check with calipers: trimmed plastic ~10.2 mm long, 2.54 wide, pin tips 8.3 mm below the PCB back.
3. Protection board: solder the 24 AWG leads: holder black to B-, holder red to B+ (lower end, 2.1 mm pitch), and 24 AWG from P+ (upper end) toward switch pin 2, from P- (upper end) up toward the BAT- splice. Check the board's output with a meter before anything else is connected.
4. Main switch: identify the latched-closed pins (see notes above). Solder the two short
   jumpers 2–5 and 3–6 on the pin tips.
5. Solder to the XIAO bottom pads, all wires leaving toward the board's long edge that
   faces away from the antenna connector, lying flat:
   radar 3V3/GND/OT1/RX (≈ 19–27 mm each + slack) and the two 28–30 AWG BAT pigtails (BAT+ 22 mm, BAT− 26 mm + 150 mm free end each, spliced to the 24 AWG battery wires at step 6.4).
6. Solder the other ends to the radar header pin tips (pins 2–5, lower 2 mm of each pin, wire against the +y face of the pin; pin order from the −x end after the clipped pin 1: RX, OT1, GND, 3V3) .
7. Plug the camera FPC into the Sense connector (latch closed) and the antenna U.FL.
8. Power the whole harness from a bench supply on BAT+/BAT− (3.7 V) and test again.

---------------------------------------------------------------------------------------
## 4. Top module — assembled FACE DOWN on a flat glass plate

Gravity holds every part in its pocket; nothing is pressed or flexed. Each keeper is laid
in from the inside and later glued only by its ears in the insert seam.

| Step | Part | Motion (device frame) | Proven by verify §3 |
|---|---|---|---|
| 4.1 | insert face-down on glass, rim side up | — | — |
| 4.2 | radar, face-down into its pocket, header edge toward the USB-C | +z into pocket | radar fits pocket (§2, §5) |
| 4.3 | (removed: there is no front tact switch) | | |
| 4.4 | **keeper A**: first lay the 4 radar wires straight down their lane (out of the pin tips, no loops under the plate) and hold them there; the wire slot (open to +y) slides around them (keeper A no longer has a tact bridge or cup); 3 posts land on the radar back, cup on the tact switch. The gap between the plate top (z 135.7) and the radar back components (z 136.4) is only 0.7 mm: a wire left under the plate is squeezed (simulated 0.40 mm) | +z | keeper_a install path: no hits; wire squeeze: `SIMULATION.md` |
| 4.5 | camera head with heatsink, barrel into the Ø8.0 lens hole, FPC trailing toward +y. **Keep the XIAO stack (wires soldered, FPC plugged in) at least 12.5 mm above the seat and beside the work (simulated: 14 mm) until keeper B is in, and do not pre-dress the FPC loop**: with the XIAO 11 mm up or less, keeper B's floor drags the ribbon through a 0.5–0.7 mm radius (`SIMULATION.md` §3b; keeper B's floor underside, not the heatsink, sets the 12.1 mm minimum). Heatsink: 7.0 × 7.1 × 6.0 mm on a 0.1 mm pad, centred on the base | +z | camera install path in `SIMULATION.md` |
| 4.6 | **keeper B** onto the head base | +z | keeper_b install path: no hits |
| 4.7 | XIAO stack, USB-C first into the closed collar; dress the FPC: out of the connector toward the USB end, kink outward (r 2) just below the SD socket, up past the socket, 180° fold under keeper B, down, U-loop (bottom ≈ z 112), up and 90° into the head (see `out/img/section_top_x14.7.png`). Lay the signal wires into their lanes (straight toward the XIAO edge). Lower the XIAO slowly and guide the ribbon with tweezers during the last 10 mm: its first bend below the connector tightens to about 1.6 mm (limit 2.0 mm) in the simulation and relaxes to 1.96 mm when seated. | +z | XIAO install path: no hits |
| 4.8 | **keeper C** (first move every radar-wire loop away from the U-foot and its arms: in one simulation run keeper C caught a radar wire, 0.18 mm squeeze, 51 % strain): U-foot under the XIAO bottom end; the battery leads pass its −y-open notch, the coax its +y-open notch | +z | keeper_c install path: no hits (wires already in place) |
| 4.9 | antenna FPC on the +y face of the FPC guide wall (its own adhesive backing), coax along the model route | — | coax clear of all parts |
| 4.10 | Test everything again (USB-C cable into the collar, camera image, radar; press the bottom switch). | | |

---------------------------------------------------------------------------------------
## 5. Plug sub-assembly

1. Switch (with jumpers) slides into the chosen carrier along +y; knob through the shelf slot.
2. Carrier slides into the plug through the opening in the plug's −x side face, knob
   travelling in the hidden channel, until it stops at the +x end. The pins and wires come
   up through the roof slot. (The sleeve wall later closes this opening: carrier play 0.35 mm.)
3. Fit the protection board in the −y end gap (x 5.65–9.65, z 33–63; two dabs of epoxy to the sleeve wall are added at step 6.2). Holder black → B−, holder red → B+ (24 AWG, straight up the end gap),
   board P+ (upper end) → down the lane at x 14.7 → switch pin 2, switch pin 3 and board P− → 24 AWG up the end gap to the splices. The switch wires cross the plug's −y wall through its 8 × 4 mm passage
   (two 2.0 mm wires at x 14.7 and 17.2, z 19.0 ± 1.0).
4. Holder into the cradle (3 x-wall segments, 2 y-walls): **glue point G3**: a dot of epoxy
   on each of the 6 support pads under the holder.
5. Cells in. With a meter on the two harness ends: switch latched = 3.7–4.2 V, released = open.

---------------------------------------------------------------------------------------
## 6. Joining (glue only at the three listed points)

1. **Glue point G1 — insert seam.** With the top module still face-down on the glass: put a
   small bead of slow epoxy on the top of each faceplate pad (5 pads + the radar skirt
   bottom) and on the rim under each keeper ear (6 ears). The ears float 0.2 mm above the rim
   (nominal): the epoxy fills that gap and fixes the keepers.
2. Thread the two 28–30 AWG BAT pigtails up through the sleeve from its front opening and out of its open bottom end (the 24 AWG wires from the switch and the board are already in the plug module).
3. Before the sleeve comes down, tuck every signal-wire loop into the module's footprint (toward the holder side, away from the rim): in an earlier simulation a loose signal wire
   was caught at the sleeve rim (0.85 mm squeeze, 33 % strain). Lower the sleeve, front face first, over the top module until the sleeve's front face
   sits on the glass. The pads now float 0.25 mm under the lip (epoxy-filled). Push four
   0.2 mm paper strips into the visible 0.25 mm seam (one per side) to centre the faceplate.
   Put ~300 g on the sleeve. Cure.
   * If the sleeve does **not** reach the glass (pads too tall by up to 0.15 mm in the worst
     tolerance case), sand the pads before gluing: see REPORT.
4. Flip the device. Make the two splices of the 28–30 AWG pigtails to the 24 AWG wires (switch pin 3 → BAT+, board P− → BAT−) at z 110 / 107.8 above the holder, solder + 3 mm heat-shrink,
   splices 2.5 mm apart.
5. Test before closing (section 7).
6. Push the slack loops up into the free space above the holder (z 97–112, 24 x 72 mm).
7. **Glue point G2 — plug seam.** Epoxy on the plug rim (0–6 mm band), insert the plug, stand
   the device on the glass on its bottom face so the plug face is flush with the sleeve.
   Cure.

---------------------------------------------------------------------------------------
## 7. Test before gluing the plug (step 6.5)

| Test | Pass |
|---|---|
| Switch latched → XIAO boots on battery | LED / serial |
| Switch released → current from battery = 0 (meter in series) | 0 mA |
| USB-C cable fully seats in the face pocket; data + power OK | enumerates |
| Camera image through the lens opening, no vignetting corners at your lens FOV | image |
| Radar presence at 1, 3, 5 m through the window | compare with coupon test |
| Bottom switch latches ON/OFF (OFF: the XIAO runs from USB only) | multimeter |
| Protection board: P+/P- 3.7-4.2 V, no short between B+/P-; cut-off verified with a bench supply | multimeter |
| WiFi RSSI with sleeve on vs. off | < 6 dB worse |
| Shake test: nothing rattles (if the radar or head rattles, see REPORT §rattle) | quiet |

---------------------------------------------------------------------------------------
## 8. Glue summary

| ID | Where | Why |
|---|---|---|
| G1 | insert seam: pads ↔ lip top, keeper ears ↔ faceplate rim | holds the top module (USB-C pull-out force) and fixes the three keepers |
| G2 | plug seam: plug rim ↔ sleeve cavity | permanent bottom closure |
| G3 | holder base ↔ 6 plug supports | holds the 76 mm holder against shocks; plug sub-assembly only |
| (adhesive tape) | antenna FPC's own backing on the guide wall | supplied with the antenna |

No other glue is required.
