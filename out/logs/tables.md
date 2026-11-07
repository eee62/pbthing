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
| lens barrel to lens opening (hole Ø8.0, per side) | 0.500 | 0.3 | 0.2 | 0.0 | **+0.250** | hole tol +-0.3 [USER], barrel +-0.2 [GUESS] |
| lens barrel top to cap underside (z) | 0.400 | 0.2 | 0.2 | 0.1 | **+0.100** |  |
| lens cap A in cap pocket (hole, per side) (friction option) | 0.050 | 0.3 | 0.2 | 0.0 | **-0.200** | friction fit: pick the variant that holds |
| USB cover A in overmold pocket (per side) (friction option) | 0.050 | 0.3 | 0.2 | 0.0 | **-0.200** | friction fit |
| lens cap B in cap pocket (hole, per side) (friction option) | 0.150 | 0.3 | 0.2 | 0.0 | **-0.100** | friction fit: pick the variant that holds |
| USB cover B in overmold pocket (per side) (friction option) | 0.150 | 0.3 | 0.2 | 0.0 | **-0.100** | friction fit |
| lens cap C in cap pocket (hole, per side) | 0.250 | 0.3 | 0.2 | 0.0 | **+0.000** | friction fit: pick the variant that holds |
| USB cover C in overmold pocket (per side) | 0.250 | 0.3 | 0.2 | 0.0 | **+0.000** | friction fit |
| cable overmold 12.5 x 6.6 in pocket (per side, short side) | 0.400 | 0.3 | 0.0 | 0.0 | **+0.250** | largest spec-compliant overmold [USER] |
| cable overmold 12.5 x 6.6 in pocket (per side, long side) | 0.400 | 0.3 | 0.0 | 0.0 | **+0.250** | largest spec-compliant overmold [USER] |
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
| camera FPC 6 x 0.15 | 65.0 | 2.0 | 0.000 | 2.686 |
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
| insert | 4037 | 23.9 x 71.7 x 34.5 | 0.80 | 0.80 |
| plug | 7412 | 23.9 x 71.7 x 27.0 | 0.80 | 2.62 |
| tray | 10442 | 100.3 x 63.2 x 27.8 | nan | nan |
| coupon | 4254 | 23.9 x 74.0 x 18.0 | 0.80 | 0.80 |
| keeper_a | 444 | 23.6 x 27.2 x 6.7 | 0.80 | 2.10 |
| keeper_b | 284 | 23.6 x 8.6 x 11.9 | 0.80 | nan |
| keeper_c | 749 | 23.6 x 13.7 x 24.8 | 0.80 | nan |
| carrier_H10 | 875 | 17.2 x 10.4 x 15.7 | nan | nan |
| carrier_H11 | 875 | 17.2 x 10.4 x 15.7 | nan | nan |
| carrier_H12 | 875 | 17.2 x 10.4 x 15.7 | nan | nan |
| carrier_H13 | 875 | 17.2 x 10.4 x 15.7 | nan | nan |
| carrier_H13.5 | 875 | 17.2 x 10.4 x 15.7 | 0.95 | nan |
| carrier_H14 | 875 | 17.2 x 10.4 x 15.7 | nan | nan |
| lens_cap_A | 111 | 10.9 x 10.9 x 1.2 | 1.20 | 1.20 |
| usb_cover_A | 135 | 13.2 x 7.3 x 1.5 | 1.50 | 1.20 |
| lens_cap_B | 107 | 10.7 x 10.7 x 1.2 | nan | nan |
| usb_cover_B | 130 | 13.0 x 7.1 x 1.5 | nan | nan |
| lens_cap_C | 103 | 10.5 x 10.5 x 1.2 | nan | nan |
| usb_cover_C | 125 | 12.8 x 6.9 x 1.5 | nan | nan |

| Switch H (body+knob) | Recess released | Recess latched | Recess full press | Pin tip z | Room to holder |
|---:|---:|---:|---:|---:|---:|
| 10.0 | 1.00 | 2.50 | 3.50 | 14.50 | 6.50 |
| 11.0 | 1.00 | 2.50 | 3.50 | 15.50 | 5.50 |
| 12.0 | 1.00 | 2.50 | 3.50 | 16.50 | 4.50 |
| 13.0 | 1.00 | 2.50 | 3.50 | 17.50 | 3.50 |
| 13.5 | 1.00 | 2.50 | 3.50 | 18.00 | 3.00 |
| 14.0 | 1.00 | 2.50 | 3.50 | 18.50 | 2.50 |
