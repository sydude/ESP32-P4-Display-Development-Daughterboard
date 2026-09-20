# ESP32-P4 Displayman Development Daughterboard — PRD & Schematic

## Phase 1 — Engineering Product Requirements & Design Specification

| Document status | Version / date | Phase |
|---|---|---|
| Approved requirements / schematic baseline | v0.6 • 19 September 2026 | Phase 2 schematic architecture frozen for review; implementation records are maintained in `docs/design-notes/` |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Design decision</strong></p>
<p>The Phase 2 schematic uses one external high-voltage source: the protected nominal-12 V input. The LM5176-Q1 generates the canonical <code>SYS_24V</code> rail for the backlight and LM76003 5 V supply. Bench development uses a regulated/current-limited nominal-12 V supply through this same input and protection path. The former dedicated 24 V barrel-input and dual-source ORing architecture are deleted. Displayman's DSI evidence and UQ-02 disposition remain unchanged.</p></td>
</tr>
</tbody>
</table>

**Target platform:** Waveshare ESP32-P4-NANO + Displayman KD068HDFID009-C009A

### Revision history

| Version | Date | Change |
|---|---|---|
| v0.1 | 13 September 2026 | Initial Phase 1 PRD approved and committed. |
| v0.2 | 13 September 2026 | Recorded Displayman engineering confirmation that the supplied two-lane initialization file, including `RSOX(600)`, is correct for the exact KD068HDFID009-C009A module; narrowed the remaining uncertainty to the 600-to-480 source mapping and unconfirmed DSI transport parameters. |
| v0.3 | 14 September 2026 | Incorporated Displayman's detailed engineering response: fixed 1.8 V IOVCC and 2.8 V VCI; recorded reset/shutdown timing, 16.8–19.8 V / 240 mA backlight limits, confirmed 600-to-480 host mapping, panel-side FPC orientation, and GT9271 INT type. Kept DSI open because the supplied rate is arithmetically impossible and recorded the non-blocking GT9271 address/source-range contradictions. Integrated the independently validated Phase 2 component/GPIO recommendations without beginning schematic capture. |
| v0.4 | 14 September 2026 | Added protected nominal-12 V vehicle evaluation input, four-switch buck-boost conversion to the common 24 V-class bus, dual-source reverse blocking, safe-by-default Nano 5 V eFuse behavior, representative current estimates, vehicle brownout/recovery requirements, and an expanded power-state validation matrix. Automotive qualification remains explicitly out of scope; UQ-02 remains the schematic-release blocker. |
| v0.5 | 15 September 2026 | Added Displayman's 15 September email and LCD timing screenshot as S9; confirmed the 46–60 Hz usable range and that 55 MHz is LCD PCLK; separated confirmed timing from unverified HS-rate claims; reclassified UQ-02 as firmware/prototype bring-up verification; and completed a whole-PRD schematic-readiness and owner-action review. The v0.4 vehicle/bench/USB power architecture is unchanged. |
| v0.6 | 19 September 2026 | Simplified REV1 to one protected nominal-12 V external input for both vehicle evaluation and bench development. Deleted the dedicated 24 V barrel path and LM74700 dual-source ORing; made the LM5176 output the canonical `SYS_24V` rail; and updated the power-state, tolerance, headroom, sequencing, test, component, and verification requirements. |

## 1. Executive summary

This PRD defines a development/evaluation daughterboard that accepts one protected nominal-12 V input for vehicle evaluation or regulated/current-limited bench power, powers the Waveshare ESP32-P4-NANO and the Displayman LCD/touch module, adapts the Nano’s 15-pin two-lane MIPI-DSI interface to the panel’s 40-pin LCD FPC, controls the GT9271 touch controller, and supplies a 240 mA constant-current backlight channel with ESP32-P4 PWM dimming.

The architecture uses the retained vehicle-protection chain and LM5176-Q1 four-switch buck-boost to generate `SYS_24V`, a 5 V / 3 A system buck rail for the Nano and local regulators, fixed 1.8 V IOVCC, fixed 2.8 V VCI, hardware-enforced reset/shutdown behavior, a 24 V-fed constant-current buck LED driver, low-capacitance ESD protection, and deliberately accessible debug points. It is an evaluation design—not an automotive-qualified product.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Resolved finding: IOVCC</strong></p>
<p>Displayman engineering has explicitly approved and recommended 1.8 V nominal IOVCC for this exact module and identified the printed 1.68 V absolute maximum as a datasheet typo; its response states an approximate true absolute maximum of 3.6 V. The design shall therefore use a fixed 1.8 V rail. The response describes the normal 1.8 V operating band as 1.65–1.95 V while also mentioning a 3.3 V upper DC tolerance; this does not authorize a switchable 3.3 V implementation, which is no longer required.</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Resolved for schematic entry; open for DSI bring-up</strong></p>
<p>Displayman confirms RGB888, 600 × 1280 host-active timing, a 55 MHz LCD PCLK reference, two lanes, continuous clock recommended, and approximately 46–60 Hz operation. S9 independently reproduces the timing and identifies 55 MHz as PCLK, not D-PHY HS lane rate. The earlier 110 Mb/s/lane calculation is arithmetically incompatible with RGB888 transport, while the earlier 500 Mb/s/lane maximum has not been substantiated by an authoritative GC9703C source. Neither value shall control the design. The exact known-working HS rate, authoritative controller maximum, and best ESP32-P4 setting remain firmware/prototype parameters. The passive daughterboard channel shall be designed for at least 1.5 Gb/s/lane, matching the ESP32-P4 host capability.</p></td>
</tr>
</tbody>
</table>

### Phase boundary

The Phase 2 schematic is populated and undergoing focused electrical review. Do not begin PCB placement or layout until schematic review is accepted separately.

## 2. Scope, use case, and non-goals

### 2.1 Intended use

- Open-bench bring-up, firmware development, display characterization, touch integration, and thermal evaluation.

- Powered through the keyed nominal-12 V input from either a vehicle source or a regulated/current-limited nominal-12 V desktop/bench supply.

- One Waveshare ESP32-P4-NANO and one KD068HDFID009-C009A module per daughterboard.

- User-accessible connectors, jumpers, indicators, and test points suitable for repeated laboratory use.

### 2.2 In scope

- 15-pin Nano DSI/I²C adapter, 40-pin LCD connector, and 8-pin touch connector.

- Protected nominal-12 V input, 12 V-to-24 V conversion, 5 V/3.3 V/1.8 V conversion, sequenced VCI/IOVCC/reset, and safe-by-default Nano power feed.

- 240 mA total constant-current backlight drive and PWM dimming.

- PCB signal-integrity, power-integrity, mechanical, thermal, test, and firmware-interface requirements.

### 2.3 Explicit non-goals

- Automotive qualification, a claim of ISO 7637-2/ISO 16750 compliance, comprehensive AEC-Q component coverage, functional safety, production EMC certification, or sealed-enclosure design. Vehicle-input evaluation and conservative transient protection are in scope, but qualification requires a defined harness/source impedance and laboratory validation.

- A replacement for the ESP32-P4-NANO; Wi-Fi/C6, audio, camera, Ethernet, USB, and battery functions are outside this daughterboard’s scope.

- Panel optical redesign, LED-string rebalance, display flex modification, or reverse engineering undocumented GC9703C behavior.

- Final schematic, PCB layout, Gerbers, BOM, or firmware driver in Phase 1.

### 2.4 Design life and environment

Prototype target: indoor laboratory and supervised in-vehicle evaluation, 0–50 °C ambient at board level, non-condensing, natural convection, and accessible service protection. Component ratings shall normally be −40–85 °C or wider so the board is not the immediate temperature limitation, but this does not qualify the assembly for automotive service.

## 3. Source basis and interpretation rules

Requirements are derived from the three supplied files, written manufacturer correspondence, and current manufacturer documentation. Supplied files are identified by SHA-256 so later revisions cannot be silently substituted.

| **ID** | **Source**                          | **Revision / identity**                                           | **Use and precedence**                                                                                               |
|--------|-------------------------------------|-------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| S1     | KD068HDFID009-C009A .pdf            | Displayman, v1.0, 2024-11-25 SHA-256 4c8394ac…03bcf               | Primary panel mechanical, pinout, electrical, MIPI, reset, power, touch, and backlight source.                       |
| S2     | KD068HDFID009 -2LANE .txt           | SHA-256 81ec9ab8…e6872c                                           | Primary project-specific two-lane timing and command sequence. Treated as configuration data, not compilable source. |
| S3     | ESP32-P4-NANO-schematic.pdf         | Waveshare schematic PDF created 2024-10-25 SHA-256 1e57b31f…10de1 | Primary Nano connector mapping, header power, and GPIO connectivity source.                                          |
| S4     | ESP32-P4 Series Datasheet v0.7      | Espressif, 2026-07-14                                             | Current SoC limits, GPIO/strapping information.                                                                      |
| S5     | ESP-IDF MIPI DSI LCD API            | Current online documentation checked 2026-09-13                   | DSI host configuration model, lane count/rate, DPI timing fields.                                                    |
| S6     | ESP32-P4 Hardware Design Guidelines | Current online documentation checked 2026-09-13                   | MIPI implementation guidance; Nano already implements the SoC-side D-PHY support circuitry.                          |
| S7     | Displayman email from Anson Ho      | Received 2026-09-13; reports confirmation from Displayman engineering | Confirms S2, including `RSOX(600)`, is correct for the exact KD068HDFID009-C009A module. Does not define the 600-to-480 source mapping or DSI transport parameters. |
| S8     | Displayman email from Anson Ho      | Received 2026-09-14; repository PDF SHA-256 `76a9e533…d4d`          | Detailed answers for IOVCC, sequencing, DSI, backlight, source mapping, FPCs, and touch. Direct confirmations are controlling where internally coherent; contradictions remain explicitly open. |
| S9     | Displayman email and LCD timing screenshot from Anson Ho | Received 2026-09-15; repository Markdown SHA-256 `8823097d…89f4`; image SHA-256 `0e07dbba…97d3` | Confirms strict 60 FPS is unnecessary, approximately 46–60 Hz is usable subject to proper operation, and lower refresh may be used for host bandwidth. Screenshot independently shows 600 × 1280, HBP/HFP/HSW = 40/40/4, VBP/VFP/VSW = 20/36/4, and `LCD_PCLK = 55` MHz. It does not supply a D-PHY HS lane rate or controller limit. |

### 3.1 Interpretation rules

- A specific module pinout or operating limit in S1 overrides generic controller-family information.

- S2 overrides generic timing defaults only where it is internally coherent and electrically compatible with S1.

- A contradiction involving an absolute maximum is never resolved by assumption; it becomes a blocking manufacturer question.

- Derived engineering calculations and board constraints are labeled as such and are not represented as Displayman requirements.

- Current component status was checked against manufacturer pages and authorized-distributor listings on 2026-09-13; availability must be rechecked at procurement.

### 3.2 Source defects already identified

- S1 Section 3.1 is titled as a CTP pin description but contains the 40-pin LCM connector.

- S8 confirms that VDDI in the power-sequence section means connector pin 3 IOVCC.

- S2 includes tool-specific pseudo-functions and malformed lines such as a missing parenthesis in a write_command call; it shall be normalized into a reviewed firmware table rather than compiled verbatim.

- S8 supplies a 16.8–19.8 V backlight range at 240 mA total over temperature and confirms four parallel strings at 60 mA each.

- S8's proposed 110 Mb/s/lane rate cannot transport its confirmed RGB888 timing; it incorrectly treats twice the 55 MHz LCD PCLK as total DSI transport. S9 explicitly identifies 55 MHz as LCD PCLK and does not repeat or validate 110 Mb/s/lane.

- S1/S8 state 80–500 Mb/s/lane, but no authoritative independent GC9703C source has been located to substantiate 500 Mb/s/lane as a controlling controller limit. It remains unverified—not disproven—and shall not constrain PCB capability or be represented as an established GC9703C specification.

- S2's header says VCI = 3.3 V, whereas S8's later power-up instruction specifies VCI = 2.8 V. Both are inside S1's 2.5–3.3 V operating range; this revision adopts S8's explicit 2.8 V instruction and S1's 2.8 V typical value for the board supply.

- S8 says the preferred 7-bit touch address is 0x5D with INT high during reset; S1's timing diagrams assign INT high to 0x14 and INT low to 0x5D.

- S8 confirms that the driver masks 60 dummy host columns on each side, but its detailed source-channel ranges contain an arithmetic inconsistency: `S901–S1500` spans 600 source outputs, not the stated 180. This does not alter the confirmed host requirement of H-active = 600.

## 4. Confirmed display and touch requirements

| **Characteristic**  | **Required / observed value**                                                                                                             | **Basis**           |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| Panel               | Displayman KD068HDFID009-C009A; 6.75 in IPS, normally black                                                                               | S1 pp. 3–5          |
| Physical glass      | 480 RGB × 1280 visible pixels                                                                                                             | S1; S2 comment      |
| Vendor source configuration | Host H-active = 600 × 1280 using `RSOX(600)`; driver masks 60 dummy columns at each side to drive the 480 × 1280 physical glass. The host must transport a 600-wide active line but need not force the discarded columns black. | S2; S7; S8          |
| Timing              | H: 600 configured source positions + 4 sync + 40 back porch + 40 front porch = 684 total; V: 1280 active + 4 sync + 20 back porch + 36 front porch = 1340 total | S2; S7; S8          |
| Pixel clock / frame | Reference `LCD_PCLK` = 55 MHz; derived 55,000,000 ÷ (684 × 1340) = 60.007 Hz. Displayman permits approximately 46–60 Hz subject to proper display operation. | S2; S9; calculation |
| Display controller  | GC9703C                                                                                                                                   | S1                  |
| MIPI interface      | Two data lanes + differential clock                                                                                                       | S1/S2/S3            |
| VCI                 | Fixed 2.8 V nominal per S8 and S1 typical. S2's older 3.3 V header value is within S1 limits but is not used for the board supply.               | S1 §5.2; S2; S8     |
| IOVCC               | Fixed 1.8 V nominal; explicitly approved by Displayman. S8 identifies S1's 1.68 V absolute maximum as a typo and states approximately 3.6 V. | S1 §§5.1–5.2; S2; S8 |
| LCD logic current   | 30 mA typical, 60 mA maximum (datasheet does not split rails)                                                                             | S1 §5.2             |
| Backlight           | 24 white LEDs arranged 6S4P; 240 mA total (60 mA/string); 16.8 V min, 19.2 V typ, 19.8 V max over temperature; constant-current drive | S1 §5.3; S8         |
| Touch controller    | Goodix GT9271; ten-point capacitive touch                                                                                                 | S1 §§2, 7           |
| Touch supply        | 3.3 V target; 2.66–3.47 V allowed; 13 mA typical active                                                                                   | S1 §7.1             |
| Touch bus           | I²C at up to 400 kHz; RESET active low; INT bidirectional during address selection, then open-drain active-low with 2–10 kΩ pull-up to the powered touch domain | S1 §§3.2, 7.2–7.3; S8 |
| Touch addresses     | 7-bit 0x5D or 0x14. S1 maps INT low during reset to 0x5D and INT high to 0x14; S8's opposite parenthetical is treated as a non-blocking contradiction pending sample test. | S1 §7.3; S8         |

### 4.1 DSI payload-rate calculation

S8 confirms RGB888, H-active = 600, and two lanes. S9 independently confirms the 55 MHz value is LCD PCLK and permits approximately 46–60 Hz operation. At the 55 MHz reference timing, the derived frame rate is 60.007 Hz. The active-pixel lower bound at that point is:

`600 × 1280 × 60.007 × 24 ÷ 2 = 553.0 Mb/s/lane`

If the 55 MHz DPI pixel stream is transported continuously, the raw rate is:

`55 MHz × 24 ÷ 2 = 660 Mb/s/lane`

At 46 Hz, the corresponding active-pixel lower bound is approximately `423.9 Mb/s/lane`. Packet overhead and the selected video mode increase the required serialized rate; blanking transport differs between burst and non-burst operation. Therefore these calculations bound plausible configurations but do not establish the exact D-PHY setting.

S8's 110 Mb/s/lane figure incorrectly equates twice the 55 MHz LCD PCLK with the required RGB888 payload rate. Its stated 500 Mb/s/lane maximum is unverified and shall not be treated as a controlling GC9703C limit. Conversely, this analysis does not independently prove that the controller supports 660 Mb/s/lane or any other particular rate. Firmware/prototype bring-up shall choose and validate an ESP32-P4 `lane_bit_rate_mbps` consistent with the confirmed timing and observed panel synchronization. The schematic and PCB shall not be designed around either 110 or 500 Mb/s/lane.

### 4.2 Panel handling

- Do not connect or disconnect the LCD or touch flex while any board rail is powered.

- Use ESD-safe handling and add connector-area protection; the module connector fingers shall not be touched.

- Backlight current shall never exceed 240 mA in normal operation; firmware power-up default is 0% duty.

## 5. System architecture

The daughterboard is partitioned into five zones. This is the controlling Phase-2 architecture unless an approval-gate answer requires a change.

| **Zone**                   | **Inputs**                | **Function**                                                                                 | **Outputs**                                |
|----------------------------|---------------------------|----------------------------------------------------------------------------------------------|--------------------------------------------|
| A. Protected source        | Nominal-12 V input | Fuse, EMI/damping, transient/reverse/OV protection, and LM5176 four-switch buck-boost | SYS_24V |
| B. System power            | SYS_24V              | Existing 60 V synchronous buck; isolated local display regulators; reverse-blocked Nano feed | SYS_5V_3A, TOUCH_3V3, LCD_IOVCC_1V8 |
| C. Sequenced display logic | SYS_5V, LCD_PWR_EN        | Separately controlled VCI/IOVCC rails, reset wired-AND, early power-fail handling             | LCD_IOVCC, LCD_VCI, LCD_RESET_N, LCD_READY |
| D. Video and touch         | Nano DSI/I²C + control GPIOs | Lane-preserving adapter, ESD, four-conductor powered-off isolation, GT9271 reset/address/interrupt | 40-pin LCD FPC, 8-pin touch FPC        |
| E. Backlight               | SYS_24V, BL_PWM      | 65 V-class constant-current buck at 240 mA with disable/fault/current-test provisions         | LED_A, LED_K                               |

### 5.1 Physical integration assumption

The baseline is a stack-on daughterboard using the Nano’s two 2×13, 2.54 mm headers for 5 V, ground, and control GPIOs, plus a short 15-position FFC from the Nano DSI connector to the daughterboard. The panel then connects through its 40-position LCD and 8-position touch flexes. The manufacturer-file audit in `docs/design-notes/mechanical-interface-verification.md` establishes the Nano outline, mounting/header datums and static component envelopes. Daughterboard outline/cutouts, exact stack height, cable exit and moving/service keepouts remain provisional until the listed physical sample checks and mechanical arrangement approval.

### 5.2 Grounding

All daughterboard grounds share one low-impedance ground system. High-current LED and buck-converter return paths shall be confined locally and shall not cross the MIPI or touch reference paths. Connector ground pins shall connect directly into the continuous reference plane with nearby stitching vias.

## 6. Connector and signal assignments

### 6.1 Nano 15-pin DSI connector — source mapping

The following mapping is read directly from S3. Pin numbering and cable contact side must still be checked by continuity on the actual Nano before committing copper.

| **Nano pin** | **S3 net**          | **Daughterboard use**                                        |
|--------------|---------------------|--------------------------------------------------------------|
| 1            | DSI_D1_N            | Panel pin 11 MIPI_1N                                         |
| 2            | DSI_D1_P            | Panel pin 12 MIPI_1P                                         |
| 3            | GND                 | MIPI return / plane                                          |
| 4            | DSI_CLK_N           | Panel pin 14 MIPI_CLKN                                       |
| 5            | DSI_CLK_P           | Panel pin 15 MIPI_CLKP                                       |
| 6            | GND                 | MIPI return / plane                                          |
| 7            | DSI_D0_N            | Panel pin 8 MIPI_0N                                          |
| 8            | DSI_D0_P            | Panel pin 9 MIPI_0P                                          |
| 9            | GND                 | MIPI return / plane                                          |
| 10           | NC / unlabeled      | No connection; verify on hardware                            |
| 11           | ESP_I2C_SCL (GPIO8) | Touch I²C SCL through isolation/ESD                          |
| 12           | ESP_I2C_SDA (GPIO7) | Touch I²C SDA through isolation/ESD                          |
| 13           | GND                 | Logic return / plane                                         |
| 14           | ESP_3V3             | Nano-side logic reference only; do not parallel with TOUCH_3V3 |
| 15           | ESP_3V3             | Nano-side logic reference only; do not parallel with TOUCH_3V3 |

### 6.2 Proposed control GPIO allocation

| **Nano header** | **GPIO** | **Net**         | **Safe-state requirement**                                                           |
|-----------------|----------|-----------------|--------------------------------------------------------------------------------------|
| P1 pin 10       | GPIO4    | LCD_RESET_CMD_N | High impedance must leave panel reset asserted through hardware pull-down/wired-AND. |
| P1 pin 9        | GPIO5    | CTP_RESET_N     | High impedance must hold touch reset low until firmware takes control.               |
| P1 pin 14       | GPIO22   | CTP_INT         | Bidirectional: output during address select, input interrupt afterward.              |
| P1 pin 5        | GPIO23   | BL_PWM          | Default low; no backlight before display initialization.                             |
| P1 pin 11       | GPIO20   | LCD_PWR_EN | Baseline selection; default low. Avoid GPIO24 because it is a default USB Serial/JTAG signal; GPIO21/P1 pin 13 remains the documented alternate if the pinned application reserves GPIO20. |

These GPIOs are exposed on S3 and are not among ESP32-P4 strapping GPIO34–GPIO38 [S4]. The corrected P1 pin numbers above supersede the v0.2 labels. Phase 2 shall use GPIO20 for `LCD_PWR_EN` and verify it against the pinned Nano BSP/application during capture; GPIO21 is the documented alternate. GPIO24 shall remain available for its default USB Serial/JTAG function.

### 6.3 Panel 40-pin LCD connector

| **Pins** | **Panel signal**      | **Board disposition**                                             |
|----------|-----------------------|-------------------------------------------------------------------|
| 1        | NC                    | No connection                                                     |
| 2        | VCI                   | Sequenced fixed 2.8 V                                                |
| 3        | IOVCC                 | Fixed sequenced 1.8 V                                              |
| 4        | GND                   | Ground plane                                                      |
| 5        | RESET                 | 1.8 V-domain reset, active low, wired hardware/firmware control   |
| 6        | NC                    | No connection                                                     |
| 7        | GND                   | Ground plane                                                      |
| 8 / 9    | MIPI_0N / MIPI_0P     | Nano lane 0 N/P; no polarity swap                                 |
| 10       | GND                   | Ground plane                                                      |
| 11 / 12  | MIPI_1N / MIPI_1P     | Nano lane 1 N/P; no lane swap                                     |
| 13       | GND                   | Ground plane                                                      |
| 14 / 15  | MIPI_CLKN / MIPI_CLKP | Nano clock N/P                                                    |
| 16–22    | GND                   | Ground plane; connect all                                         |
| 23–24    | NC                    | No connection                                                     |
| 25       | GND                   | Ground plane                                                      |
| 26–29    | NC                    | No connection                                                     |
| 30       | GND                   | Ground plane                                                      |
| 31–32    | LED−                  | Tie together at connector; constant-current driver cathode output |
| 33–38    | NC                    | No connection                                                     |
| 39–40    | LED+                  | Tie together at connector; filtered protected 24 V anode feed     |

### 6.4 Panel 8-pin touch connector

| **Pin** | **Signal** | **Board disposition**                            |
|---------|------------|--------------------------------------------------|
| 1       | GND        | Ground                                           |
| 2       | NC         | No connection                                    |
| 3       | VDD        | Filtered TOUCH_3V3; local decoupling             |
| 4       | SCL        | I²C through powered-off-protected switch and ESD |
| 5       | SDA        | I²C through powered-off-protected switch and ESD |
| 6       | INT        | GPIO22 through switch; bidirectional during address select, then open-drain active-low; 2–10 kΩ touch-side pull-up |
| 7       | RST        | GPIO5 through switch plus hardware reset clamp; active low |
| 8       | GND        | Ground                                           |

## 7. Power architecture, source isolation, and sequencing

### 7.1 Mandatory power-behavior requirements

The following behaviors are requirements independent of the final controller implementation:

- Accept nominal-12 V power through one keyed connector. A regulated/current-limited nominal-12 V desktop supply uses the same path during bench development; there is no dedicated 24 V external input.

- Prevent DC or transition backfeed from `SYS_24V` through the LM5176 or protection chain toward the 12 V connector, from Nano USB into daughterboard rails, and from daughterboard 5 V into USB VBUS.

- Treat Nano USB connection during 12 V operation as normal. USB-only operation may power the Nano but shall leave the display, touch, backlight, and `SYS_24V` off.

- Force backlight off and panel reset asserted whenever `SYS_24V`, the 5 V rail, or required display rails are invalid. Brownout or cranking may reboot the system, but shall not cause latch-up, rail overshoot, or an uncontrolled backlight pulse.

- Isolate every cross-domain signal so an independently powered Nano cannot phantom-power LCD or touch circuitry and an energized display/touch domain cannot power an unpowered Nano through GPIO, I²C, RESET, INT, or DSI-adjacent logic.

- Recover automatically and deterministically after a valid source returns. Recovery shall execute a complete rail/reset/init sequence; it shall not resume in the middle of panel initialization.

### 7.2 Single-input architecture

The LM5176 output is the canonical `SYS_24V` rail. It directly supplies the 24 V→5 V, display sequencing monitor, and backlight blocks. No high-voltage branch ORing or handover behavior remains.

```mermaid
flowchart LR
  A["12 V input"] --> B["Fuse + EMI + transient / reverse / OV protection"]
  B --> C["LM5176 four-switch buck-boost"]
  C --> D["SYS_24V"]
  D --> E["5 V, display and backlight blocks"]
```

A non-inverting, synchronous four-switch buck-boost is retained. A boost-only stage is not selected: its direct input-to-output path cannot regulate an input excursion above the target bus and complicates isolation during a fast surge or a 24 V misconnection. SEPIC/flyback alternatives add loss, magnetics stress, or unnecessary isolation. `LM5176QPWPRQ1`, an ACTIVE AEC-Q100 4.2–55 V controller, is sized with external 100 V MOSFETs for 30 W continuous output capability.

The external-source boundary retains `LM74800-Q1` and common-drain back-to-back MOSFETs for reverse-polarity and reverse-current isolation. The LM5176 output connects directly to `SYS_24V`; the former LM74700-Q1 branch controllers and branch MOSFETs are not required.

### 7.3 Vehicle-input operating envelope and protection

| Condition | Required behavior |
|---|---|
| 9–18 V continuous at vehicle connector | Full-load regulation to nominal 24.0 V internal vehicle branch; verify thermals at 9 V and maximum system load. |
| Approximately 7–9 V during crank | Converter may drop out or current-limit. Use hysteretic UVLO, nominally about 8.0 V rising / 7.0 V falling, so it does not chatter. Reboot is acceptable. |
| Below UVLO, including deep crank | Vehicle converter off; backlight off; panel reset low; no excessive input current; automatic clean restart after the rising threshold and debounce delay. |
| Above the accepted charging range | Adjustable front-end OV cutoff, provisional 20 V rising, disconnects the converter. Exact divider values and hysteresis are Phase-2 calculations. |
| Positive/negative transients or reverse battery | Survive safely through fuse, bidirectional high-energy TVS, `LM74800-Q1` with back-to-back MOSFETs, input filter, and appropriately rated downstream parts. Qualification to a named ISO pulse is not claimed without a defined test plan. |
| Accidental 24 V on vehicle connector | Front-end OV cutoff shall reject the input without energizing the converter; survival must be verified at 26.4 V before vehicle use. |

Required path order is keyed connector → 5 A time-delay/serviceable fuse → damped input filter → `SM8S24CA-Q` 24 V bidirectional high-energy TVS → `LM74800-Q1` common-drain back-to-back 100 V N-MOSFET protection → `LM5176-Q1` converter → `SYS_24V`. TVS location and filter damping shall be finalized using the selected harness/source impedance so the protection FETs and controller stay within SOA and absolute maximum during clamping.

### 7.4 Rail requirements

| **Rail** | **Nominal / design target** | **Consumers** | **Requirement** |
|---|---|---|---|
| VIN_12V_RAW | 12 V nominal | Input protection | Keyed/latched 2-pin input rated ≥8 A; full vehicle operation 9–18 V; deep-crank reboot permitted; nominal-12 V regulated bench supply accepted. |
| SYS_24V | 24.0 V nominal, 30 W continuous design target | 5 V buck, LED driver, VIN-loss monitor | Direct four-switch buck-boost output. Static setpoint tolerance from the selected feedback reference and 1% divider is 23.19–24.84 V; use a conservative 23.0–25.0 V design envelope for downstream steady-state checks. |
| SYS_5V_3A | 5.0 V, 3 A continuous target | Nano and local LDOs | Existing LM76003 architecture retained. Feed Nano through a true-reverse-blocking, current-limited eFuse; service jumper normally fitted. |
| TOUCH_3V3 | 3.3 V, ≥100 mA | Touch/isolation | Not tied to Nano ESP_3V3; switched, locally decoupled, and isolated when off. |
| LCD_IOVCC | 1.8 V, ≥100 mA | Panel pin 3 | Fixed Displayman-approved voltage; sequence first; controlled discharge. |
| LCD_VCI | 2.8 V, ≥100 mA | Panel pin 2 | Fixed; separately switched after IOVCC. |
| LED_CURRENT | 240 mA total, ±5% target | Panel LED pins | Constant current; default disabled; PWM controllable; no pulse above nominal setpoint. |

### 7.5 Complete-system vehicle load and current budget

The converter is sized for the whole system, not just the backlight. The conservative electrical ceiling is 15 W delivered by the 5 V rail plus 4.752 W LED output at the confirmed 19.8 V maximum, conversion losses, supervisors, and development margin. This yields approximately 22.2 W expected worst-case draw from `SYS_24V`; the converter is designed for 30 W continuous output.

| Vehicle voltage | Assumed vehicle-stage efficiency | Input current at 22.2 W bus load | Input current at 30 W design capacity |
|---:|---:|---:|---:|
| 9.0 V | 88% | 2.80 A | 3.79 A |
| 12.0 V | 90% | 2.06 A | 2.78 A |
| 14.4 V | 92% | 1.68 A | 2.26 A |
| 16.0 V | 92% | 1.51 A | 2.04 A |

These are design estimates, not measured consumption. At the provisional 8 V turn-on threshold, 30 W at 85% would require about 4.41 A; therefore a 5 A time-delay fuse, ≥8 A connector, low-resistance protection path, and approximately 5 A input current limit are appropriate starting points. Full-load operation below 9 V is not required.

### 7.6 Nano 5 V and USB coexistence

The former removable-jumper-only concept is superseded. `SYS_5V_3A` shall feed Nano P1 pins 2/4 through an always-active true-reverse-current-blocking eFuse, provisionally `TPS259470ARPWR`, with approximately 3.2 A current limit, controlled inrush, fault indication, and no dependence on firmware. This blocks Nano/USB-derived 5 V from entering `SYS_5V_3A`. The removable jumper remains a labeled service disconnect, not an operating-mode selector.

Blocking in the opposite direction—Nano `VCC_5V` toward laptop VBUS—depends on the Nano's onboard USB power-path MOSFET. S3 shows that MOSFET path, but Waveshare gives no explicit dual-source rating. Schematic release shall preserve the safe-by-default daughterboard eFuse implementation; prototype release additionally requires a four-quadrant backfeed test at the Nano USB connector. If the Nano path fails that test, the only robust fixes require access to USB VBUS ahead of the Nano path (board modification or a dedicated data-only/debug interface), because USB VBUS is not separately exposed on the Nano headers.

The Nano DSI connector's ESP_3V3 pins remain sense/reference inputs only and shall never be driven.

### 7.7 Required LCD power-up sequence

Hardware and firmware shall jointly implement the following conservative sequence. LM3880 remains a candidate, not a requirement; the final supervisor/sequencer topology must also complete a controlled shutdown from an isolated display hold-up node after removal or switchover of the active source.

| **Step** | **Action** | **Minimum / target delay** | **Enforcement** |
|---|---|---|---|
| 0 | Keep LCD_IOVCC, LCD_VCI, LCD_RESET_N, and backlight off | Until `SYS_24V` and required local rails are valid | Pull-downs + sequencer + firmware defaults |
| 1 | Enable LCD_IOVCC (1.8 V) | After maintained supply is valid | Hardware |
| 2 | Enable LCD_VCI at 2.8 V | 10 ms after IOVCC, conservative target | Hardware |
| 3 | Keep reset low after both rails stabilize | ≥5 ms; rail rise times ≥10 µs | Hardware reset clamp |
| 4 | Release panel reset after ≥10 ms low | S8 minimum 50 µs; S2 uses 10 ms | Hardware + GPIO4 open-drain command |
| 5 | Send reviewed GC9703C init table | ≥10 ms after reset release | Firmware |
| 6 | Sleep Out 0x11, wait ≥120 ms, Display On 0x29 | S2/S8 | Firmware |
| 7 | Enable PWM from 0% and ramp | After valid frames/display-on | Firmware |

### 7.8 Shutdown and hard-unplug behavior

- Normal shutdown: PWM = 0; send 0x28 then 0x10; wait ≥120 ms; assert reset; deassert LCD power.

- Hardware reverse sequence asserts reset first, disables VCI at least 10 ms later, then disables IOVCC at least 10 ms after VCI.

- Early-fail detection shall monitor `SYS_24V`. Crossing its invalid threshold forces immediate hardware backlight disable, panel reset, the ordered stored-energy shutdown, and later full reinitialization.

- The display hold-up node excludes Nano and backlight. Final capacitance, isolation, discharge, and supervisor thresholds shall guarantee reset assertion and ordered rail removal even when firmware is unavailable.

- Input UVLO/OVLO, source removal, USB insertion/removal, or a power-stage fault shall never bypass the hardware backlight disable. Firmware may only enable backlight when bus-valid, display-rail-valid, reset-released, and initialization-complete are all true.

## 8. MIPI-DSI electrical and PCB requirements

### 8.1 Logical routing

- Maintain lane identity and polarity end-to-end: D0N→MIPI_0N, D0P→MIPI_0P, D1N→MIPI_1N, D1P→MIPI_1P, CLKN→MIPI_CLKN, CLKP→MIPI_CLKP.

- No lane swap, P/N swap, branch, test pad, probe stub, common-mode choke, or AC-coupling capacitor may be introduced without an explicit signal-integrity review.

- Provide optional 0201/0402 series-resistor locations in-line near the Nano-side connector, initially populated 0 Ω, consistent with Espressif’s hardware guidance. Pads shall be optimized to minimize discontinuity.

- Place TPD6E05U06RVZR six-channel 0.5 pF ESD protection adjacent to the panel-facing connector with flow-through routing and minimal ground inductance.

### 8.2 Controlled-impedance constraints

| **Constraint**         | **PRD target**                                                                                                       | **Acceptance evidence**                                        |
|------------------------|----------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| Differential impedance | 100 Ω nominal; fabrication tolerance ±10% or tighter                                                                 | Stack-up and field-solver coupon from PCB fabricator           |
| Single-ended reference | 50 Ω nominal for each conductor                                                                                      | Same calculation as above                                      |
| Intra-pair mismatch    | ≤0.15 mm target; ≤0.25 mm absolute on daughterboard                                                                  | KiCad length report                                            |
| Pair-to-pair skew      | Keep CLK, D0, and D1 routed to similar electrical length; ≤5 mm board-only spread target                             | KiCad length report                                            |
| Reference              | Continuous adjacent ground plane; no split/void under traces, pads, or vias                                          | Layout inspection / plane plot                                 |
| Vias                   | Avoid where possible; if required, use the same count and geometry in both legs; target ≤2 signal vias per conductor | Layout inspection                                              |
| Spacing                | At least 3× local trace width to unrelated high-speed nets; maximize spacing from buck/LED switch nodes              | DRC rule + inspection                                          |
| Cable + board channel  | Validate at confirmed operating lane rate; board designed with margin to 1.5 Gb/s per lane                           | Display stress patterns; optional TDR/eye testing if available |

### 8.3 Placement and stack-up

- Minimum four-layer board: L1 signals/components, L2 uninterrupted ground, L3 power/low-speed, L4 signals/components. A six-layer stack may be used if it materially improves uninterrupted routing.

- Place Nano DSI and panel LCD connectors so the three differential pairs form the shortest practical direct corridor.

- Keep the 24 V buck, LED driver, inductors, diodes, switch nodes, and hot-loop copper in a physically separate power zone; no DSI trace may enter or cross that zone.

- Ground stitching shall flank connector transitions and provide a short return for ESD arrays. No high-speed trace shall cross a ground-plane slot created by connector mounting pads.

### 8.4 DSI configuration acceptance

The schematic may proceed without a preselected HS lane rate because it contains no rate-dependent bridge or controller and the passive channel is specified for at least 1.5 Gb/s/lane. Firmware/prototype bring-up shall record and validate: two lanes, selected lane bit rate, pixel-clock source, RGB888 format, video/burst mode, horizontal and vertical timing, refresh rate, and continuous-clock behavior. Begin with the S9 reference timing and continuous clock; if synchronization or bandwidth requires adjustment, evaluate the manufacturer-permitted approximately 46–60 Hz range without changing the confirmed 600 × 1280 host-active geometry or S2 command sequence. The design is not accepted solely because a static image appears; it must pass color bars, checkerboard, numbered-column/cropping patterns, moving gradients, all-white/all-black, and at least a two-hour error-free run across the intended brightness range.

## 9. GT9271 touch requirements

### 9.1 Electrical interface

- Power the module touch VDD from TOUCH_3V3. Do not assume a separately accessible VDDIO; the 8-pin interface exposes only VDD.

- Use all four channels of TMUX1574DYYR between the Nano and touch domains for SCL, SDA, INT, and RESET. Power it from TOUCH_3V3 and enable it only when hardware confirms both domains valid. Translation is not required because both sides are nominally 3.3 V; powered-off isolation is the purpose.

- Provide the S8-required 2–10 kΩ INT pull-up on the touch side. Size any I²C pull-ups only after accounting for the Nano's documented 2.2 kΩ pull-ups, module pull-ups, cable capacitance, and measured rise time; do not automatically parallel another strong Nano-side pair.

- Protect SCL, SDA, INT, and RST at the external touch connector with TPD4E05U06DQAR. ESD placement takes precedence over convenient probing.

- CTP_INT must be a bidirectional GPIO: driven during address selection and reconfigured as interrupt input afterward.

### 9.2 Default address and reset sequence

Default provisionally to the 7-bit address 0x5D using INT low during reset, as shown by S1's `0xBA/0xBB` timing diagram. Firmware shall assert RESET low for at least 100 µs after touch power is valid, drive INT to the address-select state, release RESET, wait more than 5 ms, then wait at least 50 ms before releasing INT and reconfiguring it as an input. Retain the 0x14 procedure using INT high. S8's statement that 0x5D uses INT high contradicts S1 and shall be checked on the real module; the hardware supports either selection.

### 9.3 Firmware behavior

- Probe the selected address after its complete reset sequence. If identification fails, execute the alternate address sequence once and log which address responds; do not merely probe the other address without re-strapping INT and resetting.

- Do not interpret the listed 0xBA/0xBB or 0x28/0x29 values as 7-bit Linux/ESP-IDF addresses; they are 8-bit read/write address bytes.

- Log reset cause, selected address, controller/product ID, firmware version if available, touch count, and interrupt activity for bench diagnosis.

- Expose a touch-reset pushbutton or clearly labeled test pad without allowing it to force an illegal LCD power state.

## 10. Backlight requirements

### 10.1 Driver architecture

Use TI TPS922053DYYR, a current-production 4.5–65 V non-synchronous buck LED driver with an integrated 150 mΩ switch, external differential current sense, spread spectrum, fault output, and fast PWM/hybrid dimming. Feed panel LED+ from filtered `SYS_24V` and regulate the single 240 mA total return at panel LED−. A nominal 200 mV sense threshold gives an initial `R_SENSE = 0.200 / 0.240 = 0.833 Ω`; use a low-temperature-coefficient precision resistor and complete the tolerance, pulse, and thermal calculation in Phase 2.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Headroom condition</strong></p>
<p>S8 confirms 19.8 V maximum LED forward voltage at 240 mA over temperature. At the calculated 23.19 V minimum static <code>SYS_24V</code> setpoint, subtracting the 0.20 V sense drop leaves 3.19 V gross converter headroom. Allowing approximately 0.74 V for switch, diode, bead/wiring, and ripple still leaves about 2.45 V. The required duty remains below the TPS922053 300 kHz / 100 ns minimum-off-time ceiling. The buck architecture is therefore retained; actual panel-Vf, current-regulation, and thermal validation remain prototype checks.</p></td>
</tr>
</tbody>
</table>

### 10.2 Brightness control

- BL_PWM is active high and defaults low by hardware pull-down. No floating input may turn on the backlight.

- Initial firmware target is 20 kHz PWM. TPS922053 specifies fast dimming and a 2,000:1 hybrid-dimming example at 20 kHz; final mode and frequency remain subject to measured low-duty linearity, flicker, audible behavior, and camera interaction.

- Firmware shall clamp command range to 0–100%, start at 0%, and ramp after display-on. It shall never use current overdrive to obtain brightness.

- Provide a hardware backlight-disable jumper and an easily measured DIM/enable test point.

### 10.3 Current, protection, and validation

- Current regulation target: 240 mA ±5% at 100% PWM after component tolerances; never exceed 252 mA during normal tests.

- Provide nonintrusive current-measure access (zero-ohm link or dedicated sense loop) on the LED return; ordinary meter insertion shall not expose the panel to an open-load transient.

- Validate open-load, connector removal while disabled, shorted output, brownout, PWM = 0/100%, and repeated enable/disable behavior. Hot-plugging while enabled is prohibited.

- Thermal test at 24 V, 240 mA, 100% duty for at least one hour in still air; no component may exceed its derated junction/case target or discolor the PCB.

### 10.4 Parallel-string limitation

The module internally parallels four six-LED strings. S8 confirms that the daughterboard shall regulate one 240 mA total current, nominally 60 mA per internal string. The daughterboard cannot observe individual string current sharing, so sample testing shall still check temperature and luminance uniformity.

## 11. Protection, filtering, debug, and PCB implementation

### 11.1 Protection and filtering

- 12 V input: keyed ≥8 A connector, 5 A time-delay fuse, damped input filter, SM8S24CA-Q bidirectional high-energy TVS, LM74800-Q1 with common-drain back-to-back 100 V N-MOSFETs, and adjustable UVLO/OV cutoff. The protected boundary must block reverse battery and reverse current from the converter side.

- `SYS_24V`: LM5176 output capacitance and distributed local bypassing must support loop stability and transients without relying on a source-handover reservoir. Bulk capacitance shall remain inside the validated LM74800 startup/inrush/SOA envelope.

- Regulators and LED driver: local bypassing, short hot loops, exposed-pad thermal via arrays where required, and manufacturer-recommended input/output capacitor types and values.

- Panel logic rails: ferrite-bead option and local high-frequency/bulk decoupling adjacent to connector power pins; populated configuration based on stability and noise analysis.

- No TVS device substitutes may have materially higher capacitance on MIPI lanes without signal-integrity approval.

### 11.2 Required test points

| **Group**  | **Required labeled points**                                                                          |
|------------|------------------------------------------------------------------------------------------------------|
| Power      | VEH_12V_RAW, VEH_PROT, SYS_24V, SYS_5V, NANO_5V, TOUCH_3V3, LCD_IOVCC, LCD_VCI, GND near every group |
| Sequencing | VIN_GOOD, LCD_PWR_EN, SEQ_FLAG1, SEQ_FLAG2, SEQ_FLAG3/LCD_READY, LCD_RESET_N                         |
| Touch      | CTP_SCL, CTP_SDA, CTP_RESET_N, CTP_INT, CTP_3V3                                                      |
| Backlight  | BL_PWM, BL_DIM, LED_A, LED_K, LED current measurement link                                           |
| MIPI       | No ordinary probe pads. Use connector breakout or a purpose-designed high-bandwidth interposer only. |

### 11.3 Development controls

- Nano 5 V service-isolation jumper/link, normally fitted; TPS259470A true-reverse-blocking eFuse remains the default protection and operating control.

- LCD power-enable override with OFF / MCU control positions; no forced-ON position that bypasses reset sequencing.

- Backlight hardware disable and current-set access.

- Reset pushbuttons or pads for LCD and touch, electrically combined with hardware sequencing so pressing a button cannot back-power an unpowered rail.

- Power-good LEDs for 24 V and 5 V, plus low-current indicators for sequenced rails where loading is acceptable. LEDs must not be the only indication of a safe state.

### 11.4 PCB and assembly

- Fabrication: controlled-impedance four-layer minimum, IPC Class 2 prototype workmanship target, ENIG or equivalent fine-pitch-compatible finish, and solder mask dams where fabricator rules permit.

- Separate noisy power and quiet display-interface placement zones; use thermal copper and via arrays per IC datasheets.

- Clearly mark pin 1, cable contact side, both input polarities and voltage ranges, LED hazard, connector reference, rail voltage, jumper default, fuse rating, and board revision on silkscreen.

- Place and space the vehicle transient clamp, protection FETs, converter hot loops, and `SYS_24V` distribution for their calculated peak voltage/current and heat flow. The board is neither mains circuitry nor an automotive-qualified ECU.

- Use keyed/retained connectors where possible; FFC latches must remain reachable with the Nano installed.

### 11.5 KiCad readiness

The native three-sheet Phase 2 hierarchy groups Power; Display Power & Backlight; and Interfaces & Nano. `SYS_24V` is the only downstream high-voltage rail name. Every selected symbol/footprint must be checked against the manufacturer drawing, with pin numbers verified independently before PCB capture.

## 12. Selected components and rationale

These are the preferred Phase-2 design anchors. Supporting inductors, power resistors, capacitors, ferrites, and divider values are intentionally deferred until schematic calculations and manufacturer answers are complete.

| **Function**          | **Preferred manufacturer part number**          | **Key suitability**                                                 | **Status / rationale**                                                             |
|-----------------------|-------------------------------------------------|---------------------------------------------------------------------|------------------------------------------------------------------------------------|
| Vehicle connector     | Molex 43045-0200 header + 43025-0200 housing | Keyed/latching 2-position Micro-Fit 3.0; 8.5 A/contact, −40 to 105 °C header rating | Provisional mechanical selection for evaluation harness; mating terminals and wire gauge selected for ≥5 A. |
| Vehicle fuse          | 5 A time-delay/serviceable fuse, exact holder pending | Coordinates with 30 W stage and ~4.4 A current at 8 V threshold | Requirement fixed; exact fuse/holder remains a mechanical implementation choice after inrush simulation. |
| Vehicle TVS           | Bourns SM8S24CA-Q | 24 V standoff, 38.9 V clamp class, 6.6 kW bidirectional, AEC-Q101 | Preferred high-energy clamp; large DO-218 footprint and pulse/fuse coordination must be validated. |
| Vehicle protection    | TI LM74800QDRRRQ1 + two CSD19531Q5A | 3–65 V controller, reverse input to −65 V, reverse-current and adjustable OV protection; 100 V/6.4 mΩ FETs | ACTIVE controller/FETs; reviewed common-drain back-to-back arrangement retained with calculated SOA/dVdt control. |
| Vehicle buck-boost    | TI LM5176QPWPRQ1 + four CSD19531Q5A | 4.2–55 V synchronous four-switch controller; 24 V/30 W target; 100 V external FETs | ACTIVE/AEC-Q100 controller. Simpler than newer I²C-heavy LM51772-Q1 and adequate for fixed output; magnetics/compensation final in Phase 2. |
| Vehicle inductor      | Coilcraft XAL7030-682MEC class | 6.8 µH, 15 A typical saturation, 6.8 A 40 °C-rise Irms, shielded, AEC-Q200 | Provisional calculation anchor only; final L/value/package follows LM5176 loss and ripple design. |
| Nano 5 V eFuse        | TI TPS259470ARPWR | 2.7–23 V, 5.5 A, 28 mΩ typical, true reverse-current blocking, adjustable current/UV/OV and inrush | Replaces jumper-as-procedure approach; auto-retry variant with ~3.2 A limit is provisional. Service jumper retained. |
| 24 V → 5 V buck       | Texas Instruments LM76003RNPR                   | 3.5–60 V, 3.5 A synchronous buck                                    | Active; adequate 5 V / 3 A target with protection and PGOOD.                       |
| Touch 3.3 V LDO       | Texas Instruments TLV75533PDBVR                 | 500 mA, enable, low-noise/low-IQ LDO                                | Active; ample touch/support current and margin; switched domain isolated from Nano. |
| IOVCC 1.8 V LDO       | Texas Instruments TLV75518PDBVR                 | 500 mA, enable, fixed 1.8 V                                         | Active; default IOVCC source, sequencer controlled.                                |
| VCI source            | Texas Instruments TLV75528PDBVR                | Fixed 2.8 V, 500 mA LDO                                             | Selected from S8's explicit instruction and S1's typical value.                     |
| VCI load switch       | Texas Instruments TPS22919DCKR                  | 1.6–5.5 V, 1.5 A, controlled rise, quick discharge                  | Active family; provides controlled 2.8 V VCI ramp and turn-off discharge.           |
| Rail sequencer        | LM3880MF-1AA/NOPB or discrete supervisor/logic  | Hardware-controlled flags with reverse shutdown capability          | Implementation choice; must meet S8 timing and complete shutdown from isolated hold-up after hard unplug. |
| Power-fail supervisor | Texas Instruments TPS3808G01DBVR                | Adjustable 0.405 V sense, open-drain reset, programmable delay      | Selected to initiate early controlled shutdown; divider/hold-up values in Phase 2. |
| LCD reset buffer      | Texas Instruments SN74LVC1G07DBVR               | Open-drain non-inverting buffer with partial-power-down support     | Selected for wired-AND reset control and 1.8 V pull-up domain.                     |
| Touch-domain isolation | Texas Instruments TMUX1574DYYR                 | Four powered-off-protected bidirectional channels, fail-safe control | Preferred for SCL/SDA/INT/RESET; enabled only when both 3.3 V domains are valid.   |
| MIPI ESD              | Texas Instruments TPD6E05U06RVZR                | Six channels, ~0.5 pF, 5.5 V, up to 6 Gb/s class                    | Active; one part protects D0/D1/CLK conductors with low loading.                   |
| Touch ESD             | Texas Instruments TPD4E05U06DQAR                | Four channels, ~0.5 pF, IEC ESD protection                          | Active; covers SCL/SDA/INT/RST.                                                    |
| Backlight driver      | Texas Instruments TPS922053DYYR                 | 4.5–65 V, 150 mΩ integrated switch, external sense, fault output, fast PWM/hybrid dimming | Preferred for confirmed 16.8–19.8 V / 240 mA load; final 200–300 kHz design must prove worst-case headroom. |
| Nano DSI connector    | Amphenol SFW15R-2STE1LF                         | 15-position, 1.00 mm, top-contact ZIF; active/in stock              | Appropriate for underside stack mounting; baseline same-direction mouth presentation to the STEP-inferred bottom-contact Nano connector uses a Type-B cable. Nano physical pin 1/contact face still requires inspection. |
| Panel LCD connector   | Molex 505110-4096                               | 40-position, 0.50 mm, bottom-contact FD19                           | Matches S8's bottom-contact panel flex; delivered tail pin 1/stiffener/termination still requires inspection. |
| Panel LCD FFC         | Molex 0150200429 (76 mm) or 0150200431 (102 mm) | 40-way, 0.50 mm Type-A Premo-Flex                                   | Conditional extension candidates only; not direct mates to a bare integral panel flex tail. |
| Touch connector       | Hirose FH12-8S-0.5SH(55)                        | 8-position, 0.50 mm, bottom-contact ZIF                             | Electrically consistent with S8; insertion direction and flex presentation still require sample inspection. |
| Stacking sockets      | Samtec SSW-113-02-G-D (two)                     | 2×13, 2.54 mm female socket                                         | Provisional exact mounting/tail option; Nano header grid is confirmed, but mated stack height requires measurement. |

### 12.1 Component selection policy

- Use exact orderable MPNs; no generic ‘or equivalent’ substitutions on regulators, sequencer, reset buffer, ESD arrays, connectors, or LED driver without review.

- All power magnetics and capacitors shall be selected from the IC manufacturer’s calculation and stability requirements, derated for DC bias, ripple current, saturation, temperature, and tolerance.

- Prototype alternates may be added as DNP footprints only when they do not create stubs on MIPI paths or undermine sequencing.

- Procurement shall recheck lifecycle and stock immediately before schematic freeze and again before assembly release.

## 13. Firmware and bring-up requirements

### 13.1 Firmware responsibilities

- Initialize GPIO safe states before enabling the LCD sequence: LCD_PWR_EN = 0, LCD reset asserted, touch reset asserted, BL_PWM = 0.

- Configure the ESP-IDF MIPI DSI bus for two lanes, RGB888, continuous clock initially, and H-active = 600 with the S2/S9 porch timing. Select and validate the HS lane rate during prototype bring-up; do not use S8's 110 Mb/s/lane or its unverified 500 Mb/s/lane value as an established setting or limit.

- Translate S2 into a typed, bounds-checked command table with explicit command length and millisecond delays. Preserve byte order and document every normalized syntax repair.

- Execute panel reset and initialization only after LCD_READY; maintain the 120 ms delays after reset release and Sleep Out as supplied.

- Preserve `RSOX(600)` and configure a 600-pixel-wide transport canvas. S8 confirms that the controller masks/discards 60 host columns at each side to produce the 480-pixel visible image; the discarded values need not be explicitly black. Map the intended 480-pixel application image into the center of the 600-wide transport buffer and clear the ignored columns deterministically during bring-up. Validate with numbered columns, edge markers, and color bars before relying on the crop.

- Initialize GT9271 with the documented reset/INT address selection; configure I²C at no more than 400 kHz.

- Enable backlight only after stable video, starting at zero duty; provide a diagnostic command to set duty, force display reset, read touch ID, and report rail/power-good states.

### 13.2 Initialization-file acceptance

The complete S2 byte sequence remains the authoritative starting point and shall be version-controlled by its SHA-256. S7 confirms that Displayman engineering considers this initialization file correct for the exact module, S8 explains the host-visible 600-to-480 crop, and S9 independently reproduces the 600 × 1280 / 55 MHz timing. `RSOX(600)` shall be preserved. Phase 2/firmware implementation shall produce a machine-readable diff or review report showing that every command byte and delay is represented. Apparent wrapper-syntax errors shall be corrected only at the wrapper level; command payloads shall not be edited without documented evidence. The wrapper-syntax artifacts and best working DSI lane-rate setting remain bring-up items.

### 13.3 Failure behavior

- On init failure, hold backlight off, report an error, and avoid repeated rapid power cycling.

- On touch failure, the display may continue while logging the detected address/reset state.

- On power-good loss, immediately set PWM low and deassert LCD_PWR_EN; hardware must complete the safe sequence even if firmware stalls.

- Watchdog/reset events shall restore safe GPIO defaults before panel rails or backlight can re-enable.

## 14. Unresolved questions, conflicts, and assumptions

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Schematic-dependency rule</strong></p>
<p>An item blocks schematic capture only if its answer can materially change electrical safety, absolute-maximum compliance, power or isolation topology, rail sequencing, connector/header pin mapping, DSI physical connectivity, backlight requirements, component selection, GPIO allocation, or schematic nets. Mechanical, footprint, firmware, and prototype-validation items remain open in their assigned phase. No open item in this revision meets the schematic-blocker test.</p></td>
</tr>
</tbody>
</table>

| **ID / severity** | **Question or conflict**                                                                                                  | **Current evidence**                                                                                                       | **Proposed disposition / owner**                                                                                          |
|-------------------|---------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| UQ-01 CLOSED      | What is the correct IOVCC absolute-maximum rating, and is 1.8 V nominal explicitly approved?                              | S8 explicitly approves/recommends 1.8 V and identifies S1's 1.68 V absolute maximum as a typo; stated true limit is approximately 3.6 V. | Use fixed 1.8 V; do not implement user-selectable 3.3 V IOVCC. Record S8 as the controlled correction until a revised datasheet exists. |
| UQ-02 OPEN / BRING-UP | What exact HS lane rate did Displayman's known-working host use, what is the authoritative GC9703C maximum, and which ESP32-P4 setting gives best operation? | S8 confirms RGB888, 600 × 1280, two lanes, and continuous-clock recommendation but gives an invalid 110 Mb/s/lane calculation and an independently unverified 500 Mb/s/lane ceiling. S9 confirms 55 MHz is LCD PCLK, the exact porches, and approximately 46–60 Hz operation. Active-only bounds are ≈423.9 Mb/s/lane at 46 Hz and ≈553.0 Mb/s/lane at 60.007 Hz; a continuous 55 MHz RGB888 stream is 660 Mb/s/lane before overhead. | Not a schematic blocker: no bridge/component selection depends on the value, and the passive channel is required to support at least the ESP32-P4's 1.5 Gb/s/lane capability. Firmware shall select and validate the working rate/refresh/mode on the prototype. Do not design around 110 or 500 Mb/s/lane. |
| UQ-03 CLOSED      | What are LED-string VF min/max over current and temperature, and required driver headroom?                                | S8 gives 16.8 V minimum, 19.2 V typical, and 19.8 V maximum at 240 mA over temperature. The regulated `SYS_24V` minimum is 23.19 V before ripple/transient allowance. | Retain TPS922053 at 300 kHz; calculated worst-static gross headroom after the 0.20 V sense drop is 3.19 V, with about 2.45 V remaining after conservative conduction and ripple allowance. Validate on the prototype. |
| UQ-04 CLOSED      | What VCI voltage and reset/rail ordering apply?                                                                              | S8 confirms VDDI = IOVCC, specifies 1.8 V IOVCC and 2.8 V VCI, reset low through ramp, ≥5 ms rail-stable delay, ≥50 µs reset pulse, and ≥120 ms normal shutdown wait. S1 permits 2.8 V VCI and shows conservative rail ordering. | Use 2.8 V VCI and conservative IOVCC→VCI→reset power-up, reset→VCI→IOVCC power-down, early fail detection, and isolated hold-up. The older S2 3.3 V header value is documented but does not block this safe implementation. |
| UQ-05 NARROWED / PHYSICAL | What are the LCD, touch and Nano DSI physical pin-1/contact presentations? | S8 confirms bottom-contact 40-pin and 8-pin module flexes. A section through the Waveshare STEP shows a bottom-contact Nano DSI connector; selected top-contact J701 is compatible on the daughterboard underside and the baseline same-direction mouth arrangement uses a Type-B cable. Manufacturer mechanical files do not encode Nano physical pin 1 or the delivered panel-tail pin-1/stiffener details. | Inspect/continuity-check Nano J1 pin 1/contact face and inspect the exact LCD/touch tails before placement freeze; no connector-type or electrical-map change is indicated. |
| UQ-06 OPEN / PROTOTYPE | Is Nano J1 pin 10 intentionally NC, and are pins 14/15 safe reference-only 3.3 V outputs?                                 | S3 shows pin 10 unlabeled; 14/15 tied to ESP_3V3.                                                                          | Capture pin 10 as NC and pins 14/15 as sense/reference-only, never driven. Verify with Waveshare or powered-off continuity before prototype connection; no active schematic function depends on them. |
| UQ-07 OPEN / BRING-UP | What is the maximum sustained and transient 5 V current of the exact Nano build?                                          | S3 shows 5 V input and onboard conversion but no board-level input-current rating.                                         | The conservative 3 A architecture is sufficient for capture. Measure boot, CPU/PSRAM load, C6 activity, USB, and peripherals before final protection/thermal validation. |
| UQ-08 OPEN / PROTOTYPE | Does the Nano onboard USB-to-VCC_5V MOSFET guarantee zero reverse current from the externally driven 5 V header to laptop VBUS over all power transitions? | S3 shows a MOSFET power path but Waveshare provides no explicit dual-source guarantee; USB VBUS is not separately exposed at the headers. | Concurrent USB is a mandatory normal mode. Use TPS259470A from SYS_5V to NANO_5V for the Nano→daughterboard blocking direction; verify the Nano's opposite direction by four-quadrant voltage/current test before prototype release. If it fails, use the documented data-only/Nano USB-boundary modification contingency. |
| UQ-09 CLOSED      | Does the panel accept one 240 mA total sink for the internal four parallel strings?                                       | S8 confirms 240 mA total and 60 mA per each of four parallel strings.                                                      | Set one 240 mA total current channel; validate temperature and uniformity on samples.                                      |
| UQ-10 MEDIUM      | Is 0x5D the desired default GT9271 address, and what INT behavior applies?                                                | S8 confirms open-drain active-low INT after initialization and a 2–10 kΩ pull-up, but says 0x5D uses INT high during reset; S1 maps INT high to 0x14 and low to 0x5D. | Hardware supports both. Default provisionally to S1's 0x5D/INT-low timing, retry 0x14 only through a complete reset sequence, and confirm on the sample or through corrected vendor guidance. |
| UQ-11 NARROWED / PHYSICAL | Which exact socket height, cutout arrangement and cable lengths complete the stack? | Waveshare PDF/DXF/STEP establish a 50 × 50 mm board, four Ø2.70 mm holes, exact 2×13 grids and component envelopes. USB-A reaches +14.45 mm and RJ45 +13.60 mm above the Nano board plane, so an ordinary full-overlap low stack is not viable without cutouts or greater separation. | Measure the exact mated socket/PCB separation and approve cutouts or taller spacing using a 1:1 mock-up before layout. |
| UQ-12 NARROWED / SCHEMATIC REVIEW | Are GPIO4/5/22/23 and baseline GPIO20 free in the pinned firmware/BSP? | They are exposed and not strapping pins. GPIO24 was removed because it is the default USB Serial/JTAG D− pin; GPIO21 is an available alternate to GPIO20. | Capture GPIO20 as the `LCD_PWR_EN` baseline and run the pinned-BSP conflict check during schematic review. This is an engineering verification within Phase 2, not an owner preference or pre-capture blocker. |
| UQ-13 NARROWED    | Is the detailed source-channel numbering in S8 correct?                                                                    | S8 confirms H-active = 600 and internal masking of 60 host columns per side, so the host requirement is resolved. Its `S901–S1500` range spans 600 source outputs rather than the stated 180. | Implement the confirmed 600-wide transport/central 480-visible crop and validate with numbered-column patterns. Seek a corrected source-channel diagram, but this arithmetic defect does not block schematic capture. |
| UQ-14 MEDIUM      | Which S2 syntax lines are transcription artifacts versus tool-specific grammar?                                           | File contains pseudo-code and malformed parentheses but payload appears structured.                                        | Normalize wrapper syntax only; preserve command bytes; request original vendor project/export if available.               |
| UQ-15 HIGH        | Does the selected vehicle protection network survive the intended harness/source transient energy and recover without overstressing the TVS, FETs, fuse, or converter? | Component voltage ratings and topology are adequate on paper, but transient energy depends on vehicle/harness/source impedance and pulse duration. | Complete SPICE/reference-design checks, then bench-test defined positive/negative, reverse-polarity, crank, jump/miswire, and hot-plug cases. Do not claim ISO compliance from component ratings alone. |
| UQ-16 MEDIUM      | What exact vehicle connector, fuse holder, cable gauge, and harness length will be used? | Micro-Fit 43045-0200/43025-0200 and 5 A protection are suitable evaluation defaults, but harness mechanics affect inrush, EMI, and TVS stress. | Use provisional parts for schematic planning; freeze only after the physical harness is selected/measured. This is not a DSI schematic-release blocker. |
| A-01 ASSUMPTION   | Bench-supply characteristics | Bench development now uses the same J201 nominal-12 V input as vehicle evaluation. | Use a regulated/current-limited nominal-12 V desktop supply capable of at least 5 A for full-load work; observe J201 polarity and do not bypass the input protection. |
| A-02 ASSUMPTION   | Prototype environment | User specified development/evaluation use, now including vehicle-power evaluation. | Use supervised 0–50 °C board-level evaluation; no production/qualification claim. |
| A-03 ASSUMPTION   | Vehicle electrical envelope | No specific vehicle/harness was identified. | Design for full-load 9–18 V operation, hysteretic dropout below about 7–8 V, and OV rejection above about 20 V. Validate actual vehicle/harness waveforms before connection. |

## 15. Verification and acceptance plan

### 15.1 Pre-assembly design checks

- Independent pin-number audit against connector manufacturer drawings and actual mating orientation.

- Schematic ERC; netlist cross-check against Sections 6 and 7; no NC panel pin connected.

- Power-stage calculations at 9/12/14.4/16/18 V input and the calculated 23.19–24.84 V `SYS_24V` range; converter loss, SOA, transient-clamp/fuse coordination, fault stress, thermal and derating review.

- Controlled-impedance stack-up approved by fabricator; MIPI pair geometry and length report attached to layout review.

- 3D/mechanical check with actual Nano, panel flexes, cable bend radius, latch access, and standoff clearances.

### 15.2 Bring-up sequence

| **Stage**          | **Method**                                                                            | **Pass criteria**                                                             |
|--------------------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| 1\. Unpowered      | Continuity, resistance-to-ground, connector orientation, fuse and polarity inspection | No shorts; correct pin mapping; Nano 3.3 V not driven.                        |
| 2\. Protected source | Current-limited nominal-12 V bench supply, no Nano/panel | Correct polarity, UV/OV/reverse behavior, low idle current, no reverse current toward J201. |
| 2a\. Vehicle faults | Programmed dips, slow ramps, reverse input, 24 V misconnection, defined surge pulses | Safe cutoff/dropout, no overstress, backlight off, automatic deterministic recovery. |
| 3\. Rails unloaded | Scope 5 V, 3.3 V, 1.8 V; toggle enables                                               | Within tolerance; stable; expected ripple; no overshoot above device limits.  |
| 4\. Sequencing     | Four-channel scope on IOVCC, VCI, RESET, VIN_GOOD; plug/unplug and brownout           | Order and delays meet Section 7 in both directions, including abrupt removal. |
| 5\. Nano           | Connect Nano with panel absent; exercise CPU/C6/USB loads                             | 5 V regulation, thermal, and no USB backfeed violation.                       |
| 6\. Panel logic    | Panel connected, backlight hardware-disabled                                          | Correct reset/init traffic; valid MIPI video without rail disturbance.        |
| 7\. Touch          | Address select, ID read, interrupt and 10-point test                                  | Stable ≤400 kHz I²C; no stuck bus; correct coordinates/orientation.           |
| 8\. Backlight      | Electronic load/dummy LED first, then panel; ramp to 240 mA                           | ±5% current, PWM behavior, no overcurrent/overshoot, acceptable temperature.  |
| 9\. System stress  | Two-hour moving patterns, repeated resets, 0–100% brightness, input min/max           | No artifacts, resets, touch errors, or thermal limit violations.              |

### 15.3 Required instruments

- Current-limited laboratory supplies capable of 0–30 V and ≥5 A for independent/simultaneous source tests; calibrated DMM; ≥4-channel oscilloscope with suitable passive/differential probes.

- Electronic load or protected dummy LED load for current-driver validation before connecting the panel.

- Thermocouples or thermal camera; ESD-safe workstation; optional TDR/high-bandwidth probe for MIPI channel characterization.

### 15.4 Release criteria

- No open item fails the schematic-dependency rule; all deferred items have an explicit firmware, mechanical, footprint, or prototype-validation owner.

- All rails and sequences measured on a real prototype, including hard-unplug behavior.

- Backlight current and worst-case headroom verified with actual panels at the expected temperature range.

- DSI operates error-free at confirmed format/rate; touch passes ten-point and reset/address tests.

- As-built BOM, schematic, PCB revision, firmware init-table hash, and test report cross-reference one another.

## 16. Requirements traceability

| **User requirement**                        | **PRD implementation**                                                | **Primary acceptance**                       |
|---------------------------------------------|-----------------------------------------------------------------------|----------------------------------------------|
| Adapt Nano 15-pin two-lane DSI to panel FPC | Sections 6.1 and 6.3; exact lane/polarity map and selected connectors | Pin audit + continuity + display test        |
| Correct DSI routing                         | Section 8 controlled impedance, skew, reference, ESD, no stubs        | Fabricator stack-up + DRC + stress patterns  |
| GT9271 I²C/reset/INT                        | Sections 6.4 and 9; 3.3 V, isolation, address sequence                | ID/address/interrupt/ten-point test          |
| LCD rails and sequence                      | Section 7; fixed 1.8 V IOVCC, separately controlled VCI, reset clamp, hard-unplug hold-up | Four-channel oscilloscope capture |
| Single nominal-12 V input                    | Sections 7.2–7.5; LM74800 + LM5176 four-switch path                  | 9–18 V load/thermal test; UV/OV/reverse/surge tests; regulated 12 V bench operation |
| USB simultaneous operation                   | TPS259470A Nano feed plus Nano USB-path verification                  | USB-only and USB+12 V backfeed tests |
| Power Nano and LCD                          | 5 V / 3 A buck plus local LDOs and isolated Nano feed                 | Load, ripple, USB coexistence, thermal test  |
| 240 mA / 16.8–19.8 V 6S4P backlight         | Section 10; TPS922053 buck with external precision sense and fault output | Dummy load then panel current/headroom test |
| ESP PWM brightness                          | GPIO23 BL_PWM, default-off, initial 20 kHz fast/hybrid-dimming target | Duty sweep, flicker/linearity, reset default |
| Protection/filtering/decoupling/test        | Section 11 and component table                                        | Inspection, fault test, ripple/ESD review    |
| Bench-development board                     | Section 2 scope; jumpers, test points, no automotive claim            | Design review and labeling                   |
| Identify conflicts/assumptions              | Section 14; UQ-02 explicitly retained as a bring-up parameter          | Dependency classification + prototype record |
| Real/current components                     | Section 12 with MPNs and manufacturer-source checks                   | Lifecycle/stock recheck at procurement       |

### 16.1 Phase-2 schematic review checklist

- The v0.6 single-source architecture is reflected in the canonical schematic and supporting calculations.

- No true schematic-release blocker remains. UQ-02 is intentionally open for firmware/prototype validation; UQ-01, UQ-03, and UQ-04 are closed, and the panel-side electrical portion of UQ-05 is closed.

- GPIO allocation remains checked against the pinned BSP during schematic review; GPIO20 is captured and GPIO21 remains the documented alternate.

- Exact Nano/panel samples and mechanical architecture are required before footprint/PCB placement freeze, not before schematic capture.

- Final vehicle/bench harness mechanics are required before footprint/PCB placement freeze; electrical requirements and the provisional connector family are sufficient for capture.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Current phase boundary</strong></p>
<p>The v0.6 requirements are implemented in the Phase 2 schematic and are awaiting review. PCB placement/layout has not begun and requires separate authorization. Footprint/placement freeze and prototype release retain their physical and validation gates.</p></td>
</tr>
</tbody>
</table>

## 17. Optional manufacturer follow-up / bring-up information

S8 and S9 answer enough to begin hardware capture. The questions below remain useful for firmware records and prototype efficiency, but none is a schematic-release gate. Do not resend questions that S8/S9 resolved.

| **\#** | **Question to Displayman** |
|--------|-----------------------------|
| 1 | For the known-working two-lane RGB888 host, please provide the actual **D-PHY HS data-lane bit-rate setting in Mb/s per lane**, video-mode/burst setting, and clock-mode setting. Please also identify an authoritative source for any claimed GC9703C maximum. S9 establishes that 55 MHz is LCD PCLK and that approximately 46–60 Hz is usable; neither 110 nor 500 Mb/s/lane will be treated as an established hardware setting/limit without coherent supporting data. |
| 2 | For record consistency, please confirm that S8's 2.8 V VCI instruction supersedes the S2 header's 3.3 V test value. The board will use 2.8 V, which is S1's typical value and lies inside its operating range. Please also confirm whether IOVCC and VCI may rise together or must be ordered, and whether power-down requires VCI to fall before IOVCC after RESET is low. This clarification is not required to implement the conservative sequence. |
| 3 | S1's GT9271 timing diagrams map INT high during reset to 7-bit address 0x14 (`0x28/0x29`) and INT low to 0x5D (`0xBA/0xBB`), but S8 says 0x5D uses INT high. Please confirm the correct INT level for each 7-bit address. |
| 4 | S8 says source lines `S1–S180` and `S901–S1500` represent 180 dummy subpixels on each side, but `S901–S1500` contains 600 source outputs. The host-side 600-wide/60-column-per-side crop is understood; please provide a corrected source-channel range or diagram for the record. This item is not a schematic blocker. |
| 5 | If available, please provide the original machine-readable initialization export or corrected C-style sequence, including exact delays and any required read-back/error check. Command payload bytes will otherwise be preserved from S2. |

## 18. References

### Supplied sources

- S1 — Displayman (SZ) Technology Co., Ltd., KD068HDFID009-C009A datasheet, v1.0, 25 November 2024, 40 pages (user supplied).

- S2 — KD068HDFID009 -2LANE initialization file (user supplied).

- S3 — Waveshare ESP32-P4-NANO schematic, PDF created 25 October 2024 (user supplied).

- S7 — Email from Anson Ho, Displayman (SZ) Technology Co., Ltd., received 13 September 2026; reports that Displayman engineering confirmed the supplied two-lane initialization file is correct for the exact KD068HDFID009-C009A module. This confirmation includes retaining `RSOX(600)` but does not explain the 600-to-480 mapping or supply the required DSI transport parameters.

- S8 — Email from Anson Ho, Displayman (SZ) Technology Co., Ltd., received 14 September 2026; detailed engineering response stored as `docs/design-notes/Re- Displayman | Datasheet & Evaluation Units for KD068HDFID009-C009A.pdf`, SHA-256 `76a9e53303412ff29189debf72a1f4c5dcf495e249f0ce86e32092063407ed4d`.

- S9 — Follow-up email from Anson Ho, Displayman (SZ) Technology Co., Ltd., received 15 September 2026, plus reference LCD timing screenshot; stored as `docs/design-notes/email response from displayman on 9-15-2026.md` (SHA-256 `8823097df6d8f23fd516d2b6e0f963860ce33b882156e1e74eb6324d2f1189f4`) and `docs/design-notes/email response from displayman on 9-15-2026 [IMAGE].jpg` (SHA-256 `0e07dbbabf7c044b3f3cbf885d786e36a1ac6d44cc7af4ac6fe7aa517a8977d3`).

### Manufacturer documentation checked through 15 September 2026

**Espressif:** [ESP32-P4 Series Datasheet](https://documentation.espressif.com/esp32-p4_datasheet_en.html); [ESP-IDF MIPI DSI LCD API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/peripherals/lcd/dsi_lcd.html); [ESP32-P4 Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32p4/schematic-checklist-esp32p4.html)

**Display corroboration:** [Displayman bar-type product listing](https://displayman.com/bar-type-tft-lcd-displays/) for exact C009A identity/interface; [KD068HDFID009 third-party family listing](https://en.tft-tft.com/product/1658-KD068HDFID009-6.8-inch-480x1280-2-Lane-MIPI-interface-GC9703C-Bar-Type-TFT-high-brightness-IPS-LCD-Module.html); [KD068HDFID020 sibling listing](https://www.tft-tft.com/product/detail?id=899) for the related GC9703C 3/4-lane platform. The latter two are corroborative only and do not establish an HS lane-rate limit.

**Texas Instruments:** [LM5176-Q1](https://www.ti.com/product/LM5176-Q1); [LM74800-Q1](https://www.ti.com/product/LM74800-Q1); [LM76003](https://www.ti.com/product/LM76003); [TPS922053](https://www.ti.com/product/TPS922053); [LM3880](https://www.ti.com/product/LM3880); [TPS3808](https://www.ti.com/product/TPS3808); [TPS22919](https://www.ti.com/product/TPS22919); [TLV755P](https://www.ti.com/product/TLV755P); [TMUX1574](https://www.ti.com/product/TMUX1574); [SN74LVC1G07](https://www.ti.com/product/SN74LVC1G07); [TPD6E05U06](https://www.ti.com/product/TPD6E05U06); [TPD4E05U06](https://www.ti.com/product/TPD4E05U06)

**Connectors and protection:** [Molex 505110-4096](https://www.molex.com/en-us/products/part-detail/5051104096); [Amphenol SFW15R-2STE1LF](https://www.amphenol-cs.com/product/sfw15r2ste1lf.html); [Hirose FH12-8S-0.5SH(55)](https://www.hirose.com/product/p/CL0586-0744-5-55); [Molex Micro-Fit 3.0 43045-0200](https://www.molex.com/en-us/products/part-detail/430450200); [Bourns SM8S24CA-Q](https://www.bourns.com/products/diodes/tvs-diodes/automotive-power-tvs-diodes/product/SM8S-Q)

*Authorized-distributor stock is a procurement snapshot, not a design guarantee. Manufacturer electrical data—not distributor summaries—controls electrical design.*
