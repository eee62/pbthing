"""All design parameters, in the SLEEVE frame (mm):
x = width (0..29.4), y = length (0..77.2), z = height (0 = bottom face, 140.5 = front face).

Tags: [MEAS] measured from the supplied STL/STEP by measure.py, [DS] datasheet,
[USER] project facts, [VENDOR] JLC3DP rule, [GUESS] unverified -> tested by the coupon
or by measuring the real part, [DES] my design choice.
"""
import math

# ---------------- sleeve (fixed part) [MEAS] -------------------------------
SLV_X, SLV_Y, SLV_Z = 29.4, 77.2, 140.5
CAV_X0, CAV_X1, CAV_Y0, CAV_Y1 = 2.5, 26.9, 2.5, 74.7       # cavity 24.4 x 72.2
CAV_R = 4.0                                                 # inner corner radius
LIP_Z0, LIP_Z1 = 134.5, 137.0                               # lip slab
LIP_X0, LIP_X1, LIP_Y0, LIP_Y1 = 5.0, 24.4, 5.0, 72.2       # lip opening 19.4 x 67.2
LIP_R = 1.5                                                 # lip opening corner radius
Z_FRONT = 140.5                                             # front face
CX, CY = 14.7, 38.6                                         # sleeve centre line

# ---------------- printer [VENDOR] -----------------------------------------
TOL = 0.2          # +-, dimensions < 100 mm
TOL_HOLE = 0.3     # +-, holes
MIN_WALL = 0.8
MIN_ENGRAVE = 0.8  # width and depth

# ---------------- fits [DES] -----------------------------------------------
G_FACE = 0.25      # faceplate edge to bore wall (visible seam)
G_LIP = 0.25       # insert body to lip opening, per side
G_PLUG = 0.25      # plug to cavity wall, per side (glue line)
G_GLUE = 0.25      # nominal glue gap between pads/ears and lip top

# ---------------- insert / faceplate [DES] ---------------------------------
PAD_H = 1.25                           # pads under the rim (sand-to-flush datum)
Z_RIM = LIP_Z1 + G_GLUE + PAD_H        # 138.5   underside of faceplate rim
EAR_T = 0.8                            # keeper ears (float in the 1.5 mm seam zone, glued)
HOVER = 0.2                            # nominal gap ear top -> rim (glue)
FP_X0, FP_X1 = CAV_X0 + G_FACE, CAV_X1 - G_FACE
FP_Y0, FP_Y1 = CAV_Y0 + G_FACE, CAV_Y1 - G_FACE
FP_R = CAV_R - G_FACE
IN_X0, IN_X1 = LIP_X0 + G_LIP, LIP_X1 - G_LIP   # 5.25 .. 24.15
IN_Y0, IN_Y1 = LIP_Y0 + G_LIP, LIP_Y1 - G_LIP   # 5.25 .. 71.95
IN_R = LIP_R - G_LIP           # 1.25

# ---------------- radar HLK-LD2410S [DS] / [GUESS] -------------------------
RAD_W = 20.0                 # [DS] 20 x 20
RAD_T = 1.2                  # [DS] 1.2 +-10 %
RAD_T_TOL = 0.12
RAD_FRONT_H = 0.85           # [GUESS] tallest front component (radar chip)
RAD_BACK_H = 1.1             # [GUESS] tallest back component
WIN_T = 0.8                  # [DES] window thickness (<= lambda/8 for er <= 3.7)
RAD_FRONT_GAP = 0.15         # [DES] components to window
RAD_X0 = CX - RAD_W / 2      # 4.7
RAD_Y0 = 5.30                # -y edge inside the lip opening so keeper posts can reach it
RAD_Z1 = Z_FRONT - WIN_T - RAD_FRONT_GAP - RAD_FRONT_H   # PCB front face 138.75
RAD_Z0 = RAD_Z1 - RAD_T                                  # PCB back face 137.55
RAD_POCKET_CLR = 0.3
RAD_PIN_EDGE = 1.27          # [GUESS] J2 hole centre to +y edge
RAD_PIN_X0 = RAD_X0 + 1.62   # [DS] first hole 1.62 from corner, 2.54 pitch
RAD_PIN_PITCH = 2.54
RAD_PINS = ['OT2', 'RX', 'OT1', 'GND', '3V3']   # [DS fig 3-1, orientation GUESS]

# ---------------- front button [USER] / [DES] -------------------------------
BTN_X, BTN_Y = CX, 30.75
BTN_D = 7.0                  # pad diameter
BTN_SLOT = 0.8               # visible ring seam (through slot) = min printable gap
BTN_PAD_Z0 = Z_FRONT - 0.8 - 0.8 - 0.8   # pad underside: skin + gap + beam (138.1)
BTN_NUB_D, BTN_NUB_H = 2.5, 0.4
BTN_PRE = 0.20               # nub to actuator gap (pre-travel)
BEAM_T, BEAM_W = 0.8, 2.0
BEAM_ROOT_X = 23.0           # beam anchored into a root boss here
SKIN_T = 0.8                 # skin over the hidden beam
BEAM_TOP_GAP = 0.8           # beam to skin, = min printable gap
TACT_W, TACT_H = 6.0, 4.3    # [USER] 6 x 6 x 4.3
TACT_BODY_H = 3.5            # [GUESS] body without actuator
TACT_ACT_D = 3.5             # [GUESS] actuator diameter
TACT_TRAVEL = 0.25           # [GUESS] typical
TACT_LEG_PX, TACT_LEG_PY = 6.5, 4.5   # [GUESS] typical THT leg spacing
TACT_LEG_L = 3.5
TACT_Z1 = BTN_PAD_Z0 - BTN_NUB_H - BTN_PRE          # actuator top 138.0
TACT_Z0 = TACT_Z1 - TACT_H                          # body bottom 133.7

# ---------------- XIAO stack (from STEP) -----------------------------------
# STEP frame: X_s along board (USB at +X_s), Y_s stack (+ = components / expansion board),
# Z_s across board. Mapping: X_s -> +z, Y_s -> +y, Z_s -> -x.
XS_PCB_TOP = 12.28           # [MEAS] XIAO PCB edge at the USB end
ZS_CENTRE = -6.11            # [MEAS] board centre across width
BAY = 2.6                    # wire bay between XIAO bottom face and backbone (one layer of 1.1 wire + bends)
BB_T = 1.2                   # backbone thickness
TACT_POCKET_Y1 = BTN_Y + TACT_W / 2 + 0.25           # +y face of tact pocket
BB_Y0 = TACT_POCKET_Y1                               # backbone (also tact pocket wall)
BB_Y1 = BB_Y0 + BB_T
Y_S0 = BB_Y1 + BAY + 0.25    # y of STEP Y_s = 0 (XIAO bottom face is Y_s = -0.25)
Z_PT = LIP_Z1                # z of the collar stop face (XIAO PCB top edge) 137.0
XIAO_DZ = -0.05              # modelled XIAO sits 0.05 below the stop (shelf clearance 0.15 total)


def xs2z(xs):
    return Z_PT + (xs - XS_PCB_TOP)


def ys2y(ys):
    return Y_S0 + ys


def zs2x(zs):
    return CX - (zs - ZS_CENTRE)


# USB-C receptacle [MEAS]: Y_s 0.95..4.21 shell, Z_s -10.59..-1.65, tip X_s 13.81
USB_W, USB_H = 8.94, 3.26
USB_YS0, USB_YS1 = 0.95, 4.21
USB_Y = ys2y((USB_YS0 + USB_YS1) / 2)
USB_MOUTH_Z = xs2z(13.81)                  # 138.53
OVM_W, OVM_H, OVM_R = 12.9, 7.0, 2.5       # overmold pocket (cable plug) [GUESS cable]
COLLAR_CLR = 0.30                           # shell to collar, per side
COLLAR_W = 1.0

# lens / camera head [GUESS]
CAM_W = 8.65                 # [USER] base 8.65 x 8.65
CAM_BASE_T = 0.4             # [GUESS] sensor PCB / stiffener
CAM_LENS_H = 5.6             # [USER] base bottom to lens top
CAM_BARREL_D, CAM_BARREL_H = 3.8, 1.0    # [USER] lens barrel diameter, [GUESS] barrel height
CAM_BODY_H = CAM_LENS_H - CAM_BASE_T - CAM_BARREL_H   # 4.2  square lens-holder / VCM block (full base width) [GUESS]
CAM_TOTAL_H = 11.7           # [USER] camera + heatsink, lens top to heatsink bottom
CAM_HS_H = CAM_TOTAL_H - CAM_LENS_H    # 6.1  heatsink glued behind the base (includes its adhesive pad)
CAM_HS_W = 8.0               # [GUESS] heatsink footprint (square envelope; fins not modelled)
CAP_POCKET_D, CAP_T = 11.0, 1.2
CAP_UNDER_GAP = 0.4          # barrel top to cap underside
LENS_OPEN_D = 4.8            # barrel clearance hole (0.5 per side around the 3.8 barrel)
LENS_FOV_DEG = 120.0         # [GUESS] check for vignetting
LENS_FRONT_D = 3.0           # [GUESS] diameter of front glass
CAM_YS1 = 17.0               # head +y edge in Y_s (FPC exits here)
CAM_Y1 = ys2y(CAM_YS1)
CAM_Y0 = CAM_Y1 - CAM_W
CAM_Y = (CAM_Y0 + CAM_Y1) / 2
CAM_TOP = Z_FRONT - CAP_T - CAP_UNDER_GAP          # barrel top 138.9
CAM_Z0 = CAM_TOP - CAM_LENS_H        # base bottom 133.3
CAM_ZH0 = CAM_Z0 - CAM_HS_H          # heatsink bottom 127.2
CAM_POCKET_CLR = 0.25

# FPC [GUESS] (24 pin 0.5 mm)
FPC_W = 13.0
FPC_T = 0.15
FPC_LEN = 65.0
FPC_R_MIN = 2.0
FPC_X = zs2x(-6.75)          # [MEAS] connector slot centre (stock tail Z_s -13..-0.5)
FPC_YS_SLOT = 5.74           # [MEAS] stock tail Y_s 5.6..5.88
FPC_XS_MOUTH = -2.84         # [MEAS] connector front (actuator side)
FPC_TAIL_IN = 4.4            # length inside connector (stock tail X_s -7.2..-2.84)
FPC_R1 = 2.0                 # first bend at the mouth (toward +y)
FPC_R2 = 2.0                 # bend back to vertical
FPC_RFOLD = 2.0              # top fold (180 deg)
FPC_RHEAD = 2.0              # 90 deg into the camera head
FPC_HEAD_IN = 1.5

# shelf / cradle under the stack bottom end
CRADLE_CLR = 0.15            # stack bottom edge to shelf (swing-in clearance)

# antenna [GUESS] (U.FL FPC antenna supplied with the XIAO)
ANT_L, ANT_W, ANT_T = 30.0, 8.0, 0.3
COAX_D = 1.13

# ---------------- bottom plug / main switch --------------------------------
SW_BODY = 8.0                # [DS] PB-22E08 body 8 x 8 x 8
SW_BODY_H = 8.0
SW_KNOB = 3.9                # [DS] knob 3.9 square
SW_PIN_L = 3.5               # [DS]
SW_PIN_PITCH = 2.5           # [DS] (facts guessed 2.54)
SW_ROW = 6.0                 # [DS] (facts guessed 5.0)
SW_LOCK_TRAVEL = 1.5         # [DS] +-0.15
SW_FULL_TRAVEL = 2.5         # [DS] +-0.2
SW_H_DEFAULT = 13.5          # [DS] body 8 + knob 5.5 (pins excluded)
SW_H_VARIANTS = [10.0, 11.0, 12.0, 13.0, 13.5, 14.0]
SW_RECESS_OUT = 1.0          # knob tip above bottom face when released (OFF)
SW_X, SW_Y = CX, CY
PLUG_SKIN = 0.8              # floor under the hidden knob channel
DIMPLE_D, DIMPLE_DEPTH = 9.0, 1.0   # conical finger dimple around the knob hole
KNOB_HOLE_D = 6.2            # clears the 3.9 square knob diagonal (5.52)

HOLDER_X, HOLDER_Y, HOLDER_Z = 20.0, 61.0, 76.0   # [USER] 76 x 61 x 20 standing on end
HOLDER_Z0 = 21.0             # holder bottom (above the switch, wires and pocket roof)
HOLDER_CLR = 0.25

# ---------------- wires ----------------------------------------------------
WIRE_D = 1.1                 # [USER] 28-30 AWG silicone 0.9..1.1 OD (use max)
WIRE_R_MIN = 2.0             # minimum bend radius used for wire sweeps

# ---------------- caps (3 variants) -----------------------------------------
CAP_VARIANTS = {'A': 0.05, 'B': 0.15, 'C': 0.25}   # nominal clearance per side (C: worst case >= 0 for a +-0.3 hole)
COVER_T = 1.5

# ---------------- material [GUESS] ------------------------------------------
E_RESIN = 2500.0             # MPa, typical SLA standard resin flexural modulus
ELONG_SAFE = 0.01            # we keep flexure strain below 1 %

# ---------------- FPC route and walls (derived) [DES] -----------------------
FPC_Y_SLOT = ys2y(FPC_YS_SLOT)          # 41.64  FPC plane at the connector
FPC_Z_MOUTH = xs2z(FPC_XS_MOUTH)        # 121.88 connector front
FPC_Z_STIFF = xs2z(-2.2)                # 122.52 end of stiffened tail (bend may start here)
FPC_Z_TAIL0 = xs2z(-7.2)                # 117.52 tail end inside the connector
FPC_Y_DOWN = ys2y(9.8)                  # down-run just past keeper C's +y lip (Y_s 7.4-8.4) and the SD socket (Y_s 7.78)
FPC_Y_UP2 = CAM_Y1 + FPC_RHEAD          # final up-run into the head
FPC_R_LOOP = (FPC_Y_UP2 - FPC_Y_DOWN) / 2
FPC_Z_HEAD = CAM_Z0 + CAM_BASE_T / 2    # FPC centre plane where it enters the head
KB_FLOOR_Z1 = CAM_ZH0                   # keeper B floor now carries the heatsink bottom
KB_FLOOR_Z0 = KB_FLOOR_Z1 - 0.8
FPCW_Y0 = FPC_Y_UP2 + 0.6               # FPC guide wall
FPCW_Y1 = FPCW_Y0 + 1.2
ANT_Y0 = FPCW_Y1 + 0.05                 # antenna FPC on the +y face of the guide wall
ANT_Z0 = 106.5
