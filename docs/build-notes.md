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
- Panels chain left to right, oldest week on the left; the rightmost column is the current week, partly filled.

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

- Full year: 574 mm wide, so the body must be split into sections with dovetails or pins. The 3-month body (174 × 215 mm) fits a 220 mm bed in one piece.
- Print the egg-crate grid in **black** (or ≥1.2 mm walls if white) to stop light bleeding between days.
- Grille: white PLA, face down on a smooth sheet. For aluminium, laser-cut 1.5–2 mm brushed sheet from a DXF of the grille.

## Finish

- Satin white like vintage Braun: sand 220 → 400, prime, spray satin white.
- Brushed aluminium option: wrap the body skin in brushed-aluminium vinyl along its length, or have the skin bent from 1.5 mm brushed sheet (constant 8 mm bends suit a press brake).
