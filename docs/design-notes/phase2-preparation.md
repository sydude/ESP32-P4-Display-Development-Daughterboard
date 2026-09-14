# Phase 2 preparation and engineering validation

**Project:** ESP32-P4 Displayman Development Daughterboard  
**Date:** 2026-09-14  
**Controlling specification:** `docs/PRD.md`, revision 0.4 pending approval
**Status:** vehicle-power validation complete at architecture level; DSI transport remains blocking — not a schematic release

## 1. Scope and release boundary

This note records the non-blocking work completed before and after Displayman's 14 September 2026 response (S8). It validates the Phase 1 component candidates and architecture against the supplied module/Nano documents, written vendor evidence, and current manufacturer documentation. Section 15 records the response disposition and supersedes earlier statements that a now-answered item is still awaiting Displayman.

No schematic symbols, nets, footprints, PCB geometry, or other KiCad design content were added. The existing files under `hardware/kicad/` remain the canonical blank project and were inspected read-only.

The following remain prohibited until Displayman corrects the remaining DSI blocker and PRD v0.3 is approved:

- freezing the DSI host transport settings;
- releasing the schematic or beginning PCB layout.

## 2. Executive disposition

| Area | Result of independent validation | Phase 2 disposition |
|---|---|---|
| 12 V vehicle input | A simple boost is not robust against an above-output input event or 24 V misconnection. A four-switch stage preserves regulation/isolation and the common downstream bus. | Add LM74800-Q1 protected input, LM5176-Q1 24 V/30 W four-switch buck-boost, and a separate output ideal diode. Full-load target 9–18 V; crank reboot permitted. |
| Dual-source ORing | Independent ideal-diode paths can safely coexist without a procedural selector. | Retain the bench LM74700 path and add reverse blocking at the vehicle-converter output; whichever branch is higher supplies the bus. |
| 24 V input | The protection concept is sound, but the selected barrel jack is mechanically inconsistent with the PRD input requirement and the Schottky diode unnecessarily consumes voltage headroom. | Replace the jack candidate; prefer an ideal-diode controller and N-MOSFET over the series Schottky. Retain fuse and SMBJ30A subject to final inrush/transient calculations. |
| 24 V to 5 V | LM76003 remains suitable and active. Its 3.5 A rating gives 0.5 A / 16.7% current margin over the 3 A design target. | Retain LM76003RNPR and perform the manufacturer design-flow, thermal, loop, and input/output-capacitor calculations during capture. |
| LCD/touch rails | S8 closes IOVCC at fixed 1.8 V, specifies 2.8 V VCI, and confirms touch VDD may be 2.8–3.3 V. S2's 3.3 V VCI header value is also within S1 limits, but S8 and S1 typical support 2.8 V. | Retain TLV75518 for IOVCC, select TLV75528 for VCI, and retain TLV75533 for TOUCH_3V3. |
| Sequencing | S8 confirms VDDI = IOVCC, reset-low behavior, ≥5 ms rail-stable delay, and ≥120 ms normal shutdown wait. It does not remove the need for hard-unplug hardware. | Retain conservative IOVCC→VCI→reset ordering and reverse shutdown, plus early input-fail detection, isolated hold-up, active discharge, and hardware reset/backlight clamps. |
| USB/backfeed | USB-only and USB plus either high-voltage source must now be normal modes. The Nano MOSFET path is visible in S3 but lacks an explicit reverse-current specification. | Use TPS259470A true-reverse-blocking eFuse from SYS_5V to NANO_5V; retain the jumper only for service. Bench-test the Nano path toward laptop VBUS before release. |
| Backlight | S8 confirms 16.8–19.8 V at 240 mA total. Buck operation is viable but only has 1.8 V gross headroom at the 21.6 V minimum adapter. TPS92511's current tolerance is also wider than the PRD's ±5% target. | Prefer TPS922053DYYR with external precision sense, ideal-diode input, and approximately 200–300 kHz operation. Retain LT8391A only as a contingency if the completed loss budget fails. |
| DSI | Mapping/routing remain confirmed. S8 specifies RGB888 and 600-wide active timing but gives an impossible 110 Mb/s/lane value and repeats a 500 Mb/s/lane ceiling below the active-only requirement. | Keep all PCB rules. Do not freeze `lane_bit_rate_mbps`; require a known-working host setting and corrected limit from Displayman. |
| Touch | PCA9306 alone does not satisfy the full no-backpower requirement: it covers only SCL/SDA and depends on EN being low at every invalid power state. | Replace the baseline with a four-channel powered-off-protected switch such as TMUX1574, gated by both-domain-valid logic, for SCL/SDA/INT/RESET. Retain the open-drain reset clamp where useful. |
| GPIOs | The selected GPIO numbers exist and are not strapping pins, but three PRD header-pin labels are wrong. GPIO24 also conflicts with the ESP32-P4 default USB Serial/JTAG function. | Correct header pins before capture. Move `LCD_PWR_EN` from GPIO24 to an unused exposed GPIO, provisionally GPIO20 or GPIO21 after firmware/BSP confirmation. |
| Connectors | S8 confirms bottom-contact 40-pin LCD and 8-pin touch interfaces. The Nano connector family is plausible, but its exact on-board MPN is absent from the Waveshare schematic. | Retain Molex 505110-4096 and Hirose FH12-8S-0.5SH(55). Keep only Nano FFC/contact presentation and physical placement open until inspection. |

## 3. Requirements versus implementation choices

The requirements below remain controlling even where a different implementation is recommended.

| Controlling requirement | Current PRD implementation | Validation result |
|---|---|---|
| Accept nominal-12 V vehicle power, survive crank safely, and recover cleanly. | Preferred 12 V→protected four-switch buck-boost→24 V bus. | Requirement added; full-load 9–18 V, hysteretic dropout below about 7–8 V, and OV cutoff above charging range. |
| Permit simultaneous 12 V, 24 V, and Nano USB without backfeed. | Independent high-voltage ideal diodes plus Nano-feed reverse-blocking eFuse. | Requirement added; procedural source selection is not acceptable. |
| Accept a regulated, center-positive 24 V +/-10% wall adapter and tolerate accidental reverse polarity. | PJ-044AH, fuse, SS5P6, SMBJ30A | Requirement retained. Connector and reverse-protection components should change. |
| Produce a robust 5 V / 3 A rail for the Nano and local regulators. | LM76003 plus service jumper | LM76003 retained; jumper-only coexistence superseded by TPS259470A current-limited true-reverse-blocking feed. |
| Apply IOVCC, then VCI, then release reset; assert reset and remove VCI/IOVCC safely at shutdown. | LM3880, TPS22919, TPS3808, reset buffer | Sequence retained. Fixed 1.8 V IOVCC and 2.8 V VCI are resolved; the exact sequencer remains an implementation choice. |
| Prevent current injection between Nano and touch domains in every legal power state. | PCA9306 on SCL/SDA | Requirement retained. PCA9306 implementation is not sufficient by itself; isolate all four conductors. |
| Supply 240 mA constant current and PWM dimming without overdriving the module. | TPS922053 buck | Requirement retained. S8 closes the load limits; TPS922053 is preferred and buck-boost is retained only as a failed-headroom contingency. |
| Maintain a low-discontinuity two-lane DSI channel. | Straight-through mapping, optional series footprints, TPD6E05U06 | Requirement retained. ESD part retained; optional resistors may be used only as inline flow-through footprints with negligible stubs. |

## 4. Component revalidation

Lifecycle labels below are manufacturer labels observed on 2026-09-14. Distributor stock is deliberately not treated as a design guarantee.

| Function / present MPN | Manufacturer status and package check | Electrical/suitability result | Recommendation |
|---|---|---|---|
| Vehicle connector — Molex `43045-0200` / `43025-0200` | Current manufacturer pages; keyed/latching 2-circuit Micro-Fit 3.0. Header is right-angle THT, 3.00 mm pitch, −40 to 105 °C, 8.5 A/contact. | Ample for the calculated 4.41 A at 8 V/30 W threshold. Connector is not sealed or automotive-qualified. | Use as evaluation default; freeze terminals, wire gauge, and harness length after physical selection.[^20] |
| Vehicle protection — TI `LM74800QDRRRQ1` | ACTIVE; AEC-Q100, 3–65 V, −65 V reverse input, WSON-12, back-to-back N-FET control, adjustable OV cutoff and reverse-current blocking.[^21] | Covers reverse battery, controlled disconnect, and source isolation ahead of the converter. | Select with common-source 100 V FETs; complete dV/dt, SOA, and surge calculations. |
| Vehicle TVS — Bourns `SM8S24CA-Q` | Current automotive-grade/AEC-Q101 family; bidirectional 24 V standoff, 38.9 V maximum clamp class, 6.6 kW DO-218.[^22] | High energy is appropriate for evaluation, and bidirectional behavior avoids forward conduction under reverse battery. Large footprint and harness-dependent stress remain. | Preferred clamp. It does not establish ISO compliance; coordinate with fuse/filter/source impedance. |
| Vehicle converter — TI `LM5176QPWPRQ1` | ACTIVE; AEC-Q100, 4.2–55 V operating, 60 V maximum, HTSSOP-28, synchronous four-switch, UVLO/current limit/PGOOD/OVP.[^23] | Regulates 24 V when input is below/equal/above target and avoids the uncontrolled pass-through weakness of a boost-only stage. 30 W is modest for an external-FET controller. | **Select as preferred architecture.** LM51772-Q1 is newer but its 40-pin/I²C feature set is unnecessary for a fixed 24 V evaluation rail. |
| Protection/converter FET — TI `CSD19531Q5A` | ACTIVE; catalog, 100 V, 6.4 mΩ maximum at 10 V, 37 nC typical Qg, 5 × 6 mm SON, −55 to 150 °C.[^24] | Voltage and conduction margin are suitable starting points at approximately 5 A peak input. Switching and SOA losses remain layout/operating-point dependent. | Use as provisional common FET class for protection/ORing and converter calculations; exact count/alternate may change after loss model. |
| Vehicle inductor — Coilcraft `XAL7030-682MEC` class | Current/in-stock manufacturer listing; shielded AEC-Q200 series, 6.8 µH, 15 A typical Isat, 6.8 A 40 °C-rise Irms, −40 to 125 °C ambient.[^25] | Plausible thermal/current margin for the 30 W stage without excessive footprint. | Calculation anchor, not locked value; finalize from LM5176 ripple/loss/compensation design. |
| Vehicle output ideal diode — TI `LM74700-Q1` + 100 V FET | ACTIVE; 3.2–65 V, fast reverse-current blocking, SOT-23.[^3] | Prevents bench 24 V from driving the vehicle converter output even when the converter is off. | Add independently of input protection. |
| Nano feed eFuse — TI `TPS259470ARPWR` | ACTIVE; datasheet Rev. C (May 2026), 2.7–23 V, 5.5 A, 28.2 mΩ typical at 3 A, integrated back-to-back FETs and reverse-current block under all conditions.[^26] | Current limit, inrush control, UV/OV monitoring, and Nano→SYS_5V blocking in one 2 × 2 mm QFN. | **Replace jumper-as-procedure strategy.** Set about 3.2 A, auto-retry; retain jumper only as service disconnect. |
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

### 5.1 Preserved downstream architecture

`VIN_PROT_24V` is redefined as the common, source-ORed 24 V-class internal bus. Existing loads remain electrically unchanged: LM76003 generates `SYS_5V`; fixed 1.8 V IOVCC, 2.8 V VCI, and 3.3 V touch rails remain; the display hold-up/early-fail sequence remains; TPS922053 remains on the high-voltage bus; and the 24 V bench path remains a direct protected source.

At the bench extremes, `VIN_PROT_24V` remains 21.6–26.4 V. The vehicle converter targets 24.0 V nominal. No downstream rail is redesigned merely because the vehicle source was added.

### 5.2 Topology comparison

| Topology | Above/below 24 V behavior | Efficiency / thermal | Area / risk | Disposition |
|---|---|---|---|---|
| Non-synchronous boost | Input-to-output diode path passes above-output events | Diode loss | Small but unsafe surge/miswire behavior | Rejected |
| Synchronous boost | Better efficiency; still normally has input-to-output conduction | Good in boost region | Extra disconnect still required | Rejected |
| SEPIC/Zeta | Regulates across boundary without simple pass-through | Higher RMS/magnetics loss | Larger/harder EMI design | Not preferred |
| Isolated flyback | Regulates and isolates | Unnecessary loss at 30 W | Larger transformer/EMI burden | Rejected |
| Four-switch synchronous buck-boost | Regulates below, at, and above 24 V with controlled faults | External-FET losses optimizable | More FETs/area, mature design flow | **Preferred** |

LM5176-Q1 is selected over newer LM51772-Q1: both are ACTIVE and automotive-rated, while LM5176's fixed-function HTSSOP-28 avoids unnecessary I²C/40-pin complexity. Switching frequency, inductor, compensation, FETs, current shunt, and capacitors remain schematic-stage choices.

### 5.3 Vehicle protection chain

Preferred order: keyed ≥8 A connector → 5 A time-delay/serviceable fuse → damped differential input filter (optional common-mode choke only after EMI testing) → SM8S24CA-Q bidirectional TVS → LM74800-Q1 common-source back-to-back 100 V N-FETs → LM5176-Q1 24 V/30 W converter → LM74700-Q1 output ideal diode → `VIN_PROT_24V`.

Full-load target is 9–18 V. Provisional UVLO is about 8.0 V rising / 7.0 V falling; provisional OV cutoff is about 20 V rising. Deep crank may reboot: hardware first disables backlight/asserts reset, then removes rails; a stable return triggers a complete init.

A ~38.9 V TVS clamp leaves about 16 V to the controller's 55 V operating ceiling, but voltage arithmetic alone is not qualification. Dynamic resistance, pulse current, trace inductance, source impedance, fuse clearing, FET avalanche/SOA, and pin overshoot require simulation and test.

### 5.4 Full-system power and input-current calculation

| Consumer | Delivered power | Common-bus input estimate |
|---|---:|---:|
| 5 V rail ceiling | 15.0 W | 16.67 W at 90% |
| Backlight, 19.8 V × 0.240 A | 4.752 W | 5.28 W at 90% |
| Supervisors/ORing allowance | — | 0.25 W |
| Expected worst-case bus load | — | **≈22.2 W** |
| Vehicle-stage design point | — | **30 W at 24 V (1.25 A)** |

| Vehicle input | Assumed η | At 22.2 W bus load | At 30 W design capacity |
|---:|---:|---:|---:|
| 9.0 V | 88% | 2.80 A | 3.79 A |
| 12.0 V | 90% | 2.06 A | 2.78 A |
| 14.4 V | 92% | 1.68 A | 2.26 A |
| 16.0 V | 92% | 1.51 A | 2.04 A |
| 8.0 V threshold | 85% | 3.26 A | 4.41 A |

At 6 V crank the converter is below UVLO, so full-power current is not required. A 5 A time-delay fuse and approximately 5 A converter input limit cover the 30 W/8 V starting point; final I²t and peak-current values follow the controller design and transient model.

### 5.5 Source-selection matrix

| Bench | Vehicle | Common bus | Required behavior |
|---|---|---|---|
| Off | Off | Off | Both connectors isolated; backlight off/reset asserted. |
| On | Off | Bench 21.6–26.4 V | Vehicle converter cannot be energized backward. |
| Off | On | Vehicle 24.0 V | Barrel center pin sees no reverse current. |
| On | On | Higher delivered branch supplies | Other ideal diode blocks; no current-sharing claim. |
| Active source removed, other valid | Other branch takes load | Bounded dip; reset/reinit if PGOOD threshold crossed. |
| Vehicle crank/UVLO, bench valid | Bench continues | Vehicle off/reverse blocked. |
| Either branch faults | Healthy branch isolated from fault | Fuse/ideal-diode coordination verified. |
| Both invalid | Shutdown | Hardware backlight-off and ordered display power-down. |

### 5.6 USB/Nano feed strategy

The jumper-only strategy is superseded because USB plus either source is routine. New default: `SYS_5V → TPS259470A → service jumper → NANO_5V`. The eFuse provides true reverse-current blocking, ~3.2 A current limit, controlled inrush, UV/OV monitoring, and fault output. The jumper is normally fitted and used only for service/current measurement.

The opposite direction, daughterboard 5 V toward USB VBUS, is controlled by the Nano's onboard USB-to-`VCC_5V` MOSFET. USB VBUS is not separately exposed at the headers, so the daughterboard cannot independently sense a late USB insertion. A zero-reverse-current test into a programmable USB source is therefore mandatory. Failure requires Nano modification/access ahead of that MOSFET or a dedicated data-only/debug path.

### 5.7 Complete source/domain power-state matrix

| Bench | Vehicle | USB | Nano | Display/touch | Isolation result |
|---|---|---|---|---|---|
| 0 | 0 | 0 | Off | Off | All nodes discharge. |
| 0 | 0 | 1 | USB only | Forced off | eFuse and signal switches block injection. |
| 0 | 1 | 0 | Daughterboard | Allowed after bus valid | Vehicle isolated from bench/USB. |
| 0 | 1 | 1 | Powered | Allowed after bus valid | No HV backfeed; Nano USB test required. |
| 1 | 0 | 0 | Daughterboard | Allowed after bus valid | Bench isolated from vehicle. |
| 1 | 0 | 1 | Powered | Allowed after bus valid | eFuse blocks Nano→SYS_5V; Nano path blocks toward VBUS. |
| 1 | 1 | 0 | Daughterboard | Allowed after bus valid | Higher HV source wins; other blocks. |
| 1 | 1 | 1 | Powered | Allowed after bus valid | Mandatory simultaneous-source stress case. |

| Nano | Display request | Touch request | Hardware-enforced result |
|---|---|---|---|
| Off | Off | Off | All off/discharged. |
| Off | On | Any | Rejected; reset/backlight low, display rails off. |
| Off | Off | On | Rejected absent a later autonomous-touch design. |
| On | Off | Off | Nano only; cross-domain switches open. |
| On | Off | On | Touch only if common bus/SYS_5V valid. |
| On | On | Off | Display may sequence; touch isolated; backlight after init only. |
| On | On | On | Full system after all PGOOD/reset prerequisites. |
| Any | Any | Any during invalid/brownout | Hardware overrides: BL off, reset asserted, isolation open, ordered shutdown. |

These two tables exhaust the eight source combinations and independently requested domain combinations without duplicating 64 rows. TMUX1574 covers SCL/SDA/INT/RESET; DSI is Nano-driven only; ESP_3V3 remains reference-only.

### 5.8 Sequencing and hard unplug

The existing IOVCC→VCI→reset and reverse shutdown remain. Early-fail logic now considers common-bus, active-branch, and 5 V PGOOD/fault signals. If the common bus stays valid during ORing, operation may continue; any threshold crossing forces a controlled reset and later full reinit.

Hold-up remains `C ≥ I × Δt / ΔV`: 800 µF for 60 mA or 1333 µF for 100 mA at 20 ms/1.5 V. Exact capacitance still depends on measured display-domain current, dropout, ESR, and transition waveform. Nano/backlight remain excluded.

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

Suggested sheets: `00_system`, `10_bench_input`, `11_vehicle_input_buckboost`, `12_source_oring`, `20_5v_power`, `30_display_power`, `40_mipi_dsi`, `50_touch`, `60_backlight`, `70_headers_debug`.

Canonical net plan:

- power: `VIN_ADAPTER_24V`, `VIN_VEHICLE_12V`, `VEH_PROT`, `VEH_24V`, `VIN_PROT_24V`, `SYS_5V`, `DISPLAY_HOLDUP_5V`, `NANO_5V`, `TOUCH_3V3`, `LCD_IOVCC`, `LCD_VCI`
- valid/enable: `BENCH_VALID`, `VEH_VALID`, `VEH_CONV_PGOOD`, `VIN_GOOD`, `SYS_5V_GOOD`, `NANO_3V3_VALID`, `TOUCH_3V3_VALID`, `DISPLAY_PWR_EN`, `BL_HW_ENABLE`
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
- selected TPS922053 over TPS92511 so the 240 mA ±5% target and 20 kHz dimming target are both supportable;
- selected a four-switch vehicle converter over boost-only/SEPIC/flyback alternatives;
- preserved the common 24 V downstream architecture and established a 30 W vehicle-stage rating;
- replaced procedural source selection with independent ideal-diode isolation;
- replaced the Nano jumper-as-procedure concept with a true-reverse-blocking 5 V eFuse.

### 12.2 New vehicle-power risks

| Risk | Consequence | Control / closure |
|---|---|---|
| Low-input thermal stress | Approximately 3.8 A at 9 V/30 W and 4.4 A at 8 V threshold heats FETs, inductor, fuse, connector, and copper | 30 W loss model, 2 oz power copper/thermal vias as needed, current limit, and thermal test at 9 V/full load. |
| TVS/harness energy unknown | A high-energy pulse may exceed TVS/FET/fuse SOA even when voltage ratings appear adequate | Define or measure harness/source impedance; simulate pulse energy and perform controlled transient tests. No ISO claim. |
| Dual-source handover dip/chatter | Marginally equal sources can alternate or dip the bus | Fast ideal-diode controllers, adequate bus capacitance, PGOOD hysteresis/debounce, and full reinit on any invalid threshold. No current-sharing assumption. |
| Nano USB reverse behavior | Daughterboard 5 V could reach laptop if the Nano MOSFET does not block the header-to-VBUS direction | TPS259470A covers the opposite direction; perform programmable-USB backfeed test before release. Provide data-only/Nano modification contingency. |
| Power-stage EMI near MIPI | Additional four-switch node and higher 12 V input current can couple into DSI/touch | Physically separate vehicle hot loops, shielded inductor, continuous reference plane, optional filter footprint, and pre-compliance measurement. |
| Added board area | DO-218 TVS, four FETs, inductor, connectors, and thermal copper enlarge the evaluation board | Keep source conversion in a defined power zone; mechanical outline becomes a layout input, not an electrical blocker. |

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
7. use the corrected Nano header mappings and move `LCD_PWR_EN` away from GPIO24;
8. use LM74800-Q1 + LM5176-Q1 + independent output ideal diode for the nominal-12 V branch;
9. size the vehicle converter for 30 W at 24 V and full-load operation from 9–18 V;
10. use TPS259470A as the normal Nano feed, with the jumper retained only for service.

## 13. Actions requiring owner physical input

- confirm actual 24 V adapter outer/inner barrel diameter and center-positive marking;
- photograph/inspect both sides of Nano DSI connector/cable and LCD/touch flex tails with pin-1 marks/exposed contacts;
- measure Nano header pin length, board spacing, mounting holes, and underside clearance;
- choose stack-on versus side-by-side arrangement and cable lengths after a paper/3D mock-up;
- confirm the intended vehicle harness connector style, wire gauge, approximate lead length, and accessible fuse format; the documented Micro-Fit/5 A choices are safe evaluation defaults;
- during prototype bring-up, measure Nano USB VBUS current with daughterboard 5 V active and USB supply disabled, then repeat hot-plug/unplug with a current-limited programmable USB source;
- capture the actual vehicle supply at the proposed connection point during start/crank if representative transient testing is desired.

No owner electrical-design decision is required for the converter, protection, ORing, or safe-state strategy. The physical actions above affect connector/thermal/transient validation and must be completed before footprint or prototype release. The remaining DSI contradiction still requires Displayman.

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
[^20]: Molex, [43045-0200 PCB header](https://www.molex.com/en-us/products/part-detail/430450200) and [43025-0200 housing](https://www.molex.com/en-us/products/part-detail/430250200), checked 2026-09-14.
[^21]: Texas Instruments, [LM7480-Q1 datasheet Rev. C](https://www.ti.com/product/LM7480-Q1), ACTIVE status and product data checked 2026-09-14.
[^22]: Bourns, [SM8S-Q high-power automotive TVS datasheet](https://www.bourns.com/docs/product-datasheets/sm8s-q.pdf), checked 2026-09-14.
[^23]: Texas Instruments, [LM5176-Q1 datasheet Rev. B](https://www.ti.com/product/LM5176-Q1), ACTIVE status and product data checked 2026-09-14; [LM51772-Q1](https://www.ti.com/product/LM51772-Q1) comparison checked the same date.
[^24]: Texas Instruments, [CSD19531Q5A datasheet Rev. B](https://www.ti.com/product/CSD19531Q5A), ACTIVE status and product data checked 2026-09-14.
[^25]: Coilcraft, [XAL7030 series](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal7030/), part data/orderability checked 2026-09-14.
[^26]: Texas Instruments, [TPS25947 datasheet Rev. C](https://www.ti.com/product/TPS25947), ACTIVE status and May 2026 data checked 2026-09-14.

## 15. Displayman response evidence

S8 is the email from Anson Ho received 2026-09-14 and stored in the repository as `docs/design-notes/Re- Displayman | Datasheet & Evaluation Units for KD068HDFID009-C009A.pdf`, SHA-256 `76a9e53303412ff29189debf72a1f4c5dcf495e249f0ce86e32092063407ed4d`.

The direct confirmations adopted into PRD v0.3 are: fixed 1.8 V IOVCC; VDDI means connector pin 3 IOVCC; reset-low and shutdown delays; RGB888 and 600-wide active transport; 16.8–19.8 V / 240 mA total backlight; internal 60-column-per-side masking; bottom-contact LCD/touch FPCs; and open-drain active-low touch INT. The DSI arithmetic, VCI nominal voltage, GT9271 address-strap parenthetical, and detailed source-channel range are retained as explicit contradictions rather than being inferred away.
