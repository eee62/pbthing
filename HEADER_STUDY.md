# Keeping the radar's factory 5-pin header (study only, the design is NOT changed)

Inputs: header 8.3 mm total height from the PCB back, plastic spacer 1.35 mm. Assumed (not given): 5 pins at 2.54 mm pitch (matches
`RAD_PIN_PITCH`), plastic 12.7 × 2.54 mm, pins 0.64 mm square. Script: `python src/header_study.py` (exact B-rep booleans and distances against
the real insert, keepers, tact and sleeve, plus keeper A's install path).

## Answer
**It does not sit "above" the lip. It hangs through the lip opening, and it almost fits. Two things must change: pin 1 and its spacer end.**

| Question | Result |
|---|---|
| Where is it? | PCB back at z 137.50 (0.5 above the lip top, z 137.0). Header x 5.05–17.75, y 22.76–25.30, plastic z 136.15–137.50, pins down to **z 129.20**, i.e. 5.3 mm below the lip underside (z 134.5). |
| Fits the lip opening (19.4 × 67.2)? | Yes in y, but the **−x end of the plastic is 0.05 mm from the sleeve** (opening edge x 5.0 vs plastic x 5.05); 0.30 mm from the insert. No tolerance margin. |
| Clears keeper A? | **No, by one pin:** pin 1 (OT2, unused) at x 6.32 lies outside keeper A's wire slot (x 7.6–17.6) and cuts through the plate (z 134.9–135.7): 0.33 mm³ overlap, the plate hits it at 0–6 mm above its seat. Pins 2–5 pass through the slot with 0.94 mm (left) and 0.80 mm (right) margin. The plastic is above the plate (no contact). |
| Anything else? | Tact 2.45 mm, keeper C 7.5 mm, keeper B 21 mm away; no overlap. |

## What has to change
1. **Remove pin 1 (OT2, unused) and trim the plastic spacer to start at pin 2's cell** (x 7.59–17.75, 10.16 mm long). Then: overlap with everything 0,
   keeper A install path (lowering from −z with the header on the radar) **no hits**, clearance to keeper A 0.45 mm, to the insert 0.30 mm, to the sleeve **2.59 mm**.
2. Keeper A: no change needed (slot margins 0.8–0.94 mm). Optional: widen the slot 0.5 mm per side if you want more.
3. Radar model: drop the 1.0 mm solder-joint cylinders, add the trimmed header; keep-out in `radar()` stays.
4. Wire routes (`radar_wires`): lanes start at the **pin tips (z 129.2) instead of z 136.5**: 7.3 mm shorter per wire.
5. Bench prep, ASSEMBLY step 3.2 (cut the spacer, desolder pins) is deleted; new step: clip pin 1 flush and trim the spacer end.

## What the wiring looks like
* **Solder to the pin tips (recommended).** Wires of pins 2–5 (RX, OT1, GND, 3V3) are soldered on the lower 2 mm of the pins (z 129.2–131.2) and go straight down/+y in the
  existing lanes. They now pass 4–6 mm **below** keeper A's plate, so the 0.7 mm squeeze between the radar back components and the plate (found in the assembly
  simulation) no longer exists. The GND run at z 130.9 (under keeper A's tact bridge, bridge at 131.6) leaves the pin at that height. Keeper A still lowers around
  the pins and wires through its +y-open slot.
* **Pluggable 4-way 2.54 mm housing on pins 2–5** (optional): housing ~10.2 × 2.5 mm and ~8 mm tall reaches down to z ≈ 128; it is wider than the slot, so the slot
  must grow by ≥ 0.3 mm per side, and the wires then exit downward from z ≈ 128. No benefit after assembly because the bay is closed, so not recommended.
* A 5-way housing (12.7 mm) does not fit: it reaches the sleeve opening edge (0.05 mm) and the slot.

## Not simulated or measured
Real pin pitch/length, plastic size and the spacer geometry are assumptions; the simulation run in this commit does not include the header.
