# ESP32-P4 Displayman Development Daughterboard — PRD & Schematic

## Phase 1 — Engineering Product Requirements & Design Specification

| Document status | Version / date | Phase |
|---|---|---|
| Phase 1 approved | v0.2 • 13 September 2026 | PRD only |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Design decision</strong></p>
<p>The daughterboard is technically plausible, but schematic capture must not begin until the blocking Displayman electrical ambiguities and cable-contact orientation are closed. This document specifies the intended architecture, requirements, selected components, verification plan, and approval gates; it intentionally does not provide a circuit schematic.</p></td>
</tr>
</tbody>
</table>

**Target platform:** Waveshare ESP32-P4-NANO + Displayman KD068HDFID009-C009A

### Revision history

| Version | Date | Change |
|---|---|---|
| v0.1 | 13 September 2026 | Initial Phase 1 PRD approved and committed. |
| v0.2 | 13 September 2026 | Recorded Displayman engineering confirmation that the supplied two-lane initialization file, including `RSOX(600)`, is correct for the exact KD068HDFID009-C009A module; narrowed the remaining uncertainty to the 600-to-480 source mapping and unconfirmed DSI transport parameters. |

## 1. Executive summary

This PRD defines a bench-development daughterboard that accepts a regulated 24 V wall-adapter input, powers the Waveshare ESP32-P4-NANO and the Displayman LCD/touch module, adapts the Nano’s 15-pin two-lane MIPI-DSI interface to the panel’s 40-pin LCD FPC, controls the GT9271 touch controller, and supplies a 240 mA constant-current backlight channel with ESP32-P4 PWM dimming.

The recommended architecture uses a protected 24 V input, a 5 V / 3 A system buck rail for the Nano and local regulators, separate 3.3 V and 1.8 V display rails, a three-stage hardware sequencer, a 24 V-fed constant-current buck LED driver, low-capacitance ESD protection, and deliberately accessible debug points. It is an evaluation design—not an automotive-qualified product.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Blocking finding: IOVCC</strong></p>
<p>The initialization file explicitly says VCI = 3.3 V and IOVCC = 1.8 V. The panel DC table allows IOVCC = 1.65–3.3 V with 1.8 V typical, but the absolute-maximum table says IOVCC max = 1.68 V. A 1.8 V nominal rail therefore exceeds the printed absolute maximum. The likely explanation is a datasheet transcription error, but the board must not be powered until Displayman confirms the corrected absolute-maximum rating in writing. The proposed hardware defaults to 1.8 V and makes any 3.3 V alternative a DNP-only engineering option.</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Blocking finding: DSI rate / pixel format</strong></p>
<p>Displayman engineering has confirmed that the supplied 600 × 1280 source/configuration timing is correct for the exact module, but has not specified the DSI transport parameters or explained its mapping to the 480 × 1280 physical glass. Assuming the stated 55 MHz value is the host DPI pixel clock and configured source pixels are transported as RGB888, the raw payload is 660 Mb/s per lane before packet overhead; packed RGB666 would be 495 Mb/s per lane. The panel D-PHY table’s 2×UI range (4–25 ns) appears to imply roughly 80–500 Mb/s, conflicting with the RGB888 case. Displayman must still confirm pixel format, video mode, clock behavior, and supported lane bit rate. The PCB will nevertheless be designed for at least 1.5 Gb/s per lane, consistent with the ESP32-P4 transmitter capability.</p></td>
</tr>
</tbody>
</table>

### Review decision requested

- Approve the architecture and requirements as the basis for Phase 2, subject to the gates in Section 14.

- Obtain Displayman’s written answers to UQ-01 through UQ-05 before schematic release and first power.

- Confirm the daughterboard’s mechanical relationship to the Nano and desired cable lengths/contact orientation.

- Confirm whether the prototype should expose optional 3.3 V IOVCC selection; the recommendation is to fit 1.8 V only and keep 3.3 V inaccessible without rework.

### Phase boundary

STOP: Phase 2 schematic design has not started. Approval or requested modifications to this PRD are required first.

## 2. Scope, use case, and non-goals

### 2.1 Intended use

- Open-bench bring-up, firmware development, display characterization, touch integration, and thermal evaluation.

- Powered from a regulated, center-positive 24 V DC wall adapter through a PCB barrel jack.

- One Waveshare ESP32-P4-NANO and one KD068HDFID009-C009A module per daughterboard.

- User-accessible connectors, jumpers, indicators, and test points suitable for repeated laboratory use.

### 2.2 In scope

- 15-pin Nano DSI/I²C adapter, 40-pin LCD connector, and 8-pin touch connector.

- 24 V input protection; 5 V, 3.3 V, and 1.8 V conversion; sequenced VCI/IOVCC/reset; Nano power feed.

- 240 mA total constant-current backlight drive and PWM dimming.

- PCB signal-integrity, power-integrity, mechanical, thermal, test, and firmware-interface requirements.

### 2.3 Explicit non-goals

- Automotive qualification, load-dump immunity, ISO 7637-2/ISO 16750 compliance, AEC-Q component coverage, functional safety, production EMC certification, or sealed enclosure design.

- A replacement for the ESP32-P4-NANO; Wi-Fi/C6, audio, camera, Ethernet, USB, and battery functions are outside this daughterboard’s scope.

- Panel optical redesign, LED-string rebalance, display flex modification, or reverse engineering undocumented GC9703C behavior.

- Final schematic, PCB layout, Gerbers, BOM, or firmware driver in Phase 1.

### 2.4 Design life and environment

Prototype target: indoor laboratory use, 0–50 °C ambient, non-condensing, pollution degree typical of office/lab equipment, natural convection, and supervised operation. Component ratings shall normally be −40–85 °C or wider so the board is not the immediate temperature limitation, but this does not qualify the assembly for automotive service.

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

### 3.1 Interpretation rules

- A specific module pinout or operating limit in S1 overrides generic controller-family information.

- S2 overrides generic timing defaults only where it is internally coherent and electrically compatible with S1.

- A contradiction involving an absolute maximum is never resolved by assumption; it becomes a blocking manufacturer question.

- Derived engineering calculations and board constraints are labeled as such and are not represented as Displayman requirements.

- Current component status was checked against manufacturer pages and authorized-distributor listings on 2026-09-13; availability must be rechecked at procurement.

### 3.2 Source defects already identified

- S1 Section 3.1 is titled as a CTP pin description but contains the 40-pin LCM connector.

- S1 alternates between IOVCC and VDDI in the power-sequence section; this PRD interprets VDDI as the LCD I/O rail IOVCC, pending confirmation.

- S2 includes tool-specific pseudo-functions and malformed lines such as a missing parenthesis in a write_command call; it shall be normalized into a reviewed firmware table rather than compiled verbatim.

- S1 gives only typical LED forward voltage and no min/max or cold-temperature value.

- S1’s apparent D-PHY rate limit conflicts with S2 if RGB888 is intended.

## 4. Confirmed display and touch requirements

| **Characteristic**  | **Required / observed value**                                                                                                             | **Basis**           |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| Panel               | Displayman KD068HDFID009-C009A; 6.75 in IPS, normally black                                                                               | S1 pp. 3–5          |
| Physical glass      | 480 RGB × 1280 visible pixels                                                                                                             | S1; S2 comment      |
| Vendor source configuration | 600 × 1280 using `RSOX(600)`; confirmed correct for this exact module. The mapping of 600 horizontal source positions to the 480-pixel glass remains unresolved. | S2; S7              |
| Timing              | H: 600 configured source positions + 4 sync + 40 back porch + 40 front porch = 684 total; V: 1280 active + 4 sync + 20 back porch + 36 front porch = 1340 total | S2; S7              |
| Pixel clock / frame | 55 MHz; derived 55,000,000 ÷ (684 × 1340) = 60.007 Hz                                                                                     | S2 + calculation    |
| Display controller  | GC9703C                                                                                                                                   | S1                  |
| MIPI interface      | Two data lanes + differential clock                                                                                                       | S1/S2/S3            |
| VCI                 | 3.3 V design target; S1 operating range 2.5–3.3 V, 2.8 V typ; S2 explicitly says 3.3 V                                                    | S1 §5.2; S2         |
| IOVCC               | 1.8 V proposed; S1 operating range 1.65–3.3 V, 1.8 V typ; unresolved abs-max conflict                                                     | S1 §§5.1–5.2; S2    |
| LCD logic current   | 30 mA typical, 60 mA maximum (datasheet does not split rails)                                                                             | S1 §5.2             |
| Backlight           | 24 white LEDs arranged 6S4P; 240 mA total typical; 19.2 V typical; constant-current drive                                                 | S1 §5.3 and circuit |
| Touch controller    | Goodix GT9271; ten-point capacitive touch                                                                                                 | S1 §§2, 7           |
| Touch supply        | 3.3 V target; 2.66–3.47 V allowed; 13 mA typical active                                                                                   | S1 §7.1             |
| Touch bus           | I²C at up to 400 kHz; RESET active low; INT bidirectional during address selection                                                        | S1 §§3.2, 7.2–7.3   |
| Touch addresses     | 7-bit 0x5D or 0x14 (datasheet also lists 8-bit 0xBA/0xBB and 0x28/0x29)                                                                   | S1 §7.3             |

### 4.1 DSI payload-rate calculation

Assuming S2’s 55 MHz value is the host DPI pixel clock, two DSI lanes carry every configured source pixel, and the stream uses the stated native pixel packing, the unencoded payload is 660 Mb/s per lane for RGB888 (55 MHz × 24 ÷ 2) or 495 Mb/s per lane for packed RGB666 (55 MHz × 18 ÷ 2). These are conditional payload calculations, not confirmed operating settings. Packet headers, blanking transport, video mode, and implementation margin can raise the required lane rate above the raw payload. The unresolved 600-to-480 source mapping may affect implementation details but does not by itself identify the pixel format or lane rate. Phase 2 shall not choose the final DSI settings until Displayman confirms the pixel format, video mode, continuous/non-continuous clock behavior, lane bit rate, and valid D-PHY range.

### 4.2 Panel handling

- Do not connect or disconnect the LCD or touch flex while any board rail is powered.

- Use ESD-safe handling and add connector-area protection; the module connector fingers shall not be touched.

- Backlight current shall never exceed 240 mA in normal operation; firmware power-up default is 0% duty.

## 5. System architecture

The daughterboard is partitioned into five zones. This is the controlling Phase-2 architecture unless an approval-gate answer requires a change.

| **Zone**                   | **Inputs**                | **Function**                                                                                 | **Outputs**                                |
|----------------------------|---------------------------|----------------------------------------------------------------------------------------------|--------------------------------------------|
| A. Protected input         | 24 V barrel               | Fuse, reverse-polarity diode, surge clamp, bulk/high-frequency filtering, power-good sensing | VIN_PROT_24V                               |
| B. System power            | VIN_PROT_24V              | 60 V synchronous buck; isolated local display regulators                                     | SYS_5V_3A, LCD_3V3, LCD_IOVCC_1V8          |
| C. Sequenced display logic | LCD_3V3, LCD_PWR_EN       | Three-stage up/down sequencer, VCI load switch, reset wired-AND, early power-fail handling   | LCD_IOVCC, LCD_VCI, LCD_RESET_N, LCD_READY |
| D. Video and touch         | Nano DSI/I²C + five GPIOs | Lane-preserving adapter, ESD, I²C domain isolation, GT9271 reset/address/interrupt           | 40-pin LCD FPC, 8-pin touch FPC            |
| E. Backlight               | VIN_PROT_24V, BL_PWM      | 65 V constant-current buck at 240 mA with disable/current-test provisions                    | LED_A, LED_K                               |

### 5.1 Physical integration assumption

The baseline is a stack-on daughterboard using the Nano’s two 2×13, 2.54 mm headers for 5 V, ground, and control GPIOs, plus a short 15-position FFC from the Nano DSI connector to the daughterboard. The panel then connects through separate 40-position LCD and 8-position touch FFCs. Board outline, standoff locations, cable exit direction, and keepouts remain provisional until the mechanical arrangement is approved.

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
| 14           | ESP_3V3             | Nano-side logic reference only; do not parallel with LCD_3V3 |
| 15           | ESP_3V3             | Nano-side logic reference only; do not parallel with LCD_3V3 |

### 6.2 Proposed control GPIO allocation

| **Nano header** | **GPIO** | **Net**         | **Safe-state requirement**                                                           |
|-----------------|----------|-----------------|--------------------------------------------------------------------------------------|
| P1 pin 12       | GPIO4    | LCD_RESET_CMD_N | High impedance must leave panel reset asserted through hardware pull-down/wired-AND. |
| P1 pin 9        | GPIO5    | CTP_RESET_N     | High impedance must hold touch reset low until firmware takes control.               |
| P1 pin 16       | GPIO22   | CTP_INT         | Bidirectional: output during address select, input interrupt afterward.              |
| P1 pin 7        | GPIO23   | BL_PWM          | Default low; no backlight before display initialization.                             |
| P1 pin 18       | GPIO24   | LCD_PWR_EN      | Default low; enables the hardware sequence only after firmware requests it.          |

These GPIOs are exposed on S3 and are not among ESP32-P4 strapping GPIO34–GPIO38 \[S4\]. Phase 2 shall re-check them against the selected Nano hardware revision, board support package, and any user-reserved peripherals.

### 6.3 Panel 40-pin LCD connector

| **Pins** | **Panel signal**      | **Board disposition**                                             |
|----------|-----------------------|-------------------------------------------------------------------|
| 1        | NC                    | No connection                                                     |
| 2        | VCI                   | Sequenced switched 3.3 V                                          |
| 3        | IOVCC                 | Sequenced 1.8 V default; DNP 3.3 V option only after approval     |
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
| 3       | VDD        | Filtered LCD_3V3; local decoupling               |
| 4       | SCL        | I²C through translator/isolation and ESD         |
| 5       | SDA        | I²C through translator/isolation and ESD         |
| 6       | INT        | GPIO22; bidirectional; ESD and weak default bias |
| 7       | RST        | GPIO5 plus hardware reset; active low            |
| 8       | GND        | Ground                                           |

## 7. Power architecture and sequencing

### 7.1 Input and rail requirements

| **Rail**     | **Nominal / design target**      | **Consumers**                | **Requirement**                                                                                 |
|--------------|----------------------------------|------------------------------|-------------------------------------------------------------------------------------------------|
| VIN_ADAPTER  | 24 V nominal, ±10% accepted      | Input stage                  | Center-positive 5.5 × 2.1 mm adapter, ≥2 A, regulated, safety-approved.                         |
| VIN_PROT_24V | ≈VIN less reverse diode drop     | 5 V buck, LED driver         | Fused, reverse protected, surge clamped, filtered; no automotive transient claim.               |
| SYS_5V_3A    | 5.0 V, 3 A continuous target     | Nano P1 pins 2/4, local LDOs | Ripple/noise compatible with Nano; current limit and thermal protection; removable feed jumper. |
| LCD_3V3      | 3.3 V, ≥150 mA design capability | Touch, sequencer, VCI source | Not tied to Nano ESP_3V3; low-noise local regulation and test point.                            |
| LCD_IOVCC    | 1.8 V, ≥100 mA design capability | Panel pin 3                  | Sequence first; default off; current-limited by LDO; voltage option locked pending UQ-01.       |
| LCD_VCI      | 3.3 V, ≥100 mA design capability | Panel pin 2                  | Load-switched after IOVCC; controlled rise and quick discharge.                                 |
| LED_CURRENT  | 240 mA total, ±5% initial target | Panel pins 31–32 / 39–40     | Constant current; default disabled; PWM controllable; never exceed 240 mA nominal setpoint.     |

### 7.2 Preliminary worst-case input budget

| **Load**               | **Output estimate**              | **Input estimate at 24 V** | **Basis / margin**                                     |
|------------------------|----------------------------------|----------------------------|--------------------------------------------------------|
| Nano + 5 V auxiliaries | 15 W at 5 V / 3 A design ceiling | ≈0.69 A at 90%             | Design allocation; actual Nano maximum to be measured. |
| Backlight              | 4.61 W (19.2 V × 0.24 A)         | ≈0.21–0.23 A               | 90–95% LED-driver estimate.                            |
| LCD/touch logic        | \<0.3 W expected                 | Included in 5 V conversion | 60 mA panel max + 13 mA touch typ; margin added.       |
| Total design operating | ≈20 W                            | ≈0.95 A                    | Before transient and thermal margin.                   |
| Specified adapter      | 48 W available                   | 24 V / 2 A minimum         | Approximately 2× operating-current margin.             |

### 7.3 Required LCD power-up sequence

Hardware and firmware shall jointly implement this sequence, using a TI LM3880MF-1AA/NOPB three-rail sequencer with 10 ms steps as the baseline:

| **Step** | **Action**                                              | **Minimum / target delay**                                         | **Enforcement**                                               |
|----------|---------------------------------------------------------|--------------------------------------------------------------------|---------------------------------------------------------------|
| 0        | Keep LCD_IOVCC, LCD_VCI, LCD_RESET_N, and backlight off | Until SYS_5V and LCD_3V3 are valid                                 | Pull-downs + sequencer + firmware defaults                    |
| 1        | Enable LCD_IOVCC (1.8 V)                                | LM3880 FLAG1 after 10 ms enable qualification                      | Hardware                                                      |
| 2        | Enable LCD_VCI (3.3 V)                                  | 10 ms after FLAG1; both rail rise times ≥10 µs per S1              | Hardware                                                      |
| 3        | Release hardware reset clamp                            | 10 ms after VCI enable; exceeds S1 ≥5 ms rail-to-reset requirement | LM3880 FLAG3                                                  |
| 4        | Firmware drives reset low then high                     | Low ≥10 ms; high wait 120 ms before commands                       | GPIO4 via open-drain buffer; follows S2 and exceeds S1 minima |
| 5        | Send reviewed GC9703C init table                        | After reset wait                                                   | Firmware                                                      |
| 6        | Sleep Out (0x11), wait 120 ms, Display On (0x29)        | As supplied                                                        | Firmware                                                      |
| 7        | Enable PWM from 0% and ramp brightness                  | After valid frames / display-on                                    | Firmware                                                      |

### 7.4 Required shutdown and hard-unplug behavior

- Normal software shutdown: PWM = 0; Display Off 0x28; wait at least 10 ms; Sleep In 0x10; assert panel reset; deassert LCD_PWR_EN.

- The LM3880 reverse sequence shall assert reset first, disable VCI at least 10 ms later, and disable IOVCC at least 10 ms after VCI. This exceeds S1’s reset-low-before-VCI requirement and preserves VCI-before-IOVCC order.

- An early power-fail detector referenced to VIN_PROT_24V shall deassert the sequencer while the local logic hold-up node still has energy. Phase 2 shall size the hold-up capacitance and isolation path from measured rail load and dropout so all three reverse steps complete on adapter removal.

- If practical hold-up cannot guarantee the specified hard-off order at measured load, the design shall be blocked pending Displayman guidance; a software-only shutdown is not sufficient.

### 7.5 Nano power coexistence

SYS_5V_3A feeds Nano header P1 pins 2 and 4 through a removable jumper or 0 Ω link. The Nano’s attached USB power-path circuitry must be verified against S3 and bench-tested for concurrent USB + daughterboard power. The DSI connector’s ESP_3V3 pins are references only and shall never be driven by the daughterboard.

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

The final ESP-IDF settings shall record: two lanes, confirmed lane bit rate, pixel-clock source, RGB pixel format, video/burst mode, horizontal and vertical timing, and any continuous-clock requirement. The design is not accepted solely because a static image appears; it must pass color bars, checkerboard, moving gradients, all-white/all-black, and at least a two-hour error-free run across the intended brightness range.

## 9. GT9271 touch requirements

### 9.1 Electrical interface

- Power the module touch VDD from LCD_3V3. Do not assume a separately accessible VDDIO; the 8-pin interface exposes only VDD.

- Use PCA9306DCTR between Nano ESP_3V3 I²C and the daughterboard touch 3.3 V domain. The level translator is used primarily for partial-power isolation and back-power prevention; both sides are nominally 3.3 V.

- Provide separate pull-ups on each PCA9306 side sized in Phase 2 for ≤400 kHz and the measured bus/cable capacitance. Provide series-damping placeholders close to the Nano-side connector.

- Protect SCL, SDA, INT, and RST at the external touch connector with TPD4E05U06DQAR. ESD placement takes precedence over convenient probing.

- CTP_INT must be a bidirectional GPIO: driven during address selection and reconfigured as interrupt input afterward.

### 9.2 Default address and reset sequence

Default to the 7-bit address 0x5D. Firmware shall hold CTP_INT low, assert CTP_RESET_N low for at least 100 µs after the touch supply is valid and the required post-power delay has elapsed, release reset, wait more than 5 ms, then wait at least 50 ms before releasing INT and reconfiguring it as an input. A firmware-selectable 0x14 procedure shall be retained for conflict testing, using INT high during reset as specified by S1.

### 9.3 Firmware behavior

- Probe 0x5D first, then optionally 0x14 only after executing the corresponding documented reset sequence.

- Do not interpret the listed 0xBA/0xBB or 0x28/0x29 values as 7-bit Linux/ESP-IDF addresses; they are 8-bit read/write address bytes.

- Log reset cause, selected address, controller/product ID, firmware version if available, touch count, and interrupt activity for bench diagnosis.

- Expose a touch-reset pushbutton or clearly labeled test pad without allowing it to force an illegal LCD power state.

## 10. Backlight requirements

### 10.1 Driver architecture

Use TI TPS92511DDA, a 4.5–65 V, 500 mA constant-current buck LED driver with integrated switch and PWM/analog dimming. Feed panel LED+ from filtered VIN_PROT_24V and regulate total cathode current at panel LED−. Set the nominal current to 240 mA; the final IADJ resistor, inductor, switching frequency, and thermal copper are Phase-2 calculations using the confirmed LED voltage range.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Headroom condition</strong></p>
<p>TPS92511 is a buck driver and therefore requires the LED-string forward voltage to remain sufficiently below the minimum protected input after cable, diode, switch, and ripple losses. Displayman provides only 19.2 V typical. If cold/max VF does not leave adequate headroom from a 21.6 V minimum adapter, the architecture must change to buck-boost or the permitted adapter range must change. This is a schematic-release blocker (UQ-03).</p></td>
</tr>
</tbody>
</table>

### 10.2 Brightness control

- BL_PWM is active high and defaults low by hardware pull-down. No floating input may turn on the backlight.

- Initial firmware target is 20 kHz PWM, subject to the TPS92511 requirement that PWM remain below one-tenth of switching frequency and to observed low-duty linearity/flicker.

- Firmware shall clamp command range to 0–100%, start at 0%, and ramp after display-on. It shall never use current overdrive to obtain brightness.

- Provide a hardware backlight-disable jumper and an easily measured DIM/enable test point.

### 10.3 Current, protection, and validation

- Current regulation target: 240 mA ±5% at 100% PWM after component tolerances; never exceed 252 mA during normal tests.

- Provide nonintrusive current-measure access (zero-ohm link or dedicated sense loop) on the LED return; ordinary meter insertion shall not expose the panel to an open-load transient.

- Validate open-load, connector removal while disabled, shorted output, brownout, PWM = 0/100%, and repeated enable/disable behavior. Hot-plugging while enabled is prohibited.

- Thermal test at 24 V, 240 mA, 100% duty for at least one hour in still air; no component may exceed its derated junction/case target or discolor the PCB.

### 10.4 Parallel-string limitation

The module internally parallels four six-LED strings. The daughterboard regulates only the 240 mA total and cannot observe individual string current sharing. Displayman must confirm that the internal module construction is intended for one external total-current sink at 240 mA.

## 11. Protection, filtering, debug, and PCB implementation

### 11.1 Protection and filtering

- Barrel input: 2 A fuse, 60 V / 5 A Schottky reverse-polarity protection, SMBJ30A TVS to ground after the fuse, and bulk + ceramic capacitors rated with adequate DC-bias margin.

- Regulators and LED driver: local bypassing, short hot loops, exposed-pad thermal via arrays where required, and manufacturer-recommended input/output capacitor types and values.

- Panel logic rails: ferrite-bead option and local high-frequency/bulk decoupling adjacent to connector power pins; populated configuration based on stability and noise analysis.

- No TVS device substitutes may have materially higher capacitance on MIPI lanes without signal-integrity approval.

### 11.2 Required test points

| **Group**  | **Required labeled points**                                                                          |
|------------|------------------------------------------------------------------------------------------------------|
| Power      | VIN_RAW, VIN_PROT_24V, SYS_5V, LCD_3V3, LCD_IOVCC, LCD_VCI, GND near every group                     |
| Sequencing | VIN_GOOD, LCD_PWR_EN, SEQ_FLAG1, SEQ_FLAG2, SEQ_FLAG3/LCD_READY, LCD_RESET_N                         |
| Touch      | CTP_SCL, CTP_SDA, CTP_RESET_N, CTP_INT, CTP_3V3                                                      |
| Backlight  | BL_PWM, BL_DIM, LED_A, LED_K, LED current measurement link                                           |
| MIPI       | No ordinary probe pads. Use connector breakout or a purpose-designed high-bandwidth interposer only. |

### 11.3 Development controls

- Nano 5 V feed isolation jumper/link.

- LCD power-enable override with OFF / MCU control positions; no forced-ON position that bypasses reset sequencing.

- Backlight hardware disable and current-set access.

- Reset pushbuttons or pads for LCD and touch, electrically combined with hardware sequencing so pressing a button cannot back-power an unpowered rail.

- Power-good LEDs for 24 V and 5 V, plus low-current indicators for sequenced rails where loading is acceptable. LEDs must not be the only indication of a safe state.

### 11.4 PCB and assembly

- Fabrication: controlled-impedance four-layer minimum, IPC Class 2 prototype workmanship target, ENIG or equivalent fine-pitch-compatible finish, and solder mask dams where fabricator rules permit.

- Separate noisy power and quiet display-interface placement zones; use thermal copper and via arrays per IC datasheets.

- Clearly mark pin 1, cable contact side, 24 V polarity, LED hazard, connector reference, rail voltage, jumper default, and board revision on silkscreen.

- Place high-voltage-rated spacing suitable for 24 V SELV and 48.4 V clamped transients. This is not mains circuitry.

- Use keyed/retained connectors where possible; FFC latches must remain reachable with the Nano installed.

### 11.5 KiCad readiness

Phase 2 shall use hierarchical schematic sheets for Input Protection, 5 V Power, Display Rails & Sequencing, MIPI Adapter, Touch, Backlight, and Headers/Test. Net names in this PRD shall be retained. Every selected symbol/footprint must be checked against the manufacturer drawing, with pin numbers verified independently before PCB capture.

## 12. Selected components and rationale

These are the preferred Phase-2 design anchors. Supporting inductors, power resistors, capacitors, ferrites, and divider values are intentionally deferred until schematic calculations and manufacturer answers are complete.

| **Function**          | **Preferred manufacturer part number**          | **Key suitability**                                                 | **Status / rationale**                                                             |
|-----------------------|-------------------------------------------------|---------------------------------------------------------------------|------------------------------------------------------------------------------------|
| 24 V barrel jack      | Same Sky PJ-044AH                               | Horizontal PCB jack; 5.5 × 2.1 mm class; 24 V / 5 A listing         | Selected for common bench adapters; verify drawing and plug fit before layout.     |
| Input fuse            | Littelfuse 0451002.MRL                          | 2 A, 125 V, surface-mount fuse                                      | Selected; voltage margin above 24 V. I²t to be checked against measured inrush.    |
| Reverse protection    | Vishay SS5P6-M3/86A                             | 60 V, 5 A Schottky                                                  | Selected for simple, visible bench behavior; thermal loss to be calculated.        |
| Input TVS             | Littelfuse SMBJ30A                              | 30 V standoff, ≈48.4 V clamp class, 600 W                           | Selected for adapter-cable transients while remaining below 60/65 V IC ratings.    |
| 24 V → 5 V buck       | Texas Instruments LM76003RNPR                   | 3.5–60 V, 3.5 A synchronous buck                                    | Active; adequate 5 V / 3 A target with protection and PGOOD.                       |
| Local 3.3 V LDO       | Texas Instruments TLV75533PDBVR                 | 500 mA, enable, low-noise/low-IQ LDO                                | Active; ample LCD/touch/sequencer current and margin.                              |
| IOVCC 1.8 V LDO       | Texas Instruments TLV75518PDBVR                 | 500 mA, enable, fixed 1.8 V                                         | Active; default IOVCC source, sequencer controlled.                                |
| VCI load switch       | Texas Instruments TPS22919DCKR                  | 1.6–5.5 V, 1.5 A, controlled rise, quick discharge                  | Active family; provides controlled 3.3 V VCI and turn-off discharge.               |
| Rail sequencer        | Texas Instruments LM3880MF-1AA/NOPB             | Three open-drain flags; 10 ms up steps and reverse 10 ms down steps | Active/in stock; directly matches IOVCC → VCI → RESET ordering.                    |
| Power-fail supervisor | Texas Instruments TPS3808G01DBVR                | Adjustable 0.405 V sense, open-drain reset, programmable delay      | Selected to initiate early controlled shutdown; divider/hold-up values in Phase 2. |
| LCD reset buffer      | Texas Instruments SN74LVC1G07DBVR               | Open-drain non-inverting buffer with partial-power-down support     | Selected for wired-AND reset control and 1.8 V pull-up domain.                     |
| I²C domain isolation  | Texas Instruments PCA9306DCTR                   | Two-bit bidirectional I²C translator, up to 400 kHz                 | Active; isolates Nano ESP_3V3 from daughterboard touch rail when disabled.         |
| MIPI ESD              | Texas Instruments TPD6E05U06RVZR                | Six channels, ~0.5 pF, 5.5 V, up to 6 Gb/s class                    | Active; one part protects D0/D1/CLK conductors with low loading.                   |
| Touch ESD             | Texas Instruments TPD4E05U06DQAR                | Four channels, ~0.5 pF, IEC ESD protection                          | Active; covers SCL/SDA/INT/RST.                                                    |
| Backlight driver      | Texas Instruments TPS92511DDA                   | 4.5–65 V, up to 500 mA constant-current buck, PWM dimming           | Active/in stock; conditional on confirmed LED max VF/headroom.                     |
| Nano DSI connector    | Amphenol SFW15R-2STE1LF                         | 15-position, 1.00 mm, top-contact ZIF; active/in stock              | Provisional; cable type/contact side must mate the Nano’s actual connector.        |
| Panel LCD connector   | Molex 505110-4096                               | 40-position, 0.50 mm, bottom-contact FD19                           | Selected because S1 explicitly identifies this part on the module drawing.         |
| Panel LCD FFC         | Molex 0150200429 (76 mm) or 0150200431 (102 mm) | 40-way, 0.50 mm Premo-Flex class                                    | Provisional length/contact orientation; choose after mechanical mock-up.           |
| Touch connector       | Hirose FH12-8S-0.5SH(55)                        | 8-position, 0.50 mm, bottom-contact ZIF                             | Provisional; verify FPC contact/stiffener side and insertion depth.                |
| Stacking sockets      | Samtec SSW-113-02-G-D (two)                     | 2×13, 2.54 mm female socket                                         | Provisional; stack height and Nano header geometry require confirmation.           |

### 12.1 Component selection policy

- Use exact orderable MPNs; no generic ‘or equivalent’ substitutions on regulators, sequencer, reset buffer, ESD arrays, connectors, or LED driver without review.

- All power magnetics and capacitors shall be selected from the IC manufacturer’s calculation and stability requirements, derated for DC bias, ripple current, saturation, temperature, and tolerance.

- Prototype alternates may be added as DNP footprints only when they do not create stubs on MIPI paths or undermine sequencing.

- Procurement shall recheck lifecycle and stock immediately before schematic freeze and again before assembly release.

## 13. Firmware and bring-up requirements

### 13.1 Firmware responsibilities

- Initialize GPIO safe states before enabling the LCD sequence: LCD_PWR_EN = 0, LCD reset asserted, touch reset asserted, BL_PWM = 0.

- Configure the ESP-IDF MIPI DSI bus for two lanes and the manufacturer-confirmed lane bit rate/pixel format; configure the DPI timing exactly as approved.

- Translate S2 into a typed, bounds-checked command table with explicit command length and millisecond delays. Preserve byte order and document every normalized syntax repair.

- Execute panel reset and initialization only after LCD_READY; maintain the 120 ms delays after reset release and Sleep Out as supplied.

- Preserve the vendor-confirmed 600-pixel source configuration, including `RSOX(600)`, when implementing S2. The present 60-black-columns-per-side model is an interpretation, not a confirmed source-to-glass mapping; do not hard-code it as a manufacturer requirement until Displayman explains how the 600 horizontal source positions map to the 480-pixel glass. Validate the mapping with edge-marker and color-bar test patterns.

- Initialize GT9271 with the documented reset/INT address selection; configure I²C at no more than 400 kHz.

- Enable backlight only after stable video, starting at zero duty; provide a diagnostic command to set duty, force display reset, read touch ID, and report rail/power-good states.

### 13.2 Initialization-file acceptance

The complete S2 byte sequence remains the authoritative starting point and shall be version-controlled by its SHA-256. S7 confirms that Displayman engineering considers this initialization file correct for the exact KD068HDFID009-C009A module; `RSOX(600)` shall therefore be preserved and shall not be treated as a likely typo or accidental value. Phase 2/firmware implementation shall produce a machine-readable diff or review report showing that every command byte and delay is represented. Apparent wrapper-syntax errors shall be corrected only at the wrapper level; command payloads shall not be edited without documented evidence. S7 does not resolve the wrapper-syntax artifacts, source-to-glass mapping, or DSI transport parameters.

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
<td><p><strong>Approval gate</strong></p>
<p>Items marked BLOCKING must be closed before schematic release. Manufacturer confirmation means written confirmation tied to the exact KD068HDFID009-C009A module revision, not an inference from a similar panel or a generic GC9703C datasheet.</p></td>
</tr>
</tbody>
</table>

| **ID / severity** | **Question or conflict**                                                                                                  | **Current evidence**                                                                                                       | **Proposed disposition / owner**                                                                                          |
|-------------------|---------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| UQ-01 BLOCKING    | What is the correct IOVCC absolute-maximum rating, and is 1.8 V nominal explicitly approved?                              | S1 abs max = 1.68 V; S1 DC table = 1.65–3.3 V, 1.8 V typ; S2 = 1.8 V.                                                      | Displayman to issue corrected value. Hardware defaults to 1.8 V but first power is prohibited until answered.             |
| UQ-02 BLOCKING    | What pixel format, video mode, clock behavior, and lane bit rate are required for the supplied two-lane timing? Is the D-PHY 2×UI 4–25 ns table valid? | S7 confirms S2 is correct but provides none of these transport parameters. Under the assumptions in §4.1, RGB888 raw = 660 Mb/s/lane and packed RGB666 = 495 Mb/s/lane; the table appears to cap near 500 Mb/s. | Displayman to confirm RGB888/RGB666 or other format, video mode, continuous/non-continuous clock, min/max lane rate, and the valid D-PHY range. ESP32 settings follow the answer. |
| UQ-03 BLOCKING    | What are LED-string VF min/max over current and temperature, and required driver headroom?                                | S1 gives 19.2 V typical only for internal 6S4P array.                                                                      | Displayman to provide limits; measure samples at 240 mA. Keep TPS92511 only if 21.6 V input leaves verified margin.       |
| UQ-04 BLOCKING    | Does VDDI in the power diagram mean IOVCC, and is the stated shutdown order mandatory for hard unplug?                    | S1 pin name is IOVCC; sequence calls it VDDI and requires VCI off before it.                                               | Displayman to confirm. Baseline sequencer enforces IOVCC→VCI→reset and reverse.                                           |
| UQ-05 BLOCKING    | What are the LCD and touch cable contact-side/orientation requirements at both ends?                                      | S1 names Molex 5051104096 for LCD and drawings imply contact sides; Nano connector MPN is absent.                          | Continuity-test actual Nano and inspect physical panel samples. Freeze connector/cable MPNs only after mock-up.           |
| UQ-06 HIGH        | Is Nano J1 pin 10 intentionally NC, and are pins 14/15 safe reference-only 3.3 V outputs?                                 | S3 shows pin 10 unlabeled; 14/15 tied to ESP_3V3.                                                                          | Verify with Waveshare and a powered-off continuity check. Do not drive ESP_3V3.                                           |
| UQ-07 HIGH        | What is the maximum sustained and transient 5 V current of the exact Nano build?                                          | S3 shows 5 V input and onboard conversion but no board-level input-current rating.                                         | Allocate 3 A; measure boot, CPU/PSRAM load, C6 activity, USB, and peripherals before final fuse/thermal sizing.           |
| UQ-08 HIGH        | Is concurrent USB and daughterboard 5 V power explicitly permitted?                                                       | S3 includes a USB-to-VCC_5V MOSFET path, but no operating statement was supplied.                                          | Default user instruction: isolate Nano 5 V jumper before USB-only power. Bench-test backfeed before allowing concurrency. |
| UQ-09 HIGH        | Does the panel accept one 240 mA total sink for the internal four parallel strings?                                       | S1 shows 6S4P and lists IF = 240 mA but does not explicitly say total/module current.                                      | Displayman confirmation; baseline interprets 240 mA as total module current.                                              |
| UQ-10 MEDIUM      | Is 0x5D the desired default GT9271 address, and is INT push-pull/open-drain after initialization?                         | S1 documents both 0x5D and 0x14 selection but not board default or output type in the pin table.                           | Default 0x5D with conservative pull/buffer arrangement; confirm interrupt electrical mode.                                |
| UQ-11 MEDIUM      | Which Nano mechanical arrangement, standoff pattern, and cable lengths are preferred?                                     | No enclosure or placement drawing was supplied.                                                                            | User to approve stack-on baseline or request side-by-side board before layout.                                            |
| UQ-12 MEDIUM      | Are GPIO4/5/22/23/24 free in the intended firmware/BSP?                                                                   | They are exposed and not strapping pins, but application reservations are unknown.                                         | User/firmware owner to confirm; allocation remains configurable before schematic.                                         |
| UQ-13 MEDIUM      | What is the exact source-driver/source-to-glass mapping by which the confirmed `RSOX(600)` configuration drives the 480-pixel physical glass? | S2 uses `RSOX(600)` and controller-specific source ranges. S7 confirms the file is correct for this exact module but does not explain the disposition of the additional 120 horizontal source positions. The 60-black-columns-per-side model remains an interpretation, not an established fact. | Keep `RSOX(600)` unchanged; ask Displayman to explain the mapping and validate it with color-bar and edge-marker patterns. |
| UQ-14 MEDIUM      | Which S2 syntax lines are transcription artifacts versus tool-specific grammar?                                           | File contains pseudo-code and malformed parentheses but payload appears structured.                                        | Normalize wrapper syntax only; preserve command bytes; request original vendor project/export if available.               |
| A-01 ASSUMPTION   | Adapter characteristics                                                                                                   | User specified a standard 24 V DC wall adapter.                                                                            | Assume regulated 24 V ±10%, center-positive, 5.5 × 2.1 mm, ≥2 A, SELV/Class II. User to confirm regional supply and plug. |
| A-02 ASSUMPTION   | Prototype environment                                                                                                     | User specified bench-development, not automotive production.                                                               | Use indoor 0–50 °C design target, supervised operation, no load-dump/automotive qualification.                            |

## 15. Verification and acceptance plan

### 15.1 Pre-assembly design checks

- Independent pin-number audit against connector manufacturer drawings and actual mating orientation.

- Schematic ERC; netlist cross-check against Sections 6 and 7; no NC panel pin connected.

- Power-stage calculations at 21.6, 24.0, and 26.4 V; component stress at fault limits; thermal and derating review.

- Controlled-impedance stack-up approved by fabricator; MIPI pair geometry and length report attached to layout review.

- 3D/mechanical check with actual Nano, panel flexes, cable bend radius, latch access, and standoff clearances.

### 15.2 Bring-up sequence

| **Stage**          | **Method**                                                                            | **Pass criteria**                                                             |
|--------------------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| 1\. Unpowered      | Continuity, resistance-to-ground, connector orientation, fuse and polarity inspection | No shorts; correct pin mapping; Nano 3.3 V not driven.                        |
| 2\. Protected 24 V | Current-limited bench supply, no Nano/panel connected                                 | TVS not conducting at 26.4 V; correct polarity and low idle current.          |
| 3\. Rails unloaded | Scope 5 V, 3.3 V, 1.8 V; toggle enables                                               | Within tolerance; stable; expected ripple; no overshoot above device limits.  |
| 4\. Sequencing     | Four-channel scope on IOVCC, VCI, RESET, VIN_GOOD; plug/unplug and brownout           | Order and delays meet Section 7 in both directions, including abrupt removal. |
| 5\. Nano           | Connect Nano with panel absent; exercise CPU/C6/USB loads                             | 5 V regulation, thermal, and no USB backfeed violation.                       |
| 6\. Panel logic    | Panel connected, backlight hardware-disabled                                          | Correct reset/init traffic; valid MIPI video without rail disturbance.        |
| 7\. Touch          | Address select, ID read, interrupt and 10-point test                                  | Stable ≤400 kHz I²C; no stuck bus; correct coordinates/orientation.           |
| 8\. Backlight      | Electronic load/dummy LED first, then panel; ramp to 240 mA                           | ±5% current, PWM behavior, no overcurrent/overshoot, acceptable temperature.  |
| 9\. System stress  | Two-hour moving patterns, repeated resets, 0–100% brightness, input min/max           | No artifacts, resets, touch errors, or thermal limit violations.              |

### 15.3 Required instruments

- Current-limited laboratory supply capable of 27 V and ≥2 A; calibrated DMM; ≥4-channel oscilloscope with suitable passive/differential probes.

- Electronic load or protected dummy LED load for current-driver validation before connecting the panel.

- Thermocouples or thermal camera; ESD-safe workstation; optional TDR/high-bandwidth probe for MIPI channel characterization.

### 15.4 Release criteria

- All BLOCKING UQs closed and recorded; no requirement waived verbally.

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
| LCD rails and sequence                      | Section 7; separate IOVCC/VCI and LM3880 reverse sequence             | Four-channel oscilloscope capture            |
| 24 V wall adapter                           | Section 7.1 and selected barrel/protection parts                      | 21.6–26.4 V test; polarity/fault checks      |
| Power Nano and LCD                          | 5 V / 3 A buck plus local LDOs and isolated Nano feed                 | Load, ripple, USB coexistence, thermal test  |
| 240 mA / ~19.2 V 6S4P backlight             | Section 10; TPS92511DDA conditional buck design                       | Dummy load then panel current/headroom test  |
| ESP PWM brightness                          | GPIO23 BL_PWM, default-off, initial 20 kHz target                     | Duty sweep, flicker/linearity, reset default |
| Protection/filtering/decoupling/test        | Section 11 and component table                                        | Inspection, fault test, ripple/ESD review    |
| Bench-development board                     | Section 2 scope; jumpers, test points, no automotive claim            | Design review and labeling                   |
| Identify conflicts/assumptions              | Section 14, especially UQ-01 through UQ-05                            | Written closure before schematic release     |
| Real/current components                     | Section 12 with MPNs and manufacturer-source checks                   | Lifecycle/stock recheck at procurement       |

### 16.1 Phase-2 entry checklist

- User approves this PRD or returns a marked set of changes.

- UQ-01, UQ-02, UQ-03, UQ-04, and UQ-05 are answered with evidence.

- Mechanical architecture and GPIO allocation are approved.

- Exact Nano and panel samples are available for connector/contact-side verification.

- Final adapter specification is agreed.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Phase 1 stop point</strong></p>
<p>No schematic capture, passive-value calculation, or KiCad implementation is authorized by this document until the review and entry checklist are complete.</p></td>
</tr>
</tbody>
</table>

## 17. Manufacturer question package

Send the following questions together, referencing KD068HDFID009-C009A and attaching the exact S1/S2 revisions. Request answers from Displayman engineering rather than sales shorthand.

| **\#** | **Question to Displayman**                                                                                                                                                                                                                |
|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1      | Please confirm the correct absolute-maximum rating for LCD IOVCC. Page 12 says 1.68 V max, while the DC table allows up to 3.3 V and the supplied two-lane file says IOVCC = 1.8 V. Is 1.8 V nominal approved for this exact module?      |
| 2      | Please confirm that VDDI in the power-on/off diagram is the same physical rail as connector pin 3 IOVCC, and confirm the required power-up and power-down order/timing.                                                                   |
| 3      | For the supplied 600 × 1280, 55 MHz, two-lane timing, what DSI pixel format is required (RGB888, packed RGB666, loosely packed RGB666, or another format), what video mode is required, and what lane bit rate should the host configure? |
| 4      | The D-PHY table’s 2×UI range of 4–25 ns appears to limit the maximum rate to about 500 Mb/s. Is that table correct for this module? Please provide the supported min/max lane rate and continuous/non-continuous clock requirements.      |
| 5      | Please provide LED backlight forward-voltage minimum and maximum at 240 mA total across temperature, required compliance/headroom, and confirm that 240 mA is the total current for the internal 6S4P array.                              |
| 6      | Please confirm the 40-pin LCD and 8-pin touch FPC contact side, stiffener side, insertion direction, acceptable cable type, and recommended board-side mating connector/cable part numbers.                                               |
| 7      | Displayman engineering has confirmed that the supplied two-lane initialization file, including `RSOX(600)`, is correct for KD068HDFID009-C009A. Please explain the exact source-driver/source-to-glass mapping between this 600-position horizontal source configuration and the 480-pixel physical glass, including the disposition of the additional 120 source positions and the meaning of source ranges S181–S900 / S1501–S2220. Please state whether the host must generate any black columns or whether the module/controller performs another mapping. |
| 8      | Please provide the original machine-readable initialization export or corrected C-style sequence, including all delays, pixel format, DSI mode, and any required read-back or error-check step.                                           |
| 9      | Please confirm GT9271 INT electrical type after initialization and the recommended default 7-bit address for this module.                                                                                                                 |

## 18. References

### Supplied sources

- S1 — Displayman (SZ) Technology Co., Ltd., KD068HDFID009-C009A datasheet, v1.0, 25 November 2024, 40 pages (user supplied).

- S2 — KD068HDFID009 -2LANE initialization file (user supplied).

- S3 — Waveshare ESP32-P4-NANO schematic, PDF created 25 October 2024 (user supplied).

- S7 — Email from Anson Ho, Displayman (SZ) Technology Co., Ltd., received 13 September 2026; reports that Displayman engineering confirmed the supplied two-lane initialization file is correct for the exact KD068HDFID009-C009A module. This confirmation includes retaining `RSOX(600)` but does not explain the 600-to-480 mapping or supply the required DSI transport parameters.

### Manufacturer documentation checked 13 September 2026

**Espressif:** [ESP32-P4 Series Datasheet](https://documentation.espressif.com/esp32-p4_datasheet_en.html); [ESP-IDF MIPI DSI LCD API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/peripherals/lcd/dsi_lcd.html); [ESP32-P4 Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32p4/schematic-checklist-esp32p4.html)

**Texas Instruments:** [LM76003](https://www.ti.com/product/LM76003); [TPS92511](https://www.ti.com/product/TPS92511); [LM3880](https://www.ti.com/product/LM3880); [TPS3808](https://www.ti.com/product/TPS3808); [TPS22919](https://www.ti.com/product/TPS22919); [TLV755P](https://www.ti.com/product/TLV755P); [PCA9306](https://www.ti.com/product/PCA9306); [SN74LVC1G07](https://www.ti.com/product/SN74LVC1G07); [TPD6E05U06](https://www.ti.com/product/TPD6E05U06); [TPD4E05U06](https://www.ti.com/product/TPD4E05U06)

**Connectors and protection:** [Molex 505110-4096](https://www.molex.com/en-us/products/part-detail/5051104096); [Amphenol SFW15R-2STE1LF](https://www.amphenol-cs.com/product/sfw15r2ste1lf.html); [Hirose FH12-8S-0.5SH(55)](https://www.hirose.com/product/p/CL0586-0744-5-55); [Same Sky PJ-044AH](https://www.sameskydevices.com/product/interconnect/connectors/dc-power-connectors/jacks/pj-044ah); [Littelfuse SMBJ series](https://www.littelfuse.com/products/tvs-diodes/surface-mount/smbj); [Vishay SS5P6](https://www.vishay.com/en/product/88721/)

*Authorized-distributor stock is a procurement snapshot, not a design guarantee. Manufacturer electrical data—not distributor summaries—controls electrical design.*
