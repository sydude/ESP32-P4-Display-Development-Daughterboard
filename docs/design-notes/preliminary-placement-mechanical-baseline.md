# Preliminary placement and mechanical baseline

Date: 2026-09-22
Status: preliminary real placement complete; routing has not started

This note records the first placement-based board envelope, the validation of the user-created Nano geometry, and adoption of Samtec `SSQ-113-01-G-D` at J1001/J1002. It supersedes the generic rectangular-board and ESW height assumptions in `nano-interface-floorplanning-study.md`. It does not freeze the outline, FFC slot, stackup, copper, thermal-via pattern, or differential-pair tuning.

## Source hierarchy

| Item | Controlling source | Use in this review |
|---|---|---|
| Nano dimensions and component envelopes | Original Waveshare `ESP32-P4-NANO-20260331.pdf`, DXF and STEP under `hardware/mechanical/vendor/Waveshare/ESP32-P4-NANO/` | Board outline, holes, headers, cutouts and underside clearance |
| Nano header pin positions | Official Waveshare Wiki GPIO/pinout image, cross-checked against the schematic and mechanical files | P1/P2 pin numbering and orientation |
| PCB Nano overlay | Locked `User.1` geometry in the KiCad PCB | Derived visual reference only |
| P1/P2 location graphics | User-created `F.Fab` geometry in the KiCad PCB | Numerically validated placement datum |
| Stack socket | Samtec [`SSQ-113-01-G-D`](https://www.samtec.com/products/ssq-113-01-g-d), SSQ drawing Rev. BH, and Samtec recommended-footprint drawing | Exact socket, holes, body and stack geometry |

The original Waveshare files remain authoritative. The `User.1` overlay remains an edited/rescaled derivative and is not promoted to manufacturer authority by this review.

## Result summary

| Area | Result |
|---|---|
| Edge.Cuts topology | **PASS** — 32 entities: 14 lines, 14 arcs and four Ø2.70 mm circles; every line/arc endpoint has degree two, with no duplicates, open ends or tiny gaps |
| Header reference layers | **PASS** — P1/P2 construction graphics remain on `F.Fab`; no header marker or pad surrogate is on `Edge.Cuts` |
| Nano/header alignment | **PASS** — validated header datums agree with the Waveshare dimensions within 0.001 mm after the intentional PCB-view Y reversal |
| SSQ selection | **PASS** — `SSQ-113-01-G-D` is compatible with the Nano posts and a 1.6 mm daughterboard |
| USB-A and RJ45 cutouts | **PASS, tight tolerance to verify physically** — no nominal STEP interference; the RJ45 left-side nominal margin is only 0.20 mm |
| DSI slot and top-side J701 corridor | **PASS concept / NEEDS PHYSICAL VERIFICATION** — nominal cable width and connector geometry fit; Nano contact face, delivered cable stiffener and bend remain sample checks |
| Preliminary placement | **PASS for floorplanning** — all 197 BOM footprints plus two board-only support holes are placed with no courtyard overlaps; 106 named nets are assigned and there are zero tracks or zones |
| Outline adequacy | Original outline fails; revised **130.03 × 100.02 mm** outline is the recommended REV1 starting envelope |

## Validated Nano datums

The Waveshare DXF/PDF define a nominal 50 × 50 mm Nano, four Ø2.70 mm holes on a 45.10 mm square, and 13-position header rows on 2.54 mm pitch. The current PCB coordinate transform is approximately:

`Xpcb = 117.710 mm + Xstep`; `Ypcb = 124.060 mm - Ystep`.

The minus sign is an intentional view/orientation reversal, not a scale error.

| Datum | PCB coordinates (mm) | Result |
|---|---:|---|
| Nano mounting holes | X = 120.159998 / 165.259997; Y = 76.500000 / 121.599999; Ø2.70 | Matches 45.10 mm spans |
| J1001 pad 1 / odd row | X = 119.190000, Y = 80.619713 | P1 outboard row |
| J1001 pad 2 / even row | X = 121.730000, Y = 80.619713 | P1 inboard row |
| J1002 pad 1 / odd row | X = 163.690000, Y = 80.619713 | P2 inboard row |
| J1002 pad 2 / even row | X = 166.230000, Y = 80.619713 | P2 outboard row |
| Last header positions | Y = 111.099713 | 12 × 2.54 = 30.48 mm from first position |

J1001 and J1002 are locked to these pad-1 datums in the preliminary PCB. The existing five control assignments remain unchanged, and P2 remains electrically unused.

## SSQ-113-01-G-D

The exact selected part is a vertical 2 × 13 through-hole socket on a 2.54 × 2.54 mm grid. `-01` selects the 2.64 mm (`0.104 in`) square-tail lead style; `G` is the 20 µin gold contact option with a flash-plated tail; `D` is double row.

| Parameter | Verified value / implementation |
|---|---|
| Contacts | 26, numbered odd/even by position |
| Pitch / row spacing | 2.54 mm / 2.54 mm |
| Mating post | 0.64 mm square; matches the Nano posts |
| Accepted insertion | 3.68–6.35 mm; Nano exposure is approximately 5.80 mm |
| Body | 33.53 × 4.95 × 8.51 mm nominal/reference envelope |
| Tail | 2.64 mm; approximately 1.04 mm remains beyond a nominal 1.6 mm PCB before the top solder fillet |
| PCB hole | Ø1.02 mm PTH on the Samtec grid |
| Local land | Ø1.80 mm copper, giving 0.39 mm radial annulus around the recommended drill |
| Contact durability | Samtec catalog class is suitable for prototype mating; standoffs must react service loads rather than connector solder joints |

The project-local footprint is `Phase2:Samtec_SSQ-113-01-G-D_BottomMount`; it uses intentionally pre-mirrored library geometry so a normal KiCad back-side placement produces the validated physical pin coordinates. Its simplified STEP envelope is rotated within the footprint so KiCad's back-side 3D transform leaves the body below the daughterboard and aligned with the two hole rows. J1001/J1002 are necessarily **bottom-mounted**; this is the justified exception to the top-side-only assembly preference. Their solder tails and fillets are on the daughterboard top side.

### Actual stack height

With the Nano male-header body approximately 2.50 mm above the Nano PCB and the SSQ body 8.51 mm from its daughterboard seating plane to its mating face:

- Nano top surface to daughterboard underside: **11.01 mm nominal**.
- Nano top surface to daughterboard top surface with a 1.60 mm PCB: **12.61 mm nominal**.
- Nano post insertion: approximately **5.80 mm**, inside the 3.68–6.35 mm range.

Do not substitute the former 16–19 mm ESW values; the USB-A/RJ45 openings make the lower SSQ stack viable.

## Local underside clearance

The table compares the 11.01 mm daughterboard underside plane with top-side Nano STEP envelopes. It does not include a bottom-side daughterboard component because none is permitted above these regions. Reserve at least 1.0 mm of the nominal clearance for component/PCB tolerances, solder, assembly skew and vibration.

| Nano item | Height above Nano PCB | Nominal clearance to daughterboard underside | Assessment |
|---|---:|---:|---|
| Auxiliary header, tallest | 8.50 mm | **2.51 mm** | Minimum solid-board clearance; no daughterboard THT tails or bottom components here |
| Other auxiliary header | 8.30 mm | 2.71 mm | Same keepout requirement |
| Nano DISPLAY / CAMERA FFC connector | 5.68 mm | 5.33 mm | DISPLAY is served through the routed slot |
| Small auxiliary connectors | 4.70 mm | 6.31 mm | Maintain service/bend keepout |
| Buttons | 3.30 mm | 7.71 mm | Preserve finger/tool access from the board edge |
| USB-C | 3.25 mm | 7.76 mm | Preserve plug approach corridor |
| ESP32-C6/module/antenna region | 2.465 mm | 8.545 mm | No copper/noisy switching placement over the antenna region |
| Microphone | 1.10 mm | 9.91 mm | Do not obstruct acoustic port |
| USB-A | 14.45 mm | Intersects plane by 3.44 mm | Cleared by open-edge cutout |
| RJ45 | 13.60 mm | Intersects plane by 2.59 mm | Cleared by open-edge cutout |

The microSD holder is on the Nano underside and does not collide with the daughterboard, but its card-access path depends on the final Nano-to-chassis standoffs.

All daughterboard THT parts other than J1001/J1002 are outside the Nano 50 × 50 mm projection. A future routing pass must keep vias and solder protrusions out of the auxiliary-header, connector and antenna keepouts. At the 2.51 mm minimum region, a conservative 1.0 mm tolerance/vibration reserve still leaves about 1.5 mm nominal free space.

## Board perimeter, cutouts and slot

### Outline and area

The incoming outline bounded **85.026 × 80.016 mm** and provided approximately **6,204.9 mm²** of FR-4 after the slot and four routed holes. It could not contain credible power-stage loops, connector service corridors and all verified footprints.

The revised outline grows only toward the left and top, preserving the Nano, right/bottom edges, mounting holes and connector cutouts:

- X: 42.700000 to 172.725958 mm — **130.026 mm**.
- Y: 24.043731 to 124.059702 mm — **100.016 mm**.
- Bounding-rectangle area: **13,004.7 mm²**.
- Actual FR-4 area after perimeter cutouts, DSI slot and four Ø2.70 holes: **12,408.2 mm²**.
- Descriptive comparison: 4.96 × the Nano's 2,500 mm² area.

The two imported sub-0.02 mm outer-edge skews were removed while extending the outline; the four outside corners are now true 2.00 mm radii. No Nano datum or local cutout moved.

Area removed by the open USB/RJ45 relief is approximately **513.2 mm²**. The DSI slot removes **57.0 mm²**, and the four Nano holes remove **22.9 mm²**.

### Ethernet and USB relief

Using the STEP body envelopes after the validated transform:

| Item | Body projection in PCB coordinates | Nominal relief margin |
|---|---|---|
| RJ45 | X 123.951–139.991; Y 103.780–125.180 mm | 0.20 mm left, 0.90 mm right, 0.80 mm at the inner/top wall; open at board edge |
| USB-A | X 140.810–148.010; Y 106.510–125.710 mm | 0.85 mm right and 1.50 mm at the inner/top wall; continuous with the RJ45 opening on the left and open at board edge |

There is no nominal body or shell interference. Plug insertion remains along the open board edge. The smallest FR-4 web is at the lower-left Nano hole/cutout transition: approximately **1.87 mm** from routed-hole edge to cutout. A 5 mm-OD spacer boss is feasible there, but a large washer is not.

The 0.375 mm local cutout radii require a router no larger than 0.75 mm if reproduced exactly. A fabricator may round these to a 0.40–0.50 mm radius without affecting the STEP clearance materially; confirm the fabrication rule before release. Keep copper at least 0.50 mm from these routed edges, and more around the narrow mounting-hole web.

The 0.20 mm nominal RJ45 left clearance is the tightest XY tolerance. It was retained because enlarging it reduces the already-small mounting-hole/header web. Verify an actual Nano in the first bare-board/mechanical article; enlarge locally only if the sample or chosen fabricator tolerance requires it.

### DSI pass-through and J701

The current rounded slot is retained:

- X 125.844670–129.017460 mm.
- Y 76.578107–94.810263 mm.
- **3.173 × 18.232 mm**, 1.00 mm end radius.

The transformed Nano DISPLAY connector envelope is approximately X 124.160–129.232 and Y 74.560–96.960 mm, so the slot is centered over the usable exit region. A nominal 15-way, 1.0 mm-pitch FFC around 15.5 mm wide has about 1.37 mm side margin in the long dimension. The 3.17 mm short dimension passes the cable and ordinary stiffener thickness, but final bend/installability depends on the delivered cable.

J701 is preliminarily top-mounted at **(136.0, 85.0) mm, 90°**. Its body mouth is approximately 0.48 mm from the slot edge and faces the slot. J701, the slot and U701 form a reserved MIPI corridor; the nearest switching power stages remain above/left of that corridor. Top-side J701 does not introduce an inherent MIPI problem: it avoids vias at the Nano end and permits a short, direct fanout. Pair geometry and length tuning remain routing tasks.

The repository evidence still supports, but does not conclusively prove, a bottom-contact Nano DISPLAY connector. With top-contact J701 and straight-through electrical pin mapping, that implies a **Type-B/opposite-contact** FFC. Do not purchase or freeze the cable until Nano pin 1/contact face is physically confirmed.

## Preliminary real placement

The PCB contains all **197** BOM footprints, plus two non-BOM M3 support holes. It carries **106** named nets and 636 net-assigned physical pads. Intentionally unassigned pads are NCs, mechanical pads, the electrically unused P2 pins, unused Nano P1 functions, and the documented LM74800 RTN exposed pad. There are **zero tracks and zero copper zones**.

| Functional region | Approximate reserved envelope | Placement rationale |
|---|---:|---|
| J201, fuse, TVS/filter and LM74800 | 35 × 36 mm | Left/top service edge; fuse and harness accessible; protected-current path proceeds toward LM5176 |
| LM5176 four-switch stage | 41 × 39 mm | Two MOSFET half bridges flank L301; U301, gate parts, shunt and local bulk/ceramics remain within the same power island |
| LM76003 and TPS25947 | 25 × 30 mm | Local input/output ceramics around U501/L501; short feed toward Nano/hold-up domains |
| C601 and display sequencing | 30 × 26 mm plus Ø16 mm capacitor | C601 is outside the Nano projection; sequencer/LDO/load-switch parts remain together and testable |
| TPS922053 backlight | 27 × 33 mm | U901/D901/L901 and local capacitors form a separate noisy-power island adjacent to the display edge but outside the MIPI corridor |
| DSI/LCD/touch corridor | approximately 46 × 55 mm, shared with Nano overlap | J701 at the slot, U701 near the panel side, J702 on the right edge and J801 on the top edge preserve flex exits and service access |

The sum of axis-aligned footprint-courtyard envelopes is about **4,184 mm²**, or 34% of actual FR-4 area. That number is descriptive only; the remaining area is consumed by switching-loop routing, thermal copper, MIPI/ground continuity, high-current planes, edge clearance, flex/harness approaches, Nano overlap/keepouts and test access. It is not unused packing margin.

The smallest credible conventional outline is approximately **128 × 98 mm** if edge margins and left-wing support clearances are tightened. The recommended REV1 working outline is the implemented **130 × 100 mm nominal** envelope. The extra approximately 1 mm per affected edge is justified by the M3 support-hole edge web, J702 service edge, J1003 access and routing margin around the power islands. No edge can be reduced materially without moving a connector/support or compressing a switching block.

The conventional outline is sufficient. A U-shaped or larger central opening would remove useful routing/thermal area and is not justified by the current placement. Revisit only if enclosure access or cable installation—not area ratio—demands it.

## Mechanical support

Both SSQ rows are retained for alignment and electrical mating; J1002 remains electrically unused. The two connector rows improve torsional alignment, but their solder joints must not be the vehicle shock/vibration load path.

- Use matched M2.5-class spacers at the four Nano Ø2.70 mm hole coordinates wherever the enclosure permits.
- The lower-left Nano hole accepts a small approximately 5 mm-OD spacer boss; avoid a broad washer because of the connector cutout.
- Two board-only M3 holes were added on the expanded left wing at **(47.70, 29.05) mm** and **(47.70, 119.05) mm**. Chassis posts here react J201/fuse service loads and the left-wing bending moment.
- Set standoff length from the measured mated SSQ assembly, nominally 11.01 mm between facing PCB surfaces. Do not force the connector rows to compensate for a mismatched spacer.

## Remaining physical verification

1. **Nano DSI contact face and pin 1:** inspect the actual Nano connector under magnification and continuity-check pin 1 if necessary. This determines the final Type-A/Type-B cable purchase and confirms the J701 rotation.
2. **FFC installation mock-up:** pass the exact 15-way cable and its stiffener through the 3.17 × 18.23 mm slot, mate both ends, and verify bend radius, abrasion margin and service removal. Widen the slot toward the P1 side only if this test requires it.
3. **SSQ mating sample:** mate both exact sockets to one Nano; measure board separation, simultaneous insertion depth and binding. Select spacers from the measured value.
4. **USB/RJ45 first article:** verify shell clearance, plug/latch access and the 0.20 mm RJ45-side nominal margin before production release.
5. **Standoff hardware:** verify that the chosen boss/washer fits the lower-left Nano hole beside the cutout and that the two left-wing M3 posts align with the enclosure load path.
6. **Panel and touch flex:** confirm delivered flex pin 1, exposed-contact side, stiffener and exit direction as already required by the connector-interface review.

These checks gate mechanical freeze. They do not block schematic correctness or further PCB routing authorization.
