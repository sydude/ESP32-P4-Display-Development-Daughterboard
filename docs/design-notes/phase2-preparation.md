# Phase 2 preparation and engineering validation

**Project:** ESP32-P4 Displayman Development Daughterboard  
**Date:** 2026-09-14  
**Controlling specification:** `docs/PRD.md`, revision 0.3 pending approval
**Status:** vendor-response analysis complete — not a schematic release

## 1. Scope and release boundary

This note records the non-blocking work completed before and after Displayman's 14 September 2026 response (S8). It validates the Phase 1 component candidates and architecture against the supplied module/Nano documents, written vendor evidence, and current manufacturer documentation. Section 15 records the response disposition and supersedes earlier statements that a now-answered item is still awaiting Displayman.

No schematic symbols, nets, footprints, PCB geometry, or other KiCad design content were added. The existing files under `hardware/kicad/` remain the canonical blank project and were inspected read-only.

The following remain prohibited until Displayman corrects the remaining DSI blocker and PRD v0.3 is approved:

- freezing the DSI host transport settings;
- releasing the schematic or beginning PCB layout.

## 2. Executive disposition

| Area | Result of independent validation | Phase 2 disposition |
|---|---|---|
| 24 V input | The protection concept is sound, but the selected barrel jack is mechanically inconsistent with the PRD input requirement and the Schottky diode unnecessarily consumes voltage headroom. | Replace the jack candidate; prefer an ideal-diode controller and N-MOSFET over the series Schottky. Retain fuse and SMBJ30A subject to final inrush/transient calculations. |
| 24 V to 5 V | LM76003 remains suitable and active. Its 3.5 A rating gives 0.5 A / 16.7% current margin over the 3 A design target. | Retain LM76003RNPR and perform the manufacturer design-flow, thermal, loop, and input/output-capacitor calculations during capture. |
| LCD/touch rails | S8 closes IOVCC at fixed 1.8 V, specifies 2.8 V VCI, and confirms touch VDD may be 2.8–3.3 V. S2's 3.3 V VCI header value is also within S1 limits, but S8 and S1 typical support 2.8 V. | Retain TLV75518 for IOVCC, select TLV75528 for VCI, and retain TLV75533 for TOUCH_3V3. |
| Sequencing | S8 confirms VDDI = IOVCC, reset-low behavior, ≥5 ms rail-stable delay, and ≥120 ms normal shutdown wait. It does not remove the need for hard-unplug hardware. | Retain conservative IOVCC→VCI→reset ordering and reverse shutdown, plus early input-fail detection, isolated hold-up, active discharge, and hardware reset/backlight clamps. |
| USB/backfeed | The Nano contains a USB-to-`VCC_5V` MOSFET path, but its documentation does not authorize arbitrary dual-source operation. USB can keep Nano GPIOs live while all display rails are off. | Add a removable isolation jumper and reverse-blocking/switching in the daughterboard-to-Nano 5 V feed; design all cross-domain signals for Nano-only power. |
| Backlight | S8 confirms 16.8–19.8 V at 240 mA total. Buck operation is viable but only has 1.8 V gross headroom at the 21.6 V minimum adapter. TPS92511's current tolerance is also wider than the PRD's ±5% target. | Prefer TPS922053DYYR with external precision sense, ideal-diode input, and approximately 200–300 kHz operation. Retain LT8391A only as a contingency if the completed loss budget fails. |
| DSI | Mapping/routing remain confirmed. S8 specifies RGB888 and 600-wide active timing but gives an impossible 110 Mb/s/lane value and repeats a 500 Mb/s/lane ceiling below the active-only requirement. | Keep all PCB rules. Do not freeze `lane_bit_rate_mbps`; require a known-working host setting and corrected limit from Displayman. |
| Touch | PCA9306 alone does not satisfy the full no-backpower requirement: it covers only SCL/SDA and depends on EN being low at every invalid power state. | Replace the baseline with a four-channel powered-off-protected switch such as TMUX1574, gated by both-domain-valid logic, for SCL/SDA/INT/RESET. Retain the open-drain reset clamp where useful. |
| GPIOs | The selected GPIO numbers exist and are not strapping pins, but three PRD header-pin labels are wrong. GPIO24 also conflicts with the ESP32-P4 default USB Serial/JTAG function. | Correct header pins before capture. Move `LCD_PWR_EN` from GPIO24 to an unused exposed GPIO, provisionally GPIO20 or GPIO21 after firmware/BSP confirmation. |
| Connectors | S8 confirms bottom-contact 40-pin LCD and 8-pin touch interfaces. The Nano connector family is plausible, but its exact on-board MPN is absent from the Waveshare schematic. | Retain Molex 505110-4096 and Hirose FH12-8S-0.5SH(55). Keep only Nano FFC/contact presentation and physical placement open until inspection. |

## 3. Requirements versus implementation choices

The requirements below remain controlling even where a different implementation is recommended.

| Controlling requirement | Current PRD implementation | Validation result |
|---|---|---|
| Accept a regulated, center-positive 24 V +/-10% wall adapter and tolerate accidental reverse polarity. | PJ-044AH, fuse, SS5P6, SMBJ30A | Requirement retained. Connector and reverse-protection components should change. |
| Produce a robust 5 V / 3 A rail for the Nano and local regulators. | LM76003 | Requirement and candidate retained. |
| Apply IOVCC, then VCI, then release reset; assert reset and remove VCI/IOVCC safely at shutdown. | LM3880, TPS22919, TPS3808, reset buffer | Sequence retained. Fixed 1.8 V IOVCC and 2.8 V VCI are resolved; the exact sequencer remains an implementation choice. |
| Prevent current injection between Nano and touch domains in every legal power state. | PCA9306 on SCL/SDA | Requirement retained. PCA9306 implementation is not sufficient by itself; isolate all four conductors. |
| Supply 240 mA constant current and PWM dimming without overdriving the module. | TPS922053 buck | Requirement retained. S8 closes the load limits; TPS922053 is preferred and buck-boost is retained only as a failed-headroom contingency. |
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
| Touch 3.3 V LDO — TI `TLV75533PDBVR` | ACTIVE; fixed 3.3 V, 500 mA, SOT-23-5; soft start, output discharge, current limit.[^5] | Ample for the 13 mA typical touch load plus support margin. | Retain on a separately switchable TOUCH_3V3 domain. |
| IOVCC LDO — TI `TLV75518PDBVR` | ACTIVE; fixed 1.8 V, 500 mA, SOT-23-5 with output discharge. | Capacity is ample for the panel's unsplit 60 mA maximum. S8 explicitly approves 1.8 V and corrects the printed absolute maximum. | **Retain and fix at 1.8 V.** Do not provide a user-selectable 3.3 V option. |
| VCI LDO — TI `TLV75528PDBVR` | ACTIVE/production; fixed 2.8 V, 500 mA, SOT-23-5 with output discharge.[^5] | Matches S8's explicit VCI instruction and S1's typical value; ample for the panel's unsplit 60 mA maximum. | **Select as the VCI source**, followed by the controlled TPS22919 switch. |
| VCI switch — TI `TPS22919DCKR` | ACTIVE; 1.6–5.5 V, 1.5 A, 90 mOhm typical, SC70-6, controlled rise and adjustable quick-output discharge.[^6] | More than adequate current and useful for deterministic discharge. | Retain. Select QOD resistor and capacitance against confirmed power-down timing. |
| Sequencer — TI `LM3880MF-1AA/NOPB` | ACTIVE family and exact 6-pin SOT-23 orderable; fixed three-stage behavior. | Orders flags, including reverse sequence, but cannot preserve sequencing after its own supply collapses and does not itself sense 24 V early. | Keep as candidate, not requirement. Freeze after the hold-up calculation; discrete supervisor/logic may be more flexible. |
| Power-fail supervisor — TI `TPS3808G01DBVR` | ACTIVE; adjustable 0.405 V sense, open-drain reset, programmable delay, SOT-23-6. | Suitable when powered from the maintained low-voltage node. It cannot connect directly to 24 V; use a divider and verify pin ratings. | Retain the function; select the exact supervisor with the hold-up/discharge design. |
| Reset buffer — TI `SN74LVC1G07DBVR` | ACTIVE; SOT-23-5 open-drain buffer, overvoltage-tolerant I/O, Ioff partial-power/back-drive protection.[^7] | Suitable for a wired-AND reset clamp pulled up to the destination rail. | Retain where a one-way reset clamp is needed. Do not use it to isolate bidirectional INT. |
| I2C translator — TI `PCA9306DCTR` | ACTIVE VSSOP-8 pass-FET translator. High impedance requires EN low; only SCL/SDA are covered. | It does not guarantee no backpower across all four touch conductors, and two 3.3 V domains do not require translation. | **Replace as baseline.** |
| Touch-domain switch — TI `TMUX1574DYYR` or `TMUX1574PWR` | ACTIVE; 1.5–5.5 V, four bidirectional SPDT channels, powered-off protection to 3.6 V, fail-safe controls, 2 ohm typical on-resistance.[^8] | One device disconnects SCL, SDA, INT, and RESET and tolerates Nano-side signals while its touch-domain supply is off. | **Recommended substitution** for PCA9306, using one throw/channel and hardware enable only when both 3.3 V domains are valid. |
| MIPI ESD — TI `TPD6E05U06RVZR` | ACTIVE; six channels, 14-USON flow-through package, 0.47 pF typical I/O capacitance, up to 6 Gb/s class.[^9] | Channel count covers clock plus two data pairs. Loading is suitable if placement/ground return are excellent. | Retain adjacent to panel connector. |
| Touch ESD — TI `TPD4E05U06DQAR` | ACTIVE; four channels, 10-USON flow-through package, 0.5 pF typical. | Correct conductor count for SCL/SDA/INT/RESET. | Retain adjacent to touch connector, on connector side of isolation. |
| Original buck LED driver — TI `TPS92511DDA` | ACTIVE; 4.5–65 V buck, <=500 mA, exposed-pad HSOIC-8. Its 249 mA nominal test condition spans 233–268 mA over temperature, wider than the project's ±5% target.[^10] | The topology fits S8's voltage range, but current accuracy and deep-dimming performance are weaker than a current-generation alternative. | **Replace as baseline.** Retain only as a prototype fallback with a deliberately derated current setpoint. |
| Preferred buck LED driver — TI `TPS922053DYYR` | ACTIVE/production; 4.5–65 V, integrated 150 mΩ switch, 100 ns minimum off-time, external 200 mV differential sense, fault output, spread spectrum, and fast/hybrid PWM dimming.[^19] | At 240 mA, 0.833 Ω nominal sense resistance and the ±3% threshold allow the ±5% system target with a precision resistor. A 200–300 kHz target provides high-duty margin for 19.8 V from the protected 21.6 V minimum input. | **Recommended selection.** Complete loss, inductor, diode, sense-tolerance, compensation, thermal, and fault calculations during Phase 2. |
| Buck-boost fallback — ADI `LT8391A` | Recommended for new designs; 4–60 V input, 0–60 V output, synchronous four-switch single-inductor LED controller, 600 kHz–2 MHz, PWM dimming.[^11] | Regulates with input above, below, or equal to LED voltage. More complex and uses four external MOSFETs. | Retain only if the completed TPS922053 worst-case budget or dummy-load test cannot regulate 19.8 V at minimum protected input. |
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

### 5.3 Confirmed LCD and touch rails

- `LCD_IOVCC` remains separate, fixed at the S8-approved 1.8 V, and sequenced.
- `LCD_VCI` is fixed at 2.8 V using TLV75528 and remains separately switched after IOVCC. This follows S8's explicit instruction and S1's typical value; the older S2 3.3 V header value remains documented but is within S1's allowed range and does not block the safer nominal selection.
- `TOUCH_3V3` should be separately switchable, establishing a defined off state during Nano USB-only power.
- S1 does not split its 60 mA maximum between VCI and IOVCC. Size both LCD paths for the PRD's >=100 mA requirement and measure actual current at bring-up.

### 5.4 Sequencing and hard unplug

Conservative order remains: validate maintained supply; enable 1.8 V IOVCC; enable VCI after delay; hold reset low until both rails have been stable for at least 5 ms; release reset after at least a 10 ms low interval; initialize in firmware; enable backlight last. Normal shutdown forces backlight off, sends 0x28 then 0x10, waits at least 120 ms, asserts reset, then removes VCI and IOVCC. Hard unplug still requires the hardware path below.

A reliable hard-unplug implementation needs:

- divider/supervisor sensing `VIN_PROT_24V` early;
- a low-current `DISPLAY_HOLDUP_5V` reservoir;
- hardware forcing `BL_HW_ENABLE = 0` and asserting LCD/touch reset;
- active discharge/controlled switches guaranteeing VCI falls before IOVCC.

LM3880 orders outputs while powered but cannot create the energy needed to complete shutdown. Initial capacitor sizing is `C >= I x delta_t / delta_V`. For 20 ms and 1.5 V permitted droop:

- 60 mA load: `C >= 800 uF`
- 100 mA load: `C >= 1333 uF`

This demonstrates why hold-up excludes Nano/backlight. Final capacitance, ESR, temperature derating, regulator dropout, and timing depend on measured load. A nominal 1000–1500 uF is a bench starting range, not a released value.

### 5.5 USB and backfeed state model

| 24 V | Nano USB | Required behavior |
|---|---|---|
| Off | Off | All rails discharged; reset asserted; backlight disabled. |
| On | Off | Daughterboard powers Nano through `NANO_5V`; normal sequence permitted. |
| Off | On | Nano may run, but must not energize `SYS_5V`, LCD, touch, or adapter input. All cross-domain conductors tolerate Nano-side activity without injection. |
| On | On | Allowed only after bench validation. Default build/instructions must permit isolation with the Nano-feed jumper. |

Nano DSI pins 14/15 are `ESP_3V3` references and must never be driven.

## 6. Backlight architecture and calculations

S8 confirms 240 mA total, with `VLED,min = 16.8 V`, `VLED,typ = 19.2 V`, and `VLED,max = 19.8 V` over temperature. `PLED,typ = 19.2 V x 0.240 A = 4.608 W`. Before protection and converter losses, worst-case buck headroom at minimum input is `21.6 - 19.8 = 1.8 V`.

Use TPS922053DYYR as the preferred buck. At 200 kHz, its 100 ns minimum off-time gives an ideal maximum duty near 98%; at 300 kHz it is near 97%. The completed worst-case inequality remains:

`19.8 V + Vdriver/conduction + Vinput_path + Vcable + Vripple/tolerance <= 21.6 V`

The LM74700 ideal-diode input and TPS922053's low switch resistance materially improve the margin. If the calculation or dummy-load test fails, use the LT8391A four-switch buck-boost branch; it is not a pin-compatible contingency and requires its own design.[^11]

At the nominal 200 mV sense threshold, `R_SENSE = 0.200 / 0.240 = 0.833 ohm`. The threshold's ±3% limit plus a precision resistor supports the project's ±5% target, unlike TPS92511's wider full-temperature current spread.

TPS922053 supports fast PWM and hybrid dimming, including a manufacturer 2,000:1 example at 20 kHz. The original 20 kHz firmware target is reasonable with the new baseline, subject to measured current pulses, low-duty linearity, flicker, audible behavior, and camera interaction.

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

S8 confirms RGB888, H-active = 600, two lanes, continuous clock recommended, and video-mode support, but UQ-02 remains blocking because its rate answer is impossible. At the S2-derived 60.007 Hz frame rate, active pixels alone require about 553 Mb/s/lane before overhead. A continuous 55 MHz RGB888 stream is 660 Mb/s/lane before overhead. S8's 110 Mb/s/lane and stated 500 Mb/s/lane maximum are both insufficient. Obtain the actual data-lane bit-rate setting from a known-working host; do not confuse the DPI pixel clock with D-PHY clock-lane frequency.

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

S8 confirms that INT becomes open-drain active-low after initialization and requires a 2–10 kohm pull-up to the powered touch domain. It recommends 0x5D but incorrectly associates that address with INT high during reset; S1's timing diagrams map INT low to 7-bit 0x5D (`0xBA/0xBB`) and INT high to 0x14 (`0x28/0x29`). Hardware shall support both. Firmware shall provisionally use S1's 0x5D/INT-low sequence, then repeat the full reset sequence for 0x14 if identification fails.

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
| Panel LCD | S1 names Molex 5051104096; the connector manufacturer and S8 confirm 40 positions, 0.50 mm, bottom contact.[^13] | Board face/cable bend, pin 1, contact exposure on sample. |
| Panel FFC | Candidates are 40 way, 0.50 mm, type A same-side, 76/102 mm.[^14] | Select length after mock-up; verify installed mating orientation. |
| Touch | S8 confirms 8 positions/0.50 mm and bottom contact; FH12 candidate is bottom-contact, 0.3 mm FPC, front ZIF.[^15] | Actual thickness, insertion direction/depth, bend radius, and board-side flex presentation. |
| Nano headers | 2 x 13/2.54 mm topology; SSW family available.[^16] | Pin length, board gap, underside clearance, standoffs, keepouts. |

## 11. Schematic organization and net naming plan

This is a plan only; KiCad remains blank.

Suggested sheets: `00_system`, `10_input_power`, `20_5v_power`, `30_display_power`, `40_mipi_dsi`, `50_touch`, `60_backlight`, `70_headers_debug`.

Canonical net plan:

- power: `VIN_ADAPTER_24V`, `VIN_PROT_24V`, `SYS_5V`, `DISPLAY_HOLDUP_5V`, `NANO_5V`, `TOUCH_3V3`, `LCD_IOVCC`, `LCD_VCI`
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
- selected TPS922053 over TPS92511 so the 240 mA ±5% target and 20 kHz dimming target are both supportable.

### 12.2 Displayman-response disposition

- **UQ-01 CLOSED:** fixed 1.8 V IOVCC is approved; 1.68 V absolute maximum is identified as a typo.
- **UQ-02 STILL BLOCKING:** RGB888/mode/continuous-clock guidance is narrowed, but 110 Mb/s/lane and the stated 500 Mb/s/lane ceiling cannot carry the confirmed timing.
- **UQ-03/UQ-09 CLOSED:** 16.8–19.8 V at 240 mA total, 60 mA per internal string.
- **UQ-04 CLOSED:** use S8's 2.8 V VCI instruction and S1's conservative IOVCC→VCI→reset / reverse shutdown ordering, with hardware hold-up for hard unplug.
- **UQ-05 NARROWED:** panel/touch bottom-contact requirements are confirmed; Nano-side physical presentation remains sample-dependent.
- **UQ-10 NARROWED/NON-BLOCKING:** open-drain active-low INT is confirmed; the address-strap polarity conflicts with S1, but hardware and firmware can support/test both.
- **UQ-13 HOST REQUIREMENT CLOSED:** use H-active = 600 and let the driver discard 60 columns per side. The detailed source-channel ranges remain arithmetically inconsistent but do not block the schematic.
- **UQ-14 OPEN/NON-BLOCKING:** original machine-readable initialization export and wrapper/delay semantics remain desirable.

Vendor connector recommendations may help, but final board-facing orientation still requires sample verification.

### 12.3 Decisions now finalized or ready

1. fix IOVCC at 1.8 V using TLV75518;
2. use RGB888, 600 × 1280 H-active/V-active timing, and continuous clock as the initial mode, but leave lane rate blocked;
3. use TPS922053DYYR buck, approximately 200–300 kHz, 0.833 ohm nominal sense, and 20 kHz PWM as the Phase 2 baseline;
4. design GT9271 INT as open-drain active-low with a 2–10 kohm touch-side pull-up and support both reset-selected addresses;
5. retain conservative rail sequencing plus isolated hard-unplug hold-up;
6. retain bottom-contact panel/touch connectors, subject to sample presentation and insertion-direction checks;
7. use the corrected Nano header mappings and move `LCD_PWR_EN` away from GPIO24.

## 13. Actions requiring owner physical input

- confirm actual 24 V adapter outer/inner barrel diameter and center-positive marking;
- photograph/inspect both sides of Nano DSI connector/cable and LCD/touch flex tails with pin-1 marks/exposed contacts;
- measure Nano header pin length, board spacing, mounting holes, and underside clearance;
- choose stack-on versus side-by-side arrangement and cable lengths after a paper/3D mock-up.

No owner electrical-design decision is required to resolve the remaining DSI or VCI contradictions; those require Displayman. The physical actions above remain necessary before footprint/placement freeze.

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
[^19]: Texas Instruments, [TPS922052/TPS922053/TPS922054/TPS922055 datasheet Rev. B](https://www.ti.com/product/TPS922053), February 2025; product/orderability checked 2026-09-14.

## 15. Displayman response evidence

S8 is the email from Anson Ho received 2026-09-14 and stored in the repository as `docs/design-notes/Re- Displayman | Datasheet & Evaluation Units for KD068HDFID009-C009A.pdf`, SHA-256 `76a9e53303412ff29189debf72a1f4c5dcf495e249f0ce86e32092063407ed4d`.

The direct confirmations adopted into PRD v0.3 are: fixed 1.8 V IOVCC; VDDI means connector pin 3 IOVCC; reset-low and shutdown delays; RGB888 and 600-wide active transport; 16.8–19.8 V / 240 mA total backlight; internal 60-column-per-side masking; bottom-contact LCD/touch FPCs; and open-drain active-low touch INT. The DSI arithmetic, VCI nominal voltage, GT9271 address-strap parenthetical, and detailed source-channel range are retained as explicit contradictions rather than being inferred away.
