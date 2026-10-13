# Firmware plan (ESP32, Arduino/PlatformIO, FastLED)

Not written yet. This is the design.

## Data

GitHub GraphQL API, `POST https://api.github.com/graphql`, token with `read:user`:

```graphql
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
  }
}
```

`contributionLevel` is `NONE`, `FIRST_QUARTILE` … `FOURTH_QUARTILE` → levels 0–4. Refresh every 15–30 min; keep the last good result if a fetch fails. The year version shows the last 53 weeks; the 3-month version the last 13.

## Display

- Palettes (level 1–4; level 0 off):
  - GitHub green `#0e4429 #006d32 #26a641 #39d353`
  - Halloween `#631c03 #bd561d #fa7a18 #fddf68`
  - Winter `#0a3069 #0969da #54aeff #b6e3ff`
  - Single colour: one picked hue at 22 / 42 / 68 / 100% brightness
- Today's square pulses gently.
- FastLED dithering on; global brightness from the knob.

## Settings

- Wi-Fi setup by captive portal (WiFiManager).
- Small web page on the device: GitHub username, token, palette, brightness, refresh interval. Stored in NVS (Preferences).
- Knob: turn = brightness, press = next palette, long press = show the device's IP address scrolling across the grid.
