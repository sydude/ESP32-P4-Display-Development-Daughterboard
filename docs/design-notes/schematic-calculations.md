# Phase 2 schematic calculations and design basis

**Project:** ESP32-P4 Displayman Development Daughterboard

**Date:** 2026-09-19

**Controlling specification:** `docs/PRD.md` v0.6

**Schematic revision:** Phase 2 / single-source v0.4

## 1. Scope

This note records the component-value, electrical-margin, sequencing, and power-state calculations for the reviewed schematic. REV1 has one protected nominal-12 V external input; bench work uses a regulated/current-limited 12 V source at the same connector. It is the design basis for review, not a substitute for prototype measurements.

The PCB has not been started. Manufacturer-specific land patterns called out in `schematic-review.md` remain intentionally unresolved until the physical interfaces are checked.

## 2. System load and vehicle-input budget

The converter is sized for a 30 W continuous output budget on `SYS_24V`. This covers the 240 mA backlight, Nano, LCD/touch logic, conversion loss, and development loads with margin. Representative full-load input currents are:

| Vehicle input | Assumed efficiency | Calculated input current |
|---:|---:|---:|
| 14.4 V | 90% | 2.31 A |
| 12.0 V | 88% | 2.84 A |
| 9.0 V | 86% | 3.88 A |
| 8.0 V | 85% | 4.41 A |

The 5 A MINI fuse, Micro-Fit connector, power MOSFETs, input filter, shunt, inductor, and power copper are therefore sized around approximately 4.5 A continuous at the low-input boundary and a higher controlled switching peak. Reboot during a deeper crank is intentional; the branch must turn off cleanly rather than attempt expensive ride-through.

## 3. Vehicle protection

`U201` is an LM74800-Q1 driving `Q201` and `Q202` as a back-to-back, common-drain pair. The common-drain arrangement provides reverse-polarity disconnect and reverse-current blocking on this TVS-protected evaluation input. A common-source load-dump topology would be reconsidered for an unsuppressed production automotive input, but is not required by this evaluation-board scope.

- UVLO divider: 56.2 kΩ / 10.0 kΩ. Using the nominal 1.22 V operating threshold gives approximately 8.08 V; the design label rounds the effective rising threshold to about 8.15 V after device/divider tolerances.
- OV divider: 100 kΩ / 6.49 kΩ. Using the nominal 1.22 V threshold gives approximately 20.0 V; tolerance places the intended cutoff near 20.2 V.
- `D201` is the 24 V-standoff, bidirectional SM8S24CA-Q clamp after the damped input filter.
- `F201` is a replaceable 5 A MINI blade fuse. This board does not claim ISO 7637-2 or ISO 16750 qualification.

The protection cutoff deliberately allows normal charging voltage while rejecting gross overvoltage and accidental 24 V connection to the nominal-12 V port. The actual clamp current and TVS energy depend on the external source and harness impedance and remain a controlled test item.

### 3.1 Reverse-battery-safe filter arrangement

`C203`, the 100 µF polarized bulk capacitor, is now connected to `VEH_PROT`, downstream of both LM74800-controlled MOSFETs. A reversed battery therefore sees no substantial reverse voltage across a polarized capacitor. The unprotected `VEH_FILTER` node contains only reverse-tolerant MLCCs: `C201` 100 nF, `C202` 22 µF, and the `R201`/`C204` 1 Ω/10 µF series damping branch. The bidirectional TVS also remains upstream of the disconnect.

For `L201 = 2.2 µH` and `C202 = 22 µF`, the undamped resonance is approximately:

`f0 = 1 / (2π√(LC)) = 22.9 kHz`.

The corresponding characteristic impedance is `√(L/C) = 0.316 Ω`. The 1 Ω damping resistor is about 3.2 times that value, and its 10 µF branch begins contributing at about `1 / (2πRC) = 15.9 kHz`. This remains a deliberately damped input network; final conducted-EMI optimization still requires the real harness/source impedance.

### 3.2 LM74800 startup and inrush

Capacitance charged through the HGATE-controlled `Q202` is:

- `C203 = 100 µF`;
- `C309 = 220 µF`;
- `C310 = 22 µF`;
- nominal total `COUT = 342 µF`;
- worst positive tolerance, using +20% for all three, `COUT(max) = 410.4 µF`.

This is the capacitance directly on `VEH_PROT`; the LM5176 `SYS_24V` output bank is behind the switching stage and is not part of TI's HGATE dV/dt-capacitor formula. Its startup load is checked separately below.

TI gives `CdV/dt = IHGATE × COUT / IINRUSH`. `C207 = 82 nF, 25 V, X7R` and `R206 = 10 kΩ` are therefore fitted from HGATE to OUT in the TI-recommended series network. At the 55 µA typical HGATE source current, nominal inrush is `55 µA × 342 µF / 82 nF = 0.229 A`. For the worst high-current corner, use 75 µA, `COUT(max) = 410.4 µF`, and an effective `C207(min) = 82 nF × 0.9 tolerance × 0.9 bias/aging = 66.4 nF`; this gives `IINRUSH(max) = 0.464 A`. The design target is therefore approximately 0.25 A nominal and no more than 0.5 A at the calculated worst corner.

At the just-below-OV maximum input of 20 V, the high-current startup lasts approximately `410.4 µF × 20 V / 0.464 A = 17.7 ms`. The opposite tolerance corner (39 µA HGATE current and +10% C207) produces approximately 0.177 A for 46 ms. The direct-capacitance SOA checkpoints are therefore 20 V/0.47 A/18 ms and 20 V/0.18 A/46 ms. The capacitor-charging energy deposited in the controlled FET is approximately `½ × 410.4 µF × 20² = 0.082 J`.

The LM5176 can begin its own soft start after `VEH_PROT` crosses its UVLO threshold, so that overlap is not assumed away. Its 100 nF SS capacitor gives 12.4–21.7 ms from the 6.35–3.75 µA data-sheet current range. After removal of the ORing reservoir, the converter has 264 µF at its output plus 19.547 µF distributed local bypass, or 283.547 µF nominal and about 340.3 µF at +20%. In the fastest corner, charging that maximum bank to 24 V requires approximately `340.3 µF × 24 V / 12.4 ms = 0.659 A` at the output. At the slow HGATE-ramp corner and 20 V source, the protected node reaches about 13.5 V as that fast soft start ends. Referred to the input at 85% efficiency, capacitor charging is about 1.38 A; allowing the complete 30 W load instead gives 2.62 A. Adding 0.18 A of direct-capacitor current yields the same conservative full-load source bound of about 2.8 A, while the capacitor-only simultaneous-start case falls to about 1.56 A. Q202 then sees about 6.5 V for no more than the remaining 15 ms of its ramp. These combined-load points and the two direct-capacitance points are comfortably inside the CSD19531Q5A single-pulse SOA in TI Figure 10. The dV/dt network therefore remains 0.25 A nominal/0.5 A worst for direct precharge; removing the second source and its bus reservoir reduces, rather than increases, startup stress.

`Q202` is the controlled linear-pass device; `Q201` is already enhanced as the ideal-diode FET before HGATE ramping, so it does not carry a worse linear-startup stress. Both FETs retain 100 V VDS rating against the 38.9 V-class TVS clamp plus layout overshoot. SOA shall still be confirmed by measuring Q202 VDS/current and case temperature on the prototype.

## 4. LM5176-Q1 four-switch converter

`U301` converts the protected 12 V input directly to canonical `SYS_24V`.

- Feedback: 580 kΩ / 20.0 kΩ with the 0.8 V reference gives `0.8 × (1 + 580/20) = 24.0 V` nominal. Applying the LM5176 0.788–0.812 V reference range and both 1% resistor extremes gives 23.187–24.836 V static setpoint range. Downstream checks use 23.0–25.0 V as a conservative steady-state envelope.
- Frequency: 27.4 kΩ sets approximately 300 kHz per the LM5176-Q1 programming curve.
- Inductor: Coilcraft XAL7070-153MEC, 15 µH, shielded, with 10.1 A saturation-rating class.
- PWM current shunt: 20 mΩ. The data-sheet boost peak threshold of 100/120/140 mV corresponds to approximately 5/6/7 A before slope effects; this is adequate for the calculated low-line input current while providing fault margin.
- Current-sense filtering: 100 Ω in each CS/CSG lead and 47 pF differential.
- Mode: 93.1 kΩ selects CCM with hiccup protection.
- Soft start: 100 nF.
- Compensation starting point: 15.0 kΩ, 82 nF, and 270 pF. This must be checked by loop measurement with the final PCB parasitics and load.
- Gate drive: 100 nF BOOT-to-SW capacitors and external BAT46W-E3-08 Schottky charging diodes from VCC to each BOOT node, as required for the two high-side drivers.
- Output: 220 µF electrolytic plus two 22 µF/50 V ceramics directly on `SYS_24V` (264 µF nominal), with 19.547 µF of downstream local bypass for 283.547 µF total distributed capacitance. The former 220 µF/10 µF ORing-handover reservoir is deleted.

The optional average-current ISNS inputs are shorted at the output, disabling that loop. Cycle-by-cycle current limiting remains active through CS/CSG.

The quantitative low-line check uses the required 9 V full-load boundary. At 9 V, 30 W, and 86% efficiency, average inductor current is 3.876 A. With 15 µH at 300 kHz, boost ripple is 1.25 A peak-to-peak and peak current is 4.50 A. With the shunt at +1% and the controller at its 100 mV minimum boost limit, the minimum limit is `100 mV / 20.2 mΩ = 4.95 A`, leaving 0.45 A or 10% margin. At the approximately 8.15 V LM74800 UVLO boundary, calculated peak current is 4.93 A, intentionally close to that minimum limit; current limiting or reboot during a crank dip is acceptable by requirement.

The selected XAL7070-153MEC 10.1 A saturation-rating class remains above the 7 A maximum threshold corner. The nominal input bank after the protection FETs is 342 µF. Using all 283.547 µF electrically present on `SYS_24V`, the 9 V ideal capacitive output ripple estimate is about 9.2 mV peak-to-peak before ESR and DC-bias effects. The boost-mode output-capacitor ripple-current estimate remains 1.61 A RMS; the low-impedance ceramics carry most of the 300 kHz component, but capacitor temperature and current sharing remain prototype checks.

For the worst normal 9 V boost point, `D = 0.625`, `ROUT = 19.2 Ω`, and the right-half-plane zero is about 28.6 kHz. The data-sheet limit of one-third that value is 9.55 kHz. Reapplying the data-sheet small-signal approximation to 283.547 µF, the populated 15 kΩ/82 nF/270 pF network predicts approximately 1.05 kHz crossover; its 129 Hz compensation zero and 39.3 kHz high-frequency pole are unchanged. This is conservative rather than fast, and no compensation change is justified. The power stage, MOSFET gate loss, and compensation were checked over 9–18 V; 100 V MOSFETs and the 15 µH inductor retain voltage/current margin. Bode, load-step, efficiency, and 9 V/30 W thermal testing remain mandatory because the quick-start calculation cannot include PCB parasitics.

## 5. Single-source `SYS_24V` bus

There is one external high-voltage source boundary. `J201`, `F201`, the input EMI/damping network, `D201`, and the LM74800/Q201/Q202 disconnect protect the nominal-12 V input. The LM5176 output then connects directly to `SYS_24V`. The dedicated 24 V barrel branch, both LM74700 branch controllers, their MOSFETs/passives, current-measure links, and the ORing/handover bulk are deleted.

Bench operation uses a regulated/current-limited nominal-12 V supply at J201, so the same protection, converter, 5 V supply, display rails, and backlight path are exercised as in vehicle evaluation. The LM74800 boundary continues to prevent reverse battery and reverse current toward J201. USB coexistence remains isolated separately by TPS25947 at the 5 V/Nano boundary.

The remaining `SYS_24V` capacitance is:

- converter bank: `C311` 220 µF + `C312`/`C313` 22 µF each = 264 µF;
- LM76003 local input: `C505`/`C506` 4.7 µF each + `C507` 47 nF = 9.447 µF;
- backlight local input: `C901` 10 µF + `C902` 100 nF = 10.1 µF;
- total electrically connected: 283.547 µF nominal.

The removed `C403`/`C404` 230 µF was principally a source-handover reservoir. It is not needed for loop stability, transient response, VIN-loss handling, or backlight bypass in the single-source architecture. Local input capacitors remain adjacent to LM76003 and TPS922053; the converter's own 264 µF bank remains the controlling compensation basis.

## 6. `SYS_24V` to 5 V and Nano isolation

`U501` is an LM76003RNPR configured as follows:

- output: 100 kΩ / 24.9 kΩ with the 1.0 V reference gives approximately 5.016 V;
- switching frequency: RT left open for the 500 kHz default;
- inductor: XAL7070-103MEC, 10 µH;
- worst calculated inductor ripple at the 24.836 V maximum static `SYS_24V` setpoint and 5 V output is about 0.80 A peak-to-peak;
- at a 3 A load, nominal peak inductor current is therefore about 3.41 A, below the selected inductor's ≥5.5 A saturation class and the converter current limit;
- soft-start capacitor: 22 nF, approximately 11 ms;
- output capacitance: four 22 µF/10 V ceramics, subject to DC-bias derating.

`U502`, TPS259470A, is the normal `SYS_5V` to `NANO_5V` path:

- 1.05 kΩ ILIM resistor gives approximately 3.18 A nominal; the parallel 549 Ω laboratory option is DNP;
- 100 kΩ / 26.7 kΩ sets an approximately 5.69 V overvoltage threshold;
- 100 kΩ / 100 kΩ enable division requires approximately 2.5 V at `SYS_5V`;
- 10 nF dV/dt capacitance targets an approximately 5 ms controlled rise;
- the integrated back-to-back FETs provide true reverse-current blocking, so USB-powered `NANO_5V` cannot raise `SYS_5V`;
- `J501` is a normally closed service/current-measure disconnect, not an operating-mode selector.

The hardware is safe by default with USB connected. No user jumper sequence is required.

## 7. Display hold-up, sequencing, and reset

The logic-only hold-up path is isolated from the Nano, touch regulator, and backlight by `D601`. `R601` limits initial charge current into `C601`:

- initial ideal charge current from 5 V through 3.3 Ω is about 1.5 A before diode/source resistance; the schematic note conservatively states about 1.4 A;
- the held load is the LCD 1.8 V IOVCC rail (60 mA maximum), the 2.8 V VCI rail (60 mA maximum until FLAG2 falls), and less than 2 mA conservatively reserved for both LDOs, LM3880, TPS3808, divider and reset logic;
- the touch 3.3 V regulator is supplied from `SYS_5V_3A`, not `DISP_HOLD_5V`, and is not included in the stored-energy load;
- `LM3880MF-1AA/NOPB` is the exact sequence-1 option: FLAG1→FLAG2→FLAG3 on startup and FLAG3→FLAG2→FLAG1 on shutdown. Each selected delay is 10 ms nominal and 11.5 ms maximum at +15%; the first shutdown interval also includes the approximately 0.4 ms timer overhead;
- after VIN_GOOD falls, reset is therefore asserted within 11.9 ms, VCI is removed by 23.4 ms, and IOVCC is removed by 34.9 ms worst case.

Worst stored charge is `122 mA × 23.4 ms + 62 mA × 11.5 ms = 3.57 mC`. Taking a conservative 4.85 V minimum 5 V rail, 0.55 V diode drop, 3.3 Ω +5% charge resistor, and 122 mA load gives about 3.88 V at C601 before the event. `C601 = 6800 µF` is retained: after -20% capacitance tolerance and 15% aging allowance its effective minimum is 4624 µF, giving 0.77 V total droop. Including 0.1 V ESR/transient allowance leaves approximately 3.0 V after FLAG1 falls. More importantly, the held node remains about 3.16 V when VCI must turn off, above the conservative 3.04 V needed for 2.8 V plus maximum LDO dropout. A 4700 µF part would be marginal at this corner; 6800 µF provides useful engineering margin without holding up the Nano.

`U601` senses `SYS_24V` through 1.00 MΩ / 21.5 kΩ. With the TPS3808G01 0.405 V nominal threshold, ±2% supervisor accuracy, ±1% resistors, and ±25 nA SENSE current, the calculated trip range remains 18.47–20.04 V (19.24 V nominal). `C607 = 1 nF C0G` is fitted directly from SENSE to GND per TI's 1–10 nF recommendation; `C603 = 1 µF` remains the VDD bypass. The worst static voltage separation is 23.187 − 20.04 = 3.15 V. If conversion ceases abruptly at the minimum setpoint, 283.547 µF supplies about 0.64 ms before the high trip corner at a full 30 W constant-power load, or 0.87 ms at the 22.2 W expected ceiling. RESET assertion is a hardware path; after the trip, C601—not the falling 24 V bus—powers the 34.9 ms ordered shutdown. From 20.04 V to a conservative 5.5 V LM76003-loss point, the bus adds about 1.75 ms at 30 W. No threshold or C601 change is justified.

`U602` implements IOVCC→VCI→reset enable ordering and reset→VCI→IOVCC shutdown. The display enable is also hardware-clamped by `VIN_GOOD`; firmware cannot keep the display or backlight active after input validity is lost. The three SN74LVC1G07 open-drain stages form a wired-AND reset command with Ioff behavior, preventing an unpowered source from driving the panel reset rail.

Selected rails are:

| Rail | Device | Voltage | Control behavior |
|---|---|---:|---|
| `LCD_IOVCC` | TLV75518 | 1.8 V | First sequenced rail; output discharge |
| `LCD_VCI_RAW` | TLV75528 | 2.8 V | Regulator enabled by sequence |
| `LCD_VCI` | TPS22919 | 2.8 V | Controlled switch and quick discharge |
| `TOUCH_3V3` | TLV75533 | 3.3 V | Held off outside the valid display sequence |

Commanded and unexpected shutdown are different cases. For a commanded shutdown, firmware shall set PWM to zero, send DCS `0x28`, send `0x10`, wait at least 120 ms, and only then deassert the hardware display-power command. On unexpected source removal the Nano is not held up, so those DCS commands are not guaranteed. Hardware instead disables the backlight and asserts panel reset immediately, then removes VCI before IOVCC using C601's stored energy. Oscilloscope verification must demonstrate both paths separately.

## 8. Backlight driver

`U901` is TPS922053DYYR operating as a 300 kHz asynchronous buck from `SYS_24V`.

- Current sense: two 1.65 Ω, 0.1% resistors in parallel give 0.825 Ω. With the 200 mV nominal threshold, current is 242.4 mA. At the +3% threshold limit, current is approximately 249.7 mA, remaining below the 252 mA +5% project limit before resistor tolerance.
- Inductor: Vishay `IHLP6767GZER680M11`, 68 µH, 6.1 A heat-rated and 4.5 A typical saturation current. The 4.5 A saturation rating exceeds the TPS922053 3.6 A maximum cycle-by-cycle current-limit threshold; this replaces the earlier 120 µH / 3.0 A-saturation candidate, which lacked worst-case fault-current margin.
- At the 24.836 V maximum static input, 19.8 V LED load, and 300 kHz, estimated worst-normal-corner ripple is about 192 mA peak-to-peak and peak current is about 346 mA at the +3% current threshold. Both remain far below the selected inductor ratings.
- Catch diode: SS2H10-E3/52T, 100 V/2 A Schottky.
- `FB901` is an EMI bead in the LED-anode feed; its DC resistance and saturation behavior must be included in the headroom test.
- PWM is gated by `LCD_VCI`, `VIN_GOOD`, and the Nano command through `U902`; `J901` provides a physical hard-disable shunt.

At the 23.187 V minimum static `SYS_24V` setpoint and 19.8 V maximum LED string, subtracting the 0.2 V current-sense drop leaves 3.187 V gross headroom. Reserving 0.04 V switch drop, 0.50 V Schottky drop, 0.10 V bead/wiring loss, and 0.10 V ripple/tolerance allowance leaves approximately 2.45 V. The calculated duty is about 86.5%, below the 97% theoretical maximum at 300 kHz and 100 ns minimum off-time. The regulated internal bus therefore removes the former narrow 21.6 V external-adapter corner. Validate current and temperature with a programmable 16.8–19.8 V LED-equivalent load across the measured `SYS_24V` tolerance; retain the LT8391A contingency only if prototype data contradicts this margin.

## 9. DSI and touch powered-off behavior

The DSI path is passive and straight-through: six 0 Ω/0201 inline links followed by a TPD6E05U06 flow-through ESD array. No common-mode choke, bridge, lane swap, or stub is present. The PCB channel remains required to support at least the ESP32-P4 approximately 1.5 Gb/s/lane capability with 100 Ω differential impedance, tight intra-pair skew, continuous reference, and short ESD return.

The exact D-PHY HS lane rate is a firmware/prototype setting, not a schematic parameter.

All four touch signals pass through a TMUX1574 powered from `TOUCH_3V3`. Its powered-off protection and a Nano-3.3 V detector keep the switch disabled unless both sides are valid. The connector-side INT has a 4.7 kΩ pull-up to `TOUCH_3V3`; RESET has a 100 kΩ pull-down so the module remains reset when isolated. No passive pull-up bridges the Nano and touch rails.

## 10. Power-state matrix

| 12 V input | USB/Nano independently powered | Display command | Result and safety disposition |
|---|---|---|---|
| Off | Off | Either | All rails off; reset and backlight disabled. |
| Off | On | Either | Nano only. TPS25947 blocks `NANO_5V`→`SYS_5V`; display/touch switch stays isolated; no backlight or `SYS_24V`. |
| On | Off | Off | Protected converter, `SYS_24V`, and `SYS_5V` valid; Nano feed may power Nano; display rails remain commanded off. |
| On | Off | On | Normal single-source operation. Hardware sequence controls display and backlight. |
| On | On | Off/On | Normal USB + 12 V development. TPS25947 blocks Nano/header 5 V from entering `SYS_5V`; the Nano's onboard header-to-USB-VBUS path must pass the specified reverse-current test. |

On unexpected removal of the 12 V source, `VIN_GOOD` falls, hardware disables the backlight and asserts reset, and the isolated logic capacitor supports the reverse shutdown sequence; the Nano is deliberately not held up to transmit DCS commands. A later source insertion starts a full sequence and firmware must not assume state retention. A commanded shutdown follows the DCS sequence and 120 ms wait specified in Section 7 before hardware rail removal.

## 11. Thermal and validation boundaries

- Vehicle converter: verify FET, shunt, inductor, and PCB temperatures at 9 V/30 W and at nominal charging voltage.
- LM76003: verify 5 V/3 A temperature across the measured `SYS_24V` range and the actual copper area/airflow.
- Backlight: verify switch, diode, inductor, bead, and sense-network temperature at 240 mA and worst LED voltage.
- Protection: test reverse polarity, reverse current toward J201, current limiting, hot plug, hard unplug, and controlled surge conditions with current-limited equipment.
- Nano USB: the published Waveshare schematic distinguishes Type-C `USB0_5V` from header/board `VCC_5V` and shows onboard power-path circuitry; it does not, however, give a conclusive reverse-current guarantee for every fitted power-path part and transition. Measure both directions of VBUS current during USB-only, daughterboard-only, and hot-plug transitions with a current-limited USB source before connecting an unrestricted laptop. TPS25947 guarantees output-to-input blocking toward `SYS_5V`, but it cannot by itself prevent the intended forward `SYS_5V`→Nano feed from reaching laptop VBUS through the Nano's onboard path. If the Nano fails this test, use a data-only/debug USB connection or modify the Nano-side USB power path; USB VBUS is not separately accessible on the daughterboard headers.
- Compensation: measure LM5176 and TPS922053 loop/transient response; the populated networks are data-sheet-based starting values.

No automotive qualification claim is made. All tests begin with current-limited supplies and the panel replaced by appropriate dummy loads.
