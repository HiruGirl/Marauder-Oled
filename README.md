<!---[![License: MIT](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/justcallmekoko/ESP32Marauder/blob/master/LICENSE)--->
<!---[![Gitter](https://badges.gitter.im/justcallmekoko/ESP32Marauder.png)](https://gitter.im/justcallmekoko/ESP32Marauder)--->
<!---[![Build Status](https://travis-ci.com/justcallmekoko/ESP32Marauder.svg?branch=master)](https://travis-ci.com/justcallmekoko/ESP32Marauder)--->
<!---Shields/Badges https://shields.io/--->

# ESP32 Marauder
<p align="center"><img alt="Marauder logo" src="https://github.com/justcallmekoko/ESP32Marauder/blob/master/pictures/marauder_skull_patch_04_full_final.png?raw=true" width="300"></p>
<p align="center">
  <b>A suite of WiFi/Bluetooth offensive and defensive tools for the ESP32</b>
  <br><br>
  <a href="https://github.com/justcallmekoko/ESP32Marauder/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/mashape/apistatus.svg"></a>
  <a href="https://gitter.im/justcallmekoko/ESP32Marauder"><img alt="Gitter" src="https://badges.gitter.im/justcallmekoko/ESP32Marauder.png"/></a>
  <br>
  <a href="https://twitter.com/intent/follow?screen_name=jcmkyoutube"><img src="https://img.shields.io/twitter/follow/jcmkyoutube?style=social&logo=twitter" alt="Twitter"></a>
  <a href="https://www.instagram.com/just.call.me.koko"><img src="https://img.shields.io/badge/Follow%20Me-Instagram-orange" alt="Instagram"/></a>
  <br><br>
</p>
    
[![Build and Push](https://github.com/justcallmekoko/ESP32Marauder/actions/workflows/build_push.yml/badge.svg)](https://github.com/justcallmekoko/ESP32Marauder/actions/workflows/build_push.yml)
[![Firmware coverage](https://codecov.io/gh/justcallmekoko/ESP32Marauder/branch/develop/graph/badge.svg?flag=firmware-unit-tests)](https://app.codecov.io/gh/justcallmekoko/ESP32Marauder/tree/develop)

## Getting Started
Download the [latest release](https://github.com/justcallmekoko/ESP32Marauder/releases/latest) of the firmware.  

Check out the project [wiki](https://github.com/justcallmekoko/ESP32Marauder/wiki) for a full overview of the ESP32 Marauder

## FCC module identifiers

The Device Info screen reports the FCC ID of the radio module fitted to supported JustCallMeKoko hardware. This is the module identifier, not a claim that every carrier-board or enclosure configuration has a separate end-product grant.

| Hardware | Radio module | FCC ID |
| --- | --- | --- |
| Marauder v8, Marauder Mini v3, C5 Wardriver, C5 LowKey, BFFB v2 | ESP32-C5-WROOM-U | `2AC7Z-ESPC5WROOMU` |
| Marauder v4, v6, v6.1, v7, original Mini, Marauder Kit | ESP32-WROOM-32U | `2AC7Z-ESP32WROOM32U` |
| BFFB / Marauder Dev Board Pro | ESP32-WROOM-32E | `2AC7Z-ESP32WROOM32E` |

The legacy mappings are the closest modular approvals for the modules specified by the repository hardware designs. Confirm the module marking on a physical unit before using an FCC ID for labeling or compliance documentation. Third-party targets display `See hardware label` because their module or complete-device certification can vary by production revision.

## Marauder OLED variant

This fork adapts ESP32 Marauder to a **standard ESP32 DevKit (ESP32-WROOM-32)**
with a **0.96" 128x64 SSD1306 I2C OLED** instead of the color TFT. It is a new,
self-contained board profile (`MARAUDER_OLED`) — not a rewrite of the tool, and
untouched from the upstream TFT and POOM variants.

| Item | Choice |
| --- | --- |
| MCU | ESP32-WROOM-32 (standard DevKit, USB-UART) |
| Display | 0.96" 128x64 SSD1306 I2C, address 0x3C |
| User interface | Physical buttons only (no touch) |
| Storage / sensors / output | None — no SD, no GPS, no NEOPIXEL LED, no battery, no CSI |
| Wired pins | SCL 22, SDA 21, L 4, U 5, R 17, D 18, C 19, B 25 (all to GND via pushbutton, internal pull-ups) |

What is kept from upstream: boot splash, WiFi/Bluetooth scan/sniff/attack menus,
the button-driven mini keyboard, serial CLI, settings/SPIFFS. Verified against
the upstream behavior by the existing unit tests plus a dedicated OLED check.

What is not present: SD card logging/uploads, GPS tracking, NEOPIXEL status LED,
touch input, CSI motion, PSRAM. The monochrome OLED is always lit (no backlight
pin). FCC reporting displays `See hardware label` — this is a third-party target.

### Building

```sh
pio run -e marauder-oled
```

Flashes to the ESP32 DevKit at `0x1000` (`esptoolChip: esp32`). Build output is
`.pio/build/marauder-oled/firmware.bin`.

> **Status:** the source and configuration are implemented and covered by
> unit tests, but the firmware build itself has not been exercised end-to-end in
> this sandbox (the ESP32 platform could not be downloaded there). Treat the
> compiled firmware as unverified until `pio run -e marauder-oled` succeeds on a
> machine with network access to the ESP32 platform packages.

### Files

See `docs/OLED-PLAN.md` for the plan, `esp32_marauder/OledDisplay.h` /
`.cpp` for the driver, and `installer/targets.json` for the installer registry
entry (`marauder-oled`).

# For Sale Now
You can buy the ESP32 Marauder using [this link](https://www.justcallmekokollc.com)
