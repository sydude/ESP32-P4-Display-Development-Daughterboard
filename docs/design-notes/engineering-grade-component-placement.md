# Engineering-grade component placement

**Date:** 2026-09-23

**Baseline:** canonical `main` including `8f5947f1c6219271b844365a723d20d0ee3fe34f` and the later J1001 no-connect correction

**Status:** routing-ready placement complete; routing has not started

## Scope and acceptance basis

This pass replaces the first broad floorplan with pad- and net-driven component placement. The validated Nano/header coordinates, `SSQ-113-01-G-D` stack, mounting holes, USB-A/RJ45 reliefs, DSI pass-through, Nano orientation and GPIO map were not changed. The existing **130.03 x 100.02 mm** outline remains adequate; no electrical-placement reason was found to enlarge or reshape it.

Acceptance was not based only on fitting courtyards. Each critical block was rebuilt from the relevant controller pins, commutation/current paths, gate-drive/boot loops, sense and feedback paths, bypass loops, connector flow and future routing channels. TI's LM5176-Q1, LM76003 and TPS922053 layout guidance and layout examples were used as the controlling references.

The finished PCB contains **199 footprints: 197 on the top and two on the bottom**. The two bottom footprints are the mechanically required J1001/J1002 through-hole socket bodies. There are **no bottom-side SMD parts, no tracks, no vias and no zones**.

## Placement readiness

| Block | Status | Placement result |
|---|---|---|
| Vehicle entrance / LM74800 | **ROUTING-READY** | J201, F201, L201, the filter capacitors and damping branch, D201, Q201/Q202 and U201 form a visible source-to-protected-rail progression. Controller gate/capacitor parts remain with their corresponding U201/FET nodes, while the large TVS has a short, wide future shunt path to ground. |
| LM5176 four-switch stage | **ROUTING-READY** | The two half bridges flank L301 in power-flow order. U301 is immediately below them with its driver side facing the FETs; the analog side faces the quiet passive row. The SW1/SW2 regions terminate at the bridge/inductor interfaces rather than expanding into unused board area. |
| LM76003 5 V stage | **ROUTING-READY** | U501 is oriented with its SW side toward L501 and its PVIN side toward C507/C505/C506. C507 is the closest high-frequency input bypass; the larger ceramics follow immediately. C501/C502/C504 and the FB divider occupy the quiet sides of the package. C503 is the first output ceramic after L501, followed by the bulk output bank. |
| TPS25947 Nano feed | **ROUTING-READY** | U502 follows the 5 V output and precedes J501/Nano power. Input/output bypass, dV/dt, current-limit, OV, enable and fault parts surround the pins they serve without crossing the protected power path. |
| Hold-up / sequencing | **ROUTING-READY** | D601 and R601 feed C601 without placing any component beneath the capacitor body. The supervisor and divider/filter are grouped by SENSE, VDD and CT pins; the sequencer, LDOs, load switch and reset clamps proceed in rail-order toward the display-interface region. |
| TPS922053 backlight | **ROUTING-READY** | U901 and C902/C903 form the local input/VCC loops; D901, U901 SW and the left pad of L901 define the smallest practicable switch region with the selected 17 mm-class inductor. The current-sense pair is placed directly after L901. CSP filtering, frequency, UVP and compensation parts remain on the quiet side of U901. |
| MIPI DSI | **ROUTING-READY** | J701 remains aligned to the pass-through. R701-R706 are six inline 0201 links in connector order. The protected pair corridor remains free of converter parts and rises along the right side to J702. U701 is beside the panel connector as a short-stub, panel-side shunt ESD device; it is not incorrectly treated as a series device. |
| Touch / low speed | **ROUTING-READY** | J801 -> U803 -> U802 is physically ordered from panel to Nano. U801 and C801/C802 supply the isolated touch domain; C803 is beside U802 VCC. Pull-ups, reset and Nano-powered isolation control remain with the pins they serve and above the MIPI/power regions. |

## LM5176 placement detail

The implemented topology is `VEH_PROT -> Q301/Q302 half bridge -> L301 -> Q303/Q304 half bridge -> SYS_24V`.

- Q301/Q302 and Q303/Q304 are oriented so each half-bridge switch node faces L301.
- The high-side and low-side driver pins on U301 face the bridges. The design intentionally has no external gate resistors in the approved schematic; the LM5176 drivers therefore route directly to the FET gates. Adding gate resistors would be a schematic/EMI-tuning change, not a placement omission.
- C307/C308 are placed between their BOOT and SW destinations; C306 is on the U301 VCC/PGND side.
- R301 carries the main low-side current. R302 and R309 leave its power terminals as independent Kelvin branches and terminate with C301 at U301 CS/CSG.
- R303/R304, C302/C303 and the R305/C304/C305 compensation network line the quiet analog edge of U301.
- R306/R307 and the feedback connection approach FB from the quiet side and do not pass through either switch-node region.
- C310 is the closest input ceramic at the buck-side bridge. C312 is the first output ceramic at the boost-side bridge; C313 and C311 provide progressively less local bulk energy.

Routing must keep the copper named `SW1` and `SW2` to the FET/inductor/controller-pin islands only, route each gate above an unbroken ground reference where possible, and preserve the R301 Kelvin departures before joining any power copper.

## LM76003 placement detail

The physical flow is `SYS_24V input ceramics -> U501 -> LM760_SW -> L501 -> SYS_5V_3A ceramics`.

- C507 is the smallest and closest PVIN bypass. C505/C506 provide the adjacent larger ceramic bank.
- C501 bridges BOOT to SW on the switch/inductor side; C502 and C504 are on the VCC/SS side.
- C503 is placed at the inductor output; C508-C511 are the following output bank.
- R501/R502 approach FB from the quiet lower side. R503/R504 and R510 remain outside the SW copper region.
- The exposed-pad footprint retains room for its specified filled/capped thermal-via array and a continuous L2 ground plane.

## TPS922053 placement detail

The large L901 footprint prevents the diode, controller and inductor bodies from being packed as tightly as a small-inductor datasheet sketch. The selected placement minimizes the **electrical pad-to-pad** switch-node path without overlapping assembly courtyards.

- C902 is the local high-frequency IN-to-ground bypass; C901 is bulk input energy and may be farther away.
- C903 is beside VCC.
- D901, U901 SW and L901 pad 1 form the only intended `BL_SW` copper island.
- R901/R902 are the 0.825-ohm effective sense element directly after L901. R903/C904 connect to CSP as the local Kelvin/noise filter.
- R905/C906 and the DNP C907 option remain on the analog/COMP side, away from the inductor and switch node.
- The LED output filter and connector-side parts are adjacent to J702 pins 31/32 and 39/40 without entering the MIPI corridor.

## Decoupling and local-capacitor audit

| Capacitor(s) | Served pin/rail | Placement disposition |
|---|---|---|
| C201/C202 | Vehicle input filter | Immediately after L201; C201 is the smaller/high-frequency part and is closest to the protected-current entry. |
| C205/C206/C207 | LM74800 CAP/inter-FET/HGATE dV/dt | Placed with U201, Q201/Q202 and the exact nodes served. |
| C306 | U301 VCC-PGND | On the U301 driver edge with a direct future ground-via location. |
| C307/C308 | U301 BOOT1-SW1 / BOOT2-SW2 | On the driver edge, oriented by BOOT and SW pads rather than reference-number order. |
| C310/C312/C313 | LM5176 input/output commutation bypass | C310 at the input bridge; C312 first at the output bridge; C313 follows. |
| C501 | U501 BOOT-SW | On the SW/L501 side. |
| C502 | U501 VCC-GND | Below the VCC side with a direct future ground-via location. |
| C503 | First LM76003 output bypass | Immediately after L501; smallest local output capacitor precedes the larger bank. |
| C504 | U501 SS-GND | On the quiet control edge. |
| C505/C506/C507 | U501 PVIN-PGND | C507 is closest; C505/C506 are the adjacent high-value ceramics. |
| C508-C511 | 5 V output bank | Immediately downstream of C503/L501 with wide future output/ground copper. |
| C512 | U502 dV/dt | Beside the dV/dt pin. |
| C513/C514 | U502 input/output bypass | On their corresponding sides of the eFuse. |
| C602/C603/C607 | U601 CT, VDD and SENSE | Each is placed by the corresponding U601 pin; C607 remains inside the quiet supervisor area. |
| C604 | U603 1.8 V output | Directly beside the LDO output/ground side. |
| C605 | U604 2.8 V output | Directly beside the LDO output/ground side. |
| C606 | U605 switched VCI output | Directly beside the load-switch output/ground side. |
| C801/C802 | U801 input/output | On the corresponding regulator sides. |
| C803 | U802 TOUCH_3V3-GND | Beside U802 pin 16/ground return, between switch and connector protection. |
| C901/C902 | U901 input bulk/HF bypass | C902 is local to IN/PGND; C901 is deliberately treated as bulk. |
| C903 | U901 VCC-GND | Beside the VCC pins. |
| C904 | U901 CSP-CSN filter | Beside CSP and the sense-return region. |
| C905/C908 | LED string/output filtering | At the connector-side LED path, not in the controller bypass loop. |
| C906/C907 | U901 COMP network | On the quiet analog side; C907 remains DNP. |

No bypass capacitor was assigned by sheet grouping alone. Routing must place a ground via at each local bypass ground pad before expanding the surrounding ground copper.

## Sensitive analog audit

- LM5176 RT, MODE, SLOPE, SS, COMP, FB and current-sense filters occupy the controller's quiet edge and are separated from L301 and both switch nodes.
- LM76003 FB, SS and EN networks remain below/right of U501 and outside `LM760_SW`.
- TPS3808 SENSE divider/C607 and CT/C602 are adjacent to U601; their ground returns must join quiet ground rather than a converter commutation return.
- TPS922053 CSP/CSN, COMP, FSET and UVP networks are below U901 and outside `BL_SW`.
- The LED current-sense resistors retain room for independent Kelvin traces from their correct pads.

## MIPI path and Nano FFC orientation

The official Waveshare top-view photograph `hardware/mechanical/vendor/Waveshare/ESP32-P4-NANO/esp32-p4-nano.jpg` visibly identifies the DISPLAY connector, its exposed contact presentation and its pin-1 silkscreen marker. The official Nano schematic identifies J1 pin 1 as DSI_D1_N and numbers the remaining contacts consistently through pin 15. Taken together, these sources resolve the previously open Nano pin-1/contact-presentation question.

With the Nano connector below the daughterboard and J701 (`SFW15R-2STE1LF`) on the daughterboard top facing the pass-through, the provisional cable is:

- **15 positions**
- **1.00 mm pitch**
- **Type B / opposite-side contacts**
- straight-through electrical numbering

The remaining physical mock-up is limited to exact cable length, stiffener dimensions, bend radius, abrasion/service clearance and insertion ergonomics. Pin 1/contact orientation is no longer classified as unknown.

## Connector and service placement

- J201 and F201 remain on the vehicle-entry edge with direct harness and fuse access.
- J701 remains at the DSI slot; its latch is accessible from the top.
- J702 remains at the right edge with panel-flex latch and bend access. MIPI pins 8-15 face the protected routing corridor; LED pins 31/32 and 39/40 face the backlight/output parts.
- J801 remains on the top edge with ESD immediately downstream.
- J1003 remains on the lower-left service edge. Test pads were moved out of power courtyards and remain top-accessible.

## Board area, assembly and layer plan

The board remains **130.03 x 100.02 mm**. Critical placement fits without changing the validated outline, Nano reliefs, DSI slot, header datums or mounting holes. No meaningful edge reduction is recommended before routing because the apparent open areas are reserved for wide vehicle/SYS_24V/5 V copper, thermal spreading, the continuous MIPI reference, Nano keepouts and connector/service access.

Single-sided SMT assembly remains practical:

- top-side footprints: **197**;
- bottom-side footprints: **2** (`J1001`, `J1002`, through-hole socket bodies);
- bottom-side SMD footprints: **0**.

A four-layer board remains appropriate: L1 components/critical routing, uninterrupted L2 ground, L3 power/secondary routing and L4 low-speed/secondary routing. Placement does not reveal a need for six layers. L2 must remain continuous below the MIPI path and should not be cut by power islands.

## Routing gates and known constraints

Placement is routing-ready, but routing must still prove the following before fabrication:

1. Keep SW1, SW2, `LM760_SW` and `BL_SW` copper no larger than their component-pad islands require.
2. Route U301 gate and bootstrap loops first; do not place unrelated vias or copper inside them.
3. Route R301 and R901/R902 Kelvin pairs before filling high-current copper.
4. Give every local bypass ground pad a short dedicated via to L2.
5. Preserve the right-side MIPI corridor and continuous L2 reference; route the three pairs before low-speed signals enter that corridor.
6. Confirm that thermal-via patterns do not conflict with bottom-side Nano hardware or standoffs.
7. Run native KiCad 10 DRC after routing rules/stackup are defined. The present environment does not provide `kicad-cli`, so this pass uses structural PCB parsing, pad/net audits, edge-diff checks and courtyard checks rather than claiming a native DRC run.

## Pre-routing verification result

- 199 footprints / 106 named nets retained;
- 197 top-side and two bottom-side footprints;
- zero bottom-side SMD parts;
- zero tracks, zero vias and zero zones;
- zero top-side courtyard-envelope overlaps;
- J1001/J1002 locations and all mechanical datums unchanged;
- `Edge.Cuts`, cutouts, holes and the 130.03 x 100.02 mm outline unchanged;
- four layers still appropriate;
- all major blocks classified **ROUTING-READY**.
