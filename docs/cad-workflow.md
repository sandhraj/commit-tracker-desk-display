# CAD workflow (CadQuery / OpenCASCADE)

The case is code, not a drawing. `cad/case_tracker.py` is a [CadQuery](https://github.com/CadQuery/cadquery) script. CadQuery is a Python layer over the OpenCASCADE (OCCT) solid-modelling kernel, installed through the `cadquery-ocp` wheel, so no separate CAD install is needed.

## Setup

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r cad/requirements.txt     # cadquery 2.8, OCP 7.9, numpy/scipy, vtk
```

Tested with Python 3.13 on Linux. The first install pulls several hundred MB of wheels.

## Edit, build, inspect

1. Change a parameter near the top of `cad/case_tracker.py` (tilt, bend radius, window size, depth, bezel).
2. Build: `COLS=16 python cad/case_tracker.py /tmp/out` (about a minute; `COLS=56` for the full year).
3. Open `body.stl` and the other STLs in a slicer or mesh viewer, or the `.step` assembly in FreeCAD to check dimensions and wall thickness.
4. The script prints the key dimensions as JSON (`W` must be 604.0 for 56 columns, 204.0 for 16).
5. When it looks right, rebuild into `cad/exports/year` and `cad/exports/quarter` and commit the result.

## Notes on the model

- Units are millimetres. X = width, Y = up, Z = towards the viewer.
- The side profile is one polyline extruded across the width; every fold is a fillet of the same radius (`R_BEND`), which is what keeps the "folded sheet" look. Changing one radius changes the whole character, so change them together.
- Fillets are applied by selecting edges with a bounding box at a profile vertex. If you move a vertex, the box has to follow it, or the fillet silently misses.
- OpenCASCADE fillets fail when a radius is larger than the adjacent face allows. The usual fixes are a smaller radius, or filleting before cutting windows and pockets (as the script does).
- STL export uses `tolerance=0.05`, `angularTolerance=0.2`. Tighten them for smoother curves at the cost of file size.
- The full-year body is 604 mm wide, so it must be split for printing; the quarter body (204 mm) fits a 220 mm bed.
- Fits and mounting live in a block of constants near the top of the script (`FIT`, `LIP_W`, `PAD_T`, `BOSS_R`, `FOAM_T`, `ENC_*`, `USB_*`, `ESP_*`). After changing one, rebuild and re-run an interference check: intersect every pair of parts and expect volume 0 for all of them. Parts that merely touch intersect with zero volume.
- Face-local coordinates (`on_face`): z = 0 on the outer face and negative behind it, so the stack from the grille to the backer reads as plain depths.
- The body, side cap and base are separate solids; the cap lip is derived from the cavity profile so it follows the sweep radii.
