# Commit Tracker Desk Display

A desk object that shows your GitHub contribution graph in light: one LED per day, 53 weeks × 7 days, glowing through a white grille in five shades of green. The case is a soft wedge inspired by Dieter Rams and the Braun DN 40: the screen leans back at the front, the body sweeps down into a long low plinth, and the front rolls under so the whole thing floats on a thin shadow line.

## Two lengths

| | Full year | 3 months |
|---|---|---|
| Weeks × days | 53 × 7 (371 LEDs) | 13 × 7 (91 LEDs) |
| Width | 574 mm (22.6″) | 174 mm (6.9″) |
| Depth × height | 215 × 117 mm | 215 × 117 mm |
| LED panels | 7 × WS2812B 8×8 | 2 × WS2812B 8×8 |
| Print | split into sections | one piece on a 220 mm bed |

Both are generated from one parametric script: `WEEKS=53` or `WEEKS=13`.

## How it works

- **LEDs:** WS2812B 8×8 matrix panels at 10 mm pitch. Each column of 8 is one week; 7 LEDs are the days (Sunday at top) and the 8th sits hidden behind the bezel.
- **Data:** an ESP32 fetches your contribution calendar from GitHub's GraphQL API every 15–30 minutes. GitHub returns each day's count and its level (0–4), so the device shows exactly what your profile shows.
- **Colour:** brighter means more commits. The default palette is GitHub's dark-theme greens (`#0e4429`, `#006d32`, `#26a641`, `#39d353`); level 0 is off. Halloween, Winter and single-colour palettes are planned, set from a small web page on the device.
- **Control:** one knob on the plinth (rotary encoder): turn for brightness, press to change palette. The knob sits in line with the "today" column.

## The case

Front to back: white grille with 8.6 mm rounded square windows → smoked black diffuser → 10 mm egg-crate grid → LED panels → hollow wedge body, ESP32 in the plinth, USB-C at the back, recessed base plate.

Design rules (applied throughout the CAD):
- Screen at 62° to the desk; flat 16 mm top; back flank at 30° with a 60 mm sweep into a 35 mm plinth.
- One 8 mm radius for every fold of the profile; one crisp 1.5 mm radius on every side edge and window.
- Front rolls under: lifted 10 mm, footprint set 22 mm back; body sits on a base inset 2 mm (shadow gap).

Finishes explored: white, red, black, or brushed aluminium body; white, black or aluminium grille.

## Repo layout

```
cad/case_tracker.py      parametric CadQuery model (WEEKS env var)
cad/exports/year/        STEP + STLs, 53 weeks
cad/exports/quarter/     STEP + STLs, 13 weeks
docs/build-notes.md      parts, wiring, printing, finishes
docs/firmware-plan.md    ESP32 firmware design (not written yet)
docs/cad-workflow.md     CadQuery / OpenCASCADE workflow
```

## Rebuild the CAD

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r cad/requirements.txt
WEEKS=53 python cad/case_tracker.py cad/exports/year
WEEKS=13 python cad/case_tracker.py cad/exports/quarter
```

## Status

- [x] Case design and CAD (both lengths)
- [ ] LED panels bought and pitch checked
- [ ] Firmware (see `docs/firmware-plan.md`)
- [ ] Print, finish, assemble

## Licence

MIT
