from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (ROOT / "esp32_marauder" / "configs.h").read_text(encoding="utf-8")


class OledTargetTests(unittest.TestCase):
    def test_oled_gpio_and_i2c_map_is_preserved(self) -> None:
        expected = {
            "L_BTN": 4,
            "C_BTN": 19,
            "U_BTN": 5,
            "R_BTN": 17,
            "D_BTN": 18,
            "B_BTN": 25,
            "OLED_I2C_SDA": 21,
            "OLED_I2C_SCL": 22,
            "OLED_I2C_ADDRESS": 60,  # 0x3C
        }
        for macro, value in expected.items():
            self.assertRegex(CONFIG, rf"#define\s+{macro}\s+(0x[0-9a-fA-F]+|{value})\b")

    def test_oled_is_a_public_esp32_target(self) -> None:
        registry = json.loads((ROOT / "installer" / "targets.json").read_text())
        oled = next(target for target in registry["targets"] if target["id"] == "marauder-oled")
        self.assertEqual(oled["buildFlag"], "MARAUDER_OLED")
        self.assertEqual(oled["assetSuffix"], "oled")
        self.assertEqual(oled["chipFamily"], "ESP32")
        self.assertNotIn("MARAUDER_OLED", registry["privateBuildFlags"])

    def test_oled_uses_its_own_adapter_without_changing_tft_targets(self) -> None:
        display_header = (ROOT / "esp32_marauder" / "Display.h").read_text()
        self.assertIn('#if defined(MARAUDER_OLED)\n  #include "OledDisplay.h"', display_header)
        self.assertIn('#elif defined(MARAUDER_POOM)\n  #include "PoomDisplay.h"', display_header)
        self.assertIn("#else\n  #include <TFT_eSPI.h>", display_header)

    def test_oled_is_minimal(self) -> None:
        # A minimal OLED target: no SD, no GPS, no LED, no touch, no PSRAM,
        # no CSI motion control.
        feature_block = CONFIG[CONFIG.index("#ifdef MARAUDER_OLED"):]
        feature_block = feature_block[:feature_block.index("#endif") + 6]
        for forbidden in (
            "HAS_SD", "HAS_C5_SD", "HAS_GPS", "HAS_BATTERY",
            "HAS_NEOPIXEL_LED", "HAS_PSRAM", "HAS_CSI_MOTION",
            "HAS_TOUCH", "HAS_SIMPLEX_DISPLAY", "HAS_DIRECT_UPLOAD",
            "HAS_C5_SD", "HAS_BT_REMOTE", "HAS_FULL_SCREEN",
        ):
            self.assertNotIn(f"#define {forbidden}", feature_block)
        for required in (
            "HAS_SCREEN", "HAS_MINI_SCREEN", "HAS_BUTTONS", "HAS_MINI_KB",
            "HAS_BT", "HAS_IDF_3", "HAS_NIMBLE_2",
        ):
            self.assertIn(f"#define {required}", feature_block)

    def test_oled_compact_layout_reserves_the_status_row(self) -> None:
        display = (ROOT / "esp32_marauder" / "Display.cpp").read_text()
        menus = (ROOT / "esp32_marauder" / "MenuFunctions.cpp").read_text()
        recon = (ROOT / "esp32_marauder" / "ReconMission.cpp").read_text()
        self.assertIn("STATUS_BAR_WIDTH + (i * TEXT_HEIGHT)", display)
        self.assertIn('drawString("C" + (String)wifi_scan_obj.old_channel, 0, 0, 1)', menus)
        self.assertIn("RECON_SCREEN_HEIGHT - STATUS_BAR_WIDTH", recon)
        self.assertIn("fillRect(button_x, button_y, KEY_W, KEY_H, background)", menus)

    def test_oled_has_a_physical_button_text_editor(self) -> None:
        menus = (ROOT / "esp32_marauder" / "MenuFunctions.cpp").read_text()
        self.assertIn("if (b_btn.justPressed())", menus)
        self.assertIn("return wifi_scan_obj.current_mini_kb_ssid;", menus)

    def test_oled_needs_no_led_and_no_sd_backend(self) -> None:
        led_header = (ROOT / "esp32_marauder" / "LedInterface.h").read_text()
        poom_ws2812 = (ROOT / "esp32_marauder" / "PoomWs2812.cpp").read_text()
        self.assertIn("#ifdef MARAUDER_POOM", led_header)
        self.assertNotIn("MARAUDER_OLED", poom_ws2812)


if __name__ == "__main__":
    unittest.main()
