# Marauder → OLED — plan

Status: **implemented (2026-11-21), firmware build unverified in the sandbox**.
This file is the plan for "turn ESP32 Marauder to OLED" for this repo
(`HiruGirl/Marauder-Oled`).
The source changes in this plan are in place; the firmware build has not been
exercised end-to-end here (the ESP32 platform packages could not be downloaded
from this sandbox). See the README for the exact build status.

---

## 1. Goal

Adapt the open-source **ESP32 Marauder** firmware (WiFi/Bluetooth tool) so it
runs on a **standard ESP32 DevKit (ESP32-WROOM-32)** with a **0.96\" 128x64
SSD1306 monochrome OLED** instead of the color TFT, while keeping the device
minimal: **display + physical buttons only**.

The OLED target is a new board profile in the firmware — it is not a rewrite of
the tool. All WiFi/Bluetooth functionality is inherited unchanged from upstream;
no new attack or scanning capability is added in this work.

## 2. Upstream base

- Source of the firmware: `https://github.com/justcallmekoko/ESP32Marauder`
  (currently HEAD = `d9197cf`, v1.21.0). Verified by reading the source in this
  session; the local `Marauder-Oled` repo starts empty (README only), so the
  firmware tree is copied in and this repo becomes the fork.
- **Keep upstream's license (MIT) and attribution.**
- **Note on the existing POOM target:** upstream already ships a monochrome
  128x64 OLED target (`MARAUDER_POOM`) for the ESP32-C5 — a custom SSD1306-style
  driver (`PoomDisplay`), the `TFT_eSPI` API alias trick
  (`using TFT_eSPI = PoomDisplay;`), and a `BUTTON_ARRAY_LEN = 5` compact layout.
  That is the reference pattern this plan reuses. Our target is **not** POOM:
  it targets the classic ESP32 (not ESP32-C5), with our own display class, pin
  map and features, so POOM stays untouched and functional.

## 3. Hardware target (from your answers)

| Item | Choice |
| --- | --- |
| MCU board | Standard ESP32 DevKit (ESP32-WROOM-32), USB-UART, no on-board display |
| Display | 0.96\" 128x64 SSD1306 I2C OLED module (4-pin: VCC, GND, SCL, SDA), address 0x3C |
| User interface | Physical buttons (no touch screen) |
| Storage / sensors / output | **None** — no SD card, no GPS, no NEO LED, no backlight PWM, no battery |
| Display features | Compact 128x64 monochrome layout (like the existing POOM target) |

**Core Marauder app is kept**: boot splash, menu system, WiFi scan/sniff/attack
menus, mini (button-driven) keyboard, serial CLI, settings/SPIFFS. Nothing in
the app logic is rewritten or changed — only the display backend and the
peripheral set are.

Out of scope for v1: SD logging/uploads, GPS tracking, NEOPIXEL status LED,
touch input, CSI motion, battery charging.

## 4. Proposed wiring / pin map

All pins are non-strapping, non-flash GPIOs on a standard DevKit (avoid
0/2/12/15/6–11; avoid I2C 21/22 for anything else):

| Signal | ESP32 GPIO | OLED/module |
| --- | --- | --- |
| VCC | 3.3 V | VCC |
| GND | GND | GND |
| SCL | **22** | SCL |
| SDA | **21** | SDA |
| Button L (left) | 4 | — |
| Button U (up) | 5 | — |
| Button R (right) | 17 | — |
| Button D (down) | 18 | — |
| Button C (select) | 19 | — |
| Button B (cancel/back) | 25 | — |
| OLED backlight | internal to the module | (no pin — module is always lit) |

All six buttons wire to GND through a pushbutton and use the ESP32 internal
pull-ups (`Switches` handles pull-up logic). No other peripherals.

These are **proposed**; happy to adjust any pin once the physical board is
fixed.

## 5. What changes (file by file)

### 5.1 Repo setup
- Copy the upstream firmware tree (`esp32_marauder/`, `libraries/` incl.
  submodule contents, `platformio.ini`, `tools/`, `installer/`, `.github/`,
  LICENSE, pictures/, etc.) into this repo alongside `README.md`.
- Keep the top-level `README.md` (updated for OLED) and this
  `docs/OLED-PLAN.md`.
- Pin the copied `esp32_marauder/configs.h` and display-related files to the
  exact upstream commit above (record it in the README).

### 5.2 New display driver (mirrors `PoomDisplay`, generalized)
- `esp32_marauder/OledDisplay.h` / `.cpp`:
  - `class OledDisplay : public Print`, `kAddress = 0x3C`,
    `I2C_SDA`/`I2C_SCL` from `configs.h`, 1 KB framebuffer (128×64), 8 pages,
    SSD1306 init sequence (charge pump, 64-row multiplex, normal orientation,
    column offset 2, power/compression/charge-pump enables — the same
    sequence upstream uses and which is verified to initialize the module),
    same API surface as `PoomDisplay` (`init()`, `display(force)`,
    `fillScreen()`, `drawPixel()`, lines, rects, circles, bitmaps, `setCursor()`,
    `setTextColor()`, `setTextSize()`, `setTextWrap()`, `textWidth()`,
    `drawString()` / `drawCentreString()` / `drawRightString()`,
    `width()/height()`, `getCursorY()`, `write()`), colors mapped to
    white/black (monochrome), 33 ms flush throttle.
  - `class OledButton` mirroring upstream's `PoomButton` (center/edge contains
    logic, `press()/justPressed()/isPressed()/justReleased()`, label
    datum offsets) with the same method set.
  - `using TFT_eSPI = OledDisplay;` and `using TFT_eSPI_Button = OledButton;`
    (the same trick upstream uses), so `Display.h`, `Display.cpp`,
    `MenuFunctions.*` compile against it unchanged.
  - Reuse the same 5×7 ASCII font data (`PoomFont.h`) to avoid duplicating it.
- `Display.h`: add a branch next to the POOM one —
  `#if defined(MARAUDER_OLED) #include "OledDisplay.h"` (before the POOM else,
  before the default `TFT_eSPI.h`).

### 5.3 New board target in `configs.h`
- `#define MARAUDER_OLED` (build flag in `platformio.ini` / installer).
- HARDWARE_NAME → `"Marauder OLED"`; FCC_ID → `"See hardware label"`
  (third-party target, like POOM).
- Features: `HAS_SCREEN`, `HAS_MINI_SCREEN` (128×64 compact layout),
  `HAS_BUTTONS` (L/U/R/D/C/B), `HAS_MINI_KB` (button-driven mini keyboard —
  required on a no-touch build), BLE + WiFi stack on
  (`HAS_BT`, `HAS_NIMBLE_2`/`HAS_IDF_3` as upstream default targets do).
  **Not enabled:** `HAS_SD`, `HAS_C5_SD`, `HAS_GPS`, `HAS_BATTERY`,
  `HAS_NEOPIXEL_LED`, `HAS_PSRAM`, `HAS_CSI_MOTION`, `HAS_TOUCH`,
  `HAS_SIMPLEX_DISPLAY`, `HAS_DIRECT_UPLOAD`, `HAS_SIMPLEX_DISPLAY`.
  (`MARAUDER_NO_PSRAM_MEMORY_PROFILE` is auto-applied.)
- Geometry constants identical to POOM (TFT 128×64, `STATUS_BAR_WIDTH` 8,
  `CHAR_WIDTH` 6, `STANDARD_FONT_CHAR_LIMIT` 21, `CHAN_PER_PAGE` 7,
  `TEXT_HEIGHT` 8, `MAX_SCREEN_BUFFER` 5, `BUTTON_SCREEN_LIMIT` 5,
  `TOP_FIXED_AREA` 8, `BANNER_TEXT_SIZE` 1, `KEY_X 64 / KEY_Y 13 / KEY_H 10`,
  `SCREEN_BUFFER`) — same geometry as the 0.96\" panel, so the menu/graph/status
  layouts work.
- Button GPIO defines from the pin map (`L_BTN 4 / C_BTN 19 / U_BTN 5 / R_BTN 17 /
  D_BTN 18 / B_BTN 25`, all `*_PULL true`).
- `BACKLIGHT`/`backlightOn()/off()` become no-ops (module lit by default, same
  as POOM). No `TFT_BL` at all.

### 5.4 Mechanical guard refactor in shared code (POOM → OLED-aware)
~58 sites across 8 files use `#ifdef MARAUDER_POOM` for the monochrome-128x64
layout path. Change the guards to `#if defined(MARAUDER_POOM) || defined(MARAUDER_OLED)`
so the OLED target shares that layout/rendering path:
- `Display.cpp` (splash text → `"OLED"` instead of `"POOM"`, title byte screen layout,
  no graph scale buttons, etc.)
- `MenuFunctions.cpp/.h` (compact layout, mini-keyboard 5-button flow,
  status bar line, etc.)
- `WiFiScan.cpp` (128x64 status rows, OLED-friendly progress flushing)
- `ReconMission.cpp` (screen height/draw logic)
- `esp32_marauder.ino` (`B_BTN` switch creation; NO `PoomWs2812` — no LED;
  `Backlight` no-ops; TFT_BL pulse blocks disabled; splash/headless flow)
- `tools/test_poom_target.py` → keep for POOM, and add `tools/test_oled_target.py`
  verifying our pin map and the adapter include switch (mirroring POOM's test).

> Note: `LedInterface.h/.cpp` and `PoomWs2812.*` are **not** touched; the OLED
> target simply doesn't enable `HAS_NEOPIXEL_LED`, so they compile out.

### 5.5 Build files
- `platformio.ini`: add `[env:marauder-oled]` (`board = esp32dev`,
  `framework = arduino`, `build_flags = [ -D MARAUDER_OLED -D ...]`), keep the
  native test env unchanged, add our OLED env to CI/build matrix as needed.
- `installer/targets.json`: add a `marauder-oled` target entry
  (`buildFlag: MARAUDER_OLED`, `assetSuffix: oled`, `chipFamily: ESP32`,
  `displayName: Marauder OLED`, alias `OLED-128x64`) so the installer registry
  and `--validate-registry` stay consistent.
- `.github/workflows/build*.yml`: add the OLED target to the build matrix
  (or follow the upstream recommendation in this file — small edit).

### 5.6 Docs & wiring
- Rewrite `README.md`: what the fork is, hardware list, wiring table, how to
  build/flash (Arduino IDE + PlatformIO), feature list & limitations (monochrome
  128x64, no SD/GPS/LED, minimal), upstream attribution and MIT license note.

## 6. Verification plan
1. `pio run -e marauder-oled` — firmware compiles clean.
2. `pio test -e native` (existing unit tests) + new `tools/test_oled_target.py`
   (pin map, adapter include switch, registry entry) — all pass.
3. Flash on a bench ESP32 DevKit + 0.96\" OLED: splash → boot menu, menu
   navigation with all 6 buttons, mini keyboard text entry, status bar layout.
4. Confirm POOM target still builds (`MARAUDER_POOM`) — no regression.

## 7. Open questions to confirm before I implement
1. The **pin map** (L/U/R/D/C/B) — OK as proposed, or does your board use other
   GPIOs?
2. **BLE**: keep BLE scanning on the OLED target (`HAS_BT`) as proposed, or drop
   it to keep the build minimal?
3. **Buttons**: 6 buttons (L/U/R/D/C/B) as proposed, or fewer?
4. **Build system**: PlatformIO `marauder-oled` env (as upstream's installer
   registry expects), or Arduino IDE `User_Setup_oled.h` + `-DMARAUDER_OLED`?
   (Both supported — plan assumes PlatformIO + Arduino IDE compatibility via the
   build flag.)
5. **README / installers:** include the OLED target in the installer build
   matrix now, or leave it to a follow-up?

## 8. Non-goals (explicit)
- No new WiFi/BLE features, no offensive-capability changes — everything comes
  from upstream, unchanged.
- No SD card, GPS, NEOPIXEL LED, touch screen, battery support in v1.
- Not touching POOM or any other existing target.
