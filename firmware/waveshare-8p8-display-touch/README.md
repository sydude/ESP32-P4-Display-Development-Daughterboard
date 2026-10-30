# Waveshare ESP32-P4 8.8-inch display and touch baseline

Standalone ESP-IDF **6.1.0** project for the Waveshare **ESP32-P4-WIFI6-DB**, 8.8-inch **480 × 1920** DSI LCD and **GT9271** touch controller. This project lives in the Daughterboard repository; it has no dependency on a sibling source checkout.

## Build

With ESP-IDF 6.1.0 installed and activated:

```sh
cd "firmware/waveshare-8p8-display-touch"
idf.py build
```

On the current Mac, activate the existing ESP-IDF Installation Manager environment first:

```sh
source "$HOME/.espressif/tools/activate_idf_v6.1.sh"
```

The CMake project defaults to `esp32p4`. The tracked `sdkconfig` preserves the full working configuration, including **32 MB flash**, PSRAM, and chip revision constraints. `sdkconfig.defaults` contains the same full baseline so regeneration retains board settings. The existing single-app partition layout is unchanged; 32 MB flash does not imply a 32 MB app partition. Keep `dependencies.lock` tracked. The first build downloads managed components.

No flashing is performed by a build. Flashing requires the user's explicit approval and a selected serial port. Monitor baud is 115200.

## Current behavior

The app initializes the original two-lane DSI configuration, LDO channel 3 at 2500 mV, RGB888 and the driver's 8.8-inch panel preset. It shows vertical hardware color bars, probes the existing I2C bus 1, reads the touch product ID at address `0x14`, and logs up to five raw touch points every 50 ms. It preserves the working controller register protocol; coordinates are not transformed into an LVGL input device. The LCD driver creates the shared I2C bus during initialization.

Unity test registration, test-suite memory checks, unused teardown/rotation/software-pattern tests and the commented uniformity demo were removed from the executable. Runtime checks now use `ESP_ERROR_CHECK` and an allocation assertion. The active display/touch sequence is preserved. No LVGL, PlatformIO configuration, or Wi-Fi application integration is included yet; those can be added as separate changes.

## Dependencies and provenance

- `waveshare/esp_lcd_dsi`: **2.0.0**, registry package, replacing the local relative dependency.
- `espressif/i2c_bus`: **1.5.2**, preserved.
- `espressif/cmake_utilities`: **0.5.3**, preserved.
- ESP-IDF: **6.1.0**, preserved and pinned in the manifest.

Source: `~/Documents/GitHub/Libraries/Waveshare-ESP32-components/display/lcd/esp_lcd_dsi/test_apps`, branch `esp32p4-display-touch-baseline`, commit `7011ae908c04bedb7e3d035b537c6f894c4b8957`.

`reference/` preserves the original source, CMake files, manifest, dependency lock, and configuration byte-for-byte. These files are archival and do not participate in this project's build. `reference/SHA256SUMS` records their checksums. The upstream Waveshare MIT license is retained in `LICENSE.waveshare.txt`.

The downloaded registry driver's `esp_lcd_dsi.c` and entire `include/` directory match the local baseline byte-for-byte. Build compatibility is checked using the installed ESP-IDF 6.1.0 toolchain; hardware behavior still needs confirmation after an approved flash.

## Validation

Built successfully on 2026-10-21 with ESP-IDF 6.1.0 for `esp32p4`. Application image: `build/waveshare_8p8_display_touch.bin`, 0x424e0 bytes (271,584 bytes); 74% of the existing 1 MB app partition remains free. Generated flash arguments specify 32 MB flash. The active `sdkconfig` remained byte-for-byte identical to the original baseline. The source Waveshare repository remained clean at its baseline commit. No board was flashed or runtime-tested during extraction.
