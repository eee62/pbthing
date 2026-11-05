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
| HLK-LD2410S | 1 | factory J2 header must be removed |
| G-Switch PB-22E08-LC (8x8 self-locking DPDT) | 1 (buy 3) | |
| 6x6x4.3 mm THT tact switch | 1 | |
| 3x18650 parallel holder 76x61x20 with leads + 3 protected cells | 1 | |
| 28–30 AWG silicone wire, heat-shrink 1.5–2 mm | | |
| Slow epoxy (gap-filling, 30 min), CA (optional), flat glass plate, 0.2 mm paper strips | | |

---------------------------------------------------------------------------------------
## 1. Order 1: coupon + tray (cheap), and what to test on it

`coupon.stl` is cut directly out of the production insert and plug, so every pocket is
the real geometry.

1. **Radar**: drop the radar (header removed) face-down into the 20.6 mm pocket. It must
   lie flat on the 4 ledges; nothing on the front may touch the 0.8 mm window
   (front components are assumed ≤ 0.85 mm tall). Power it and compare detection range
   through the coupon window with open air (the antenna-to-window distance is only 1 mm;
   see REPORT risk 1).
2. **Button**: put the tact switch in its pocket, press the flush pad: it must click with
   ~3 N and spring back. Engraved icon: 0.8 mm lines, 0.8 mm deep.
3. **USB-C**: push the XIAO USB-C shell into the collar from below (it must slide in with
   0.3 mm per side), then plug your real cable into the overmold pocket (12.9 x 7.0, 1.97 deep
   above the receptacle). If the cable's overmold does not reach the receptacle, the pocket
   is too small for that cable (REPORT risk 3).
4. **Camera**: drop the camera head into its 9.0 x 9.0 pocket with the lens barrel in the
   Ø8.4 opening (cap pocket above it is Ø11 x 1.2). Measure the barrel top: it must sit 1.6 mm below the face (cap depth 1.2 +
   0.4 gap).
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
                      3 x 18650 holder (cells in PARALLEL, 3.0-4.2 V)
                 red (+) |                         | black (-)
                         |                         |
            +------------+--------- MAIN SWITCH PB-22E08 (DPDT latching) ---+
            |   pin 2 (common A) ====== jumper ====== pin 5 (common B)      |
            |   pin 3 (NO A)     ====== jumper ====== pin 6 (NO B)          |
            |   (both poles in parallel: 2+5 in, 3+6 out)                   |
            +------------+--------------------------------------------------+
                         | switched B+                 |
                         |                             |
                 XIAO bottom pad BAT+          XIAO bottom pad BAT-
                 (pad nearer the board end     (pad nearer the USB-C)
                  away from USB-C)

 HLK-LD2410S J2 (back side, wires soldered straight into the holes, header removed)
   3V3  ---------------------------------  XIAO 3V3   (castellation, 5V/GND/3V3 side)
   GND  ---------------------------------  XIAO GND
   OT1 (UART TX)  -----------------------  XIAO D7  = GPIO44 (UART RX)
   RX  (UART RX)  -----------------------  XIAO D8  = GPIO7  (used as UART TX)
   OT2  (not used)

 Front tact switch (two diagonal legs)
   leg A ---------------------------------  XIAO D10 = GPIO9  (INPUT_PULLUP)
   leg B ---------------------------------  XIAO D9  = GPIO8  (OUTPUT LOW = local ground)

 Camera FPC -> expansion-board 24-pin connector (contacts as for the stock camera)
 Antenna U.FL -> XIAO U.FL (under the expansion board), FPC antenna on the insert guide wall
```

Notes
* The latched state must be the ON state. Before soldering, check with a meter which
  outer pins close to the middle pins when the knob is **latched in** (datasheet diagram:
  commons are pins 2 and 5). If it is 1/4 instead of 3/6, use 1/4 for the jumper and the
  output wire.
* D8/D9/D10 are the Sense's SD-card SPI pins; with no card fitted they are free. Firmware:
  `Serial1.begin(115200, SERIAL_8N1, 44, 7); pinMode(8, OUTPUT); digitalWrite(8, LOW); pinMode(9, INPUT_PULLUP);`
* Every signal wire lands on the **bottom-side** half of a castellated pad (the side that
  faces the backbone). Keep each joint inside the board outline: there is only 0.55 mm
  per side between the XIAO edge and the lip opening.
* Switch OFF = battery fully disconnected; USB still powers the XIAO; no charging while OFF.

Wire lengths in the model (add 30 mm service slack to each): see `out/logs/verify.txt` §6.

---------------------------------------------------------------------------------------
## 3. Bench preparation (before anything goes into a printed part)

1. Flash the firmware over USB-C. Test camera, radar UART (115200 baud), button, WiFi.
   BOOT/RESET will not be reachable later.
2. Radar: cut the plastic spacer of the factory 5-pin header and desolder the pins one by
   one. Clean the holes.
3. Tact switch: cut the 4 legs to 3.5 mm.
4. Main switch: identify the latched-closed pins (see notes above). Solder the two short
   jumpers 2–5 and 3–6 on the pin tips.
5. Solder to the XIAO bottom pads, all wires leaving toward the board's long edge that
   faces away from the antenna connector, lying flat:
   radar 3V3/GND/OT1/RX (≈ 30 mm each + slack), button D10/D9 (≈ 20 mm + slack),
   BAT+ and BAT− (≈ 150 mm each; they will be spliced to the plug harness at step 7.2).
6. Solder the other ends to the radar J2 holes and the tact-switch legs.
7. Plug the camera FPC into the Sense connector (latch closed) and the antenna U.FL.
8. Power the whole harness from a bench supply on BAT+/BAT− (3.7 V) and test again.

---------------------------------------------------------------------------------------
## 4. Top module — assembled FACE DOWN on a flat glass plate

Gravity holds every part in its pocket; nothing is pressed or flexed. Each keeper is laid
in from the inside and later glued only by its ears in the insert seam.

| Step | Part | Motion (device frame) | Proven by verify §3 |
|---|---|---|---|
| 4.1 | insert face-down on glass, rim side up | — | — |
| 4.2 | radar, face-down into its pocket, J2 edge toward the button | +z into pocket | radar fits pocket (§2, §5) |
| 4.3 | tact switch, actuator down onto the button nub | +z | tact fits pocket |
| 4.4 | **keeper A**: wire slot (open to +y) slides around the 4 radar wires; 3 posts land on the radar back, cup on the tact switch | +z | keeper_a install path: no hits |
| 4.5 | camera head, lens into the Ø8.4 opening, FPC leaving toward +y | +z | |
| 4.6 | **keeper B** onto the head base | +z | keeper_b install path: no hits |
| 4.7 | XIAO stack, USB-C first into the closed collar; dress the FPC: out of the connector toward the USB end, kink outward (r 2) just below the SD socket, up past the socket, 180° fold under keeper B, down, U-loop (bottom ≈ z 112), up and 90° into the head (see `out/img/section_top_x14.7.png`). Lay the signal wires into their lanes (straight toward the XIAO edge). | +z | XIAO install path: no hits |
| 4.8 | **keeper C**: U-foot under the XIAO bottom end; the battery leads pass its −y-open notch, the coax its +y-open notch | +z | keeper_c install path: no hits (wires already in place) |
| 4.9 | antenna FPC on the +y face of the FPC guide wall (its own adhesive backing), coax along the model route | — | coax clear of all parts |
| 4.10 | Test everything again (USB-C cable into the collar, camera image, radar, button). | | |

---------------------------------------------------------------------------------------
## 5. Plug sub-assembly

1. Switch (with jumpers) slides into the chosen carrier along +y; knob through the shelf slot.
2. Carrier slides into the plug through the opening in the plug's −x side face, knob
   travelling in the hidden channel, until it stops at the +x end. The pins and wires come
   up through the roof slot. (The sleeve wall later closes this opening: carrier play 0.35 mm.)
3. Holder red lead → switch pin 2 (already planned length in the model). Route the
   switch-out wire and the holder black lead out through the −y wall passage and up the −y
   end gap.
4. Holder into the cradle (3 x-wall segments, 2 y-walls): **glue point G3**: a dot of epoxy
   on each of the 6 support pads under the holder.
5. Cells in. With a meter on the two harness ends: switch latched = 3.7–4.2 V, released = open.

---------------------------------------------------------------------------------------
## 6. Joining (glue only at the three listed points)

1. **Glue point G1 — insert seam.** With the top module still face-down on the glass: put a
   small bead of slow epoxy on the top of each faceplate pad (5 pads + the radar skirt
   bottom) and on the rim under each keeper ear (6 ears). The ears float 0.2 mm above the rim
   (nominal): the epoxy fills that gap and fixes the keepers.
2. Thread the BAT+ and BAT− leads up through the sleeve from its front opening and out of
   its open bottom end.
3. Lower the sleeve, front face first, over the top module until the sleeve's front face
   sits on the glass. The pads now float 0.25 mm under the lip (epoxy-filled). Push four
   0.2 mm paper strips into the visible 0.25 mm seam (one per side) to centre the faceplate.
   Put ~300 g on the sleeve. Cure.
   * If the sleeve does **not** reach the glass (pads too tall by up to 0.15 mm in the worst
     tolerance case), sand the pads before gluing: see REPORT.
4. Flip the device. Splice the XIAO leads to the plug harness (switch-out → BAT+, holder
   black → BAT−) with solder + heat-shrink; stagger the two splices by 15 mm.
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
| Front button toggles D10 | log |
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
