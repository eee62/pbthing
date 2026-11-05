# Project facts: 3D-printed power-bank-style sensor show piece

Read this fully before designing. Every number is tagged:
- [USER] the user decided/said it (treat as a requirement)
- [MEASURED] taken from the supplied sleeve STL (re-measure it yourself; do not trust my copy)
- [VENDOR] printer-service rule (JLC3DP); the only real manufacturing limits
- [GUESS] estimated from listings, not confirmed. Make these PARAMETERS and design around the uncertainty.

## 1. What it is
A hidden-sensor "power bank" look-alike (ZenPower style). It is a show piece / sensor node, not a real power bank. [USER]
- A hidden HLK-LD2410S 24 GHz presence radar sits behind the front face. [USER]
- A Seeed XIAO ESP32-S3 Sense with its expansion board (camera + mic) sits inside. The ONLY external port is the XIAO's own USB-C (charging at ~50 mA, programming). No microSD card is used. [USER]
- An aftermarket OV5640 wide-angle auto-focus camera on a ~6.5 cm FPC ribbon replaces the stock Sense camera. Head size is unknown: assume about 8.5 x 8.5 mm with a lens barrel up to about 7.9 mm diameter. [GUESS]
- Power: a 3 x 18650 leaded battery holder, outer box 76 x 61 x 20 mm. [USER] The cells are wired in PARALLEL (3.7 V). Protected cells. [USER]
- A main power switch must cut power to the ENTIRE device. [USER] See section 4.

## 2. The fixed part: the printed sleeve (supplied STL, cannot change) [USER]
File `zen_v7_sleeve.stl`. Frame: x width, y length, z height; z = 140.5 is the front (top) face; z = 0 is the bottom end.
- Outer 29.4 x 77.2 x 140.5. [MEASURED]
- Cavity 24.4 x 72.2 mm (x 2.5..26.9, y 2.5..74.7), wall 2.5, rounded inner corners about r4. [MEASURED]
- A lip at z 134.5..137.0 with an opening of about 19.4 x 67.2. [MEASURED]
- A bore above the lip at z 137..140.5 (the faceplate sits here and ends flush with the front face). [MEASURED]
- The sleeve is open at both ends in effect: the insert goes in from the top through the lip opening and seats on the lip; the battery holder and boards go in from the bottom; a permanent plug closes the bottom flush. Check this against the STL.
- The sleeve has no features on its side walls to use. Design everything else.

## 3. What to design (printed by JLC3DP in 9000HE resin) [USER]
1. ONE-PIECE faceplate + inner tray/frame insert (front plate plus the structure that holds the XIAO stack, camera head and radar).
2. Front face contents: radar window, camera lens opening, a small front button (printed flush flexure with an engraved power icon over a 6 x 6 x 4.3 mm tactile switch, used as a GPIO input), and a USB-C pocket for the XIAO.
3. Separate REMOVABLE flush lens cap and USB-C cover (friction fit, no snap nubs because the resin is brittle). Print 3 tolerance variants (A/B/C) of each so one fits.
4. A permanent flush BOTTOM PLUG that closes the sleeve bottom, carries the battery holder, and exposes the main latching power button (section 4) from the flat bottom face.
5. Modelled wire paths: show the camera ribbon, battery/switch wires, radar wires as real swept volumes through real channels. Wires must not be pinched at the lip or by the plug.
6. Tolerance compensation: build every fit from nominal minus printer tolerance, with a worst-case table.
7. Premium finish: flush seams, even small gaps (about 0.25 mm), no visible fasteners, crisp edges, nothing floating.

## 4. The main power switch [USER decision: latching push button, NOT a slide switch]
Chosen part family: 8 x 8 mm self-locking (push-on/push-off) DPDT through-hole push switch (G-Switch PB-22E08-LC, LCSC C2848958; the "KFC-A06 / KFC-8x8" family sold at Tayda, robu, Shopee).
- Body footprint about 8 x 8 mm (some 8.5 x 8.5). Treat as 8.7 x 8.7 clearance. [GUESS]
- Listings say overall size "8 x 8 x 13 mm". The knob (cap) height is a per-SKU option in this family (4.3 to 23 mm). The user will order the SHORTEST knob. Make the total height a parameter, default 13 mm, range 10..14 mm. [GUESS]
- 6 pins in 2 rows of 3, through-hole. Pin pitch and row spacing unconfirmed: parameter (default 2.54 mm pitch, 5.0 mm rows). [GUESS]
- Actuation force 100..350 gf (about 1..3.4 N), travel about 2..2.5 mm (latching action). [GUESS from listings]
- Rating: 0.3 A (some listings 0.5 A) per pole at 30 V DC. The two poles are wired in PARALLEL in the battery positive line to roughly double the current. [GUESS]
- It sits in the battery positive line, so with the switch OFF the battery is disconnected from everything and USB-C charging into the battery stops. The user accepts this. USB power into the XIAO still works.
- It must be pressable from the flat bottom face of the sealed device with a fingertip or pen tip. The plunger cannot be perfectly flush in both states (about 2 mm travel): use a recess so the plunger sits slightly inside the face when out and deeper when pressed. The printed plug cannot flex to press a latching switch, so the plunger pushes directly.
- The switch is hand-soldered to wires (no PCB). The plug design must hold it firmly under 3.4 N presses, with room to solder 4 wires.
- Because 13 mm of switch has to sit under or beside the holder, the holder (box 76 x 61 x 20, standing on end in the sleeve) is probably raised about 13 mm. There is a large empty gap above the holder before the XIAO stack, so raising it is fine. About 4.9 mm is free beside the holder at each y end, which is NOT enough for the switch beside it. Decide the placement yourself and justify it.

## 5. Printer rules: JLC3DP 9000HE resin (SLA) [VENDOR]
- Dimensional tolerance +-0.2 mm below 100 mm; holes +-0.3 mm.
- Minimum wall 0.8 mm; minimum engraved detail 0.8 x 0.8 mm (width x depth).
- Minimum build size of a part about 5 x 5 x 5 mm (or 10 x 2 x 2 mm), so thin parts (caps) must ride on a carrier tray with snap-off posts.
- Heat deflection about 60 C. Brittle: no snap hooks or thin cantilevers that must flex much.
- Parts drift 0.15..0.2 mm over 3..7 days after delivery.
- Fit rule to use: worst-case gap per side = nominal clearance - (tol_A + tol_B) / 2.

## 6. Electronics and assembly facts
- XIAO ESP32-S3 Sense STEP model is supplied (`XIAO_ESP32S3_Sense.step`). It shows Seeed's stock camera (8 x 8 block with a round barrel), NOT the user's camera. Use it for board outline, connector positions and USB-C position.
- The camera ribbon plugs into the expansion board's FPC connector (likely 24-pin, 0.5 mm pitch, about 13 mm wide, about 0.15 mm thick; verify). Do not fold it tighter than about 2 mm radius.
- The expansion board's BOOT/RESET are small; the user will flash over USB-C before closing, so they may be inaccessible afterwards.
- Wire gauge 28..30 AWG silicone (about 0.9..1.1 mm OD).
- Hi-Link HLK-LD2410S datasheet governs the radar outline and the material in front of it. Look it up. Earlier guidance: keep the window thin (about 0.8 mm) with nothing metallic or dense in front of it.
- The user has NO 3D printer and pays per order, so cost matters: minimise part count, combine where possible, and put tiny parts on shared trays.
- Nothing has been physically tested. Say so for every claim you cannot verify numerically.
