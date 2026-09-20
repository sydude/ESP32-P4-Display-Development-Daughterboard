# Pre-layout mechanical and cable-interface verification

**Date:** 2026-09-20

**Baseline reviewed:** `a561034`

**Scope:** ESP32-P4-NANO mechanical datums, the derived KiCad `User.1` reference, Nano stacking, Nano DSI, Displayman LCD and touch flex presentation. Component placement, routing, stackup design, board-outline design and general PCB layout were not started.

## 1. Result and limits

The Waveshare PDF, DXF and STEP agree on the Nano board outline, mounting pattern, header pitch and principal component arrangement. The derived drawing on the PCB `User.1` layer is correctly scaled and oriented for use as a visual working reference, but it is not accurate enough to become the sole source for holes, headers or connector placement. Authoritative coordinates shall be recreated from the dimensions in this note when layout is authorized.

No electrical pin-map error was found. The stack-on concept is mechanically possible only if the daughterboard either clears the Nano's tall Ethernet/USB hardware with cutouts/notches or uses a verified board separation greater than those envelopes. The existing ordinary stack height must not be assumed adequate.

The remaining sample checks are narrow: Nano DSI pin 1/contact presentation, the chosen socket's mated height, and the exact delivered panel/touch flex terminations and pin-1 presentation. They are marked **NEEDS PHYSICAL VERIFICATION** below.

## 2. Controlling sources and provenance

| Source | Identity | Use |
|---|---|---|
| Waveshare PDF | `ESP32-P4-NANO-20260331.pdf`, SHA-256 `ee1cf29a9aec2f7602889492a8fa8ded9dff3baa0776b8bc11dc2ef8e845204d` | Controlling published dimensions and orthographic presentation |
| Waveshare DXF | `ESP32-P4-NANO-20260331.dxf`, SHA-256 `d18ef20385a438091bac0770b30785841a4677e949c99e6b69e870f0eac74184` | Controlling vector geometry and dimension objects |
| Waveshare STEP | `ESP32-P4-NANO.stp`, SHA-256 `6515bce434b8a5542d99a801bd67a6f8c438cc12ef0ebad632d7e37ceb14fabe` | Controlling 3-D geometry, component envelopes and inferred connector presentation |
| Waveshare Nano schematic | PRD source S3 | Electrical connector/header numbering and signal assignment; it does not define physical pin-1 presentation |
| Displayman correspondence | PRD source S8, repository PDF | Manufacturer confirmation of bottom-contact 40-pin LCD and 8-pin touch flexes and their electrical pin assignments |
| Connector drawings | Amphenol 10172241 Rev. A; Molex 5051101008-SD Rev. C; Hirose FH12 family drawing | Daughterboard connector contact configuration, numbering and insertion direction |
| Derived KiCad reference | `ESP32-P4 Display Development Daughterboard.kicad_pcb`, pre-audit SHA-256 `dd884d6342e9c0552fbacd75f8469948aa95ae0a6cebc7b31f389cdb1510c910` | Edited/rescaled working drawing only; not a manufacturer source |

The three files under `hardware/mechanical/vendor/Waveshare/ESP32-P4-NANO/` are preserved manufacturer references. The KiCad `User.1` drawing is an edited/rescaled derivative. In particular, the DXF header declares `$INSUNITS = 1` (inches) and `$MEASUREMENT = 0`, while its coordinate values and dimension values are millimetres. This metadata conflict explains why a direct unit-aware KiCad import is not authoritative.

## 3. Nano datum system and dimensions

The following coordinate system is used only to state verified relative geometry: origin at the nominal lower-left board corner in the STEP top view, +X to the right, +Y toward the opposite board edge, Nano component side at Z = 0 and PCB underside at Z = -1.60 mm.

### 3.1 Manufacturer-defined and STEP-resolved geometry

| Item | Verified result | Classification |
|---|---|---|
| PCB outline | Nominal 50.00 × 50.00 mm; STEP body extrema are X = -0.0097…50.0097 and Y = -0.0097…50.0097 mm, reflecting CAD edge construction rather than a separate 50.019 mm requirement | PDF nominal; STEP corroboration |
| PCB thickness | 1.60 mm | PDF/DXF/STEP |
| Mounting holes | Four Ø2.70 mm through holes; centers `(2.450, 2.460)`, `(47.550, 2.460)`, `(2.450, 47.560)`, `(47.550, 47.560)` mm | PDF/DXF and STEP circular geometry |
| Hole-center spans | 45.10 mm X and 45.10 mm Y | Derived from manufacturer coordinates |
| Header pitch | 2.54 mm in both axes, two rows × thirteen positions at each side | PDF/DXF/STEP |
| Header X centers | Left header rows X = 1.48 and 4.02 mm; right header rows X = 45.98 and 48.52 mm | STEP inferred |
| Header Y centers | Y = 12.96 through 43.44 mm in 2.54 mm increments; first-to-last span 30.48 mm | PDF dimension and STEP inferred |
| Header pin section | Approximately 0.64 mm square in the STEP | STEP inferred |
| Fitted header Z envelope | Z = -3.00…+8.30 mm; modeled plastic envelope X = 0.21…5.29 and 44.71…49.79 mm, Y = 12.09…44.71 mm | STEP inferred |

The mechanical sources do not label the two modeled 2×13 headers as P1 versus P2 and do not encode header pin numbers. Electrical P1/P2 numbering remains controlled by the Waveshare schematic. **NEEDS PHYSICAL VERIFICATION:** identify P1 pin 1 on the actual Nano by silkscreen/continuity before a daughterboard footprint is oriented. Do not infer it from the symmetric STEP header body.

### 3.2 Derived KiCad `User.1` validation

The locked derivative contains the same four orthographic views and dimension presentation as the manufacturer PDF. The central component-side view preserves the PDF orientation and measures 49.9986 mm across the nominal 50 mm outline. Its measured right/left hole span is 45.0940 mm versus the authoritative 45.1000 mm, a scale error of approximately -0.013%. No rotation, mirror or gross-scale error was found.

One conversion artifact is measurable: the lower-left hole graphic is about 0.035 mm lower than the lower-right hole graphic even though the STEP centers share one Y coordinate. Curves are also tessellated into polygons, so their extrema do not reproduce the exact Ø2.70 mm circles. These sub-0.04 mm artifacts were not edited because the layer is a locked technical illustration rather than production geometry. They are documented to prevent its use as a drill/header placement source.

The imported `NANO-SVG` group also contains 660 stale member UUIDs left by earlier replacement/deletion of derived primitives. They reference no live PCB object; all 10,534 live members resolve, are locked and are on `User.1`. The stale strings do not change rendering or geometry and were left unchanged so this verification would not rewrite a multi-megabyte derivative merely to normalize group metadata. A future authorized KiCad PCB editing pass may let KiCad clean the group when the working reference is replaced by dimension-driven placement datums.

**Disposition: PASS as a visual working reference; not approved as an authoritative placement datum.**

## 4. Nano component envelopes and practical keepouts

Coordinates below are STEP-derived bounding boxes. They are useful pre-layout exclusion envelopes, not manufacturer tolerance limits. Add assembly, cable bend, finger access and manufacturing clearance when placement is authorized.

| Feature | STEP envelope, mm | Pre-layout requirement |
|---|---|---|
| Ethernet/RJ45 body | X 6.241…22.281; Y -1.120…20.280; Z -3.60…+13.60 | Board-edge opening; no daughterboard body/component intrusion above it; preserve plug/latch and cable bend access |
| USB-A body (`J2` in STEP) | X 23.100…30.300; Y -1.650…17.550; Z -3.760…+14.450 | Tallest modeled upper component and lowest overall feature; requires a cutout/notch or verified separation above 14.45 mm plus clearance |
| USB-C body (`H5` in STEP) | X 20.200…29.780; Y 43.496…51.204; Z -0.910…+3.250 | Edge opening and cable-shell/finger keepout beyond Y = 50 mm |
| Nano DSI `J1` | X 6.450…11.522; Y 27.100…49.500; Z 0…+5.680 | Preserve latch access and a flex bend corridor toward the connector mouth |
| Camera connector `J3` | X 13.700…18.772; Y 27.100…49.500; Z 0…+5.680 | Preserve latch and optional camera-cable service even though unused by this daughterboard |
| MicroSD socket | X 6.777…18.126; Y 37.526…48.776; Z -2.920…-1.600 | Underside card insertion/removal volume and finger access must remain open |
| Antenna/module region (`U1`) | X 31.200…44.400; Y 0.250…16.850; Z -0.017…+2.465 | Do not place a daughterboard ground plane, metal hardware or high-current converter directly over the antenna region; exact RF keepout is not dimensioned in the mechanical drawing |
| Two edge pushbuttons | Combined X 34.290…45.290; Y 46.451…50.453; Z -0.50…+3.30 | Preserve top actuation and edge finger/tool access |
| Microphone | X 45.800…49.200; Y 7.150…9.750; Z +0.102…+1.100 | Preserve an acoustic opening; do not cap it with a solid daughterboard plane/enclosure wall |
| Auxiliary 1×4 header | X 23.630…33.790; Y 19.030…21.570; Z -3.00…+8.30 | Avoid collision or deliberately provide a cutout; retain probe/mating access if used |
| Auxiliary 2-pin header | X 41.880…44.420; Y 39.630…44.710; Z -3.00…+8.50 | Avoid collision or deliberately provide a cutout |
| Small 1.25 mm connectors | X 0.900…4.100, Y 5.950…10.950 and X 37.303…40.505, Y 18.280…23.281; Z -1.90…+4.70 | Preserve mating/removal path if these Nano functions remain serviceable |

The STEP's extrema make a simple low-profile full-overlap daughterboard invalid: +14.45 mm USB-A and +13.60 mm RJ45 envelopes exceed the +8.30 mm male-header tips. A viable daughterboard therefore needs cutouts/notches or a taller, explicitly verified socket/standoff system. Exact moving volumes for plugs, cards, buttons and flex latches are not supplied by Waveshare; use the physical Nano during layout/mechanical freeze.

The daughterboard's vertical Micro-Fit J201 is not yet placed. Its eventual keepout must include the mating plug, latch release and harness bend height normal to the daughterboard, and must remain accessible with the Nano installed. Those volumes depend on the selected harness and cannot be projected onto the unplaced PCB in this verification pass.

## 5. Daughterboard stacking definition

| Topic | Preliminary verified definition | Status |
|---|---|---|
| Mating grid | Two 2×13 interfaces, 2.54 mm pitch; reproduce the exact row/column centers in Section 3.1 | PASS |
| Nano fitted side | STEP shows male 0.64 mm-square posts through the Nano, with approximately 8.30 mm above the component-side board plane and 3.00 mm below it | PASS, STEP inferred |
| Daughterboard mate | Female 2×13, 2.54 mm sockets mounted on the daughterboard underside are required for a daughterboard above the Nano | PASS as architecture |
| Exact socket | The schematic's generic `PinSocket_2x13` footprint and provisional Samtec `SSW-113-02-G-D` family do not, by themselves, freeze mounting side, tail option or mated height | NEEDS PHYSICAL VERIFICATION |
| Pin 1 | Electrical P1/P2 mapping is correct, but physical P1/P2 and pin-1 presentation are not marked in PDF/DXF/STEP | NEEDS PHYSICAL VERIFICATION |
| Separation | Must exceed every retained overlap envelope or be combined with cutouts; ordinary header-tip height is not adequate over USB-A/RJ45 | NEEDS PHYSICAL VERIFICATION after socket/cutout choice |
| Mounting holes | Four Ø2.70 holes can accept M2.5-class hardware. Matching daughterboard holes and spacers are practical, but the high-Y holes are close to the header end and require actual washer/standoff-envelope checking | PASS concept; hardware envelope to verify |
| Orientation | A component-side-up Nano with the daughterboard above it is viable only with the clearances in Section 4 and with the DSI connector accessible from the inter-board gap or a board edge | Conditional PASS |

**Required measurement:** mate the exact proposed female socket to one Nano header and measure Nano top-plane to daughterboard bottom-plane and PCB-plane-to-PCB-plane separation. Record socket body position, insertion depth, tail protrusion and standoff length. This cannot be recovered from the Nano files because it depends on the purchased socket configuration.

## 6. J701 — Nano DSI connector and cable

### 6.1 Mechanical presentation

- The Nano connector identified as `J1` by its schematic/reference data is the STEP component at X = 6.450…11.522, Y = 27.100…49.500 mm. A section through the manufacturer STEP shows its spring beam rising from the PCB side to contact the underside of the inserted flex: **bottom contact**. This is an inference from the manufacturer STEP, not a written PDF callout.
- The connector is side-entry and lies on the Nano component side. In the Section 3 coordinate system its slot opens toward +X, into the Nano interior and away from the adjacent left-side header; the inserted flex extends toward +X from the mouth before bending. Its latch and the full bend corridor must remain accessible in the inter-board gap.
- `J701`, Amphenol `SFW15R-2STE1LF`, is a 15-way, 1.00 mm **top-contact** side-entry connector. In the native footprint orientation its body runs from Y = 0 to +6.5 mm and the cable/slider service side is +Y. It is mechanically appropriate when mounted on the daughterboard underside: its contact face then points into the inter-board gap in the required global direction even though its manufacturer contact designation differs from the Nano's.
- For the baseline in which Nano `J1` and underside `J701` mouths face the same +X direction, a non-twisted 180° service loop uses a **Type B / opposite-side-contact** 15-way FFC. Mounting `J701` on the opposite board face or reversing its mouth changes this conclusion and shall not be done without re-deriving the cable presentation.
- The loop must not be creased at the connector. Final length and bend radius require a mock-up after the stack height is measured.

### 6.2 Pin numbering and electrical map

The schematic is straight-through by connector pin number: Nano 1/2 = D1 N/P, 4/5 = CLK N/P, 7/8 = D0 N/P, 11/12 = I²C SCL/SDA, with grounds and 3.3 V reference pins unchanged. This map agrees with Waveshare S3 and the panel map; no lane or polarity swap is present.

The mechanical files do not identify which end of the Nano connector is physical pin 1. Therefore a 1-to-1 cable cannot be released solely from the STEP. **NEEDS PHYSICAL VERIFICATION:** with power removed, locate Nano J1 pin 1 using its silkscreen or continuity to a uniquely mapped pin (for example a ground/reference versus DSI signal), record the exposed-contact face when inserted, and orient `J701` pad 1 to preserve the documented straight-through map. This is a pin-orientation check, not an electrical redesign.

**Overall J701 status: NEEDS PHYSICAL VERIFICATION for pin 1 and confirmation of the STEP-inferred Nano contact face; selected connector and baseline Type-B routing concept PASS.**

## 7. J702 — 40-pin Displayman LCD interface

Displayman's written manufacturer response defines the module's 40-pin flex as bottom contact and calls for a 40-pin, 0.5 mm bottom-contact mate. Molex `505110-4096` is a 40-position, 0.5 mm, bottom-contact/front-flip connector, so the selected board connector is mechanically and electrically appropriate.

- Connector pad 1 is the leftmost signal pad in the verified footprint when viewed in its native front-side orientation; its silkscreen/fabrication pin-1 cue is present.
- In the native footprint orientation, the connector body spans Y = -4.0…+2.85 mm and the cable mouth is at the -Y side; the flex extends toward -Y after insertion. Placement must provide the full approximately 26.1 mm connector body/courtyard width, the front-flip actuator opening area and a straight -Y flex approach/bend corridor at the board edge.
- The schematic pin map exactly matches the Displayman 1–40 assignment, including D0/D1/CLK N/P and the paired LED cathode/anode pins. No electrical remap is required.
- Molex `0150200429` (76 mm) and `0150200431` (102 mm) are Type-A/same-side-contact FFCs. They are orientation-compatible only if the final assembly contains a receptacle at both ends with the derived same-side presentation. They cannot directly join the daughterboard receptacle to a bare integral panel FPC tail. The repository's manufacturer correspondence describes an LCM FPC tail, so these parts are **not released as the direct panel connection**; use the panel tail directly in `J702` unless the delivered module actually has an intermediate 40-pin receptacle/coupler.

**NEEDS PHYSICAL VERIFICATION:** on the delivered panel, confirm that the 40-pin termination is a bare flex tail, locate physical pin 1, confirm contacts/stiffener are on the documented bottom face, measure tail thickness/insertion depth, and record its natural exit/bend direction. If it is unexpectedly a receptacle, re-evaluate the two Type-A cable candidates against the receptacle contact side and required length.

**Overall J702 status: NEEDS PHYSICAL VERIFICATION for the delivered flex termination/pin 1; selected connector, bottom-contact configuration and electrical numbering PASS.**

## 8. Touch FPC/interface

Displayman's written response defines an 8-pin, 0.5 mm bottom-contact CTP flex with pins 1 GND, 2 NC, 3 VDD, 4 SCL, 5 SDA, 6 INT, 7 RST and 8 GND. `J801`, Hirose `FH12-8S-0.5SH(55)`, is the corresponding bottom-contact side-entry connector. The schematic map is identical and needs no change.

As with the LCD, the repository does not contain a manufacturer drawing showing which physical end of the delivered tail is pin 1, its stiffener, thickness, insertion depth or relaxed bend direction. **NEEDS PHYSICAL VERIFICATION:** inspect those five features on the exact touch assembly before orienting `J801`. Preserve latch access and a straight board-edge flex exit; do not fold across the active flex bond or panel edge.

## 9. Required user actions before layout authorization

Only the following physical facts remain necessary:

1. Nano DSI: photograph/record J1 pin-1 marking, inserted cable exposed-contact face, latch operation and cable-exit direction; confirm by powered-off continuity if no marking exists.
2. Nano stack: mate the exact proposed 2×13 female socket and measure PCB-to-PCB separation, body side, insertion depth and tail protrusion; check the intended M2.5 standoff/washer envelope.
3. Panel LCD: confirm bare-tail versus receptacle termination, pin 1, bottom contacts, stiffener face/thickness, insertion depth and relaxed exit direction.
4. Panel touch: confirm pin 1, bottom contacts, stiffener face/thickness, insertion depth and relaxed exit direction.
5. Make a non-electrical 1:1 stack/cable mock-up to confirm USB/RJ45 cutouts or separation, DSI loop bend radius, panel/touch exit, latch access, MicroSD access, buttons, microphone and J201 harness clearance.

No placement or routing should begin until these facts are recorded and the mechanical arrangement is explicitly authorized.

## 10. Post-review consistency checks

- The one-page manufacturer PDF parsed as A4; the DXF parsed with 19 dimension entities and the unit-metadata conflict stated in Section 2.
- SHA-256 checks confirmed that the manufacturer PDF, DXF and STEP binaries remain byte-identical.
- All seven top-level KiCad S-expression artifacts parsed with balanced structure.
- The `NANO-SVG` group contains exactly 10,534 live members; every live member resolves, is locked and is on `User.1`. Its 660 stale non-resolving member strings are recorded above. The PCB remained byte-identical to baseline at SHA-256 `dd884d6342e9c0552fbacd75f8469948aa95ae0a6cebc7b31f389cdb1510c910`.
- No `.kicad_sch`, `.kicad_sym`, `.kicad_mod` or `.kicad_pro` file changed. The committed all-severity ERC therefore remains applicable and reports 0 messages, 0 errors and 0 warnings.
- `git diff --check` passed.
