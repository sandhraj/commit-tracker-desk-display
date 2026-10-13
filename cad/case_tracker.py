"""Commit Tracker Desk Display: parametric case (CadQuery).

Side profile, front to back: the screen leans back 28 deg from vertical
(62 deg to the desk) up to a short flat top; a back flank at 30 deg sweeps
down through a 60 mm curve into a 35 mm plinth. The front rolls under,
lifted 10 mm, so the footprint starts 22 mm behind the face, and the body
sits on a base plate inset 2 mm (shadow gap). Every fold uses one 8 mm
radius; every side edge one 1.5 mm radius.

The screen is a white grille (rounded square windows, plain border) over a
diffuser, a 10 mm egg-crate grid and WS2812B panels at 10 mm pitch.

Usage:  COLS=56 python case_tracker.py out_dir   (year: 53 weeks + 3, 604 mm wide)
        COLS=16 python case_tracker.py out_dir   (quarter: 13 weeks + 3, 204 mm wide)

COLS is the number of LED columns the panels provide (8 per 8x8 panel, 32 per
8x32). Every column is visible; how weeks, markers and spare columns map onto
them is decided in firmware.

Coordinates: X = width, Y = up, Z = towards the viewer (mm).
"""
import math, json, sys, os
import cadquery as cq

COLS = int(os.environ.get('COLS', '56'))    # 56 = year (8x32 + 3 x 8x8), 16 = quarter (2 x 8x8)
ROWS, PITCH = 7, 10.0
WIN, WIN_R = 8.6, 1.5
GRID_WALL = 1.6                # wider than the 1.4 mm grille web so a small shift never opens a light path
GRID_MARGIN = 13.0             # grille border beside the squares
BEZEL = 9.0                    # body border beside the grille
W = COLS * PITCH + 2 * GRID_MARGIN + 2 * BEZEL   # 604 mm for 56 columns, 204 mm for 16
WALL = 3.0
LIP = 6.0
TILT = 28.0                    # screen lean-back from vertical (62 deg to the desk)
FACE_L = 126.0                 # screen face length up to the top
FLANK = 30.0                   # back flank angle from vertical
TOP_FLAT = 16.0                # blunted peak: short flat top
PLINTH_Y = 35.0                # plinth height
R_SWEEP = 60.0                 # long concave sweep from the flank into the plinth
DEPTH = 215.0
GRILLE_W, GRILLE_H, GRILLE_R = W - 2 * BEZEL, 102.0, 3.0
R_BEND = 8.0                   # one bend radius for every fold of the profile
R_EDGE = 1.5                   # one crisp radius for every edge of the flat sides
GAP = 2.0                      # shadow gap: body floats on a recessed base plate
GRILLE_T, DIFF_T = 2.0, 0.5
GRILLE_Y0 = 12.0
LIFT = 10.0                    # front rolls under: underside height at the face
UNDER = 22.0                   # footprint starts this far back from the face
GRID_D, PANEL_T = 10.0, 2.0
# Fits and mounting (all editable; re-check the interference test after changing)
FIT = 0.15                     # sliding-fit clearance per side for FDM parts
LIP_W = 2.0                    # grid rim that seats the panels, so LED centres sit in the cells
PAD_T = 2.0                    # doubler inside the face wall around the opening
BOSS_R = 3.0                   # M2.5 self-tapping posts carrying the backer
FOAM_T = 1.0                   # foam sheet behind the panels (compresses to about 0.5)
BACKER_T = 3.0
CAP_LIP_W, CAP_LIP_D = 1.5, 3.0   # locating lip on the removable side cap
ENC_HOLE_D = 7.4               # EC11 M7 bushing
ENC_BUSH_ABOVE = 4.0           # bushing thread above the deck (7 mm thread, 3 mm wall, nut inside)
ENC_SHAFT = 10.0               # shaft length above the bushing: check your encoder
KNOB_GAP, KNOB_R = 0.8, 10.0
USB_W, USB_H, USB_Y = 14.0, 9.0, 9.0   # cable overmould slot; set from the real plug
ESP_L, ESP_W, ESP_PCB, ESP_STANDOFF = 52.0, 28.5, 1.6, 4.0   # devkit outline
BASE_POST_Z = (-205.0, -150.0, -95.0)  # base screw posts hang from the deck / flank

s, c = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
face_top = (-FACE_L * s, LIP + FACE_L * c)
DECK_Y = PLINTH_Y
grille_cy = GRILLE_Y0 + GRILLE_H / 2
grid_w, grid_h = COLS * PITCH, ROWS * PITCH
PANEL_H = (ROWS + 1) * PITCH   # 8 LED rows; row 8 sits behind a solid part of the grid
grid_cy = grille_cy - PITCH / 2
GRID_OUT_W = grid_w + 2 * LIP_W + 2 * FIT
GRID_OUT_H = PANEL_H + 2 * LIP_W + 2 * FIT

top_back = (face_top[0] - TOP_FLAT, face_top[1])
foot = (top_back[0] - (top_back[1] - PLINTH_Y) * math.tan(math.radians(FLANK)), PLINTH_Y)
face_bottom = (-(LIFT - LIP) * math.tan(math.radians(TILT)), LIFT)
prof = [face_bottom, face_top, top_back, foot, (-DEPTH, PLINTH_Y), (-DEPTH, 0), (-UNDER, 0), (-UNDER, LIFT)]

def profile_solid(offset=0.0, x0=-W / 2, width=W):
    wp = cq.Workplane("YZ", origin=(x0, 0, 0)).polyline([(y, z) for z, y in prof]).close()
    if offset:
        wp = wp.offset2D(offset, "intersection")
    return wp.extrude(width)

body = profile_solid()
def edge_at(zy, r):
    global body
    z, y = zy
    body = body.edges("|X").edges(cq.selectors.BoxSelector((-W, y - 1, z - 1), (W, y + 1, z + 1))).fillet(r)
# Braun-style detailing: the profile reads as one folded sheet, so every fold
# gets the same radius; the flat side faces meet it with one small, crisp radius.
edge_at(foot, R_SWEEP)
for v in (face_top, top_back, (-DEPTH, PLINTH_Y), face_bottom):
    edge_at(v, R_BEND)
edge_at((-UNDER, LIFT), 4)     # inside corner of the undercut
body = body.faces("<X or >X").edges().fillet(R_EDGE)
# shadow gap: trim the bottom so the shell sits on an inset base plate
body = body.cut(cq.Workplane("XY").box(W + 10, GAP * 2, DEPTH + 10).translate((0, 0, -DEPTH / 2)))

shell_outer = body             # outer skin before hollowing, used to trim posts flush
inner = profile_solid(-WALL, -W / 2 + WALL, W - 2 * WALL)
# keep the wall an even thickness through the long sweep
inner = inner.edges("|X").edges(cq.selectors.BoxSelector((-W, PLINTH_Y - WALL - 2, foot[0] - 10), (W, PLINTH_Y - WALL + 2, foot[0] + 4))).fillet(R_SWEEP - WALL)
foot_len = DEPTH - UNDER - 2 * WALL
inner = inner.union(cq.Workplane("XY").box(W - 2 * WALL, 2 * WALL + 2, foot_len)
                    .translate((0, 0, -UNDER - WALL - foot_len / 2)))
body = body.cut(inner)

def on_face(wp):
    return wp.rotate((0, 0, 0), (1, 0, 0), -TILT).translate((0, LIP, 0))

# --- display mounting (face-local coordinates: z = 0 on the outer face, negative behind it)
# A doubler pad thickens the inside of the face wall around the opening. M2.5 posts rise
# from it and carry a black backer plate that clamps foam, panels, grid and diffuser forward.
ledge_z = -WALL - PAD_T
stack_back = -GRILLE_T - DIFF_T - GRID_D - PANEL_T     # panel back face
back_z = stack_back - FOAM_T                           # backer front face / post ends
pad = on_face(cq.Workplane("XY", origin=(0, 0, ledge_z)).center(0, grille_cy)
              .rect(GRILLE_W + 2 * FIT, GRILLE_H + 2 * FIT).extrude(PAD_T + 0.2))
body = body.union(pad)

xe = GRID_OUT_W / 2 + FIT + 5.2                        # post column beside the opening
n_top = max(2, int(math.ceil(grid_w / 200.0)) + 1)
top_y = grid_cy + GRID_OUT_H / 2 + FIT + 6.5           # on the ledge above the opening
posts = [(sx * xe, grid_cy + dy) for sx in (-1, 1) for dy in (-25.0, 25.0)]
posts += [(-xe + i * 2 * xe / (n_top - 1), top_y) for i in range(n_top)]
boss = (cq.Workplane("XY", origin=(0, 0, ledge_z + 0.2)).pushPoints(posts)
        .circle(BOSS_R).extrude(back_z - (ledge_z + 0.2)))
boss = boss.cut(cq.Workplane("XY", origin=(0, 0, back_z)).pushPoints(posts).circle(1.05).extrude(8.0))
body = body.union(on_face(boss))

# --- base screw posts: hang from the deck and back flank, trimmed flush to the outer skin
bp_pts = [(sx * (W / 2 - 12.0), z) for sx in (-1, 1) for z in BASE_POST_Z]
bpost = cq.Workplane("XZ", origin=(0, GAP, 0)).pushPoints(bp_pts).circle(3.0).extrude(-140.0)
bpost = shell_outer.intersect(bpost)
bpost = bpost.cut(cq.Workplane("XZ", origin=(0, GAP, 0)).pushPoints(bp_pts).circle(1.05).extrude(-10.0))
body = body.union(bpost)

pocket = on_face(cq.Workplane("XY", origin=(0, 0, -(GRILLE_T + DIFF_T)))
                 .center(0, grille_cy).rect(GRILLE_W + 2 * FIT, GRILLE_H + 2 * FIT)
                 .extrude(GRILLE_T + DIFF_T + 6).edges("|Z").fillet(GRILLE_R))
# opening through the wall and pad, sized to the grid plate plus a sliding fit
window = on_face(cq.Workplane("XY", origin=(0, 0, ledge_z - 2))
                 .center(0, grid_cy).rect(GRID_OUT_W + 2 * FIT, GRID_OUT_H + 2 * FIT)
                 .extrude(-ledge_z + 3).edges("|Z").fillet(1.5))
body = body.cut(pocket).cut(window)

sweep_end = foot[0] - R_SWEEP * math.tan(math.radians((90 - FLANK) / 2))
KNOB = (grid_w / 2 - PITCH / 2, (sweep_end + (-DEPTH + R_BEND)) / 2)  # in line with the 'today' column, centred on the plinth deck
body = body.cut(cq.Workplane("XZ", origin=(KNOB[0], DECK_Y + 5, KNOB[1])).circle(ENC_HOLE_D / 2).extrude(15))
# small notch for the encoder's anti-rotation lug
body = body.cut(cq.Workplane("XZ", origin=(KNOB[0], DECK_Y + 5, KNOB[1] + ENC_HOLE_D / 2 + 0.2)).circle(1.0).extrude(15))
# USB slot at the opposite end of the back wall from the knob
USB_X = -(W / 2 - min(40, W / 4))
usb = cq.Workplane("XY").box(USB_W, USB_H, WALL + 6).translate((USB_X, USB_Y, -DEPTH))
body = body.cut(usb.edges("|Z").fillet(2.5))

cells = [(-grid_w / 2 + PITCH * (i + .5), grille_cy + grid_h / 2 - PITCH * (j + .5))
         for i in range(COLS) for j in range(ROWS)]

grille = (cq.Workplane("XY", origin=(0, 0, -GRILLE_T)).center(0, grille_cy)
          .rect(GRILLE_W, GRILLE_H).extrude(GRILLE_T).edges("|Z").fillet(GRILLE_R))
grille = grille.cut(cq.Workplane("XY", origin=(0, 0, -GRILLE_T - 1)).pushPoints(cells)
                    .rect(WIN, WIN).extrude(GRILLE_T + 2).edges("|Z").fillet(WIN_R))
grille = on_face(grille)

diffuser = on_face(cq.Workplane("XY", origin=(0, 0, -GRILLE_T - DIFF_T)).center(0, grille_cy)
                   .rect(GRILLE_W, GRILLE_H).extrude(DIFF_T).edges("|Z").fillet(GRILLE_R))
gz0 = -GRILLE_T - DIFF_T
grid_total = GRID_D + PANEL_T
grid_z0 = gz0 - grid_total
grid = (cq.Workplane("XY", origin=(0, 0, grid_z0)).center(0, grid_cy)
        .rect(GRID_OUT_W, GRID_OUT_H).extrude(grid_total).edges("|Z").fillet(1.2))
grid = grid.cut(cq.Workplane("XY", origin=(0, 0, grid_z0 - 1)).pushPoints(cells)
                .rect(PITCH - GRID_WALL, PITCH - GRID_WALL).extrude(grid_total + 2))
# seat on the back for the flexible panels (locates them to +/- FIT)
grid = grid.cut(cq.Workplane("XY", origin=(0, 0, grid_z0 - 1)).center(0, grid_cy)
                .rect(grid_w + 2 * FIT, PANEL_H + 2 * FIT).extrude(PANEL_T + 1))
grid = on_face(grid)
panel = on_face(cq.Workplane("XY", origin=(0, 0, grid_z0))
                .center(0, grid_cy).rect(grid_w, PANEL_H).extrude(PANEL_T))

# backer: clamps foam + panels + grid to the diffuser; stops short of the bottom edge so
# the panel leads exit freely at the hidden row
bk_x = xe + 3.5
bk_y1 = top_y + 3.5
bk_y0 = grid_cy - PANEL_H / 2 + 8.0
backer = (cq.Workplane("XY", origin=(0, 0, back_z - BACKER_T)).center(0, (bk_y0 + bk_y1) / 2)
          .rect(2 * bk_x, bk_y1 - bk_y0).extrude(BACKER_T).edges("|Z").fillet(3.0))
backer = backer.cut(cq.Workplane("XY", origin=(0, 0, back_z - BACKER_T - 1)).pushPoints(posts)
                    .circle(1.4).extrude(BACKER_T + 2))
backer = on_face(backer)

# base plate: inset 2 mm all round so a dark shadow line runs under the body,
# with a locating step that fits inside the shell walls
base_len = DEPTH - UNDER - 2 * GAP
base = (cq.Workplane("XY").box(W - 2 * GAP, GAP, base_len)
        .translate((0, GAP / 2, -UNDER - GAP - base_len / 2)).edges("|Y").fillet(R_EDGE))
step = (cq.Workplane("XY").box(W - 2 * WALL - 0.6, 2.0, foot_len - 0.6)
        .cut(cq.Workplane("XY").box(W - 2 * WALL - 4.6, 3.0, foot_len - 4.6)))
# leave the +X side of the ring open so the side cap's lip can slide in
step = step.cut(cq.Workplane("XY").box(10, 10, foot_len).translate((W / 2 - 6.5 + 5, 0, 0)))
base = base.union(step.translate((0, GAP + 1.0, -UNDER - WALL - foot_len / 2)))
base = base.cut(cq.Workplane("XZ", origin=(0, GAP + 1.0, 0)).pushPoints(bp_pts).circle(1.4).extrude(GAP + 3.0))
# ESP32 devkit cradle: four corner pillars with outer walls, USB end towards the back wall
esp_zc = -DEPTH + WALL + 0.5 + ESP_L / 2
for sx in (-1, 1):
    for sz in (-1, 1):
        pz = esp_zc + sz * (ESP_L / 2 - 5.0)
        px = USB_X + sx * (ESP_W / 2 - 1.0)
        wx = USB_X + sx * (ESP_W / 2 + FIT + 1.0)
        wall_h = ESP_STANDOFF + ESP_PCB + 2.0
        base = base.union(cq.Workplane("XY").box(4.0, ESP_STANDOFF, 6.0).translate((px, GAP + ESP_STANDOFF / 2, pz)))
        base = base.union(cq.Workplane("XY").box(2.0, wall_h, 6.0).translate((wx, GAP + wall_h / 2, pz)))

# knob: raised off the deck, counterbore over the bushing, D-bore for the shaft
knob_bottom = DECK_Y + KNOB_GAP
bush_top = DECK_Y + ENC_BUSH_ABOVE
bore_depth = bush_top + ENC_SHAFT - knob_bottom + 0.5
cbore_depth = bush_top - knob_bottom + 0.5
knob_h = bore_depth + 2.5
knob = (cq.Workplane("XZ", origin=(KNOB[0], knob_bottom + knob_h, KNOB[1])).circle(KNOB_R).extrude(knob_h)
        .faces(">Y").edges().chamfer(0.6))
knob = knob.cut(cq.Workplane("XZ", origin=(KNOB[0], knob_bottom + cbore_depth, KNOB[1]))
                .circle(4.75).extrude(cbore_depth + 0.01))
bore = cq.Workplane("XZ", origin=(KNOB[0], knob_bottom + bore_depth, KNOB[1])).circle(3.1).extrude(bore_depth + 0.01)
key = cq.Workplane("XY").box(6.4, bore_depth, 0.75).translate((KNOB[0], knob_bottom + bore_depth / 2, KNOB[1] + 2.725))
knob = knob.cut(bore.cut(key))

# removable +X side cap, so the shell prints on its side (X up) with no supports and
# smooth folds; a lip locates it in the opening. Bond with CA or solvent weld.
x_cap = W / 2 - WALL
split = cq.Workplane("XY").box(WALL + 2, 400, 400).translate((x_cap + (WALL + 2) / 2, 60, -110))
sidecap = body.intersect(split)
body = body.cut(split)
slab = inner.intersect(cq.Workplane("XY").box(CAP_LIP_D, 400, 400).translate((x_cap - CAP_LIP_D / 2, 60, -110)))
endwire = slab.faces(">X").val().outerWire()
lip_face = cq.Face.makeFromWires(endwire.offset2D(-FIT)[0], [endwire.offset2D(-FIT - CAP_LIP_W)[0]])
cap_lip = cq.Workplane("XY").add(cq.Solid.extrudeLinear(lip_face, cq.Vector(-CAP_LIP_D, 0, 0)))
# the cavity profile runs below the shell's bottom plane; keep the lip above it
cap_lip = cap_lip.intersect(cq.Workplane("XY").box(W, 400, 400).translate((0, GAP + 200, -110)))
sidecap = sidecap.union(cap_lip)

parts = dict(body=body, sidecap=sidecap, grille=grille, diffuser=diffuser, grid=grid, panel=panel,
             backer=backer, base=base, knob=knob)
out = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(out, exist_ok=True)
for n, wp in parts.items():
    cq.exporters.export(wp, f"{out}/{n}.stl", tolerance=0.05, angularTolerance=0.2)
asm = cq.Assembly()
for n, wp in parts.items():
    asm.add(wp, name=n)
asm.export(f"{out}/commit-tracker-{COLS}col.step")
meta = dict(W=W, LIP=LIP, TILT=TILT, FACE_L=FACE_L, DEPTH=DEPTH, face_top=face_top, DECK_Y=DECK_Y,
            GRILLE=[GRILLE_W, GRILLE_H], GRILLE_CY=grille_cy, KNOB=KNOB)
json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)
print(json.dumps(meta))
