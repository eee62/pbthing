"""Purchased parts placed in the sleeve frame. XIAO from the supplied STEP; the rest from
datasheets or [GUESS] envelopes (see params.py)."""
import os
import cadquery as cq
from params import *  # noqa
from geo import box, cyl, union_all
from step_tools import load_step_solids

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEP = os.path.join(ROOT, 'inputs', 'XIAO_ESP32S3_Sense.step')
EXCLUDE = ('MicroSD v2', 'Camer Module')     # card (not used) and stock camera (replaced)


def _xiao_tf(s):
    s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), -90)
    return s.translate(cq.Vector(CX + ZS_CENTRE, Y_S0, Z_PT - XS_PCB_TOP + XIAO_DZ))


def xiao_parts():
    """[(name, cq.Solid)] of the XIAO + Sense expansion board in the sleeve frame."""
    res = []
    for path, s in load_step_solids(STEP):
        if any(e in path for e in EXCLUDE):
            continue
        name = path.split('/')[-1] if '/' in path else path
        res.append((name, _xiao_tf(s)))
    return res


def xiao_hull_boxes():
    """Bounding boxes of the main sub-assemblies (used for the swing-in clearance check)."""
    groups = {}
    for path, s in load_step_solids(STEP):
        if any(e in path for e in EXCLUDE):
            continue
        key = path.split('/')[1] if path.count('/') >= 1 else path
        groups.setdefault(key, []).append(_xiao_tf(s))
    return groups


def radar():
    pcb = box(RAD_X0, RAD_X0 + RAD_W, RAD_Y0, RAD_Y0 + RAD_W, RAD_Z0, RAD_Z1)
    m = 1.0   # [GUESS] keep-out margin of the front components from the board edge
    front = box(RAD_X0 + m, RAD_X0 + RAD_W - m, RAD_Y0 + m, RAD_Y0 + RAD_W - 2.6,
                RAD_Z1, RAD_Z1 + RAD_FRONT_H)
    mb = 1.5  # [GUESS] keep-out margin of the back components at the 3 support corners
    back = box(RAD_X0 + mb, RAD_X0 + RAD_W - mb, RAD_Y0 + mb, RAD_Y0 + RAD_W - 2.0,   # 2.0 at the J2 edge
               RAD_Z0 - RAD_BACK_H, RAD_Z0)
    joints = [cyl(x, radar_pin_y(), RAD_Z0 - 1.0, RAD_Z0, 1.6) for x in radar_pin_xs()]
    return union_all([pcb, front, back] + joints)


def radar_pin_xs():
    return [RAD_PIN_X0 + i * RAD_PIN_PITCH for i in range(5)]


def radar_pin_y():
    return RAD_Y0 + RAD_W - RAD_PIN_EDGE


def tact():
    b = box(BTN_X - 3, BTN_X + 3, BTN_Y - 3, BTN_Y + 3, TACT_Z0, TACT_Z0 + TACT_BODY_H)
    a = cyl(BTN_X, BTN_Y, TACT_Z0 + TACT_BODY_H, TACT_Z1, TACT_ACT_D)
    legs = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0 = BTN_X + sx * 2.95 if sx > 0 else BTN_X - 3.65
            legs.append(box(x0, x0 + 0.7, BTN_Y + sy * 2.25 - 0.15, BTN_Y + sy * 2.25 + 0.15,
                            TACT_Z0 - TACT_LEG_L, TACT_Z0 + 0.8))
    return union_all([b, a] + legs)


def tact_leg_points():
    return [(BTN_X + sx * 3.3, BTN_Y + sy * 2.25) for sx in (-1, 1) for sy in (-1, 1)]


def camera():
    """OV5640 module: base PCB, square lens-holder block, Ø3.8 barrel, and the heatsink glued behind the base.
    Axis +z (lens toward the front face). Total lens-top to heatsink-bottom = 5.6 + 0.1 pad + 6.0 heatsink = 11.7 mm."""
    x0, x1 = CX - CAM_W / 2, CX + CAM_W / 2
    base = box(x0, x1, CAM_Y0, CAM_Y1, CAM_Z0, CAM_Z0 + CAM_BASE_T)
    body = box(x0, x1, CAM_Y0, CAM_Y1, CAM_Z0 + CAM_BASE_T, CAM_Z0 + CAM_BASE_T + CAM_BODY_H)
    bar = cyl(CX, CAM_Y, CAM_TOP - CAM_BARREL_H, CAM_TOP, CAM_BARREL_D)
    hx0, hx1, hy0, hy1 = CX - CAM_HS_W / 2, CX + CAM_HS_W / 2, CAM_Y - CAM_HS_L / 2, CAM_Y + CAM_HS_L / 2     # centred on the base
    hs = box(hx0, hx1, hy0, hy1, CAM_ZH0, CAM_ZH0 + CAM_HS_H)                                  # heatsink 7.0 x 7.1 x 6.0
    pad = box(hx0, hx1, hy0, hy1, CAM_ZH0 + CAM_HS_H, CAM_Z0 + 0.01)                           # 0.1 mm pad (+0.01 overlap into the base)
    return union_all([base, body, bar, hs, pad])


def main_switch(h=SW_H_DEFAULT, pressed=0.0):
    """PB-22E08 latching switch. h = body + knob height (pins excluded).
    pressed = knob travel into the body (0 released, 1.5 latched, 2.5 full)."""
    k = h - SW_BODY_H
    zb = SW_RECESS_OUT + k                     # body bottom (knob side)
    body = box(SW_X - 4, SW_X + 4, SW_Y - 4, SW_Y + 4, zb, zb + SW_BODY_H)
    tip = SW_RECESS_OUT + pressed
    knob = box(SW_X - SW_KNOB / 2, SW_X + SW_KNOB / 2, SW_Y - SW_KNOB / 2, SW_Y + SW_KNOB / 2,
               tip, max(zb + 0.01, tip + 0.2))   # knob slides into the body when pressed
    pins = []
    for i in (-1, 0, 1):
        for sy in (-1, 1):
            px, py = SW_X + i * SW_PIN_PITCH, SW_Y + sy * SW_ROW / 2
            pins.append(box(px - 0.3, px + 0.3, py - 0.15, py + 0.15,
                            zb + SW_BODY_H - 0.01, zb + SW_BODY_H + SW_PIN_L))
    return union_all([body, knob] + pins)


def switch_pin_xy():
    return {n: (SW_X + i * SW_PIN_PITCH, SW_Y + sy * SW_ROW / 2)
            for n, (i, sy) in {1: (-1, -1), 2: (0, -1), 3: (1, -1),
                               4: (-1, 1), 5: (0, 1), 6: (1, 1)}.items()}


def holder():
    x0 = CX - HOLDER_X / 2
    y0 = CY - HOLDER_Y / 2
    return box(x0, x0 + HOLDER_X, y0, y0 + HOLDER_Y, HOLDER_Z0, HOLDER_Z0 + HOLDER_Z)


def antenna():
    return box(CX - ANT_W / 2, CX + ANT_W / 2, ANT_Y0, ANT_Y0 + ANT_T, ANT_Z0, ANT_Z0 + ANT_L)






def sleeve():
    """Exact B-rep reconstruction of the supplied sleeve (checked against the STL in verify)."""
    from geo import rrect
    outer = rrect(0, SLV_X, 0, SLV_Y, 0, SLV_Z, 7.0)
    cav = rrect(CAV_X0, CAV_X1, CAV_Y0, CAV_Y1, -1, LIP_Z0, CAV_R)
    bore = rrect(CAV_X0, CAV_X1, CAV_Y0, CAV_Y1, LIP_Z1, SLV_Z + 1, CAV_R)
    lip = rrect(LIP_X0, LIP_X1, LIP_Y0, LIP_Y1, LIP_Z0 - 0.5, LIP_Z1 + 0.5, LIP_R)
    return outer.cut(cav).cut(bore).cut(lip)
