"""Printed parts, built with exact CadQuery booleans, all in the sleeve frame (assembled
position) unless stated. See params.py for every number."""
import math
import cadquery as cq
from params import *  # noqa
from geo import box, cyl, cone, rrect, union_all
import components as C

SHELF_Z0 = 114.4
SHELF_TOP_XIAO = xs2z(-8.68) - CRADLE_CLR       # under XIAO PCB bottom edge (115.89)
SHELF_TOP_EXP = xs2z(-8.97) - CRADLE_CLR        # under expansion PCB edge   (115.60)
LIP_Y0_ = ys2y(7.40)                            # keeper C +y lip (connector housing top is Y_s 7.18)
LIP_Y1_ = ys2y(8.40)
LIP_ZTOP = 117.3
COLLAR_X0, COLLAR_X1 = CX - USB_W / 2 - COLLAR_CLR - COLLAR_W, CX + USB_W / 2 + COLLAR_CLR + COLLAR_W
SHELL_X0, SHELL_X1 = CX - USB_W / 2 - COLLAR_CLR, CX + USB_W / 2 + COLLAR_CLR
SHELL_Y0 = ys2y(USB_YS0) - COLLAR_CLR
SHELL_Y1 = ys2y(USB_YS1)                         # open side, closed by keeper B tongue
TONGUE_Y0, TONGUE_Y1 = SHELL_Y1 + 0.10, SHELL_Y1 + 1.10
TACT_IN = 3.9                                    # tact pocket half width in x (legs)
TACT_WALL = 0.8
EAR_Z1 = Z_RIM - HOVER
EAR_Z0 = EAR_Z1 - EAR_T
KA_Z0, KA_Z1 = 134.9, 135.7                      # keeper A radar plate
FPCW_Z0 = 106.0
KA_EY0 = RAD_Y0 + RAD_W + RAD_POCKET_CLR + 0.8 + 0.4   # keeper A ears clear of radar skirt
KA_EY1 = BB_Y0 - 1.5
KA_LOW_Z0 = TACT_Z0 - 1.6                       # keeper A lower bridge (tact support)
KB_EY0 = CAM_Y0
KB_EY1 = CAM_Y0 + 7.2

# backbone wire windows (x0, x1, z0, z1)
BB_Z0 = 132.6                                    # short backbone: tact pocket wall + top rib only
FOOT_Z0 = 113.5
FOOT_WALL_Z = 117.7                              # keeper C -y wall top (wires run above 118.2)
ARM_Y0, ARM_Y1 = BB_Y0 - 1.2, BB_Y0 - 0.1        # keeper C arms just -y of the backbone
KC_EY0, KC_EY1 = ARM_Y0, ys2y(-0.25) - 0.2      # keeper C ears (between keeper A ears and the XIAO)
FOOT_NOTCHES = [  # (x0, x1, y0, y1): open-ended so keeper A slides past wires already in place
    (17.4, 21.4, ARM_Y0 - 1.0, ys2y(-0.25) + 0.3),        # battery wires up into the bay (open -y)
    (17.6, 21.2, ys2y(1.2), ys2y(8.3) + 1.0),              # U.FL coax down (open +y)
]


def lip_envelope():
    """Everything of the top module below the lip top must stay inside this outline
    (lip opening minus G_LIP) so it can pass the lip."""
    return rrect(IN_X0, IN_X1, IN_Y0, IN_Y1, 90, LIP_Z1 + 0.001, IN_R).union(box(-5, 35, -5, 82, LIP_Z1, 150))


# ======================================================================== insert
def insert():
    fp = rrect(FP_X0, FP_X1, FP_Y0, FP_Y1, Z_RIM, Z_FRONT, FP_R)

    # --- radar skirt (rests on the lip, carries the radar pocket walls)
    skirt = rrect(FP_X0, FP_X1, FP_Y0, FP_Y1, LIP_Z1 + G_GLUE, Z_RIM + 0.01, FP_R).intersect(
        box(0, 30, 0, BTN_Y - TACT_W / 2 - 0.25 - TACT_WALL + 0.05, 130, 140))   # skirt meets the tact pocket wall
    body = fp.union(skirt)

    # --- pads on the rim (sand-to-flush datum), clear of keeper ears
    zp0 = LIP_Z1 + G_GLUE
    for (x0, x1, y0, y1) in [(FP_X0 + 0.15, IN_X0 + 0.01, KC_EY1 + 0.6, KB_EY0 - 0.6), (IN_X1 - 0.01, FP_X1 - 0.15, KC_EY1 + 0.6, KB_EY0 - 0.6),
                             (FP_X0 + 0.15, IN_X0 + 0.01, KB_EY1 + 1.0, 68.0), (IN_X1 - 0.01, FP_X1 - 0.15, KB_EY1 + 1.0, 68.0),
                             (9.0, 20.4, IN_Y1 - 0.05, FP_Y1 - 0.15)]:   # +y pad merges with the antenna wall (no 0.4 mm slot)
        body = body.union(box(x0, x1, y0, y1, zp0, Z_RIM + 0.01))

    # --- radar pocket (open below) and 4 ledges under the window
    rx0, rx1 = RAD_X0 - RAD_POCKET_CLR, RAD_X0 + RAD_W + RAD_POCKET_CLR
    ry0, ry1 = RAD_Y0 - RAD_POCKET_CLR, RAD_Y0 + RAD_W + RAD_POCKET_CLR
    body = body.cut(box(rx0, rx1, ry0, ry1, 130, Z_FRONT - WIN_T))
    ycm = RAD_Y0 + RAD_W / 2
    zl0, zl1 = RAD_Z1, Z_FRONT - WIN_T + 0.01
    for (x0, x1, y0, y1) in [(CX - 0.75, CX + 0.75, ry0 - 0.01, RAD_Y0 + 0.8),
                             (RAD_X0 + 14.0, RAD_X0 + 15.5, RAD_Y0 + RAD_W - 0.8, ry1 + 0.01),
                             (rx0 - 0.01, RAD_X0 + 0.8, ycm - 0.75, ycm + 0.75),
                             (RAD_X0 + RAD_W - 0.8, rx1 + 0.01, ycm - 0.75, ycm + 0.75)]:
        body = body.union(box(x0, x1, y0, y1, zl0, zl1))

    # --- tact switch pocket (open below), its +y wall is the backbone
    tx0, tx1 = BTN_X - TACT_IN - TACT_WALL, BTN_X + TACT_IN + TACT_WALL
    ty0 = BTN_Y - TACT_W / 2 - 0.25 - TACT_WALL
    tp = box(tx0, tx1, ty0, BB_Y0 + 0.01, TACT_Z0, Z_RIM + 0.01).cut(
        box(BTN_X - TACT_IN, BTN_X + TACT_IN, BTN_Y - TACT_W / 2 - 0.25, BB_Y0 + 0.02, TACT_Z0 - 1, Z_RIM + 0.02))
    body = body.union(tp)

    # --- backbone with wire windows, bay ribs, shelf (cradle) with +y lip
    bb = box(6.3, 23.1, BB_Y0, BB_Y1, BB_Z0, Z_RIM + 0.01)   # narrow: keeper C ear walls pass beside it
    y_bot = ys2y(-0.25)
    rib_top = box(7.5, 21.9, BB_Y1 - 0.01, y_bot - 0.30, 136.0, Z_PT + 0.01)   # backup -y stop (collar locates)
    body = body.union(bb).union(rib_top)

    # --- USB collar: closed ring around the shell; its underside is the stop for the XIAO
    #     PCB edge. The XIAO slides in along +z (USB first).
    collar = box(COLLAR_X0, COLLAR_X1, BB_Y0, SHELL_Y1 + COLLAR_CLR + COLLAR_W, Z_PT, Z_RIM + 0.01).cut(
        box(SHELL_X0, SHELL_X1, SHELL_Y0, SHELL_Y1 + COLLAR_CLR, Z_PT - 1, Z_RIM + 1))
    body = body.union(collar)
    # overmold pocket through the faceplate
    body = body.cut(rrect(CX - OVM_W / 2, CX + OVM_W / 2, USB_Y - OVM_H / 2, USB_Y + OVM_H / 2,
                          Z_RIM - 0.01, Z_FRONT + 0.1, OVM_R))

    # --- camera head pocket, lens opening, cap pocket
    hx0, hx1 = CX - CAM_W / 2 - CAM_POCKET_CLR, CX + CAM_W / 2 + CAM_POCKET_CLR
    hy0, hy1 = CAM_Y0 - CAM_POCKET_CLR, CAM_Y1 + CAM_POCKET_CLR
    hp = box(hx0 - 0.8, hx1 + 0.8, hy0 - 0.8, hy1 + 0.8, CAM_Z0 + CAM_BASE_T, Z_RIM + 0.01).cut(
        box(hx0, hx1, hy0, hy1, 120, 140))
    hp = hp.cut(box(hx0 - 1, hx1 + 1, hy1 - 0.01, hy1 + 1, 120, CAM_Z0 + 0.8))   # FPC exit
    body = body.union(hp)
    body = body.cut(cyl(CX, CAM_Y, Z_RIM - 0.05, Z_FRONT - CAP_T + 0.01, LENS_OPEN_D))
    body = body.cut(cyl(CX, CAM_Y, Z_FRONT - CAP_T, Z_FRONT + 0.1, CAP_POCKET_D))

    # --- FPC guide wall
    body = body.union(box(IN_X0, IN_X1, FPCW_Y0, FPCW_Y1, FPCW_Z0, Z_RIM + 0.01))
    # --- antenna wall at the +y end (antenna FPC sticks on its -y face, away from the camera ribbon)
    body = body.union(box(IN_X0, IN_X1, ANTW_Y0, IN_Y1, ANT_WALL_Z0, Z_RIM + 0.01))

    # --- front button: ring seam, hidden cantilever beam, pad, nub, engraved icon
    body = body.cut(cyl(BTN_X, BTN_Y, Z_RIM - 0.05, Z_FRONT + 0.1, BTN_D + 2 * BTN_SLOT))   # visible ring seam
    rb = BTN_D / 2 + BTN_SLOT                                                              # clear walls next to the pad
    body = body.cut(box(min(BTN_X - rb, tx0 - 0.01), max(BTN_X + rb, tx1 + 0.01), BTN_Y - rb, BB_Y1 - 0.02,
                        TACT_Z1 - 0.3, Z_RIM + 0.01))
    beam_top = BTN_PAD_Z0 + BEAM_T
    body = body.cut(box(BTN_X + BTN_D / 2 - 0.5, BEAM_ROOT_X - 0.8, BTN_Y - BEAM_W / 2 - 0.8,
                        BTN_Y + BEAM_W / 2 + 0.8, Z_RIM - 0.05, beam_top + BEAM_TOP_GAP))
    beam = box(BTN_X + 1.0, BEAM_ROOT_X + 0.1, BTN_Y - BEAM_W / 2, BTN_Y + BEAM_W / 2,
               BTN_PAD_Z0, beam_top)
    pad = cyl(BTN_X, BTN_Y, BTN_PAD_Z0, Z_FRONT, BTN_D)
    nub = cyl(BTN_X, BTN_Y, BTN_PAD_Z0 - BTN_NUB_H, BTN_PAD_Z0 + 0.01, BTN_NUB_D)
    root = box(BEAM_ROOT_X - 0.8, BEAM_ROOT_X + 0.2, BTN_Y - 2.0, BTN_Y + 2.0, BTN_PAD_Z0 - 0.2, Z_RIM + 0.01)
    body = body.union(beam).union(pad).union(nub).union(root)
    body = body.cut(power_icon())
    return body.intersect(lip_envelope())


def power_icon(depth=MIN_ENGRAVE, r_in=1.6, r_out=2.4, gap_deg=50.0):
    """Power symbol, bar toward +x. Line width 0.8 (= r_out - r_in), depth 0.8."""
    z0, z1 = Z_FRONT - depth, Z_FRONT + 0.1
    ringc = cyl(BTN_X, BTN_Y, z0, z1, 2 * r_out).cut(cyl(BTN_X, BTN_Y, z0 - 1, z1 + 1, 2 * r_in))
    # wedge gap around +x
    L = 5.0
    a = math.radians(gap_deg)
    wedge = (cq.Workplane('XY', origin=(0, 0, z0 - 0.5))
             .polyline([(BTN_X, BTN_Y), (BTN_X + L * math.cos(a), BTN_Y + L * math.sin(a)),
                        (BTN_X + L, BTN_Y), (BTN_X + L * math.cos(a), BTN_Y - L * math.sin(a))])
             .close().extrude(z1 - z0 + 1))
    ringc = ringc.cut(wedge)
    bar = box(BTN_X + 0.0, BTN_X + 2.6, BTN_Y - 0.4, BTN_Y + 0.4, z0, z1)
    return ringc.union(bar)


# ======================================================================== keepers
# Three keepers, each installed from the inside (insert face-down on a glass plate) AFTER the
# parts it holds, each with ears that end up between faceplate rim and lip (the insert glue
# seam). Their install direction is +z (device frame) and their footprints avoid every wire
# laid before them (checked in verify.py).
def _ears(k, ey0, ey1, zlow):
    for (sx0, sx1, ex0, ex1) in [(5.3, 6.1, FP_X0 + 0.15, 5.3 + 0.01), (23.3, 24.1, 24.1 - 0.01, FP_X1 - 0.15)]:
        k = k.union(box(sx0, sx1, ey0, ey1, zlow, EAR_Z1))
        k = k.union(box(ex0, ex1, ey0, ey1, EAR_Z0, EAR_Z1))
    return k


def keeper_a():
    """Radar + front-button keeper: 3 posts under the radar PCB corners, cup under the tact
    switch. Wire slot open to +y so the plate passes the radar wires."""
    x0, x1 = IN_X0 + 0.05, IN_X1 - 0.05
    ry1 = RAD_Y0 + RAD_W
    yp = C.radar_pin_y()
    plate = box(x0, x1, IN_Y0 + 0.05, ry1 + 0.15, KA_Z0, KA_Z1)
    plate = plate.cut(box(7.6, 17.6, yp - 1.0, ry1 + 1.0, 120, 140))      # open to +y
    py0 = RAD_Y0 + 0.15
    py1 = RAD_Y0 + RAD_W - 1.4
    # 3 posts in the 1.5 mm component-free border of the radar back [GUESS], clear of the
    # rounded lip-opening corners and of the J2 pads
    posts = [box(9.0, 9.8, py0, py0 + 0.8, KA_Z1 - 0.01, RAD_Z0),
             box(19.6, 20.4, py0, py0 + 0.8, KA_Z1 - 0.01, RAD_Z0),
             box(23.2, 24.0, py1, py1 + 0.8, KA_Z1 - 0.01, RAD_Z0)]
    riser = box(18.8, 22.6, ry1 - 4.0, ry1 + 0.15, KA_LOW_Z0, KA_Z1)
    lower = box(18.8, 22.6, ry1 - 4.0, BTN_Y + 1.6, KA_LOW_Z0, KA_LOW_Z0 + 0.8)
    bridge = box(BTN_X - 2.5, 22.6, BTN_Y - 1.6, BTN_Y + 1.6, KA_LOW_Z0, KA_LOW_Z0 + 0.8)
    cup = box(BTN_X - 2.5, BTN_X + 2.5, BTN_Y - 1.6, BTN_Y + 1.6, KA_LOW_Z0 + 0.79, TACT_Z0)
    k = union_all([plate] + posts + [riser, lower, bridge, cup])
    for (lx, ly) in C.tact_leg_points():
        k = k.cut(box(lx - 0.75, lx + 0.75, ly - 0.6, ly + 0.6, 120, 140))
    for (sx0, sx1) in [(5.3, 6.1), (23.3, 24.1)]:
        k = k.union(box(sx0, sx1, ry1 + 0.05, KA_EY1, KA_Z0, KA_Z1))
    k = _ears(k, KA_EY0, KA_EY1, KA_Z0)
    return k.intersect(lip_envelope())


def keeper_b():
    """Camera keeper: floor carries the head base; ears in the insert seam."""
    k = box(IN_X0 + 0.05, IN_X1 - 0.05, CAM_Y0 - 0.2, CAM_Y1 - 0.3, KB_FLOOR_Z0, KB_FLOOR_Z1)
    k = _ears(k, KB_EY0, KB_EY1, KB_FLOOR_Z0)
    return k.intersect(lip_envelope())


def keeper_c():
    """XIAO foot: U-cradle under the bottom end (-z support, -y and +y walls), two arms up
    the -y side of the stack to ears in the insert seam. Installed after the XIAO."""
    x0, x1 = IN_X0 + 0.05, IN_X1 - 0.05
    y_bot = ys2y(-0.25)
    arms = [box(5.4, 7.4, ARM_Y0, ARM_Y1, FOOT_Z0, EAR_Z1), box(22.0, 24.0, ARM_Y0, ARM_Y1, FOOT_Z0, EAR_Z1)]
    foot = union_all([
        box(x0, x1, ARM_Y0, ys2y(1.0), FOOT_Z0, SHELF_TOP_XIAO),
        box(x0, x1, ys2y(1.0) - 0.01, LIP_Y1_, FOOT_Z0, SHELF_TOP_EXP),
        box(x0, x1, ARM_Y0, y_bot - 0.20, FOOT_Z0, FOOT_WALL_Z),      # -y wall (0.2 to XIAO bottom face)
        box(x0, x1, LIP_Y0_, LIP_Y1_, FOOT_Z0, LIP_ZTOP)])            # +y lip
    for (nx0, nx1, ny0, ny1) in FOOT_NOTCHES:
        foot = foot.cut(box(nx0, nx1, ny0, ny1, FOOT_Z0 - 1, 118.5))
    k = union_all(arms + [foot])
    k = _ears(k, KC_EY0, KC_EY1, EAR_Z0 - 2.0)
    return k.intersect(lip_envelope())


# ======================================================================== plug
PLUG_X0, PLUG_X1 = CAV_X0 + G_PLUG, CAV_X1 - G_PLUG
PLUG_Y0, PLUG_Y1 = CAV_Y0 + G_PLUG, CAV_Y1 - G_PLUG
CAR_HALF_Y = 5.2
CAR_X1 = SW_X + 5.4                  # carrier +x end
CAR_Z0 = PLUG_SKIN                   # carrier bottom rests on the skin
CAR_Z1 = SW_RECESS_OUT + max(SW_H_VARIANTS) + 1.5   # 16.5, same for all variants
POCKET_CLR = 0.25
POCKET_Z1 = CAR_Z1 + 0.25
ROOF_T = 1.2
SW_CLR = 0.25                        # switch body to carrier walls
SW_ZCLR = 0.15                       # switch body top to carrier bridge (lost motion)
KNOB_HOLE_D2 = 7.4
DIMPLE_D2 = 10.0
SUPPORT_TOP = HOLDER_Z0


def plug():
    base = rrect(PLUG_X0, PLUG_X1, PLUG_Y0, PLUG_Y1, 0, 2.0, CAV_R - G_PLUG)
    rim = rrect(PLUG_X0, PLUG_X1, PLUG_Y0, PLUG_Y1, 0, 6.0, CAV_R - G_PLUG).cut(
        rrect(PLUG_X0 + 1.2, PLUG_X1 - 1.2, PLUG_Y0 + 1.2, PLUG_Y1 - 1.2, -1, 7, CAV_R - G_PLUG - 1.2))
    hy = CAR_HALF_Y + POCKET_CLR
    housing = box(PLUG_X0, CAR_X1 + POCKET_CLR + 1.2, SW_Y - hy - 1.2, SW_Y + hy + 1.2, 0, POCKET_Z1 + ROOF_T)
    hx0 = CX - HOLDER_X / 2 - HOLDER_CLR
    hx1 = CX + HOLDER_X / 2 + HOLDER_CLR
    hy0 = CY - HOLDER_Y / 2 - HOLDER_CLR
    hy1 = CY + HOLDER_Y / 2 + HOLDER_CLR
    # cradle: x walls (full length) and thin y walls, up to 7 mm over the holder bottom
    # cradle: short x-wall segments (locate the holder in x) and thin y-walls (locate in y)
    segs = []
    for (ya, yb) in ((hy0 - 1.2, hy0 + 9.0), (CY - 5.0, CY + 5.0), (hy1 - 9.0, hy1 + 1.2)):
        segs += [box(hx0 - 1.2, hx0, ya, yb, HOLDER_Z0 - 4.0, HOLDER_Z0 + 6.0),
                 box(hx1, hx1 + 1.2, ya, yb, HOLDER_Z0 - 4.0, HOLDER_Z0 + 6.0)]
    walls = union_all(segs + [
        box(hx0 - 1.2, hx1 + 1.2, hy0 - 1.2, hy0, HOLDER_Z0 - 4.0, HOLDER_Z0 + 2.0),
        box(hx0 - 1.2, hx1 + 1.2, hy1, hy1 + 1.2, HOLDER_Z0 - 4.0, HOLDER_Z0 + 2.0),
    ])
    # four corner supports under the holder bottom
    sup = union_all([box(x0, x1, y0, y1, 0, SUPPORT_TOP) for (x0, x1) in ((hx0 - 1.2, hx0 + 3.0), (hx1 - 3.6, hx1 + 1.2))
                     for (y0, y1) in ((hy0 - 1.2, hy0 + 3.0), (CY - 1.5, CY + 1.5), (hy1 - 3.0, hy1 + 1.2))])
    sup = sup.cut(box(hx0 + 3.0, hx1 - 3.6, CY - 10, CY + 10, -1, 30))      # centre pair only at the x walls
    p = union_all([base, rim, housing, walls, sup])
    # wire passage through the -y thin wall (switch wires and holder leads run up the -y end gap)
    p = p.cut(box(10.7, 21.0, hy0 - 1.3, hy0 + 0.1, HOLDER_Z0 - 4.1, HOLDER_Z0 - 0.1))
    # wire passage through the -y thin wall (switch wires and holder leads go up the -y end)
    # carrier pocket: open at the -x face
    p = p.cut(box(PLUG_X0 - 1, CAR_X1 + POCKET_CLR, SW_Y - hy, SW_Y + hy, PLUG_SKIN, POCKET_Z1))
    # roof slot for switch pins / wires (open at -x face)
    p = p.cut(box(PLUG_X0 - 1, SW_X + 4.0, SW_Y - 3.8, SW_Y + 3.8, POCKET_Z1 - 0.1, POCKET_Z1 + ROOF_T + 1))
    p = p.union(ph_cage())
    # knob hole + conical finger dimple in the flat bottom face
    p = p.cut(cyl(SW_X, SW_Y, -1, PLUG_SKIN + 0.1, KNOB_HOLE_D2))
    p = p.cut(cone(SW_X, SW_Y, -0.001, DIMPLE_DEPTH, DIMPLE_D2, KNOB_HOLE_D2))
    return p


def carrier(h=SW_H_DEFAULT):
    """Switch carrier for body+knob height h. Slides into the plug along +x (knob in the
    hidden channel), the switch slides into the carrier along +y."""
    k = h - SW_BODY_H
    zb = SW_RECESS_OUT + k
    zt = SW_RECESS_OUT + h
    x0, x1 = SW_X - 5.4, CAR_X1
    y0, y1 = SW_Y - CAR_HALF_Y, SW_Y + CAR_HALF_Y
    shelf = box(x0, x1, y0, y1, zb - 1.2, zb)
    shelf = shelf.cut(box(SW_X - 2.25, SW_X + 2.25, y0 - 1, SW_Y + 2.25, CAR_Z0 - 1, zb + 1))   # knob slot (open -y)
    ends = union_all([box(x0, SW_X - 4.0 - SW_CLR, y0, y1, CAR_Z0, CAR_Z1),
                      box(SW_X + 4.0 + SW_CLR, x1, y0, y1, CAR_Z0, CAR_Z1)])
    bridge = box(x0, x1, SW_Y - 2.4, SW_Y + 2.4, zt + SW_ZCLR, zt + SW_ZCLR + 1.2)
    stop = box(SW_X - 4.0 - SW_CLR - 0.01, SW_X + 4.0 + SW_CLR + 0.01, SW_Y + 4.0 + SW_CLR, y1, zb - 0.01, zb + 3.0)
    # tail out to the plug's -x face (U frame) -> captured by the sleeve wall
    tx0 = PLUG_X0 + 0.10
    tail = union_all([box(tx0, x0 + 0.01, y0, y0 + 1.0, CAR_Z0, CAR_Z1),
                      box(tx0, x0 + 0.01, y1 - 1.0, y1, CAR_Z0, CAR_Z1),
                      box(tx0, tx0 + 1.2, y0, y1, CAR_Z0, CAR_Z1)])
    return union_all([shelf, ends, bridge, stop, tail])


# ======================================================================== caps
def lens_cap(c, at_origin=True):
    d = CAP_POCKET_D - 2 * c
    cap = cyl(0, 0, 0, CAP_T, d)
    cap = cap.cut(box(d / 2 - 0.8, d / 2 + 1, -0.6, 0.6, -1, CAP_T + 1))     # through pry notch 1.2 x 0.8
    if not at_origin:
        cap = cap.translate((CX, CAM_Y, Z_FRONT - CAP_T))
    return cap


def usb_cover(c, at_origin=True):
    w, h = OVM_W - 2 * c, OVM_H - 2 * c
    cov = rrect(-w / 2, w / 2, -h / 2, h / 2, 0, COVER_T, OVM_R - c)
    cov = cov.cut(box(w / 2 - 0.8, w / 2 + 1, -0.6, 0.6, -1, COVER_T + 1))   # through pry notch
    if not at_origin:
        cov = cov.translate((CX, USB_Y, Z_FRONT - COVER_T))
    return cov


def ph_cage():
    """Plug zone P1: two ribs (x sides), a stop bar under the header body and a back bridge above the housing.
    Open toward +y so the mated pair slides in along -y at the bench (holder not yet fitted)."""
    y0, y1 = PH_YC - PH_D / 2 - 0.25 + 0.0, PH_YC + PH_D / 2 + 0.05          # 3.05-0.25 .. 7.6
    ztop = PH_Z0 + PH_L + 1.5
    xa0 = PH_XC - PH_W / 2 - PH_CLR - RIB_T
    xb0 = PH_XC + PH_W / 2 + PH_CLR
    ribs = [box(xa0, xa0 + RIB_T, y0, y1, 1.9, ztop), box(xb0, xb0 + RIB_T, y0, y1, 1.9, ztop)]
    xi0, xi1 = xa0 + RIB_T - 0.01, xb0 + 0.01
    bar = box(xi0, xi1, y0, PH_YC - 0.8, PH_Z0 + PH_TAIL - 1.0 - 0.4, PH_Z0 + PH_TAIL - 0.4)    # 0.4 under the body
    bridge = box(xi0, xi1, y0, PH_YC - 0.8, PH_Z0 + PH_L + 0.5, ztop)                          # 0.5 over the housing
    return union_all(ribs + [bar, bridge])


# ======================================================================== coupon
def coupon():
    """Fit coupon = exact crops of the production insert (front end) and plug (switch area),
    joined by a bar. Tests: radar pocket+window, button flexure+tact pocket, USB collar +
    overmold pocket + cover, camera head pocket + lens opening + cap, switch carrier pocket +
    knob hole + dimple."""
    yc = max(CAM_Y1 + CAM_POCKET_CLR + 0.8 + 0.9, CAM_Y + CAP_POCKET_D / 2 + 0.9)   # >= 0.8 strip past every pocket
    assert yc < FPCW_Y0 - 0.3
    top = insert().intersect(box(0, 30, 0, yc, 132.0, 141.0))
    low = plug().intersect(box(0, 30, SW_Y - 7.8, SW_Y + 7.8, -1, POCKET_Z1 + ROOF_T + 0.01))
    low = low.translate((0, yc + 4.0 - (SW_Y - 7.8), 132.0))
    bar = box(12.0, 17.0, yc - 1.5, yc + 5.0, 132.0, 134.0)
    riser = box(12.0, 17.0, yc - 1.5, yc, 132.0, Z_RIM + 0.5)      # ties the bar into the faceplate
    return top.union(bar).union(riser).union(low)


# ======================================================================== tray
def _lay(part, x, y, z=3.0):
    bb = part.val().BoundingBox() if hasattr(part, 'val') else part.BoundingBox()
    return part.translate((x - bb.xmin, y - bb.ymin, z - bb.zmin))


def _posts(part, n=3, d=1.0, z0=0.0):
    """Snap-off posts from the frame (z0..2) to the lowest face of a laid part."""
    bb = part.val().BoundingBox()
    sl = part.intersect(box(bb.xmin - 1, bb.xmax + 1, bb.ymin - 1, bb.ymax + 1, bb.zmin - 0.01, bb.zmin + 0.05))
    faces = sl.faces('<Z').vals()
    faces = sorted(faces, key=lambda f: -f.Area())
    pts = []
    for f in faces:
        c = f.Center()
        if all((c.x - q[0]) ** 2 + (c.y - q[1]) ** 2 > 16 for q in pts):
            pts.append((c.x, c.y))
        if len(pts) >= n:
            break
    return [cyl(px, py, z0 + 1.0, bb.zmin + 0.05, d) for (px, py) in pts], pts


def tray_items():
    """(name, laid solid) for every small part, already placed on the tray."""
    items = []
    x = 4.0
    # row 1: caps and covers (flat)
    for v, c in CAP_VARIANTS.items():
        items.append((f'lens_cap_{v}', _lay(lens_cap(c), x, 4.0))); x += 13.0
    for v, c in CAP_VARIANTS.items():
        items.append((f'usb_cover_{v}', _lay(usb_cover(c), x, 4.0))); x += 15.5
    # row 2: switch carriers (all variants)
    x = 4.0
    for h in SW_H_VARIANTS:
        items.append((f'carrier_H{h:g}', _lay(carrier(h), x, 16.0))); x += 15.0
    # row 3: keepers
    items.append(('keeper_a', _lay(keeper_a(), 4.0, 32.0)))
    items.append(('keeper_b', _lay(keeper_b(), 32.0, 32.0)))
    items.append(('keeper_c', _lay(keeper_c(), 60.0, 32.0)))
    return items


def tray():
    items = tray_items()
    allbb = [p.val().BoundingBox() for _, p in items]
    X1 = max(b.xmax for b in allbb) + 4.0
    Y1 = max(b.ymax for b in allbb) + 4.0
    frame = union_all([box(0, X1, 0, 2, 0, 2), box(0, X1, Y1 - 2, Y1, 0, 2), box(0, 2, 0, Y1, 0, 2), box(X1 - 2, X1, 0, Y1, 0, 2)])
    t = frame
    allpts = []
    for name, p in items:
        posts, pts = _posts(p)
        allpts += pts
        t = union_all([t, p] + posts)
    # one bar per cluster of post x positions (no slivers between neighbouring bars)
    xs = sorted(x for x, _ in allpts)
    clusters = [[xs[0]]]
    for x in xs[1:]:
        if x - clusters[-1][-1] < 3.0:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    for c in clusters:
        t = t.union(box(min(c) - 1.0, max(c) + 1.0, 0, Y1, 0, 1.0 + 0.01))
    return t
