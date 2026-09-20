# Phase 2 schematic review record

**Date:** 2026-09-19
**Schematic:** `hardware/kicad/ESP32-P4 Display Development Daughterboard.kicad_sch`  
**Status:** single-source power simplification complete; PCB layout not started

## 1. Hierarchy

| Page | Sheet | Primary content |
|---:|---|---|
| 1 | Root | Project hierarchy and review boundary |
| 2 | Power | Protected nominal-12 V input, LM7480-Q1, LM5176-Q1, `SYS_24V`, LM76003 and TPS25947 Nano feed |
| 3 | Display Power & Backlight | Hold-up, supervisor/sequencing, logic rails, reset gating and TPS922053 driver |
| 4 | Interfaces & Nano | Nano headers/DSI, panel connector/MIPI ESD, touch isolation/ESD and debug |

The committed native KiCad hierarchy is the authoritative editable source. The previous generator was retired after consolidation to prevent a second source of truth from overwriting human-maintained placement and wiring. `hardware/BOM.csv` is the checked physical inventory generated from the final design data.

## 2. External connector audit

### 2.1 Power inputs

| Connector | Pin | Net/function | Controlling-source disposition |
|---|---:|---|---|
| `J201`, Molex 43045-0218 | 1 | `VEH_12V_RAW` | Positive input; vehicle source or regulated/current-limited nominal-12 V bench supply |
| `J201`, Molex 43045-0218 | 2 | GND | Input return |

There is no dedicated 24 V bench connector. Bench development uses J201 and exercises the same protection and conversion path as vehicle operation.

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

The Amphenol SFW15R-2STE1LF drawing confirms the daughterboard part is a 15-position, 1.00 mm, top-contact connector. A section through the Waveshare STEP shows the Nano connector is bottom-contact. With J701 mounted on the daughterboard underside and both mouths facing the same direction, the no-twist stack route uses a Type-B/opposite-side-contact FFC and a 180° service loop. The Waveshare mechanical files do not encode physical pin 1, so the actual Nano still requires one powered-off pin-1/continuity/contact-face check before orientation is frozen. See `mechanical-interface-verification.md`.

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

The electrical numbering is fixed from the Displayman source. Displayman confirms a bottom-contact panel flex, matching the bottom-contact Molex connector. The exact delivered tail/receptacle termination, physical pin 1, stiffener and relaxed cable bend remain pre-layout sample checks. The provisional Molex Type-A cables are not direct mates to a bare panel flex tail.

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

The connector is the documented bottom-contact Hirose FH12-8S-0.5SH(55), matching Displayman's bottom-contact touch flex. Physical pin 1, stiffener, thickness, insertion depth and relaxed bend direction remain sample checks.

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
| 9 | `NANO_EFUSE_FLT` | 10 | `SYS24_PGOOD` |

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

- LM74800-Q1 common-drain back-to-back FETs protect the 12 V connector from reverse battery and downstream reverse current;
- TPS25947 integrated back-to-back FETs prevent Nano USB/header 5 V from raising `SYS_5V`; the opposite daughterboard-to-laptop direction passes through the Nano's own, separately specified onboard power path and requires the controlled prototype test below;
- TMUX1574 powered-off protection isolates SCL, SDA, INT, and RESET whenever either touch/Nano domain is invalid;
- SN74LVC1G07 reset clamps provide Ioff behavior and do not drive an unpowered panel rail;
- TPS922053 `FAULT_N` is pulled up only to the LED driver's local VCC, so the held-up touch/display domain cannot feed an unpowered backlight driver;
- hard-unplug logic energy is isolated from both the Nano and the backlight;
- the backlight requires `VIN_GOOD`, `LCD_VCI`, firmware PWM, and a fitted hardware-enable shunt.

No prohibited intentional backfeed path exists on the daughterboard. The published Waveshare schematic distinguishes Type-C `USB0_5V` from board/header `VCC_5V` and shows onboard power-path circuitry, so the Nano path is not undocumented. It does not establish guaranteed reverse-current behavior for every transition, however. The Nano module must still be measured with a current-limited USB source before an unrestricted laptop is used. Failure requires a data-only/debug USB connection or Nano-side power-path modification; the daughterboard cannot access USB VBUS separately through its headers.

The previous vehicle-input audit made three intentional electrical changes:

- moved polarized `C203` from unprotected `VEH_FILTER` to protected `VEH_PROT`;
- added `R206`/`C207` (10 kΩ/82 nF) from LM74800 HGATE to OUT for calculated startup/inrush control;
- added `C607` 1 nF from TPS3808 SENSE to GND.

This simplification pass then made these intentional changes:

- removed the dedicated J101/F101/D101/C101–C103 bench-input path;
- removed both LM74700/Q401/Q402 branch controllers and their associated passives, links, test points, and 230 µF handover reservoir;
- connected the LM5176 output directly to canonical `SYS_24V` and renamed `VEH_PGOOD` to `SYS24_PGOOD`;
- retained the LM74800, LM5176, LM76003, TPS25947, sequencing, DSI, touch-isolation, Nano-feed, and TPS922053 topologies.

## 5. ERC and machine checks

Run with KiCad 10.0.6 on 2026-09-19 after the single-source simplification:

- hierarchical netlist export: passed;
- four-page PDF export: passed;
- pre/post electrical net-map comparison: passed; 25 physical references were intentionally removed, no references were added, and the only retained-pin changes are `VEH_24V`/`VIN_PROT_24V`→`SYS_24V` and `VEH_PGOOD`→`SYS24_PGOOD`;
- DSI, touch, Nano GPIO, LCD sequencing, backlight-current programming, connector pinouts other than removed J101, and USB isolation have identical retained pin/net membership;
- ERC errors: **0**;
- ERC warnings: **0**.

The committed `hardware/kicad/erc-report.txt` is the all-severity report. The former 622 near-coincident/off-grid endpoint violations were removed by replacing fragile long routes with ordinary-grid pin stubs and explicit net labels. `endpoint_off_grid` is enabled as an error and reports zero findings. This pass intentionally prioritizes robust electrical geometry; final owner schematic aesthetics may be adjusted later with netlist/ERC comparison.

## 6. Footprint and 3D closure

All 197 physical BOM entries resolve to a footprint: 187 use standard KiCad libraries and 10 use the committed `Phase2` project library. The manufacturer-specific/project-local assignments include:

| Reference(s) | Project-local land pattern |
|---|---|
| D201 | Bourns DO-218AB for SM8S24CA-Q |
| U201 | TI DRR WSON-12 with exposed pad |
| U301 | TI PWP HTSSOP-28 with exposed pad |
| U502 | TI RPW HotRod QFN-10 |
| J201 | Molex 43045-0218 Micro-Fit header |
| L201 | Bourns SRP1038A body/land pattern |
| U501 | TI RNP WQFN-30 with exposed pad |
| J701 | Amphenol SFW15R-2STE1LF |
| J702 | Molex 505110-4096 |
| U901 | TI DYY TSOT-23-14 |

The exact C601 selection is Nichicon `UHW1A682MHD`, using the standard KiCad 16 mm × 25 mm, 7.5 mm-pitch radial footprint. All mounted-body parts have resolving 3D models. The only 33 physical entries without a body model are 32 bare plated test pads and the J501 solder jumper, for which a 3D body is not appropriate. See `maintainability-library-review.md` for provenance and limitations. The ten project-local footprints completed their independent manufacturer-drawing/pad-number review on 2026-09-20; see `project-local-footprint-verification.md` for corrections and retained rationale.

## 7. Unresolved items by correct phase

### Schematic status after independent audit

- LM74800 common-drain topology is retained for the defined TVS-protected REV1 evaluation input; R206/C207 control direct precharge to 0.23 A nominal/0.46 A worst corner, and the overlapping LM5176 soft-start/full-load bound remains about 2.8 A with Q202 inside SOA;
- TPS3808 pinout, threshold range and recommended SENSE bypass are verified;
- C601 is retained at 6800 µF using actual rail loads and worst-case LM3880 shutdown timing;
- the former 24 V bench hot-plug path no longer exists; LM5176 low-line/current-limit/compensation margins are recalculated for 283.547 µF on `SYS_24V`;
- TPS922053 has about 2.45 V conservative residual headroom at the 23.187 V minimum static `SYS_24V` setpoint and 19.8 V LED corner; regulation and temperature remain prototype validations, not a schematic blocker.

No known electrical issue requires another schematic topology change before PCB work.

### Before placement freeze

- confirm the STEP-inferred Nano DSI bottom-contact face and physical pin 1; the baseline underside-J701 arrangement otherwise resolves to a Type-B cable;
- inspect delivered LCD/touch physical pin 1, bare-tail/receptacle termination, thickness, stiffener, insertion depth and relaxed bend direction; their bottom-contact requirement is confirmed;
- measure the exact socket's mated PCB separation and approve either USB/RJ45 cutouts or taller spacing, standoff hardware and J201 harness clearance;
- check the connector/flex samples at 1:1 as specified in `mechanical-interface-verification.md`; the PCB land-pattern and manufacturer-file geometry audits are complete.

### Prototype bring-up

- tune/verify DSI HS lane rate, video mode, continuous clock, and refresh;
- validate the 600-to-480 masking using test patterns;
- test both GT9271 reset/address sequences and unpowered pin leakage;
- validate 12 V/USB transitions and reverse current toward J201, `SYS_5V`, and laptop VBUS;
- capture startup, commanded shutdown, and hard-unplug rail timing;
- validate backlight regulation at 16.8–19.8 V equivalent LED voltage across the measured `SYS_24V` range, temperature, and PWM range;
- measure converter loop response, efficiency, EMI, and thermal margins.

## 8. Owner actions

There is no owner electrical-design action required before PCB placement begins. Before placement/footprint freeze, the owner must supply or physically verify the connector/cable/stack details listed in Section 7. Those are mechanical facts, not unresolved electrical choices.

PCB layout is outside this phase and has not begun.
