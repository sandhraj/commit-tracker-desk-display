# Build notes

## Parts

| Part | Full year | 3 months |
|---|---|---|
| WS2812B 8×8 flexible matrix panel | 7 | 2 |
| ESP32 dev board | 1 | 1 |
| SN74AHCT125N level shifter | 1 | 1 |
| 5 V 3 A supply (USB-C PD trigger or barrel) | 1 | 1 |
| EC11 rotary encoder with push switch | 1 | 1 |
| Smoked/dark-tinted acrylic or film (diffuser), ~20–30% transmission | cut to grille size | cut to grille size |
| PLA (white body + grille, black grid) | ~600 g | ~200 g |

Buy one 8×8 pack first: check the LED pitch is 10 mm, including across the edge where two panels meet, before ordering the rest.

## Grid and LED mapping

- Pitch 10 mm. Squares 8.6 mm with 1.4 mm webs, 1.5 mm corner radius.
- Each 8-LED column is one week. Rows 0–6 = Sunday–Saturday (top to bottom, as on GitHub). Row 7 is hidden behind the bezel and stays off.
- Panels chain left to right. Year: one 8×32 then three 8×8 (56 columns); quarter: two 8×8 (16 columns). The weeks, plus any marker or status columns, are laid onto the columns in firmware, so the layout can change without touching the case.

## Wiring (plan)

```
5 V supply ──+5V──┬──> panels (inject 5 V + GND at every second panel)
                  ├──> ESP32 5V/VIN
                  └── 1000 µF across 5 V/GND at the first panel
ESP32 GPIO16 ──> 74AHCT125 (VCC 5 V) ──> 330 Ω ──> DIN of panel 1
ESP32 GPIO32/33 ──> encoder A/B   GPIO25 ──> encoder push (INPUT_PULLUP)
Common ground: supply, ESP32, panels, level shifter
```

Firmware caps total current at about 2 A (FastLED `setMaxPowerInVoltsAndMilliamps(5, 2000)`).

## Printing

- Full year: 604 mm wide, so the body must be split into sections with dovetails or pins. The quarter body (204 × 215 mm) fits a 220 mm bed in one piece.
- Print the egg-crate grid in **black** (or ≥1.2 mm walls if white) to stop light bleeding between days.
- Grille: white PLA, face down on a smooth sheet. For aluminium, laser-cut 1.5–2 mm brushed sheet from a DXF of the grille.

## Finish

- Satin white like vintage Braun: sand 220 → 400, prime, spray satin white.
- Brushed aluminium option: wrap the body skin in brushed-aluminium vinyl along its length, or have the skin bent from 1.5 mm brushed sheet (constant 8 mm bends suit a press brake).

## Assembly stack (front to back)

Face-local depth below the outer face; all values come from `cad/case_tracker.py`.

| Part | Depth (mm) | Notes |
|---|---|---|
| Grille, white | 0 to -2.0 | Bonded into the pocket (0.15 mm per side clearance) |
| Diffuser, smoked | -2.0 to -2.5 | Bonded on the ledge behind the grille |
| Grid, black | -2.5 to -14.5 | Cells 8.4 mm, walls 1.6 mm (wider than the 1.4 mm grille web). Row 8 is a solid block. Fits the opening with 0.15 mm per side |
| LED panels | -12.5 to -14.5 | Seated in a rim on the back of the grid, so LED centres sit in the cells to ±0.15 mm |
| Foam sheet, black, 1 mm | -14.5 to -15.5 | Compresses to about 0.5 mm. Closes the gap at the panel and grid |
| Backer, black | -15.5 to -18.5 | Screwed to the posts. Stops short of the bottom edge so the panel leads exit freely |

- **Posts and screws:** M2.5 self-tapping screws, 8 mm long, into 2.1 mm pilots. Quarter 6, year 8. Six more M2.5 screws hold the base plate (posts hang from the deck and back flank).
- **Light-bleed rules:**
  - paint or print everything behind the grille black;
  - keep the foam sheet continuous across the panel;
  - do not leave any gap between grid and diffuser.
- **Side cap:** the +X end wall is a separate part with a locating lip. Bond it with CA or epoxy **before** the internals go in and before painting. The internals are fitted from below through the base opening. It lets the shell print on its side (see below).
- **Encoder:** EC11 with M7 bushing, nut inside, 7.4 mm hole with a notch for the anti-rotation lug. The knob sits 0.8 mm above the deck with a counterbore over the bushing and a D-bore. **Check `ENC_SHAFT`** (shaft length above the bushing) against the encoder you buy; the knob height follows from it.
- **ESP32 and USB:** a cradle on the base holds a 52 × 28.5 mm devkit with its USB end at the back wall. The USB slot is 14 × 9 mm at 9 mm height, on the opposite side from the knob. Set `USB_W`, `USB_H`, `USB_Y` from the real cable plug.
- **To verify on real parts:** 8×8 panel thickness (listing says 5 mm, the 8×32 says 2 mm), encoder shaft length, USB plug size, devkit outline.

## Print orientation and finish

- **Orientation:** print the shell **on its side, open side up** (X axis vertical). Every fold and the long R60 sweep become vertical walls, so there is no stair-stepping on the curved surfaces. Measured on the mesh: shallow-slope area drops from 471 cm² (as modelled) to 8 cm², and with the side cap off the cavity ceiling is gone, so no supports.
- **Year size:** the shell is sectioned anyway; print each slice the same way.
- **Window:** the opening is a 70 mm bridge in this orientation; add a small support bridge.
- **Settings:** 0.12 mm layers, 0.4 mm nozzle, seam on the hidden rear wall, then fill, sand 220 to 400, prime and spray.
- **Black parts:** grid, backer and the inside of the shell; print black or paint.
- **Material:** matte or standard PLA, not silk (gloss shows layer lines). PETG or ASA only if the unit will live somewhere warm. PLA softens at about 55 °C. Screw posts can crack in PLA: self-tapping M2.5 screws, not overtightened, or M2.5 heat-set inserts.

## Joining

| Part | Held by |
|---|---|
| Grille and diffuser | Bonded into the pocket (CA or epoxy on the ledge, double-sided tape for the diffuser film) |
| Grid, panels, foam, backer | M2.5 screws only, no glue, so it can be serviced |
| Base | 6 M2.5 screws; removing it gives access to everything from below |
| Side cap | Bonded (CA or epoxy), before the internals and before painting |
| Encoder | Nut inside |
| Knob | Friction on the D-bore; a drop of CA or an M3 grub screw if it slips |

## Colours (white prototype)

| Part | Colour |
|---|---|
| Body and side cap | White (same filament batch) |
| Grille | White |
| Diffuser | Smoked or dark-tinted film or acrylic, 20 to 30 % transmission (not printed) |
| Grid, backer, foam | Black, opaque |
| Base | Black, so the shadow line under the body reads dark |
| Knob | White (or black for contrast) |

White PLA is translucent. If the grille border glows near the LED rows, paint the back of the grille and the inside of the shell matte black.

## Finishing

Target: satin white, no gloss. Gloss shows every layer line and sink mark.

| Part | Finish |
|---|---|
| Body and side cap | Full paint finish (steps below) |
| Grille | Print face down on smooth PEI or glass. Light sand, one thin primer coat and satin white, or leave raw matte PLA. Keep paint out of the window edges |
| Knob | Sand and satin white, or leave raw |
| Grid, backer, base, foam | None. Matte black filament as printed |
| Diffuser | Not printed |

Body and cap, in order:
1. Bond the cap and fill the seam (thin CA or spot putty), then sand flush.
2. Degrease with isopropyl, then high-build filler primer, 2 to 3 light coats, 10 minutes apart.
3. Wet-sand 320, then 400, then 600 grit. Re-prime low spots and repeat until even.
4. Final primer coat, light 800 grit wet sand.
5. Satin white, 2 to 3 thin coats, 10 minutes apart.
6. Optional satin clear coat.

Notes:
- Paint thickness takes up the 0.15 mm fits. Mask or leave bare the grille pocket, the opening for the grid, the cap lip, the post holes and the encoder hole, and sand any paint off them.
- Print a small coupon with the fit features first to see how much the paint changes the clearances.
- Level A (prototype): print on its side, light sand (400), one primer coat, 2 coats satin white. Level B (show piece): the full filler and wet-sand cycle, once the geometry is final.

