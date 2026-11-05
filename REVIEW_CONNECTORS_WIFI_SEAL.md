# Review: connectors, Wi-Fi, permanent build

Section map: §1 connectors (your questions 1 and 2) · §2 Wi-Fi (3) · §3 permanent build (4) · §4 what changed (5).

Tags: **[model]** computed by `src/verify.py` from the CAD (exact booleans/distances) · **[src]** from a document I
read (links at the end) · **[judgement]** my engineering call, not a measured fact · **[not found]** I looked and
there is no published number. Nothing here has been built or measured on hardware.

## 0. Bottom line

* **No board in this project has a JST-PH connector** [model/src]. XIAO: solder pads. Radar: 5 plated holes at
  2.54 mm. Expansion board: FPC socket + U.FL. So "PH on every board connection" can only mean a PH *pigtail*
  soldered to the pads. I added exactly one PH pair, at the one place a disconnect is useful: the battery line between
  the plug module and the top module.
* **I cannot see your cell/holder connector.** §1.1 tells you how to identify it in a minute and the cheapest fix for each case.
* **Wi-Fi: the antenna was in a bad place** (1.8 mm from the camera ribbon, 3.9 mm from the camera head). Moved to the +y
  end wall: 13.3 / 15.4 mm. Cell tops are still only 11.1 mm below it, so the range test in §2.4 decides.
* **Permanent build: seams can be glued for good, but "sealed for good" is the wrong goal.** The biggest threat is
  heat, not water: the XIAO with a camera was reported at 80–95 °C while the resin's HDT/Tg is 60 / 61–68 °C (§3.2).
  With the PH pair the plug module can be separated without soldering, so a cut-the-seam repair is possible (§3.5).

## 1. Connectors

### 1.0 Premises that do not match the files

| You said | What the files show | What I did |
|---|---|---|
| PH connectors "on the boards" | none (list above) | PH only on the battery break; radar/button stay soldered |
| "plug zones" and "finger columns" | neither exists in my design or in `01_PROJECT_FACTS.md` (probably from your other design; I never had it) | built one plug zone (P1); the only vertical open shafts are the two 5.6 mm end gaps, kept clear and checked (§1.4). They fit tweezers, not a fingertip |
| "my cell", "LiPo pouches swell", "cell foil" | spec: 3 × 18650 in a leaded holder (rigid steel cans) | both cases covered (§2.3, §3.4) |
| 22 AWG RCY wire | PH contact SPH-002T-P0.5S takes AWG 24–30, insulation 0.9–1.5 mm [src] | PH pigtails use 24–28 AWG (model 1.1 mm OD); the 22 AWG RCY wire does not crimp into PH |

### 1.1 Which connector does your cell/holder have? (question 1)

I can't check it from here. Measure the contact pitch with calipers:

| What you see | It is | Cheapest fix |
|---|---|---|
| bare tinned leads | no connector | none needed: the default design solders them to the switch and to a PH tail |
| 2 pins, **2.0 mm** pitch, housing ≈ 5.8 × 4.5 mm | JST-PH (PHR-2) [src] | nothing |
| 2 pins, **2.5 mm** pitch, red | JST RCY (SYR/SYP): *not* compatible with PH [src] | cut it off and solder the two wires to the PH header tails (2 joints per lead). Cheapest because it needs no extra part |
| anything else (XH, SM, etc.) | not PH | same: cut it off and solder |

No price is quoted: I did not find a Shopee price I could verify. Tell me the pitch and I'll adapt the lead routing.

### 1.2 What the PH pair is (real size) [src: JST PH catalog]

| | Value |
|---|---|
| pitch | 2.0 mm |
| header B2B-PH-K-S, 2 circuits | 5.9 wide × 4.5 deep × 6.0 high; tails 3.4 below the seating plane |
| mated height | 8.0 mm above the seating plane ("8.0 mm in height after mounting") |
| in-line mated pair, tails included | **5.9 × 4.5 × 11.4 mm** (used for the zone) |
| lock | none listed in the catalog: friction only |

### 1.3 Plug zone P1 (default build) [model]

* Location: −y end column (the 5.6 mm gap between the cavity wall and the holder), x centre 19.0, z 27.0–38.4, axis vertical,
  tails down. Gaps: 0.55 mm to the cavity wall, 0.55 mm to the holder face, 0.3 mm to each rib.
* Printed cage on the plug: two ribs (1.2 thick), a stop bar 0.4 below the header body and a bridge 0.5 above the housing.
  Open toward +y: slide the mated pair in along −y at the bench, before the holder is fitted.
* Keep-out check: the zone (real size + 0.2 mm margin, plus a wire corridor at the tails) overlaps no printed part, holder or sleeve.
* Wires end exactly on the tail and housing faces; min bend radius stays 2.0 mm.
* The pair is **mated outside the sleeve** (section ASSEMBLY 6.4) and then pushed in: it needs about 87 mm of extra XIAO-side
  pigtail (PH zone to the sleeve mouth + 60 mm hand room). Pigtails ≈ 210 mm.
* The PH has no lock: heat-shrink the mated pair (or a drop of flexible adhesive).

### 1.4 "Finger columns"

The only vertical shafts are the end gaps: 5.6 mm × 24.4 mm cross-section. Checked: no printed part inside either gap for
z 40.5–105.5 (the cage tops out at z 39.9, the antenna wall starts at z 106). Reach is for tweezers; a fingertip needs ≈ 14 mm,
which this sleeve cannot offer.

### 1.5 Red RCY splice (question 2)

Modelled as 23.3 (length, [user]) × 4.0 (thickness, [user]) × 7.0 (width, **[GUESS]**: JST's RCY drawing was blocked and
Farnell returned 503). Option `PB_RCY=1`.

* Where it fits: only in-line on the straight vertical run above the PH pair (z 50.0–73.3, x 19.0). Elsewhere (flat over the
  holder, along the end gap) it either does not fit or forces the wires to hairpin back past it **[judgement: not modelled]**.
* It is **not needed** in the default build. It would only be needed if your holder ships with an RCY plug and you refuse to cut it off.
* Retention: none printed (the run is free). Heat-shrink + a dab of flexible adhesive to the cavity wall is the minimum.

### 1.6 Length cost (question 5: "report the new length") [model]

The sleeve length (140.5) is fixed, so "length" = wire length per conductor and column length used.

| Conductor path | Direct-solder baseline (v1) | With PH (default) | With PH + RCY |
|---|---:|---:|---:|
| B+ switch → XIAO BAT+ | 168.5 mm | 173.0 mm | 181.0 mm |
| B− holder → XIAO BAT− | 138.1 mm | 142.0 mm | 150.0 mm |
| column length used (z) | 0 | 11.4 mm (z 27.0–38.4) | 11.4 + 23.3 mm (z 50.0–73.3) |
| vertical run left above the PH | – | 71.6 mm | RCY needs 31.3 (23.3 + 2 × 4 allowance): margin +40.3 mm |

Each figure = routed wire + connector body + allowance (3 mm per PH joint, 4 mm per RCY side, [GUESS]). The PH adds only
+4.5 / +3.9 mm because the new route is shorter than the old one (cage next to the passage). **The RCY splice costs +8.0 mm of
conductor** (its 23.3 mm body replaces wire on a straight run; only the 2 × 4 mm crimp allowance is extra), but it **occupies
23.3 mm (31.3 with allowances) of the 71.6 mm straight run**, leaving 40.3 mm. Free box above the holder for slack:
24.4 × 72.2 × 15.2 mm (unchanged).

## 2. Wi-Fi review

### 2.1 What Seeed and the antenna maker actually say

| Source | Statement |
|---|---|
| Seeed wiki | install the included antenna on the "WiFi/BT Antenna Connector"; the included antenna "cannot support high-intensity network work"; a U.FL external antenna can extend range "over 100 meters". **No clearance numbers** |
| A-02 antenna reseller guide | "keep the radiating FPC section away from metal and large ground planes"; hidden flat against conductive hardware it can perform worse than a lower-gain antenna with clearance; route coax without sharp folds. **No numbers; no dimensions** |
| Core Electronics forum | mount on the inside of a *plastic* enclosure; avoid creasing, avoid "mounting near large metal items" |
| ESP32 forum | "the most important bit is to not have any metal things in the neighbourhood of an antenna" |
| Espressif hardware design guidelines | **[not found]**: I could not read the keep-out section |

So there is **no official clearance number**. I use λ/10 = 12.2 mm at 2.45 GHz as a **[judgement]** yardstick (λ = 122.4 mm).
The A-02's real size is also **[not found]**; 30 × 8 × 0.3 mm remains a guess (parameter `ANT_*`).

### 2.2 Layout: before and after [model]

| Antenna to … | Old (on FPC guide wall) | New (+y end wall) |
|---|---:|---:|
| camera FPC ribbon (copper) | **1.8 mm** | 13.3 mm |
| camera head (metal VCM/shield) | **3.9 mm** | 15.4 mm |
| XIAO + expansion board | 13.1 mm | 24.6 mm |
| XIAO RF shield can | 17.8 mm | 29.3 mm |
| radar PCB | 33.6 mm | 45.1 mm |
| cell tops (steel cans) | 9.5 mm | 11.1 mm |
| main switch | 90.1 mm | 94.5 mm |

The antenna sits at z 108–138 on a 1.2 mm resin wall (new insert feature); the coax is 48.3 mm. The cell tops are the one thing
still below λ/10 and cannot be raised further (antenna top z 138.0, faceplate rim z 138.5).

### 2.3 Item by item

| Item | Finding |
|---|---|
| Cells | 3 steel cans below the antenna at 11.1 mm, spanning the whole holder footprint. Biggest remaining detuning/shadowing risk. Cannot be fixed inside this sleeve; the test decides |
| Cell foil | applies only if you swap to pouch cells (aluminium foil): same 11.1 mm distance, larger flat metal area, so worse. Not modelled |
| USB-C shell | 29 mm away (y 38–41 vs 70); no issue [model] |
| Main switch | 94.5 mm away; no issue |
| Screws | the design has **none**. Metal in the sleeve: XIAO shield + USB shell, camera head, radar PCB, FPC copper, switch (spring/brass pins), cell cans |
| Resin | 9000HE dielectric constant 3.2–4.0 at 1 MHz [src]; **no 2.4 GHz value published**. The antenna sticks to one 1.2 mm wall (εr ≈ 3–4 loads it slightly, may shift tuning a little). Do not paint with metallic paint |

### 2.4 Range test (bare vs enclosed)

Setup (same for both runs): same 2.4 GHz access point and channel, line of sight, 3.00 m, device 1 m above the floor on a
non-metal stand, USB-C up, front face toward the AP, battery power (no USB cable), same Tx power, people out of the room.

1. Firmware: connect as a station, print `WiFi.RSSI()` twice per second for 60 s (120 samples).
2. Take the median. Repeat with the device rotated 90°, 180°, 270° about its long axis (4 medians).
3. **Bare**: XIAO + antenna as supplied, lying on cardboard, antenna taped flat. **Enclosed**: fully assembled, plug fitted, nothing glued.
4. Third run, enclosed, with the camera streaming at 1 fps (catches camera/ribbon noise).

Δ = median(bare) − median(enclosed), using the *worst* of the four orientations for the enclosed case.

| Result | Meaning |
|---|---|
| **PASS** | Δ ≤ 6 dB **and** enclosed median ≥ −67 dBm at 3 m |
| **MARGINAL** | 6 < Δ ≤ 10 dB, or enclosed −67 to −70 dBm: usable near the AP only |
| **FAIL** | Δ > 10 dB, or enclosed < −70 dBm, or any orientation < −75 dBm |

Why these numbers: 6 dB is a halving of free-space range [physics]; −67 dBm and −70 dBm are the usual "reliable" and
"minimum" Wi-Fi levels from MetaGeek [src, heuristics, not a standard]. RSSI noise is ±2–3 dB, hence 120 samples.
If it fails: raising the antenna further is impossible inside this sleeve; the remaining options are a different antenna (a stick/rod type on the U.FL)
or placing it outside the sleeve. Test before gluing anything.

## 3. Permanent-build review

**Can it be sealed for good?** Seams: yes, with epoxy. Hermetic or waterproof: no, and it should not be. The device
has intentional openings: USB-C pocket + friction cover, lens opening + friction cap, button ring seam, the dimple hole in the
plug, 0.25 mm seams. Gas from a failing cell needs those paths (§3.4).

### 3.1 Glue and epoxy vs. the resin

* JLC's 9000HE page says nothing about adhesives or chemicals [src]. **No vendor guidance exists for this resin.**
* Formlabs (other resins) recommends 5–30 min two-part epoxy for the largest/strongest joints (longest working time),
  cyanoacrylate for small/medium parts (quick, low impact strength), and its bonding/finishing tutorial starts with sanding (~150 grit dry, ~320 wet) [src]; a forum user advises scuffing before gluing.
* Our joints G1/G2/G3 are 0.25–0.5 mm gaps: use **slow epoxy** (gap-filling, time to position). CA only for tiny spots.
* Sand the bonding faces and wash with isopropyl alcohol; let the parts settle first (your facts file: parts drift 0.15–0.2 mm over 3–7 days).
* The PH/RCY housings are nylon (PA66) [src]; I did not find a source on bonding nylon: **test before trusting a bond to it**.
* Test on your actual parts: glue two spare lens caps (you get three variants of each) with your epoxy, wait 24 h, then try to break the joint by hand.
  The coupon and tray make this free.

### 3.2 Heat and the 60 °C resin

| Fact | Value |
|---|---|
| 9000HE heat deflection (ASTM D648, 0.45 MPa) | 60 °C [src] |
| glass transition (DMA) | 61–68 °C [src] |
| vendor warning | "not suitable for exposure to UV light, high temperatures, or strong sunlight" [src] |
| thermal expansion | 90–103 × 10⁻⁶ /°C |
| XIAO ESP32-S3 Sense with camera, Wi-Fi AP, no enclosure | board alone ~55–60 °C; camera attached 67–75 °C; **streaming: chip > 80 °C, board surface > 95 °C** (one user; another unit stayed < 50 °C; 1 × 1 × 0.5 cm heatsink at 1 fps: 60–62 °C) [src, anecdotal] |
| Panasonic NCR18650B (example cell) | charge 0–45 °C, discharge −20 to 60 °C, storage −20 to 50 °C [src; check *your* cell] |

What the model shows [model]:

* The XIAO PCB edge **rests on the resin collar (0.05 mm)** at the USB-C end; the RF shield can is 2.42 mm from keeper C.
  If the board reaches the reported 80–95 °C, the nearest resin is above its Tg.
* Self-heating of the whole sleeve is small: ~345 cm² of surface is far more than a ~1 W load needs **[judgement, from
  convection of ~10 W/m²K]**. The problem is the local hot spot on the board and the environment (sun, car).
* Expansion does not jam the seams: it would take a 68 K temperature *difference* between faceplate and sleeve to close the
  0.5 mm y-gap (71.7 mm × 103 × 10⁻⁶/K).

Recommended **[judgement]**: the camera runs only on demand, ≤ 1 fps; read the chip temperature (`temperatureRead()`) and
stop the camera at 55 °C. Thermal test before gluing, 60 min at your real duty cycle at 25 °C ambient, thermocouple on the
USB end of the XIAO PCB: **PASS ≤ 50 °C, MARGINAL 50–60 °C, FAIL > 60 °C**. Do not leave the device in a car or in sunlight.

### 3.3 Strain relief

| Point | What holds it now | Risk | Fix (cheap) |
|---|---|---|---|
| XIAO BAT± pads (0.76 × 1.78 mm each) | wires lie in the 2.6 mm bay | pad lifts if the pigtail is tugged while mating outside the sleeve | tack the wire to the board 3 mm from the pad with flexible adhesive; mate only with the sleeve held still |
| Radar J2 holes | through-hole joints; keeper A slot holds the wires | low | a dot of adhesive where the 4 wires leave the board |
| Tact switch legs | cut to 3.5 mm, keeper A cup | low | none |
| Main switch pins | wires wrapped on the 3.5 mm pins | the 8 × 8 body takes 2.5 N presses; wires are not loaded | adhesive on the carrier roof slot after the continuity test |
| PH pair | friction fit + cage ±0.5 mm | no lock | heat-shrink the mated pair |
| Holder leads | exit the −y face | lead pulled when the holder is pushed in | adhesive dot at the lead exit |
| Camera FPC | 4 bends at r = 2.0 mm, 0.25 mm clearances | connector latch, crease | latch the connector, never re-fold |

### 3.4 Cell swelling, venting, and what a sealed case does [model unless noted]

* The spec is 3 × 18650 in a holder: rigid steel cans, **not** pouch-type swelling.
* If you use pouch cells: a patent cites up to 8–10 % swelling over 500 cycles for some pouch types, and a paper treats 10 % as the practical ceiling [src]; a rigid
  housing turns that into force on the walls [src: Frontiers]. Free room around the holder: **2.2 mm per side in x**, 5.6 mm per
  end in y, 15.2 mm above. 10 % of a 20 mm thick pack is 2.0 mm: it just fits. Use a compressible pad, not glue.
* Gas from a venting cell: about 2 L/Ah (UCL/Sandia; NIOSH measured 2–9.2 L/Ah) [src]. A 2.5 Ah cell is ~5 L; the free
  internal volume is **130 cm³ = 0.13 L**: ~39 times too small, ~116 times for all three cells. **No sealed printed case
  can contain that.** Do not add gaskets over the USB pocket or lens opening; the cells' protection boards are the only protection.
* Charging: your 50 mA charge rate on 3 × 2.5 Ah (7.5 Ah) is ~150 h [arithmetic]. Not a safety problem, but plan for it.

### 3.5 What fails after sealing [judgement]

| Dies | Symptom | Access path | What you destroy | With PH pair |
|---|---|---|---|---|
| cell / holder | no run time | cut the plug seam G2 (0.25 mm gap, 6 mm band) | epoxy only; plug re-glueable | pull the plug module out (≈ 87 mm slack), unmate PH, swap, no soldering |
| camera | no image | cut G1, lift the top module out of the front | epoxy spots (11); the camera is on the module | unmate PH at the plug module first |
| XIAO | dead | same as camera; the XIAO is held by keeper C | keeper C may need re-gluing | same |
| radar / button | no presence / button | same | keeper A | same |
| main switch | no power | plug seam G2 | carrier slides out toward −x | – |
| PH connector | intermittent power | plug seam G2 | – | reseat it |

Without the PH pair the same repairs need desoldering the battery splice inside a 24 mm cavity.

### 3.6 Recommended sealing strategy

1. Do the range test (§2.4) and the heat test (§3.2) **dry**, before any glue.
2. Glue G1/G2 with **spot** epoxy dabs (not a full bead) so a blade can cut them.
3. Keep every opening; no gaskets.
4. If the heat test fails, do not seal: reduce camera duty first.

## 4. What changed in the design (and was re-verified)

* Antenna moved to a new +y end wall of the insert (parameters `ANT_*`, `ANTW_Y0`); old FPC-wall position still exists as the guide wall.
* PH plug zone P1 with printed cage on the plug; passage in the cradle widened; holder lead positions moved ([GUESS] anyway).
* Optional RCY splice (`PB_RCY=1`), no printed change.
* `src/verify.py` gains section 10 (zone keep-out, end-column clearance, length cost, Wi-Fi distances, heat proximity, free volume).
* Radar window note corrected: the 9000HE permittivity range is 3.2–4.0 (1 MHz); at 4.0 the 0.8 mm window is 0.02 mm thicker than λ/8.

Results: `out/logs/verify.txt` (default) and `out/logs/verify_rcy.txt` (RCY variant).

## Sources

* JST PH catalog pages 1–2 (mirror): <https://datasheet.chipsmall.com/PHR-2/341438.pdf>
* RCY is a 2.5 mm family: <https://uk.rs-online.com/web/p/pcb-sockets/1724969>, <https://keszoox.com/blogs/%E6%96%B0%E9%97%BB/the-12-most-commonly-used-jst-connectors>
* Seeed XIAO ESP32S3 Wi-Fi: <https://wiki.seeedstudio.com/xiao_esp32s3_wifi_usage/>
* A-02 antenna guide: <https://www.unmannedtechshop.co.uk/blogs/knowledge-base/xiao-fpc-antenna-a01-vs-a02-esp32-c3-c5-s3>
* Mounting thread: <https://forum.core-electronics.com.au/t/how-should-the-seeed-xiao-esp32-s3-antenna-be-mounted/19308>; metal near antenna: <https://esp32.com/viewtopic.php?p=136930>
* RSSI levels: <https://metageek.com/training/resources/understanding-rssi/>
* 9000HE: <https://jlc3dp.com/help/article/9000he-resin>
* Bonding SLA parts (Formlabs): <https://formlabs.com/blog/how-to-create-models-larger-than-your-3d-printers-build-volume/>
* XIAO overheating thread: <https://forum.seeedstudio.com/t/my-xiao-esp32s3-with-camera-attached-is-overheating/276523>
* NCR18650B datasheet copy: <https://files.batteryjunction.com/frontend/files/Panasonic-NCR18650B.pdf>
* Vent gas: <https://discovery.ucl.ac.uk/10041857/1/Finegan_et_al-2018-Advanced_Science.pdf>, <https://stacks.cdc.gov/view/cdc/215523/cdc_215523_DS1.pdf>
* Pouch swelling: <https://www.frontiersin.org/articles/10.3389/fceng.2022.828375>, <https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10930978>
