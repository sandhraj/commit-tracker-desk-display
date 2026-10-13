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
GRID_WALL = 1.2
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

s, c = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
face_top = (-FACE_L * s, LIP + FACE_L * c)
DECK_Y = PLINTH_Y
grille_cy = GRILLE_Y0 + GRILLE_H / 2
grid_w, grid_h = COLS * PITCH, ROWS * PITCH

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

inner = profile_solid(-WALL, -W / 2 + WALL, W - 2 * WALL)
# keep the wall an even thickness through the long sweep
inner = inner.edges("|X").edges(cq.selectors.BoxSelector((-W, PLINTH_Y - WALL - 2, foot[0] - 10), (W, PLINTH_Y - WALL + 2, foot[0] + 4))).fillet(R_SWEEP - WALL)
foot_len = DEPTH - UNDER - 2 * WALL
inner = inner.union(cq.Workplane("XY").box(W - 2 * WALL, 2 * WALL + 2, foot_len)
                    .translate((0, 0, -UNDER - WALL - foot_len / 2)))
body = body.cut(inner)

def on_face(wp):
    return wp.rotate((0, 0, 0), (1, 0, 0), -TILT).translate((0, LIP, 0))

pocket = on_face(cq.Workplane("XY", origin=(0, 0, -(GRILLE_T + DIFF_T)))
                 .center(0, grille_cy).rect(GRILLE_W + 0.4, GRILLE_H + 0.4)
                 .extrude(GRILLE_T + DIFF_T + 6).edges("|Z").fillet(GRILLE_R))
window = on_face(cq.Workplane("XY", origin=(0, 0, -WALL - 4))
                 .center(0, grille_cy).rect(grid_w + 4, grid_h + 4)
                 .extrude(WALL + 5).edges("|Z").fillet(1.5))
body = body.cut(pocket).cut(window)

sweep_end = foot[0] - R_SWEEP * math.tan(math.radians((90 - FLANK) / 2))
KNOB = (grid_w / 2 - PITCH / 2, (sweep_end + (-DEPTH + R_BEND)) / 2)  # in line with the 'today' column, centred on the plinth deck
body = body.cut(cq.Workplane("XZ", origin=(KNOB[0], DECK_Y + 5, KNOB[1])).circle(3.6).extrude(15))
usb = cq.Workplane("XY").box(12.5, 6.5, WALL + 6).translate((W / 2 - min(40, W / 4), 18, -DEPTH))
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
grid = (cq.Workplane("XY", origin=(0, 0, gz0 - GRID_D)).center(0, grille_cy)
        .rect(grid_w + GRID_WALL, grid_h + GRID_WALL).extrude(GRID_D))
grid = grid.cut(cq.Workplane("XY", origin=(0, 0, gz0 - GRID_D - 1)).pushPoints(cells)
                .rect(PITCH - GRID_WALL, PITCH - GRID_WALL).extrude(GRID_D + 2))
grid = on_face(grid)
panel = on_face(cq.Workplane("XY", origin=(0, 0, gz0 - GRID_D - PANEL_T))
                .center(0, grille_cy - PITCH / 2).rect(grid_w, grid_h + PITCH).extrude(PANEL_T))

# base plate: inset 2 mm all round so a dark shadow line runs under the body,
# with a locating step that fits inside the shell walls
base_len = DEPTH - UNDER - 2 * GAP
base = (cq.Workplane("XY").box(W - 2 * GAP, GAP, base_len)
        .translate((0, GAP / 2, -UNDER - GAP - base_len / 2)).edges("|Y").fillet(R_EDGE))
step = (cq.Workplane("XY").box(W - 2 * WALL - 0.6, 2.0, foot_len - 0.6)
        .cut(cq.Workplane("XY").box(W - 2 * WALL - 4.6, 3.0, foot_len - 4.6)))
base = base.union(step.translate((0, GAP + 1.0, -UNDER - WALL - foot_len / 2)))
knob = (cq.Workplane("XZ", origin=(KNOB[0], DECK_Y + 9, KNOB[1])).circle(8).extrude(9)
        .faces(">Y").edges().chamfer(0.6))

parts = dict(body=body, grille=grille, diffuser=diffuser, grid=grid, panel=panel, base=base, knob=knob)
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
