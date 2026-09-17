# Phase 2 schematic maintainability and library review

**Date:** 2026-09-17

**Baseline:** `main` at `ef40668d49dea3c53273733ae0076216ed86ab80`

**Scope:** schematic organization, graphical wiring, ERC hygiene, component inventory, footprint/3D completion and project portability

**Phase boundary:** PCB placement and layout were not started

## 1. Result

The electrical design was consolidated from ten functional subsheets into three primary A1 sheets. Ordinary local circuits now use actual wires and junctions; global labels remain for named power rails, cross-block controls, DSI pairs and other interface nets where direct wiring would reduce legibility.

| Metric | Before | After |
|---|---:|---:|
| Functional subsheets | 10 | 3 |
| Global-label instances | 663 | 475 |
| Wire objects | 0 | 897 |
| Junction objects | 0 | 271 |

Final sheets:

1. `01_power.kicad_sch` — 24 V bench input, vehicle input/protection, LM5176-Q1 buck-boost, source ORing, LM76003 and TPS25947 Nano feed.
2. `02_display_power_backlight.kicad_sch` — hold-up, power-fail/sequencing, 1.8/2.8/3.3 V rails, reset gating and TPS922053 backlight driver.
3. `03_interfaces_nano.kicad_sch` — Nano headers and DSI connector, MIPI ESD/panel connector, touch isolation/ESD and debug/service interfaces.

The root sheet remains the project hierarchy page. Its user-raised title text and KiCad 10 format were preserved.

## 2. Electrical-equivalence controls

- The pre-audit netlist contains 193 named nets; the corrected netlist contains 194 because the intentional `VEH_HGATE_DVDT` node was added.
- A node-by-node comparison of all non-`PWR` references found zero differences in net membership.
- All prior BOM references remain present. `R206`, `C207`, and `C607` were added by the independent-audit correction.
- Component values and DNP states are unchanged.
- External connector and Nano GPIO mappings remain those documented in `schematic-review.md`.
- `U201` pin 10 (`VS`) was corrected from a `power_in` symbol-pin type to an ordinary input/sense pin. Its connected net did not change.
- The physical PCB file SHA-256 remains `7829957e7338e332a94dc7033609c47f00a6f41b9c34c8ad4c085579b7a6338f`, identical to the starting checkout.

The only component-identification completion was C601: the formerly blank manufacturer/MPN fields were filled with Nichicon `UHW1A682MHD`, matching the existing 6800 µF/10 V value and the required 16 mm × 25 mm, 7.5 mm-pitch envelope. This was necessary to make the existing hold-up-capacitor requirement mechanically determinate; capacitance, voltage rating and topology did not change.

## 3. ERC and wiring policy

KiCad 10.0.6 exported the four-page hierarchy and netlist successfully. The committed all-severity ERC report contains **0 messages, 0 errors and 0 warnings**.

The post-audit project enables `endpoint_off_grid` as an error. All former near-coincident doglegs were replaced with normal-grid pin stubs and explicit labels; no coordinate snapping was used to infer connectivity. A programmatic comparison showed only the documented C203 relocation and new R206/C207/C607 memberships. Future edits must preserve that separation and rerun ERC and the netlist comparison.

Other intentionally ignored low-value checks are recorded in `erc-report.txt`: global label appearing once, four connection points joined, SPICE model issues and footprint-filter matching. None suppresses an active electrical error or warning in the committed report.

## 4. `PWR_FLAG` audit

Six placed flags remain, down from seven. They are schematic-only (`in_bom no`, `on_board no`), have no footprint and do not enter the physical BOM.

| Reference | Net | Reason retained |
|---|---|---|
| `PWR101` | `GND` | Establishes the externally supplied common return as a driven power net for ERC. |
| `PWR201` | `VEH_PROT` | Marks the LM7480/pass-FET protected vehicle output, whose passive FET path does not otherwise present a KiCad power-output pin. |
| `PWR301` | `VEH_24V` | Marks the four-switch LM5176 output after MOSFETs/inductor; the controller pins do not directly drive this rail in ERC terms. |
| `PWR401` | `VIN_PROT_24V` | Marks the common bus after two passive ideal-diode branches. |
| `PWR501` | `SYS_5V_3A` | Marks the LM76003 buck output after its passive inductor. |
| `PWR601` | `DISP_HOLD_5V` | Marks the diode-isolated hold-up rail supplied through a passive charge path. |

The redundant former `PWR202` was removed. No flag was used merely to hide an unresolved ERC message.

## 5. Physical-component inventory

The regenerated BOM contains 222 physical entries: 218 populated and four DNP.

| Category | Count | Treatment |
|---|---:|---|
| Required for normal operation | 171 | Functional power, sequencing, display, touch, DSI, protection and interconnect parts. |
| Development/test/service | 47 | 37 test points; J501/J901 service links; R401/R402/R910 measurement links; J1003 debug header; D1001/D1002 indicators and R1006/R1007 series resistors. |
| Optional/DNP | 4 | `R505`, `C907`, `R907`, `R1005`. |
| **Total** | **222** | 218 POP + 4 DNP. |

J501, J901, R401, R402 and R910 are categorized as service hardware but are normally fitted and electrically required in the circuit as drawn.

Recommended reductions for a later production-focused revision, **not implemented here**:

- reduce duplicate ground/control observation points after placement and routing review;
- omit J1003 if the production test strategy does not require the debug header;
- omit one or both status LEDs and their resistors if visual indication is unnecessary;
- reconsider dedicated branch current links and normally fitted service jumpers after prototype characterization.

## 6. Footprint coverage

All 222 physical BOM entries resolve to a footprint:

- 211 use standard KiCad 10 footprint libraries;
- 11 use the project-local `Phase2` library;
- zero footprint links are unresolved.

Project-local footprints:

1. `Amphenol_SFW15R-2STE1LF`
2. `Bourns_DO-218AB`
3. `L_Bourns_SRP1038A_10.0x10.0mm`
4. `Molex_505110-4096`
5. `Molex_Micro-Fit_3.0_43045-0218_2x01-1MP_P3.00mm_Vertical`
6. `Switchcraft_RAPC722X_RightAngle`
7. `Texas_DRR0012E_WSON-12_3x3mm_P0.5mm_EP1.3x2.5mm`
8. `Texas_DYY0014A_TSOT-23-14`
9. `Texas_PWP0028V_TSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP3.4x9.7mm_Mask2.94x5.62mm_ThermalVias`
10. `Texas_RNP0030B_WQFN-30-1EP_4x6mm_P0.5mm_EP1.8x4.5mm_ThermalVias`
11. `Texas_RPW0010A_VQFN-HR-10_2x2mm`

The four local Bourns-inductor, Micro-Fit, TI PWP and TI RNP land patterns retain verified KiCad/manufacturer geometry but use local model links because the corresponding KiCad 10 model package did not contain the filename referenced by the stock footprint. The remaining manufacturer-specific patterns were created from the controlling package/connector drawings with courtyard, fabrication outline, silkscreen, pin-1 indication and paste/mask details as appropriate.

A pin-set audit found all critical/custom symbol pins represented in their footprint pad sets. The Micro-Fit footprint additionally has the intentional non-electrical `MP` mechanical hold-down pad. The Switchcraft pad numbering is function-based—1 center, 2 sleeve, 3 normally closed shunt—because the manufacturer drawing identifies functions but does not assign schematic numbers.

## 7. 3D-model coverage and provenance

Of the 222 physical entries, 184 mounted component instances resolve to a 3D body. The remaining 38 are 37 bare plated test pads and the J501 solder jumper, for which no mounted body exists or is useful. There are zero broken model paths and no mounted-body component lacking a model.

Official manufacturer models committed locally:

- Amphenol `SFW15R-2STE1LF`;
- Molex `505110-4096`.

Dimension-controlled simplified models committed locally where a redistributable exact model was unavailable or the standard KiCad model link was incomplete:

- Bourns DO-218AB and SRP1038A body;
- Switchcraft RAPC722X;
- Molex 43045-0218 Micro-Fit header;
- TI DRR0012E, DYY0014A, PWP0028V, RNP0030B and RPW0010A packages.

The simplified models intentionally represent mechanical envelope, terminal locations and board height rather than decorative detail. The Molex model-download endpoint did not return a usable file during this pass, so its committed model follows the sales-drawing/verified-footprint envelope. Standard KiCad models cover the Nano stacking sockets/headers, touch FFC, fuse holder, large capacitors, ordinary inductors and common packages.

## 8. Portability and source of truth

- `sym-lib-table` and `fp-lib-table` use project-relative or KiCad 10 environment-variable paths only.
- Project-local footprint model paths use `${KIPRJMOD}/Phase2.3dshapes/...`.
- No user-specific absolute filesystem paths are present.
- All project-owned footprints and models are committed alongside the schematic.
- The earlier generator is blocked from writing and the ten superseded sheets are retained only as explicitly unreferenced historical snapshots. Native active `.kicad_sch`, `.kicad_sym`, `.kicad_mod` and model files are the sole design authority; `hardware/kicad/LEGACY_GENERATED_SHEETS.md` prevents ambiguity.

## 9. Remaining actions by phase

### Before independent schematic acceptance

No owner action is required. The project still requires the planned independent electrical review before PCB authorization.

### Before footprint/placement freeze

The owner or layout reviewer must physically verify:

- Nano 15-pin FFC contact side, pin 1, insertion direction and mating cable presentation;
- Displayman 40-pin FPC and GT9271 8-pin flex exposed-contact side, pin 1, thickness, stiffener, insertion depth, bend direction and practical cable length;
- Nano socket/header height, standoff, board separation, mounting-hole and enclosure-clearance needs;
- the selected 24 V adapter plug fits the RAPC722X 2.0 mm center pin / 5.5 mm-class interface and is center-positive;
- connector and critical custom land patterns by independent drawing audit and, where samples exist, a 1:1 physical overlay.

These are physical/mechanical facts, not unresolved electrical-design choices.

### Prototype bring-up

- tune and validate DSI HS lane rate, video mode, continuous clock and refresh;
- validate the confirmed 600-to-480 masking behavior with test patterns;
- characterize actual backlight-string forward voltage and regulation margin;
- test GT9271 reset/address behavior and unpowered leakage;
- validate 12 V, 24 V and USB transitions/reverse current with current-limited sources;
- capture startup, shutdown and hard-unplug timing; and
- measure loop response, efficiency, EMI and thermal margin.

PCB layout remains outside this pass and requires separate authorization after independent review.
