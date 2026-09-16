# Phase 2 schematic calculations and design basis

**Project:** ESP32-P4 Displayman Development Daughterboard  
**Date:** 2026-09-16  
**Controlling specification:** `docs/PRD.md` v0.5  
**Schematic revision:** Phase 2 / v0.1

## 1. Scope

This note records the component-value, electrical-margin, sequencing, and power-state calculations used for the first complete schematic capture. It is the design basis for review, not a substitute for prototype measurements. Compensation values, thermal estimates, transient behavior, and the narrow backlight headroom must be verified on assembled hardware before release.

The PCB has not been started. Manufacturer-specific land patterns called out in `schematic-review.md` remain intentionally unresolved until the physical interfaces are checked.

## 2. System load and vehicle-input budget

The vehicle converter is sized for a 30 W continuous output budget on the common 24 V-class bus. This covers the 240 mA backlight, Nano, LCD/touch logic, conversion loss, and development loads with margin. Representative full-load input currents are:

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

## 4. LM5176-Q1 four-switch converter

`U301` converts the protected vehicle input to nominal 24 V.

- Feedback: 580 kΩ / 20.0 kΩ with the 0.8 V reference gives `0.8 × (1 + 580/20) = 24.0 V` nominal.
- Frequency: 27.4 kΩ sets approximately 300 kHz per the LM5176-Q1 programming curve.
- Inductor: Coilcraft XAL7070-153MEC, 15 µH, shielded, with 10.1 A saturation-rating class.
- PWM current shunt: 20 mΩ. The data-sheet boost peak threshold of 100/120/140 mV corresponds to approximately 5/6/7 A before slope effects; this is adequate for the calculated low-line input current while providing fault margin.
- Current-sense filtering: 100 Ω in each CS/CSG lead and 47 pF differential.
- Mode: 93.1 kΩ selects CCM with hiccup protection.
- Soft start: 100 nF.
- Compensation starting point: 15.0 kΩ, 82 nF, and 270 pF. This must be checked by loop measurement with the final PCB parasitics and load.
- Gate drive: 100 nF BOOT-to-SW capacitors and external BAT46W-E3-08 Schottky charging diodes from VCC to each BOOT node, as required for the two high-side drivers.
- Output: 220 µF electrolytic plus two 22 µF/50 V ceramics before the independent vehicle-branch ideal diode.

The optional average-current ISNS inputs are shorted at the output, disabling that loop. Cycle-by-cycle current limiting remains active through CS/CSG.

## 5. Source isolation and common bus

The protected bench input and converted vehicle output each use an LM74700-Q1 plus a 100 V N-channel MOSFET. Each controller receives its own charge-pump and local anode/cathode bypassing. These branches implement reverse-blocked diode ORing into `VIN_PROT_24V`; they are not a current-sharing system.

Consequences:

- bench 24 V cannot feed the vehicle converter or connector;
- vehicle power cannot feed the bench barrel connector;
- either source may be connected first or removed first;
- if both are present, the branch with the slightly higher effective voltage supplies the load and handover may cause a small bus transient;
- all dependent enables treat a bus-valid loss as a reset/reinitialization event.

## 6. Common bus to 5 V and Nano isolation

`U501` is an LM76003RNPR configured as follows:

- output: 100 kΩ / 24.9 kΩ with the 1.0 V reference gives approximately 5.016 V;
- switching frequency: RT left open for the 500 kHz default;
- inductor: XAL7070-103MEC, 10 µH;
- worst calculated inductor ripple at 26.4 V input and 5 V output is about 0.81 A peak-to-peak;
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

The logic-only hold-up path is isolated from the Nano and backlight by `D601`. `R601` limits initial charge current into `C601`:

- initial ideal charge current from 5 V through 3.3 Ω is about 1.5 A before diode/source resistance; the schematic note conservatively states about 1.4 A;
- 6800 µF supplying 200 mA for 30 ms loses `0.2 × 0.03 / 0.0068 = 0.88 V`;
- this stored energy supplies only sequencing, LCD logic, and touch circuitry. It is not intended to maintain the Nano or LED backlight.

`U601` senses the common high-voltage bus through 1.00 MΩ / 21.5 kΩ. With a nominal 0.405 V threshold, the falling trip is approximately 19.24 V. This provides early warning before the 5 V regulator loses regulation.

`U602` implements 10 ms IOVCC→VCI→reset enable ordering and reverse shutdown. The display enable is also hardware-clamped by `VIN_GOOD`; firmware cannot keep the display or backlight active after input validity is lost. The three SN74LVC1G07 open-drain stages form a wired-AND reset command with Ioff behavior, preventing an unpowered source from driving the panel reset rail.

Selected rails are:

| Rail | Device | Voltage | Control behavior |
|---|---|---:|---|
| `LCD_IOVCC` | TLV75518 | 1.8 V | First sequenced rail; output discharge |
| `LCD_VCI_RAW` | TLV75528 | 2.8 V | Regulator enabled by sequence |
| `LCD_VCI` | TPS22919 | 2.8 V | Controlled switch and quick discharge |
| `TOUCH_3V3` | TLV75533 | 3.3 V | Held off outside the valid display sequence |

The 6800 µF value is a calculated prototype starting point. Oscilloscope verification must show reset asserted, VCI removed, and IOVCC removed in the required order during both commanded shutdown and abrupt source removal.

## 8. Backlight driver

`U901` is TPS922053DYYR operating as a 300 kHz asynchronous buck from `VIN_PROT_24V`.

- Current sense: two 1.65 Ω, 0.1% resistors in parallel give 0.825 Ω. With the 200 mV nominal threshold, current is 242.4 mA. At the +3% threshold limit, current is approximately 249.7 mA, remaining below the 252 mA +5% project limit before resistor tolerance.
- Inductor: Vishay `IHLP6767GZER680M11`, 68 µH, 6.1 A heat-rated and 4.5 A typical saturation current. The 4.5 A saturation rating exceeds the TPS922053 3.6 A maximum cycle-by-cycle current-limit threshold; this replaces the earlier 120 µH / 3.0 A-saturation candidate, which lacked worst-case fault-current margin.
- At 26.4 V input, 19.8 V LED load, and 300 kHz, estimated worst-normal-corner ripple is about 243 mA peak-to-peak and peak current is about 371 mA at the +3% current threshold. Both remain far below the selected inductor ratings.
- Catch diode: SS2H10-E3/52T, 100 V/2 A Schottky.
- `FB901` is an EMI bead in the LED-anode feed; its DC resistance and saturation behavior must be included in the headroom test.
- PWM is gated by `LCD_VCI`, `VIN_GOOD`, and the Nano command through `U902`; `J901` provides a physical hard-disable shunt.

At the 21.6 V minimum bench input and 19.8 V maximum LED string, only about 1.6 V gross remains after the 0.2 V current-sense drop, before switch, diode, bead, wiring, and ripple losses. The 100 ns minimum off-time gives a 97% theoretical maximum duty cycle at 300 kHz, or about 20.95 V ideal output from 21.6 V. The topology is therefore valid but has a deliberately flagged narrow corner. Validate regulation and current with a programmable 16.8–19.8 V LED-equivalent load over 21.6–26.4 V input and temperature. If it cannot maintain 240 mA without violating ratings, the approved LT8391A buck-boost contingency replaces the backlight sheet before PCB layout.

## 9. DSI and touch powered-off behavior

The DSI path is passive and straight-through: six 0 Ω/0201 inline links followed by a TPD6E05U06 flow-through ESD array. No common-mode choke, bridge, lane swap, or stub is present. The PCB channel remains required to support at least the ESP32-P4 approximately 1.5 Gb/s/lane capability with 100 Ω differential impedance, tight intra-pair skew, continuous reference, and short ESD return.

The exact D-PHY HS lane rate is a firmware/prototype setting, not a schematic parameter.

All four touch signals pass through a TMUX1574 powered from `TOUCH_3V3`. Its powered-off protection and a Nano-3.3 V detector keep the switch disabled unless both sides are valid. The connector-side INT has a 4.7 kΩ pull-up to `TOUCH_3V3`; RESET has a 100 kΩ pull-down so the module remains reset when isolated. No passive pull-up bridges the Nano and touch rails.

## 10. Power-state matrix

| Bench 24 V | Vehicle 12 V | USB/Nano powered | Display command | Result and safety disposition |
|---|---|---|---|---|
| Off | Off | Off | Either | All rails off; reset and backlight disabled. |
| Off | Off | On | Either | Nano only. TPS25947 blocks `NANO_5V`→`SYS_5V`; display/touch switch stays isolated; no backlight. |
| On | Off | Off | Off | Common bus and `SYS_5V` valid; Nano feed may power Nano; display rails remain commanded off. No bench→vehicle path. |
| On | Off | Off | On | Normal bench-powered system. Hardware sequence controls display and backlight. |
| Off | On | Off | Off/On | Same downstream states through the protected converter. No vehicle→bench path. |
| On | On | Off | Off/On | Ideal-diode ORing selects the higher branch; no reverse feed and no current-sharing assumption. |
| On | Off | On | Off/On | Normal USB + bench development. TPS25947 blocks Nano/header 5 V from entering `SYS_5V`; the Nano's onboard header-to-USB-VBUS path must pass the specified reverse-current test. |
| Off | On | On | Off/On | Normal USB + vehicle development with the same isolation and Nano-path test requirement. |
| On | On | On | Off/On | High-voltage branches remain isolated and Nano/header 5 V cannot feed `SYS_5V`; laptop-VBUS safety remains conditional on the Nano-path test below. |

On removal of the active high-voltage source, `VIN_GOOD` falls first, hardware disables the backlight and asserts reset, and the isolated logic capacitor supports the reverse shutdown sequence. A later source insertion starts a full sequence; firmware must not assume state retention across the transition.

## 11. Thermal and validation boundaries

- Vehicle converter: verify FET, shunt, inductor, and PCB temperatures at 9 V/30 W and at nominal charging voltage.
- LM76003: verify 5 V/3 A temperature with 26.4 V input and the actual copper area/airflow.
- Backlight: verify switch, diode, inductor, bead, and sense-network temperature at 240 mA and worst LED voltage.
- Protection: test source handover, reverse polarity, current limiting, hot plug, hard unplug, and controlled surge conditions with current-limited equipment.
- Nano USB: measure both directions of VBUS current during USB-only, daughterboard-only, and hot-plug transitions with a current-limited USB source before connecting an unrestricted laptop. TPS25947 guarantees output-to-input blocking toward `SYS_5V`, but it cannot by itself prevent the intended forward `SYS_5V`→Nano feed from reaching laptop VBUS through an unspecified Nano onboard path. If the Nano fails this test, use a data-only/debug USB connection or modify the Nano-side USB power path; that function is not separately accessible on the daughterboard headers.
- Compensation: measure LM5176 and TPS922053 loop/transient response; the populated networks are data-sheet-based starting values.

No automotive qualification claim is made. All tests begin with current-limited supplies and the panel replaced by appropriate dummy loads.
