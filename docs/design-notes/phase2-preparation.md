# Phase 2 preparation and engineering validation

**Project:** ESP32-P4 Displayman Development Daughterboard  
**Date:** 2026-09-14  
**Controlling specification:** `docs/PRD.md`, revision 0.2  
**Status:** preparation only — not a schematic release

## 1. Scope and release boundary

This note records the non-blocking work completed while awaiting Displayman's answers. It validates the current Phase 1 component candidates and architecture against the supplied module/Nano documents and current manufacturer documentation. It also identifies corrections and recommended substitutions for Phase 2.

No schematic symbols, nets, footprints, PCB geometry, or other KiCad design content were added. The existing files under `hardware/kicad/` remain the canonical blank project and were inspected read-only.

The following remain prohibited until the blocking vendor information is received and reviewed:

- applying power to the LCD IOVCC pin;
- freezing the DSI host transport settings;
- freezing the buck-versus-buck-boost backlight choice;
- releasing the schematic or beginning PCB layout.

## 2. Executive disposition

| Area | Result of independent validation | Phase 2 disposition |
|---|---|---|
| 24 V input | The protection concept is sound, but the selected barrel jack is mechanically inconsistent with the PRD input requirement and the Schottky diode unnecessarily consumes voltage headroom. | Replace the jack candidate; prefer an ideal-diode controller and N-MOSFET over the series Schottky. Retain fuse and SMBJ30A subject to final inrush/transient calculations. |
| 24 V to 5 V | LM76003 remains suitable and active. Its 3.5 A rating gives 0.5 A / 16.7% current margin over the 3 A design target. | Retain LM76003RNPR and perform the manufacturer design-flow, thermal, loop, and input/output-capacitor calculations during capture. |
| LCD/touch rails | TLV755P and TPS22919 remain electrically suitable. The IOVCC voltage itself remains blocked by UQ-01. | Retain as candidates; keep IOVCC physically unpopulated or inhibited until written approval. Give touch its own switched 3.3 V domain. |
| Sequencing | The required order is valid, but LM3880 is an implementation candidate, not a complete hard-unplug solution. | Add early input-fail detection, an isolated hold-up node, active rail discharge, and hardware reset/backlight clamps. Select the sequencer only after vendor timings are known. |
| USB/backfeed | The Nano contains a USB-to-`VCC_5V` MOSFET path, but its documentation does not authorize arbitrary dual-source operation. USB can keep Nano GPIOs live while all display rails are off. | Add a removable isolation jumper and reverse-blocking/switching in the daughterboard-to-Nano 5 V feed; design all cross-domain signals for Nano-only power. |
| Backlight | TPS92511 is active and electrically valid only when `VLED,max` leaves adequate buck compliance at the protected 21.6 V minimum input. The current typical condition has only 2.4 V gross margin before input-path and switching losses. | Retain TPS92511 as the preferred low-complexity branch only if UQ-03 passes the stated inequality. Use LT8391A four-switch synchronous buck-boost as the technically valid fallback. |
| DSI | The logical mapping is confirmed from the Nano schematic. Current Espressif routing limits are stricter than several provisional PRD targets. | Route straight-through with no swaps, stubs, AC coupling, or common-mode choke; use 100 ohm differential impedance, <=10 mil within-pair skew, <=30 mil pair-to-pair skew, continuous ground, and return vias at transitions. |
| Touch | PCA9306 alone does not satisfy the full no-backpower requirement: it covers only SCL/SDA and depends on EN being low at every invalid power state. | Replace the baseline with a four-channel powered-off-protected switch such as TMUX1574, gated by both-domain-valid logic, for SCL/SDA/INT/RESET. Retain the open-drain reset clamp where useful. |
| GPIOs | The selected GPIO numbers exist and are not strapping pins, but three PRD header-pin labels are wrong. GPIO24 also conflicts with the ESP32-P4 default USB Serial/JTAG function. | Correct header pins before capture. Move `LCD_PWR_EN` from GPIO24 to an unused exposed GPIO, provisionally GPIO20 or GPIO21 after firmware/BSP confirmation. |
| Connectors | The panel and touch connector specifications can be validated. The Nano connector family is plausible, but its exact on-board MPN is absent from the Waveshare schematic. | Retain Molex 505110-4096 and Hirose FH12-8S-0.5SH(55). Keep Nano FFC/contact orientation and board stack height open until physical inspection. |

## 3. Requirements versus implementation choices

The requirements below remain controlling even where a different implementation is recommended.

| Controlling requirement | Current PRD implementation | Validation result |
|---|---|---|
| Accept a regulated, center-positive 24 V +/-10% wall adapter and tolerate accidental reverse polarity. | PJ-044AH, fuse, SS5P6, SMBJ30A | Requirement retained. Connector and reverse-protection components should change. |
| Produce a robust 5 V / 3 A rail for the Nano and local regulators. | LM76003 | Requirement and candidate retained. |
| Apply IOVCC, then VCI, then release reset; reverse the order at shutdown. | LM3880, TPS22919, TPS3808, reset buffer | Sequence retained. Specific sequencer and timing remain choices pending UQ-01/UQ-04. |
| Prevent current injection between Nano and touch domains in every legal power state. | PCA9306 on SCL/SDA | Requirement retained. PCA9306 implementation is not sufficient by itself; isolate all four conductors. |
| Supply 240 mA constant current and PWM dimming without overdriving the module. | TPS92511 buck | Requirement retained. Buck selection is conditional on UQ-03; buck-boost is the fallback. |
| Maintain a low-discontinuity two-lane DSI channel. | Straight-through mapping, optional series footprints, TPD6E05U06 | Requirement retained. ESD part retained; optional resistors may be used only as inline flow-through footprints with negligible stubs. |

## 4. Component revalidation

Lifecycle labels below are manufacturer labels observed on 2026-09-14. Distributor stock is deliberately not treated as a design guarantee.

| Function / present MPN | Manufacturer status and package check | Electrical/suitability result | Recommendation |
|---|---|---|---|
| Barrel jack — Same Sky `PJ-044AH` | Manufacturer identifies a vertical through-hole, 2.0 x 6.5 mm, 5 A jack. | It is not the 5.5 x 2.1 mm-class horizontal jack stated in PRD section 12. | **Substitute.** Switchcraft `RAPC722X` is the leading 24 V/5 A right-angle through-hole candidate for the common 5.5 mm barrel family, but verify the actual adapter plug before footprint freeze.[^1] |
| Fuse — Littelfuse `0451002.MRL` | Current 451-series surface-mount, 2 A/125 V very-fast-acting fuse. | Voltage rating is ample. A very-fast fuse can nuisance-open on bulk-capacitor inrush. | Retain provisionally; freeze after LM76003 soft-start, total bulk capacitance, adapter surge, and fuse time-current/I2t are calculated. |
| Reverse protection — Vishay `SS5P6-M3/86A` | Correct manufacturer family is product 88988; 60 V, 5 A, TO-277A Schottky. The existing reference URL points to the wrong Vishay product. | Electrically valid but dissipates heat and reduces the already small buck-LED headroom. | Prefer `LM74700-Q1` plus a suitably rated low-RDS(on) N-MOSFET. Keep SS5P6 as a low-complexity fallback.[^2] |
| Ideal-diode alternative — TI `LM74700-Q1` | ACTIVE; 3.2–65 V controller in 6/8-pin SOT-23; 20 mV forward-drop regulation and reverse-current blocking. | Well matched to 24 V, preserves backlight headroom, and prevents reverse current toward the adapter. | **Recommended substitution** for SS5P6. Select a >=60 V MOSFET with SOA, surge, thermal, and gate ratings checked in Phase 2.[^3] |
| Input TVS — Littelfuse `SMBJ30A` | Current SMBJ family; 30 V standoff, 33.3–36.8 V breakdown, about 48.4 V maximum clamp at specified surge current, 600 W DO-214AA. | 26.4 V normal maximum is below standoff; published clamp remains below the 65 V absolute ceiling of the main power ICs. This is bench protection, not an automotive qualification claim. | Retain. Verify real source impedance, pulse energy, fuse coordination, and PCB thermal path. |
| 5 V buck — TI `LM76003RNPR` | ACTIVE; 3.5–60 V operating, 65 V maximum, 3.5 A, 30-pin 6 x 4 mm WQFN; PGOOD and adjustable soft start.[^4] | 26.4 V maximum input has 33.6 V operating-range margin; 3 A target has 0.5 A margin. | Retain. Use a 50 V-rated input-capacitor system with DC-bias margin and verify junction temperature at 5 V/3 A. |
| 3.3 V LDO — TI `TLV75533PDBVR` | ACTIVE; fixed 3.3 V, 500 mA, SOT-23-5; soft start, output discharge, current limit.[^5] | Panel 60 mA maximum plus touch 13 mA typical gives about 0.124 W nominal dissipation from 5 V; a 150 mA design load gives about 0.255 W. | Retain, but split or switch the touch branch so touch can be off without backfeed. Recalculate with all support loads. |
| Provisional IOVCC LDO — TI `TLV75518PDBVR` | ACTIVE; fixed 1.8 V, 500 mA, SOT-23-5 with output discharge. | Capacity is ample for the panel's unsplit 60 mA maximum. Voltage cannot be approved while S1's 1.68 V absolute maximum conflicts with its 1.8 V nominal data. | Retain only as provisional/DNP. Do not populate or enable until UQ-01 is answered. |
| VCI switch — TI `TPS22919DCKR` | ACTIVE; 1.6–5.5 V, 1.5 A, 90 mOhm typical, SC70-6, controlled rise and adjustable quick-output discharge.[^6] | More than adequate current and useful for deterministic discharge. | Retain. Select QOD resistor and capacitance against confirmed power-down timing. |
| Sequencer — TI `LM3880MF-1AA/NOPB` | ACTIVE family and exact 6-pin SOT-23 orderable; fixed three-stage behavior. | Orders flags, including reverse sequence, but cannot preserve sequencing after its own supply collapses and does not itself sense 24 V early. | Keep as candidate, not requirement. Freeze after UQ-04 and hold-up calculation; discrete supervisor/logic may be more flexible. |
| Power-fail supervisor — TI `TPS3808G01DBVR` | ACTIVE; adjustable 0.405 V sense, open-drain reset, programmable delay, SOT-23-6. | Suitable when powered from the maintained low-voltage node. It cannot connect directly to 24 V; use a divider and verify pin ratings. | Retain the function; select the exact supervisor with the hold-up/discharge design. |
| Reset buffer — TI `SN74LVC1G07DBVR` | ACTIVE; SOT-23-5 open-drain buffer, overvoltage-tolerant I/O, Ioff partial-power/back-drive protection.[^7] | Suitable for a wired-AND reset clamp pulled up to the destination rail. | Retain where a one-way reset clamp is needed. Do not use it to isolate bidirectional INT. |
| I2C translator — TI `PCA9306DCTR` | ACTIVE VSSOP-8 pass-FET translator. High impedance requires EN low; only SCL/SDA are covered. | It does not guarantee no backpower across all four touch conductors, and two 3.3 V domains do not require translation. | **Replace as baseline.** |
| Touch-domain switch — TI `TMUX1574DYYR` or `TMUX1574PWR` | ACTIVE; 1.5–5.5 V, four bidirectional SPDT channels, powered-off protection to 3.6 V, fail-safe controls, 2 ohm typical on-resistance.[^8] | One device disconnects SCL, SDA, INT, and RESET and tolerates Nano-side signals while its touch-domain supply is off. | **Recommended substitution** for PCA9306, using one throw/channel and hardware enable only when both 3.3 V domains are valid. |
| MIPI ESD — TI `TPD6E05U06RVZR` | ACTIVE; six channels, 14-USON flow-through package, 0.47 pF typical I/O capacitance, up to 6 Gb/s class.[^9] | Channel count covers clock plus two data pairs. Loading is suitable if placement/ground return are excellent. | Retain adjacent to panel connector. |
| Touch ESD — TI `TPD4E05U06DQAR` | ACTIVE; four channels, 10-USON flow-through package, 0.5 pF typical. | Correct conductor count for SCL/SDA/INT/RESET. | Retain adjacent to touch connector, on connector side of isolation. |
| Buck LED driver — TI `TPS92511DDA` | ACTIVE; 4.5–65 V buck, <=500 mA, exposed-pad HSOIC-8, 50–500 kHz, typically +/-3.6% current accuracy. TI lists newer buck-only parts.[^10] | Ratings fit, but topology is conditional on unknown `VLED,max`. Its about 6 us example DIM pulse makes 20 kHz poor for deep dimming. | Retain conditionally. Start firmware validation nearer 1 kHz if used, then tune for flicker/camera behavior. |
| Buck-boost fallback — ADI `LT8391A` | Recommended for new designs; 4–60 V input, 0–60 V output, synchronous four-switch single-inductor LED controller, 600 kHz–2 MHz, PWM dimming.[^11] | Regulates with input above, below, or equal to LED voltage. More complex and uses four external MOSFETs. | Use as the valid fallback if UQ-03 fails the buck criterion. Do not lock until vendor data arrive. |
| Nano DSI connector — Amphenol `SFW15R-2STE1LF` | ACTIVE; 15 position, 1.00 mm, top-contact, side-entry SMT ZIF, 2.7 mm high.[^12] | Matches documented count/pitch. Waveshare S3 omits fitted MPN and contact orientation. | Keep provisional; physical inspection/continuity mandatory. |
| Panel LCD connector — Molex `505110-4096` | 40 circuits, 0.50 mm, bottom contact, front flip, right-angle SMT, 1.90 mm mated height; manufacturer page has limited catalog information.[^13] | Matches the exact part named by Displayman's drawing. | Retain. Final orientation depends on panel FPC presentation/placement. |
| Panel FFC — Molex `0150200429` / `0150200431` | Both 40-circuit, 0.50 mm, type-A same-side-contact; lengths 76 and 102 mm; 0.5 A/contact.[^14] | Electrically compatible. Same-side contacts are documented; length/end presentation are mechanical choices. | Retain as mock-up candidates; do not order production quantity before fit check. |
| Touch connector — Hirose `FH12-8S-0.5SH(55)` | Current listing; 8 position, 0.50 mm, bottom contact, front-actuated ZIF, horizontal insertion, 2.0 mm height, 0.3 mm FPC class.[^15] | Matches circuit count/pitch. | Retain; confirm actual contact side/insertion on sample. |
| Nano sockets — Samtec `SSW-113-02-G-D` | SSW family supports 2 x 13, 2.54 mm vertical through-hole configurations; exact option controls stack height.[^16] | Electrically suitable, but male-header height/clearance are not established. | Keep provisional; choose exact tail/body option after measurement and stack sketch. |

## 5. Power architecture validation

### 5.1 Input protection

Validated functional chain: `24V_JACK` -> `FUSE_2A` -> `IDEAL_DIODE` -> `VIN_PROT_24V`, with `SMBJ30A` and bulk/ceramic capacitance on the protected node. Final TVS placement relative to the ideal-diode MOSFET must follow the selected reference topology and intended reverse-input behavior; this note does not silently prescribe a schematic connection.

At required adapter tolerance:

- `VIN,min = 24 V x 0.90 = 21.6 V`
- `VIN,max = 24 V x 1.10 = 26.4 V`
- LM76003 operating-range margin at maximum input: `60 - 26.4 = 33.6 V`
- approximate published SMBJ30A clamp margin to the 65 V IC absolute ceiling: `65 - 48.4 = 16.6 V`

### 5.2 24 V to 5 V conversion

The 5 V / 3 A ceiling is 15 W. At 90% assumed efficiency, input power is 16.7 W and input current at 21.6 V is about 0.77 A. Adding the 4.608 W typical backlight and control losses leaves expected steady-state input below about 1.1 A. A 2 A adapter/fuse therefore has useful continuous margin. These are architecture estimates, not a substitute for the final LM76003 loss/thermal calculation.

Divide the 5 V rail logically into:

- `SYS_5V`: main buck output;
- `DISPLAY_HOLDUP_5V`: diode/ideal-diode isolated low-load node for sequence logic and LCD/touch regulators;
- `NANO_5V`: separately switched/reverse-blocked feed through a removable jumper.

Keeping Nano transient load off `DISPLAY_HOLDUP_5V` makes hard-unplug sequencing practical without storing energy for the full 3 A system.

### 5.3 LCD VCI, provisional IOVCC, and touch rails

- `LCD_IOVCC` remains separate and sequenced; proposed 1.8 V remains blocked by UQ-01.
- `LCD_VCI` remains switched 3.3 V after IOVCC. TPS22919 controlled rise/discharge supports deterministic sequencing.
- `TOUCH_3V3` should be separately switchable, not an always-on synonym for `LCD_3V3`, establishing a defined off state during Nano USB-only power.
- S1 does not split its 60 mA maximum between VCI and IOVCC. Size both LCD paths for the PRD's >=100 mA requirement and measure actual current at bring-up.

### 5.4 Sequencing and hard unplug

Required order remains: validate maintained supply; enable IOVCC; enable VCI after delay; release hardware reset; initialize in firmware; enable backlight last. Shutdown reverses LCD order and forces backlight off immediately.

A reliable hard-unplug implementation needs:

- divider/supervisor sensing `VIN_PROT_24V` early;
- a low-current `DISPLAY_HOLDUP_5V` reservoir;
- hardware forcing `BL_HW_ENABLE = 0` and asserting LCD/touch reset;
- active discharge/controlled switches guaranteeing VCI falls before IOVCC.

LM3880 orders outputs while powered but cannot create the energy needed to complete shutdown. Initial capacitor sizing is `C >= I x delta_t / delta_V`. For 20 ms and 1.5 V permitted droop:

- 60 mA load: `C >= 800 uF`
- 100 mA load: `C >= 1333 uF`

This demonstrates why hold-up excludes Nano/backlight. Final capacitance, ESR, temperature derating, regulator dropout, and timing depend on UQ-04 and measured load. A nominal 1000–1500 uF is a bench starting range, not a released value.

### 5.5 USB and backfeed state model

| 24 V | Nano USB | Required behavior |
|---|---|---|
| Off | Off | All rails discharged; reset asserted; backlight disabled. |
| On | Off | Daughterboard powers Nano through `NANO_5V`; normal sequence permitted. |
| Off | On | Nano may run, but must not energize `SYS_5V`, LCD, touch, or adapter input. All cross-domain conductors tolerate Nano-side activity without injection. |
| On | On | Allowed only after bench validation. Default build/instructions must permit isolation with the Nano-feed jumper. |

Nano DSI pins 14/15 are `ESP_3V3` references and must never be driven.

## 6. Backlight architecture and calculations

S1 gives 240 mA and 19.2 V typical, so `PLED,typ = 19.2 V x 0.240 A = 4.608 W`. Before protection/switch loss, gross buck headroom at minimum input is only `21.6 - 19.2 = 2.4 V`.

TPS92511 remains acceptable only if the completed worst-case inequality passes:

`VLED,max(cold, 240 mA) + Vdriver_required + Vinput_path_drop + Vcable_drop + Vripple_margin <= 21.6 V`

The ideal diode improves the result versus a series Schottky but cannot establish compliance without `VLED,max`. If it fails or margin is inadequate, use a non-inverting four-switch buck-boost. LT8391A is valid because it regulates when input is above, below, or equal to the LED string.[^11]

The choice can be finalized immediately when Displayman supplies LED Vf min/max at 240 mA over temperature, confirmation that 240 mA is total module current, and any required compliance/PWM restriction.

PWM validation narrowed another internal issue. TPS92511 documents an approximately 6 us DIM pulse example at 500 kHz switching. A 20 kHz period is 50 us, so 6 us corresponds to about 12% duty; at 1 kHz it is about 0.6%. If TPS92511 is retained, begin near 1 kHz and optimize after measuring current pulses, flicker, audible behavior, and camera interaction. Do not treat 20 kHz as finalized.

## 7. MIPI-DSI validation

### 7.1 Confirmed mapping

| Nano J1 pin / net | Panel pin / net | Disposition |
|---|---|---|
| 1 `DSI_D1_N` | 11 `MIPI_1N` | Straight-through |
| 2 `DSI_D1_P` | 12 `MIPI_1P` | Straight-through |
| 4 `DSI_CLK_N` | 14 `MIPI_CLKN` | Straight-through |
| 5 `DSI_CLK_P` | 15 `MIPI_CLKP` | Straight-through |
| 7 `DSI_D0_N` | 8 `MIPI_0N` | Straight-through |
| 8 `DSI_D0_P` | 9 `MIPI_0P` | Straight-through |
| 3, 6, 9, 13 `GND` | panel grounds | Uninterrupted ground plane |
| 10 unlabeled | no use | No connect; verify continuity on sample |
| 11 `ESP_I2C_SCL` / GPIO8 | touch SCL | Through touch isolation, not LCD FPC |
| 12 `ESP_I2C_SDA` / GPIO7 | touch SDA | Through touch isolation, not LCD FPC |
| 14, 15 `ESP_3V3` | Nano reference | Reference only; never drive |

No lane or polarity swap is assumed because neither supplied source authorizes one.

### 7.2 Routing rules from current Espressif guidance

ESP32-P4 supports two DSI lanes, video mode, RGB888/RGB666/RGB565, and up to 1.5 Gb/s/lane.[^17] This confirms host capacity but not panel transport.

Apply:[^18]

- four layers minimum with continuous adjacent ground;
- 100 ohm differential impedance, +/-10%;
- <=10 mil (0.254 mm) within-pair mismatch;
- <=30 mil (0.762 mm) clock/data-pair mismatch where the guidance applies;
- >=3W clearance to unrelated high-speed traces and >=2W between MIPI pairs without ground surround;
- clock ground surround where practical;
- no plane splits/voids under channel;
- avoid signal vias; if unavoidable, symmetric geometry/count plus a ground-return-via pair at each transition;
- ESD at panel connector with short, low-inductance ground and flow-through routing;
- no test pads, branches, long pad neck-downs, common-mode chokes, or AC coupling without SI review.

Optional series footprints may remain only when genuinely inline and included in impedance review. No dangling tuning pads.

S3 shows no separate Nano-side DSI ESD. The complete channel includes Nano PCB/FFC, daughterboard connector/PCB, and panel FFC, so keep the adapter route very short.

UQ-02 remains fully open. Conditional payloads remain useful: RGB888 at the assumed 55 MHz host pixel clock is about 660 Mb/s/lane raw; packed RGB666 is about 495 Mb/s/lane. Protocol overhead, blanking transport, and actual mode remain unconfirmed.

## 8. GT9271 touch-domain validation

Both domains are nominally 3.3 V, so translation is not the goal; preventing partial powering is.

Recommended architecture:

- use all four TMUX1574 channels for SCL, SDA, INT, and RESET;
- power it from `TOUCH_3V3` and keep global enable inactive unless hardware confirms both domains valid;
- leave unused SPDT throws unconnected;
- hold touch RESET low on the touch side while isolated, then enable during the documented address-selection sequence;
- keep TPD4E05U06 on the connector side;
- add only pull-ups proven necessary after measurement, because the Nano already has pull-ups.

This is simpler than an I2C translator plus separate INT/RESET isolation and preserves bidirectional INT.[^8]

S3 also shows GPIO8/SCL and GPIO7/SDA shared with onboard ES8311 and CSI, 2.2 kohm pull-ups in the CSI block, and 22 pF shunts near the codec. Therefore do not add another strong Nano-side pull-up pair; audit total capacitance; check any module pull-ups; and scope VOL/rise time at 100 and 400 kHz.

Measure the unpowered panel from SCL/SDA/INT/RESET to VDD/GND to detect embedded pull-ups/clamps. This is physical characterization, not a request for owner electrical judgment.

## 9. GPIO and Nano schematic audit

### 9.1 Corrected header mapping

| Function | GPIO | PRD P1 pin | S3-confirmed P1 pin | Result |
|---|---:|---:|---:|---|
| `LCD_RESET_CMD_N` | 4 | 12 | **10** | PRD pin incorrect |
| `CTP_RESET_N` | 5 | 9 | **9** | Correct |
| `CTP_INT` | 22 | 16 | **14** | PRD pin incorrect |
| `BL_PWM` | 23 | 7 | **5** | PRD pin incorrect |
| `LCD_PWR_EN` | 24 | 18 | **18** | Correct pin; functional conflict risk |

This is internally resolved: capture must use S3-confirmed pins, not the erroneous PRD header labels.

GPIO4/5/22/23/24 are not strapping GPIO34–38. However, current Espressif guidance assigns GPIO24/25 as default USB Serial/JTAG D-/D+.[^18] Using GPIO24 for `LCD_PWR_EN` would preclude that default function. GPIO23 can be an alternative 50 MHz RMII reference-clock pad; the Nano does not show that selection, but firmware must not enable it while GPIO23 is PWM.

Recommendation: retain GPIO4/5/22/23 with corrected P1 pins; move `LCD_PWR_EN` from GPIO24 to provisionally GPIO20/P1 pin11 or GPIO21/P1 pin13; confirm against the pinned BSP/application during schematic review. No owner electrical preference is needed.

## 10. Connector and mechanical audit

| Interface | Documentation-resolved facts | Still physical/sample dependent |
|---|---|---|
| 24 V | PJ-044AH mismatch confirmed. RAPC722X is 24 V/5 A, right-angle through-hole, 2.0 mm center-pin family; manufacturer lists compatible 2.1 mm plug products.[^1] | Measure/read actual adapter outer/inner size and confirm center-positive. 5.5 x 2.1 and 5.5 x 2.5 are both common. |
| Nano DSI | 15 positions/1.00 mm in S3; Amphenol candidate is active/top-contact.[^12] | Fitted MPN, exposed-contact side, pin-1 view, cable type A/B, insertion direction, length. |
| Panel LCD | S1 names Molex 5051104096; manufacturer confirms 40 positions, 0.50 mm, bottom contact.[^13] | Board face/cable bend, pin 1, contact exposure on sample. |
| Panel FFC | Candidates are 40 way, 0.50 mm, type A same-side, 76/102 mm.[^14] | Select length after mock-up; verify installed mating orientation. |
| Touch | 8 positions/0.50 mm; FH12 candidate is bottom-contact, 0.3 mm FPC, front ZIF.[^15] | Actual thickness, contact/stiffener side, insertion depth, bend radius. |
| Nano headers | 2 x 13/2.54 mm topology; SSW family available.[^16] | Pin length, board gap, underside clearance, standoffs, keepouts. |

## 11. Schematic organization and net naming plan

This is a plan only; KiCad remains blank.

Suggested sheets: `00_system`, `10_input_power`, `20_5v_power`, `30_display_power`, `40_mipi_dsi`, `50_touch`, `60_backlight`, `70_headers_debug`.

Canonical net plan:

- power: `VIN_ADAPTER_24V`, `VIN_PROT_24V`, `SYS_5V`, `DISPLAY_HOLDUP_5V`, `NANO_5V`, `LCD_3V3`, `TOUCH_3V3`, `LCD_IOVCC`, `LCD_VCI`
- valid/enable: `VIN_GOOD`, `SYS_5V_GOOD`, `NANO_3V3_VALID`, `TOUCH_3V3_VALID`, `DISPLAY_PWR_EN`, `BL_HW_ENABLE`
- control: `LCD_RESET_N`, `LCD_RESET_CMD_N`, `CTP_RESET_N`, `CTP_INT`, `BL_PWM`
- DSI: `DSI_D0_P/N`, `DSI_D1_P/N`, `DSI_CLK_P/N`
- touch: `NANO_I2C_SCL/SDA`, `CTP_I2C_SCL/SDA`
- backlight: `LED_ANODE`, `LED_CATHODE`, `LED_SW`, `LED_CURRENT_SENSE` as applicable

## 12. Risk register after validation

### 12.1 Resolved or narrowed internally

- confirmed exact Nano DSI electrical mapping and straight-through lane/polarity assumption;
- confirmed current ESP32-P4 DSI impedance/skew/return-path guidance;
- identified three erroneous P1 header references before copper;
- identified GPIO24 USB Serial/JTAG conflict and reassignment path;
- found PCA9306 insufficient alone and selected a four-conductor powered-off-protected alternative;
- confirmed panel/touch connector pitch, count, and contact location;
- confirmed panel FFCs are same-side type A and differ in length;
- identified barrel-jack mismatch and substitute;
- corrected Vishay reference;
- established a valid four-switch buck-boost fallback;
- established why hard unplug needs stored energy isolated from Nano/backlight;
- narrowed PWM: 20 kHz is not the default if deep TPS92511 dimming is required.

### 12.2 Blocked specifically on Displayman

- **UQ-01:** corrected IOVCC absolute maximum and approved operating voltage.
- **UQ-02:** DSI pixel format, video/burst mode, lane rate, clock behavior, D-PHY range.
- **UQ-03/UQ-09:** LED Vf limits over temperature, compliance margin, total-current confirmation.
- **UQ-04:** VDDI/IOVCC identity and mandatory sequence/timing.
- **UQ-10:** GT9271 INT type and preferred address, if available.
- **UQ-13:** confirmed 600-source to 480-glass mapping.
- original machine-readable initialization export/delay semantics, if available.

Vendor connector recommendations may help, but final board-facing orientation still requires sample verification.

### 12.3 Decisions available immediately after vendor response

1. approve/reject and set IOVCC regulator;
2. choose sequencer/delays and calculate hold-up;
3. set exact ESP-IDF DSI format/mode/clock/lane rate;
4. retain TPS92511 or use LT8391A-class buck-boost;
5. set LED current network, PWM range, and protections;
6. finalize touch reset/address defaults and biasing;
7. make a targeted PRD implementation revision, then authorize capture.

## 13. Actions requiring owner physical input

- confirm actual 24 V adapter outer/inner barrel diameter and center-positive marking;
- photograph/inspect both sides of Nano DSI connector/cable and LCD/touch flex tails with pin-1 marks/exposed contacts;
- measure Nano header pin length, board spacing, mounting holes, and underside clearance;
- choose stack-on versus side-by-side arrangement and cable lengths after a paper/3D mock-up.

No immediate owner electrical-design decision is required while Displayman's reply is pending.

## 14. Sources

[^1]: Same Sky, [PJ-044AH](https://www.sameskydevices.com/product/interconnect/connectors/dc-power-connectors/jacks/pj-044ah); Switchcraft, [RAPC722X](https://www.switchcraft.com/right-angle-pc-mount-dc-power-jack-pin-size-0-080-2-0mm-open-frame/rapc722x/), checked 2026-09-14.
[^2]: Vishay, [SS5P5/SS5P6 product page](https://www.vishay.com/en/product/88988/), checked 2026-09-14.
[^3]: Texas Instruments, [LM74700-Q1, datasheet Rev. G](https://www.ti.com/product/LM74700-Q1), checked 2026-09-14.
[^4]: Texas Instruments, [LM76002/LM76003, datasheet Rev. A](https://www.ti.com/product/LM76003), checked 2026-09-14.
[^5]: Texas Instruments, [TLV755P, datasheet Rev. D](https://www.ti.com/product/TLV755P), checked 2026-09-14.
[^6]: Texas Instruments, [TPS22919, datasheet Rev. B](https://www.ti.com/product/TPS22919), checked 2026-09-14.
[^7]: Texas Instruments, [SN74LVC1G07, datasheet Rev. AG](https://www.ti.com/product/SN74LVC1G07), checked 2026-09-14.
[^8]: Texas Instruments, [TMUX1574, datasheet Rev. C](https://www.ti.com/product/TMUX1574), checked 2026-09-14.
[^9]: Texas Instruments, [TPD6E05U06 and TPDxE05U06 datasheet](https://www.ti.com/product/TPD6E05U06), checked 2026-09-14.
[^10]: Texas Instruments, [TPS92511, datasheet Rev. A](https://www.ti.com/product/TPS92511), checked 2026-09-14.
[^11]: Analog Devices, [LT8391A](https://www.analog.com/en/products/lt8391a.html) and [datasheet Rev. A](https://www.analog.com/media/en/technical-documentation/data-sheets/lt8391a.pdf), checked 2026-09-14.
[^12]: Amphenol Communications Solutions, [SFW15R-2STE1LF](https://www.amphenol-cs.com/product/sfw15r2ste1lf.html), checked 2026-09-14.
[^13]: Molex, [5051104096](https://www.molex.com/en-us/products/part-detail/5051104096), checked 2026-09-14.
[^14]: Molex, [0150200429](https://www.molex.com/en-us/products/part-detail/150200429) and [0150200431](https://www.molex.com/en-us/products/part-detail/150200431), checked 2026-09-14.
[^15]: Hirose, [FH12-8S-0.5SH(55)](https://www.hirose.com/product/p/CL0586-0744-5-55), specifications updated 2026-02-07.
[^16]: Samtec, [SSW connector family/configuration](https://www.samtec.com/products/ssw-113-02-g-d-ll), checked 2026-09-14.
[^17]: Espressif Systems, [ESP32-P4 Series Datasheet v0.7](https://documentation.espressif.com/esp32-p4_datasheet_en.html), 2026-07-14.
[^18]: Espressif Systems, [ESP32-P4 Hardware Design Guidelines v1.9](https://documentation.espressif.com/esp-hardware-design-guidelines/en/latest/esp32p4/esp-hardware-design-guidelines-en-master-esp32p4.pdf), 2026-07-21.
