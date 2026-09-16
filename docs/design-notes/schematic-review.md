# Phase 2 schematic review record

**Date:** 2026-09-16  
**Schematic:** `hardware/kicad/ESP32-P4 Display Development Daughterboard.kicad_sch`  
**Status:** complete for independent schematic review; PCB layout not started

## 1. Hierarchy

| Page | Sheet | Primary content |
|---:|---|---|
| 1 | Root | Project hierarchy and review boundary |
| 2 | Bench 24 V Input | Barrel input, fuse, TVS, filtering, test points |
| 3 | Vehicle Input Protection | Connector, blade fuse, filter, TVS, LM74800-Q1 reverse/OV protection |
| 4 | LM5176 Vehicle Buck-Boost | Four-switch 12 V-to-24 V converter and PGOOD |
| 5 | Source ORing | Independent bench and vehicle ideal-diode branches |
| 6 | System 5 V and Nano Feed | LM76003 5 V/3 A and TPS25947 reverse-blocked Nano feed |
| 7 | Display Rails and Sequencing | Hold-up, supervisor, sequencer, 1.8/2.8/3.3 V rails, reset clamps |
| 8 | MIPI DSI and LCD Connector | Nano FFC, inline DSI links, ESD, 40-pin panel connector |
| 9 | GT9271 Touch Interface | Touch rail, powered-off-safe four-signal isolation, ESD, connector |
| 10 | 240 mA Backlight | TPS922053 buck, hardware gate, current sense and test access |
| 11 | Nano Headers and Debug | Nano sockets, corrected GPIO mapping, debug header and indicators |

The BOM is generated as `hardware/BOM.csv`. The reproducible source model is `hardware/kicad/tools/generate_schematic.py`; generated KiCad sheets and the embedded symbol library are committed so reviewers do not need the generator to open the project.

## 2. External connector audit

### 2.1 Power inputs

| Connector | Pin | Net/function | Controlling-source disposition |
|---|---:|---|---|
| `J101`, Switchcraft RAPC722X | 1 | `BENCH_24V_RAW` | Center contact, positive bench input |
| `J101`, Switchcraft RAPC722X | 2 | GND | Sleeve/return |
| `J101`, Switchcraft RAPC722X | 3 | NC | Switched contact deliberately unused |
| `J201`, Molex 43045-0218 | 1 | `VEH_12V_RAW` | Vehicle-positive input |
| `J201`, Molex 43045-0218 | 2 | GND | Vehicle return |

The exact 24 V adapter plug dimensions and polarity marking remain a pre-layout procurement/physical check; the electrical polarity is fixed center-positive.

### 2.2 Nano 15-pin DSI connector `J701`

| Pin | Net | Controlling-source disposition |
|---:|---|---|
| 1 | `DSI_D1_N_SRC` | Panel `MIPI_1N`; routed straight-through |
| 2 | `DSI_D1_P_SRC` | Panel `MIPI_1P`; routed straight-through |
| 3 | GND | DSI return/plane |
| 4 | `DSI_CLK_N_SRC` | Panel `MIPI_CLKN`; routed straight-through |
| 5 | `DSI_CLK_P_SRC` | Panel `MIPI_CLKP`; routed straight-through |
| 6 | GND | DSI return/plane |
| 7 | `DSI_D0_N_SRC` | Panel `MIPI_0N`; routed straight-through |
| 8 | `DSI_D0_P_SRC` | Panel `MIPI_0P`; routed straight-through |
| 9 | GND | DSI return/plane |
| 10 | NC | Nano source marks this unconnected/unlabeled |
| 11 | `NANO_I2C_SCL` | Nano GPIO8 touch I²C clock |
| 12 | `NANO_I2C_SDA` | Nano GPIO7 touch I²C data |
| 13 | GND | Logic return |
| 14–15 | `NANO_3V3_REF` | Nano-side sense/reference only; never driven |

The SFW15R-2STE1LF remains a provisional board connector until the fitted Nano connector and cable contact presentation are physically inspected.

### 2.3 Displayman 40-pin LCD connector `J702`

| Pin(s) | Net/function |
|---:|---|
| 1 | NC |
| 2 | `LCD_VCI` 2.8 V |
| 3 | `LCD_IOVCC` 1.8 V |
| 4 | GND |
| 5 | `LCD_RESET_N` |
| 6 | NC |
| 7 | GND |
| 8 / 9 | `MIPI_D0_N` / `MIPI_D0_P` |
| 10 | GND |
| 11 / 12 | `MIPI_D1_N` / `MIPI_D1_P` |
| 13 | GND |
| 14 / 15 | `MIPI_CLK_N` / `MIPI_CLK_P` |
| 16–22 | GND |
| 23–24 | NC |
| 25 | GND |
| 26–29 | NC |
| 30 | GND |
| 31–32 | `LED_K` |
| 33–38 | NC |
| 39–40 | `LED_A` |

The electrical numbering is fixed from the Displayman source. The board-facing physical orientation, pin-1 presentation, and cable bend remain pre-layout physical checks.

### 2.4 GT9271 touch connector `J801`

| Pin | Net/function |
|---:|---|
| 1 | GND |
| 2 | NC |
| 3 | `TOUCH_3V3` |
| 4 | `CTP_SCL` |
| 5 | `CTP_SDA` |
| 6 | `CTP_INT` |
| 7 | `CTP_RESET_N` |
| 8 | GND |

The connector is the documented bottom-contact Hirose FH12-8S-0.5SH(55); sample flex presentation and thickness remain physical checks.

### 2.5 Nano headers and debug connector

| Function | ESP32-P4 GPIO | Nano P1 pin | Schematic net |
|---|---:|---:|---|
| `LCD_RESET_CMD_N` | 4 | 10 | `LCD_RESET_CMD_N` |
| `CTP_RESET_N` | 5 | 9 | `CTP_RESET_N_NANO` |
| `LCD_PWR_EN` | 20 | 11 | `LCD_PWR_EN` |
| `CTP_INT` | 22 | 14 | `CTP_INT_NANO` |
| `BL_PWM` | 23 | 5 | `BL_PWM` |

GPIO21/P1-13 is intentionally unconnected. GPIO24 is not used, preserving its default USB Serial/JTAG role. `J1002` is mechanically present but no P2 signals are required by this daughterboard.

The remaining header pins are captured explicitly: P1 pins 2 and 4 are `NANO_5V`; P1 pins 25 and 26 are GND; all other unused P1 pins are NC. P2 pins 1–24 are NC and pins 25–26 are GND. This preserves the Waveshare header numbering without inventing uses for unneeded pins.

`J1003` is an internal 2×5 development header with this exact pin map:

| Pin | Net | Pin | Net |
|---:|---|---:|---|
| 1 | GND | 2 | `SYS_5V_3A` |
| 3 | `VIN_GOOD` | 4 | `SEQ_FLAG1` |
| 5 | `SEQ_FLAG2` | 6 | `SEQ_FLAG3` |
| 7 | `LCD_RESET_N` | 8 | `BL_FAULT_N` |
| 9 | `NANO_EFUSE_FLT` | 10 | `VEH_PGOOD` |

## 3. DSI electrical review

- lane and polarity mapping is straight-through with no swap;
- 0 Ω 0201 parts are inline flow-through provisions, not branches;
- one six-channel TPD6E05U06 ESD array is placed conceptually at the panel connector;
- no common-mode choke or bridge is used;
- PCB rules remain 100 Ω differential, continuous reference plane, minimal layer transitions, no stubs, tight intra-pair skew, and a very short ESD ground return;
- the PCB channel must support at least approximately 1.5 Gb/s/lane;
- exact HS lane rate, video-mode tuning, and 46–60 Hz optimization remain firmware/prototype work.

## 4. Power-state and backfeed review

The full state matrix is recorded in `schematic-calculations.md`. The reviewed isolation boundaries are:

- LM74700-Q1 on each high-voltage branch prevents bench/vehicle cross-feed;
- LM74800-Q1 back-to-back FETs protect the vehicle connector from reverse battery and downstream reverse current;
- TPS25947 integrated back-to-back FETs prevent Nano USB/header 5 V from raising `SYS_5V`; the opposite daughterboard-to-laptop direction passes through the Nano's own, separately specified onboard power path and requires the controlled prototype test below;
- TMUX1574 powered-off protection isolates SCL, SDA, INT, and RESET whenever either touch/Nano domain is invalid;
- SN74LVC1G07 reset clamps provide Ioff behavior and do not drive an unpowered panel rail;
- TPS922053 `FAULT_N` is pulled up only to the LED driver's local VCC, so the held-up touch/display domain cannot feed an unpowered backlight driver;
- hard-unplug logic energy is isolated from both the Nano and the backlight;
- the backlight requires `VIN_GOOD`, `LCD_VCI`, firmware PWM, and a fitted hardware-enable shunt.

No prohibited intentional backfeed path exists on the daughterboard. The Nano module's internal USB/header power path must still be measured with a current-limited USB source before an unrestricted laptop is used because Waveshare does not specify its reverse-current performance. Failure of that test requires a data-only/debug USB connection or a Nano-side power-path modification; the daughterboard cannot access USB VBUS separately through the Nano headers.

## 5. ERC and machine checks

Run with KiCad 9.0.9 on 2026-09-16:

- hierarchical netlist export: passed;
- eleven-page PDF export: passed;
- design-model validation in the generator: passed (unique references/pins, physical IC pin sets, connector maps, and key IC net assignments);
- ERC errors: **0**;
- ERC warnings: **10**, all `footprint_link_issues` for intentionally unresolved custom land patterns.

The committed `hardware/kicad/erc-report.txt` is the all-severity report. An errors-only ERC run returns zero violations.

## 6. Footprint warnings and pre-layout closure

These footprints are deliberately named but not fabricated or guessed during schematic capture:

| Reference | Required exact land pattern |
|---|---|
| J101 | Switchcraft RAPC722X right-angle jack |
| D201 | Bourns DO-218AB for SM8S24CA-Q |
| U201 | TI DRR WSON-12 with exposed pad |
| U301 | TI PWP HTSSOP-28 with exposed pad |
| U502 | TI RPW HotRod QFN-10 |
| C601 | Selected 6800 µF/10 V electrolytic body |
| J701 | Amphenol SFW15R-2STE1LF |
| U701 | TI RVZ USON-14 flow-through array |
| J702 | Molex 505110-4096 |
| U901 | TI DYY TSOT-23-14 |

Before PCB placement, each must be created directly from the current manufacturer package drawing, checked by an independent pin-1/pad-number audit, and printed or overlaid at 1:1 where a physical connector/component is available.

## 7. Unresolved items by correct phase

### Independent schematic review

- recheck regulator/driver compensation and worst-case tolerances;
- independently audit every IC pin and connector pin against the cited controlling source;
- challenge the LM74800-Q1 common-drain protection assumption for the defined TVS-protected evaluation use case;
- review the narrow TPS922053 headroom corner and contingency trigger.

No known issue presently requires a schematic topology change, but the design is intentionally awaiting this independent review before PCB work.

### Before footprint or placement freeze

- inspect Nano DSI connector contact side, pin 1, insertion direction, and cable type;
- inspect the LCD and touch flex exposed-contact side, pin 1, thickness, bend direction, and insertion depth;
- confirm the actual 24 V adapter plug size/polarity;
- select the exact 6800 µF capacitor body;
- confirm Nano header height, board separation, mounting holes, keepouts, and the vehicle-harness arrangement;
- create and verify the 10 custom footprints above.

### Prototype bring-up

- tune/verify DSI HS lane rate, video mode, continuous clock, and refresh;
- validate the 600-to-480 masking using test patterns;
- test both GT9271 reset/address sequences and unpowered pin leakage;
- validate 12 V/24 V/USB source transitions and reverse current;
- capture startup, commanded shutdown, and hard-unplug rail timing;
- validate backlight regulation at 16.8–19.8 V equivalent LED voltage, 21.6–26.4 V bus input, temperature, and PWM range;
- measure converter loop response, efficiency, EMI, and thermal margins.

## 8. Owner actions

There is no owner electrical-design action required before independent schematic review. Before PCB layout is frozen, the owner must supply or physically verify the connector/cable/stack details listed in Section 7. Those are mechanical facts, not unresolved electrical choices.

PCB layout is outside this phase and has not begun.
