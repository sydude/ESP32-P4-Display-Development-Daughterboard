# Final project-local footprint verification

**Date:** 2026-09-20

**Baseline:** `0d672004f35eafac3cfa5a801327b5b2c78ea6a8`

**Scope:** independent manufacturer-drawing audit of all ten project-local footprints, their symbol-pad correspondence, and their project-local 3D models. PCB placement, mechanical arrangement, routing, and system cable selection were not started.

## Result

All ten land patterns now match the controlling manufacturer package or connector drawing, or retain a documented and defensible assembly-oriented enlargement. Definite errors were corrected in six footprints. No schematic connectivity changed.

For `J701` and `J702`, the PCB land patterns are verified independently of the system-level flex presentation. The subsequent manufacturer-file mechanical review resolved the documented contact configurations and is recorded in `mechanical-interface-verification.md`; only the exact physical pin-1/sample/stack presentation checks listed there remain.

| Ref. | Exact populated part | Status | Controlling source | Discrepancy and disposition |
|---|---|---|---|---|
| `D201` | Bourns `SM8S24CA-Q`, DO-218AB | **CORRECTED** | Bourns *SM8S-Q Series* datasheet, package and recommended-pad drawing | The copper land pattern was correct (9.0 × 10.0 mm pad 1, 2.0 × 2.7 mm pad 2, 9.0 mm centers), but the fabrication/courtyard origin treated the 15.5 mm overall package as centered on pad 1 and failed to enclose pad 2. Corrected the molded-body outline, courtyard, pin-1 cue, and 3D-envelope offset. |
| `U201` | TI `LM74800QDRRRQ1`, DRR0012E WSON-12 | **CORRECTED** | TI LM7480-Q1 datasheet Rev. C; DRR0012E drawing 4224874 Rev. C11 | Signal-pad pitch/count/numbering and 1.3 × 2.5 mm exposed pad were correct. Retained the 0.75 mm signal-pad length as a defensible toe extension with adequate terminal overlap. Replaced full exposed-pad paste with the specified two-window stencil, removed silk from the pads, enlarged the courtyard, and added a clear pin-1 cue. EP pad 13 remains deliberately unconnected because TI defines it as RTN and says not to connect it to ground. |
| `U301` | TI `LM5176QPWPRQ1`, PWP0028V HTSSOP-28 PowerPAD | **PASS** | TI LM5176-Q1 datasheet Rev. B; PWP0028V drawing 4230409 Rev. A01 | 28 signal pads, 0.65 mm pitch, counter-clockwise numbering, 3.4 × 9.7 mm EP, 2.94 × 5.62 mm mask opening, and symbol mapping agree. The 1.575 × 0.40 mm signal lands preserve the TI outer toe extent and add heel length relative to TI's 1.50 × 0.45 mm recommendation. The segmented paste and 24 plated 0.20 mm thermal drills are intentional assembly/thermal provisions; specify filled or suitably capped via-in-pad processing with the assembler. |
| `U502` | TI `TPS259470ARPWR`, RPW0010A VQFN-HR-10 | **CORRECTED** | TI TPS25947 datasheet Rev. C (May 2026); RPW0010A drawing 4225183 Rev. A08 | The four corner L-pads were undersized, rotated, and assigned to the wrong physical corners (`4` and `10` interchanged). Rebuilt pads 1/4/7/10 to TI's horizontal and vertical dimensions/positions, added the TI stencil reductions for the corner and long center pads, and corrected silkscreen/pin-1 clearance. Pads 5 and 6 are the long IN/OUT terminals; there is no separate exposed pad. Symbol functions 1–10 correspond to the datasheet. |
| `J201` | Molex `43045-0218`, Micro-Fit 3.0 vertical SMT, 2 circuits | **PASS** | Molex sales drawing SD-43045-007, current `43045-0218` configuration | Two 1.27 × 2.54 mm signal lands on 9.40 mm centers and two 3.43 × 1.65 mm SMT board-hold-down lands agree with the drawing. The hold-downs are soldered mechanical tabs, not drilled holes. Pin 1 is `BATT+` and pin 2 is `BATT-`. The simplified model aligns to the body envelope and board-side Z origin but is intentionally featureless; the drawing controls latch/mating orientation. |
| `L201` | Bourns `SRP1038A-2R2M`, SRP1038A lead-frame variant | **PASS** | Bourns `SRP1038A` datasheet, current mechanical and recommended-pad drawing | Two 3.55 × 3.50 mm lands at ±4.475 mm retain the manufacturer 5.40 mm inner gap and provide at least 0.50 mm toe coverage at maximum terminal span. The slightly shorter outer toe than the 4.10 × 3.50 mm Bourns nominal land is a valid IPC-style land and does not reduce package-terminal overlap. Non-polarized pins 1/2 and the 10.0 × 10.0 × 3.8 mm body model agree. |
| `U501` | TI `LM76003RNPR`, RNP0030B WQFN-30 PowerPAD | **PASS** | TI LM76003 datasheet Rev. A; RNP0030B drawing 4222784 Rev. B09 (also checked against compatible RNP0030G 4229347 Rev. A01) | Pad count, 0.50 mm pitch, four-side numbering, 1.8 × 4.5 mm EP, and symbol mapping agree. Side and end pads retain the TI inner edges while extending only outward for toe fillet. Segmented paste and fifteen plated 0.20 mm thermal drills are intentional; arrange filled/capped via-in-pad processing. The simplified 3D body is centered and conservatively 0.2 mm taller than the 0.8 mm package maximum. |
| `J701` | Amphenol ICC `SFW15R-2STE1LF`, 15-way, 1.0 mm, top-contact | **CORRECTED — PHYSICAL PIN-1 VERIFICATION REMAINS** | Amphenol drawing 10172241 Rev. A, sheets 4–6 | The fifteen 0.60 × 2.00 mm contacts and 1.00 mm pitch were correct. The two 1.00 × 4.20 mm mounting lands were centered 1.0 mm too close to the signal row; corrected from y=1.6 to y=2.6 mm per the 1.5 mm reference dimension. Expanded the courtyard for the 1.6 mm slider-opening travel and improved the pin-1 cue. Corrected the manufacturer STEP rotation: it had been mirrored through the board plane. The later floorplanning study supersedes the underside concept: this top-contact part is reserved on the daughterboard top, with a Type-B cable through a radiused opening to the STEP-inferred bottom-contact Nano connector; physical Nano DSI pin 1/contact face still requires inspection. |
| `J702` | Molex `505110-4096`, FD19 40-way, 0.5 mm, bottom-contact/front-flip | **CORRECTED — PHYSICAL PIN-1/TAIL VERIFICATION REMAINS** | Molex product drawing 5051101008-SD Rev. C and exact `505110-4096` order-number row | The 40 signal lands, 0.50 mm pitch, 0.30 × 1.00 mm signal land, retention lands, numbering, and bottom-contact variant agree. The courtyard failed to enclose the outer edges of the 2.60 mm retention lands; expanded it and removed an overlapping silk edge. Corrected the drawing identifier and the official STEP rotation; the model had been mirrored through the board plane. Displayman confirms a bottom-contact panel flex; the delivered tail termination and physical pin 1 remain sample checks. |
| `U901` | TI `TPS922053DYYR`, DYY0014A TSOT-23-14 | **CORRECTED** | TI TPS922053 datasheet Rev. B; DYY0014A drawing 4224643 Rev. D07 | The 14 pads, 0.50 mm pitch, 1.05 × 0.30 mm land dimensions, numbering, and symbol functions agree. The courtyard ended at the pad centers rather than outside the copper, and the body-side silk crossed the inner pad area. Enlarged the courtyard, clipped the silk to clear copper, and added a visible pin-1 cue. |

## Detailed checks

### Pad numbering and symbol correspondence

- Every electrical symbol pin has a like-numbered copper pad in its assigned footprint.
- `U201` includes pad 13 for the WSON RTN exposed pad; its symbol pin is intentionally marked no-connect in accordance with TI guidance.
- `U301` pad 29 and `U501` pad 31 are their grounded PowerPADs and are represented in both symbol and footprint.
- `U502` has ten terminals only. Pads 5 and 6 are the wide center IN and OUT terminals; no fictitious exposed-pad number is present.
- `J201` has the additional non-electrical `MP` hold-down pads. `J701` and `J702` use unnumbered retention pads. These have no symbol pins by design.
- Connector contact numbering is viewed from the component/PCB side shown in each controlling drawing. This confirms footprint-to-symbol numbering, but does not establish which exposed-contact orientation the actual system flexes must present.

### Holes, retention, and thermal vias

None of the three project-local connectors uses a locating post, peg, NPTH, or signal PTH in the selected variant. Their retention features are SMT solder tabs. `D201`, `L201`, `U201`, `U502`, and `U901` are also fully surface mount.

Only `U301` and `U501` contain drilled footprint features. Their 0.20 mm drills are plated, same-number thermal vias within the grounded exposed-pad structure. They are not locating holes. The model/footprint audit found no project-local NPTH requirement that is missing.

### 3D models

The committed Amphenol `J701` and Molex `J702` models are manufacturer STEP data. The other eight models are dimension-controlled simplified envelopes. They were checked for XY centering/orientation, board-side Z origin, body height, and connector mating direction where applicable. KiCad STEP export exposed and confirmed correction of the former below-board rotation on both manufacturer connector models. Simplified IC models omit decorative detail and fine leads; they are suitable for approximate clearance, but the connector drawings and physical samples remain controlling for mechanical freeze.

`D201` was the only model with a definite footprint-origin error; the footprint now offsets the model +2.25 mm in X so its 15.5 mm overall envelope follows the asymmetric heat-sink/lead land pattern. `U501` intentionally retains a conservative 1.0 mm model height versus the drawing's 0.8 mm maximum.

## Verification performed after correction

- KiCad 10.0.6 parsed and exported all ten project-local footprints to SVG, including copper, paste, mask, silkscreen, fabrication, and courtyard layers.
- A temporary, non-project footprint test fixture passed KiCad 10.0.6 all-severity DRC with **0 violations and 0 unconnected items** after setting its minimum plated-drill rule to the intentional 0.20 mm thermal-via drill.
- The corrected schematic hierarchy exported to a netlist successfully.
- All-severity ERC: **0 messages, 0 errors, 0 warnings**.
- A symbol/footprint pin-set comparison passed for all ten references, including the exposed pads and deliberate mechanical pads described above.
- All project-local 3D model paths resolve.
- KiCad STEP export of each footprint/model pair confirmed that all ten bodies are above the PCB top surface; this check caught and verified the `J701`/`J702` rotation corrections.
- The project PCB file remained byte-identical to the starting baseline; no placement or layout work was performed.

## Required physical checks before placement freeze

1. Inspect the actual Waveshare Nano DSI connector to confirm the STEP-inferred bottom-contact face, physical pin 1, cable exit and bend direction for the top-side-J701/Type-B pass-through arrangement.
2. Mate the exact Displayman panel flex to `J702` to confirm bottom-contact presentation, pin 1, stiffener thickness, insertion depth and cable exit/bend direction.

These are system/mechanical presentation checks. They do not indicate a remaining PCB-land-pattern defect.
