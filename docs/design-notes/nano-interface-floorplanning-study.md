# Nano interface correction and preliminary floorplanning study

> Historical conceptual study: its P1/P2 mapping and GPIO decisions remain authoritative, but its generic rectangular outline and ESW socket/height recommendations were superseded by the real SSQ placement in `preliminary-placement-mechanical-baseline.md` on 2026-09-22.

**Date:** 2026-09-21

**Electrical baseline:** canonical `main` at `388b9dd` before this focused correction

**Scope:** complete ESP32-P4-NANO P1/P2 audit, deliberate control-GPIO selection, and quantitative pre-layout stacking/area study. This is not PCB placement, routing, stackup selection, board-outline release, or FFC-slot release.

## 1. Source hierarchy and method

The following repository files controlled this review:

| Use | Controlling source | Identity |
|---|---|---|
| Physical P1/P2 positions and GPIO names | Waveshare Wiki pinout chart, `hardware/mechanical/vendor/Waveshare/ESP32-P4-NANO/ESP32-P4-NANO-details_inter.jpg` | SHA-256 `271259f821264dd8cfbf8c967bf27c6e222504c9732fbecd41ff1b8f88b8f5d9` |
| Header electrical cross-check and Nano onboard connections | `ESP32-P4-NANO-schematic.pdf` | Waveshare PDF created 2024-10-25; SHA-256 `1e57b31f9ecc98be77c6cfba7ff1720e0f764d36208cbe18dff7f1fbea310de1` |
| Mechanical geometry | Waveshare `ESP32-P4-NANO-20260331.pdf`, DXF and STEP | hashes and validation in `mechanical-interface-verification.md` |
| Visual orientation only | `esp32-p4-nano.jpg` | SHA-256 `33af2c478b6011fef705875fb0169669572f1e7a66d5a6dd63cc9580f5725f76` |
| SoC restrictions | Espressif ESP32-P4 Series Datasheet v0.7 and ESP-IDF GPIO/LEDC documentation | checked 2026-09-21 |
| Elevated socket geometry | Samtec ESW drawing and catalog F-226 Rev. 16JUN26 | checked 2026-09-21 |

The pinout chart was transcribed row by row. The schematic's connector block was then used as an electrical cross-check; crossing lines elsewhere in the schematic were not used to infer physical header positions. The original Waveshare mechanical files continue to control dimensions. The KiCad `User.1` Nano drawing remains only a validated, edited/rescaled working reference.

## 2. Corrected complete P1 map

On P1, odd pins are the chart's left column and even pins its right column when viewed in the published top-side pinout orientation. `NC` below means no daughterboard electrical connection; it does not mean the Nano pin is functionless.

| P1 pin | Waveshare Nano function | Relevant alternate/onboard use | Daughterboard connection |
|---:|---|---|---|
| 1 | 3V3 | Nano 3.3 V rail | NC |
| 2 | 5V | Nano 5 V rail | `NANO_5V` |
| 3 | GPIO7 | touch channel 5; Nano `ESP_I2C_SDA` | NC |
| 4 | 5V | Nano 5 V rail | `NANO_5V` |
| 5 | GPIO8 | touch channel 6; Nano `ESP_I2C_SCL` | NC |
| 6 | GND | ground | `GND` |
| 7 | GPIO23 | ADC1 channel 7 | `BL_PWM` |
| 8 | GPIO37 | UART0 TX; strapping pin | NC |
| 9 | GND | ground | `GND` |
| 10 | GPIO38 | UART0 RX; strapping pin | NC |
| 11 | GPIO5 | touch channel 3; pad JTAG group | NC |
| 12 | GPIO4 | touch channel 2; pad JTAG group | NC |
| 13 | GPIO20 | ADC1 channel 4 | `LCD_PWR_EN` |
| 14 | GND | ground | `GND` |
| 15 | GPIO21 | ADC1 channel 5 | `LCD_RESET_CMD_N` |
| 16 | GPIO22 | ADC1 channel 6 | `CTP_RESET_N_NANO` |
| 17 | 3V3 | Nano 3.3 V rail | NC |
| 18 | GPIO24 | `USB1P1_N0`; USB Serial/JTAG pair option | NC |
| 19 | GPIO25 | `USB1P1_P0`; USB Serial/JTAG pair option | NC |
| 20 | GND | ground | `GND` |
| 21 | GPIO26 | `USB1P1_N1`; USB Serial/JTAG pair option | NC |
| 22 | GPIO27 | `USB1P1_P1`; USB Serial/JTAG pair option | NC |
| 23 | GPIO32 | ordinary GPIO | `CTP_INT_NANO` |
| 24 | GPIO33 | ordinary GPIO | NC; reserve alternate |
| 25 | GND | ground | `GND` |
| 26 | GPIO36 | strapping/ROM-print control | NC |

The previous mapping was not a one-row offset that could safely be patched locally: it put controls on two ground pins, mislabeled several adjacent GPIOs, omitted two 3.3 V functions, left a ground unidentified, and called GPIO36 ground. The complete symbol and all connected P1 nets were therefore corrected together.

## 3. Corrected complete P2 map

P2 uses the same odd-left/even-right row convention in the Waveshare chart. Every P2 pad is intentionally electrically unconnected on the daughterboard; the actual Nano function remains visible in the connector symbol.

| P2 pin | Waveshare Nano function | Relevant alternate/onboard use | Daughterboard connection |
|---:|---|---|---|
| 1 | 5V | Nano 5 V rail | NC |
| 2 | `ESP_LDO_VO4` | Nano internal rail/test exposure | NC |
| 3 | GND | ground | NC |
| 4 | GND | ground | NC |
| 5 | 3V3 | Nano 3.3 V rail | NC |
| 6 | GPIO0 | XTAL_32K_N option | NC |
| 7 | GND | ground | NC |
| 8 | GPIO1 | XTAL_32K_P option | NC |
| 9 | GPIO3 | touch channel 1; pad JTAG group | NC |
| 10 | GND | ground | NC |
| 11 | GPIO2 | touch channel 0; pad JTAG group | NC |
| 12 | GPIO6 | touch channel 4 | NC |
| 13 | GPIO54 | ADC2 channel 7 | NC |
| 14 | GPIO53 | ADC2 channel 6 | NC |
| 15 | GPIO47 | ordinary GPIO | NC |
| 16 | GPIO48 | ordinary GPIO | NC |
| 17 | GPIO46 | ordinary GPIO | NC |
| 18 | GND | ground | NC |
| 19 | GPIO45 | ordinary GPIO | NC |
| 20 | C6_U0RXD | ESP32-C6 UART0 RX | NC |
| 21 | C6_IO12 | ESP32-C6 GPIO12 | NC |
| 22 | C6_U0TXD | ESP32-C6 UART0 TX | NC |
| 23 | C6_IO13 | ESP32-C6 GPIO13 | NC |
| 24 | C6_IO9 | ESP32-C6 GPIO9 | NC |
| 25 | GND | ground | NC |
| 26 | GND | ground | NC |

## 4. Final control-GPIO assignments

| Daughterboard function | Final Nano connection | Selection reason |
|---|---|---|
| `LCD_PWR_EN` | P1-13 / GPIO20 | Ordinary input/output GPIO, no Nano onboard peripheral connection shown, not a strapping pin, not in a USB/JTAG/UART0 caution group, and safe for a default-low enable. |
| `LCD_RESET_CMD_N` | P1-15 / GPIO21 | Same conflict-free class as GPIO20; ordinary output operation and the existing hardware pull-down/open-drain reset architecture preserve asserted reset until firmware takes control. |
| `BL_PWM` | P1-7 / GPIO23 | Conflict-free ordinary output on P1. ESP32-P4 output routing supports LEDC/PWM through the GPIO matrix; the external pull-down preserves backlight-off at reset. |
| `CTP_RESET_N_NANO` | P1-16 / GPIO22 | Conflict-free ordinary digital output. GT9271 reset does not require an ESP32-P4 touch-capable pad. |
| `CTP_INT_NANO` | P1-23 / GPIO32 | Conflict-free ordinary bidirectional GPIO. It can drive the GT9271 address strap during reset and then become a digital interrupt input; native capacitive-touch capability is irrelevant. |

GPIO33/P1-24 is the preferred spare alternate. GPIO7/8 were not selected because the Nano schematic connects them to its shared `ESP_I2C_SDA/SCL` nets. GPIO2–5 were avoided because they are in the pad-JTAG caution group. GPIO24–27 were avoided to preserve both USB Serial/JTAG transceiver options. GPIO36–38 were avoided because they are strapping pins; GPIO37/38 also carry UART0. The selected five pins are not ESP32-P4 strapping pins and show no Nano onboard load other than their header breakout.

## 5. Is P2 electrically required?

**No.** P1 supplies both 5 V pins, five ground returns and all five controls. Nano DSI plus the Nano-carried I2C pair arrive through the separate 15-pin display flex. No daughterboard function requires a P2 signal or power pin. The former two P2 ground connections were removed so J1002 is now unambiguously a mechanically optional connector rather than an electrical return path.

Retaining P2 can still be useful. In an overlapping stack, a matching non-electrical P2 socket greatly improves alignment and torsional stiffness. It should not be treated as the only structural restraint in a vehicle environment; properly height-matched standoffs should carry shock and insertion loads. In a side-stack, P2 can be omitted if two remote standoffs create a rigid support polygon.

## 6. Elevated-header result

Samtec ESW is a vertical, through-hole, 2.54 mm-pitch elevated socket family for 0.64 mm-square mating posts. The manufacturer specifies 3.68–6.35 mm insertion depth. The Nano STEP gives approximately 0.64 mm-square pins, a 2.50 mm header body above the Nano PCB, and approximately 5.80 mm pin exposure above that body.

| Use | Exact candidate | ESW dimension B | Approx. mated PCB separation | USB-A clearance | RJ45 clearance | Assessment |
|---|---|---:|---:|---:|---:|---|
| Minimum overlap | `ESW-113-23-G-D` | 13.59 mm | 13.59 + 2.50 = **16.09 mm** | **1.64 mm** | **2.49 mm** | Pin insertion is 5.80 mm and valid, but component clearance is tight after tolerance/vibration allowance. |
| Recommended overlap | `ESW-113-33-G-D` | 16.13 mm | 16.13 + 2.50 = **18.63 mm** | **4.18 mm** | **5.03 mm** | Preferred REV1 overlap height; the modest extra height gives materially better tolerance and vibration margin. |

Both are available as 2×13 configurations. The standard ESW solder tail is 0.41 × 0.79 mm; the selected daughterboard implementation will require a 2.54 mm through-hole grid and a manufacturer-footprint check for the exact lead style before placement. Style `-33` has a nominal 2.29 mm solder tail, adequate for a normal 1.6 mm PCB. `-LL` locking leads and the corresponding low-insertion-force `-58` style can be evaluated at procurement, but the standard-force `-33` is the baseline because standoffs—not reduced contact retention—should carry service loads. ESW is wave/hand-soldered rather than reflow-only.

The socket body must be mounted on the daughterboard underside to mate the Nano's upward male posts. This is the unavoidable exception to the otherwise top-side component objective. No active or passive circuit component needs bottom-side placement.

## 7. Functional area budget

These are planning envelopes, not placement rectangles. They include local bypass parts, credible switching loops, thermal copper, probe access and immediate routing channels; they are intentionally larger than raw courtyard sums.

| Functional block | Planning envelope | Area | Main contents / constraint |
|---|---:|---:|---|
| Input/service/protection | 45 × 30 mm | 1,350 mm² | J201 harness approach, MINI fuse/holder, TVS, L201, electrolytic, LM74800 and two protection FETs; board-edge service access dominates. |
| LM5176 24 V buck-boost | 55 × 40 mm | 2,200 mm² | U301, four power FETs, L301, current shunt, two 10 mm electrolytics, ceramics, gate loops, hot-node containment and heat spreading. |
| LM76003 5 V + Nano eFuse | 36 × 25 mm | 900 mm² | L501, input/output ceramics, U501/U502, short high-current loops and thermal vias/copper. |
| Hold-up and rail sequencing | 40 × 40 mm | 1,600 mm² | 16 mm C601 plus insertion resistor/diode, supervisor, sequencer, three rail/reset channels and test points. |
| Backlight power | 35 × 35 mm | 1,225 mm² | TPS922053, L901, catch diode, sense resistors/link, filtering, connector-side LED corridor and thermal copper. |
| DSI/LCD/touch interface | 60 × 30 mm | 1,800 mm² | J701, ESD, six 0201 links, J702, J801, TMUX/touch ESD and controlled, unobstructed flex exits. |
| Nano stack/control/debug reservation | 50 × 50 mm gross | 2,500 mm² gross | Headers, hardware, DSI pass-through, Nano service/RF restrictions and low-speed control/test access; only part is usable for circuitry. |
| Integration allowance | 2,500–3,500 mm² | — | Mounting, edge clearances, thermal separation, power/ground continuity, test probes and routing channels between blocks. |

The first six blocks total approximately 9,075 mm² before integration allowance. This is why a raw courtyard-packing estimate would be misleading; the four-switch converter, harness/fuse access, flex corridors and thermal copper set the board size.

## 8. Nano-overlap efficiency

The Nano's nominal 2,500 mm² outline is not 2,500 mm² of freely placeable daughterboard area. Approximate exclusions are:

- 300–400 mm² for the two header bodies, plated holes and solder-access bands;
- 250–400 mm² for mounting hardware and tool/washer access;
- 400–650 mm² for the DSI pass-through, cable bend and J701 service corridor;
- 300–450 mm² for the ESP32-C6 antenna/RF no-copper and thermal-separation region;
- 300–500 mm² for USB/RJ45/button/SD access and no-protrusion zones.

Some exclusions overlap. Approximately **900–1,100 mm² (36–44%)** of the area above the Nano is realistically usable for top-side low/medium-power SMD circuitry or routing. It is not appropriate for through-hole bodies/tails, large hot power parts, external connectors, or dense switching loops. The overlap is therefore useful but cannot absorb an entire major power block.

## 9. Architecture comparison

Dimensions are pre-layout estimates with a few millimetres of edge/courtyard margin. Ratios are descriptive comparisons to the Nano's 2,500 mm², not design targets.

| Architecture | Minimum credible daughterboard | Area / Nano ratio | Overall assembly XY at minimum | Approx. vertical envelope | Principal drivers |
|---|---:|---:|---:|---:|---|
| A. Dual-header elevated overlap | **130 × 90 mm** | 11,700 mm² / 4.68× | about 130 × 90 mm | about 49–50 mm with recommended 18.63 mm separation and 25 mm C601 | Power-stage spacing, Nano service/RF zones, DSI opening and edge connectors. |
| B. P1-only side-stack with remote supports | **120 × 85 mm** | 10,200 mm² / 4.08× | about 165–170 × 85 mm including adjacent Nano | about 38–40 mm with low-profile socket | Efficient board use and lower height, but larger assembly width and mandatory chassis/backplate support. |
| C. P1 electrical + P2 mechanical support | **130 × 90 mm** | 11,700 mm² / 4.68× | about 130 × 90 mm | about 49–50 mm at recommended separation | Same packaging as A, without any P2 electrical dependency; best self-aligning stack. |

### Recommended REV1

Use Architecture C as the primary conventional concept and reserve **145 × 100 mm = 14,500 mm² (5.80× Nano area)** for REV1. Use `ESW-113-33-G-D`-class sockets at P1 and P2, with P2 electrically unconnected, plus at least two height-matched M2.5-class standoffs placed to react connector and harness loads. This size provides credible routing freedom around the LM5176, test access on all rails, flex service corridors and separation between switching nodes and MIPI.

Architecture B remains a strong packaging alternative when assembly height matters more than width. A practical development size is **135 × 95 mm = 12,825 mm² (5.13×)**, producing roughly **180 × 95 mm** total XY when the Nano sits alongside it. Use the low-profile P1 socket only as alignment/electrical interconnect and provide at least two remote, height-matched standoffs tied to a rigid carrier or chassis. With that support polygon, P1-only can be mechanically equivalent or superior to a header-only dual stack because the connector is not asked to react bending loads.

Architecture A offers no electrical advantage over C. If both headers are fitted, leaving P2 electrically open is preferable: it preserves the mechanical benefit and avoids creating an unnecessary parallel return path or future assumption that P2 signals are used.

## 10. Structural and service comparison

| Topic | Both P1/P2 populated | P1 + non-electrical P2 | P1-only + standoffs |
|---|---|---|---|
| Rocking/torsion | Good; two separated header lines resist rotation | Same mechanical result as dual electrical headers | Poor without remote supports; good with two far-edge standoffs and a rigid carrier |
| Connector bending load | Moderate unless standoffs carry insertion/harness loads | Moderate; P2 is a dedicated alignment/support element | Can be lowest when standoffs carry the board and P1 floats within tolerance |
| Assembly alignment | Self-aligning but 52 contacts increase mating force | Self-aligning; no electrical dependence on P2 contacts | Requires controlled standoff datum and careful parallel insertion |
| Vibration | Headers alone are insufficient | Preferred with two or more standoffs | Acceptable only with fastened remote supports; no cantilevered free edge |
| Maintenance | Highest mating force; both connectors must release together | Same contact count but simple electrical diagnosis | Lowest connector count and best Nano access, but carrier fasteners must be removed |
| Packaging | Compact XY, taller Z | Compact XY, taller Z | Lower Z and better port access; wider overall assembly |

## 11. Top-side J701 and DSI pass-through

The Nano board image corroborates the STEP orientation: Nano DISPLAY connector J1 is on the top face, its mouth opens toward the board interior, and the cable initially exits inward. A section through the manufacturer STEP indicates bottom-contact construction, so the exposed conductors face the Nano PCB when inserted. The Waveshare schematic fixes the electrical order but does not define the physical pin-1 end of the real connector.

`J701` remains Amphenol `SFW15R-2STE1LF`, a top-contact connector. It is now reserved on the daughterboard **top**, not underside. The preferred conceptual route is:

1. FFC exits Nano J1 inward with contacts down.
2. It bends upward without a crease.
3. It passes through a radiused daughterboard opening.
4. It makes a broad second bend into top-side J701.

Reserve a preliminary **22–24 mm × 8–10 mm radiused opening**, suitable for the approximately 16 mm-wide 15-way/1.0 mm-pitch flex plus lateral tolerance and edge protection. Reserve an overall **about 25 × 30 mm** slot/bend/J701 service corridor. Apply at least 1.0–1.5 mm copper clearance from the routed edge, remove burrs, and consider an edge liner or smooth controlled-radius finish. Final slot dimensions require the selected cable's thickness/stiffener and bend-radius data and are deliberately not frozen here.

With J701's mouth facing the slot, the shortest untwisted S-bend preserves the cable face at each horizontal end: Nano bottom-contact and daughterboard top-contact therefore require a **Type B / opposite-side-contact** 15-way FFC. Turning J701's mouth away from the slot can create a 180° return loop that permits a Type A cable, but it consumes more area and complicates service. Type B with the mouth toward the slot is the preliminary preference; do not release the cable or pad-1 orientation until the physical Nano pin-1/contact-face check is complete.

The DSI electrical map remains straight-through. Moving J701 to the top creates no intrinsic signal-integrity problem: place J701, the six inline links and U701 so the three 100 Ω differential pairs leave the connector directly, avoid vias if practical, keep continuous ground away from the routed-edge clearance, and do not run the pairs around the slot perimeter. The extra cable/PCB path is small relative to the 1.5 Gb/s/lane design target. Detailed length/skew/impedance work belongs to authorized layout.

## 12. Single-sided assembly result

Single-sided **SMT** assembly is feasible and preferred. All converters, MOSFETs, small passives, J201, J701, J702 and J801 can remain on top. C601, the MINI fuse holder, debug header and service jumper are top-side through-hole bodies. The Nano mating sockets are the only required underside bodies; they are through-hole and hand/wave soldered. No electrical or thermal block justifies bottom-side SMD placement.

Keep through-hole tails and test-point pins out of the Nano overlap, especially over USB-A, RJ45, the antenna and buttons. The recommended 18.63 mm separation provides clearance but does not authorize arbitrary underside protrusion.

## 13. Outline conclusion

A conventional rectangular board with local edge notches as needed and one radiused DSI pass-through is sufficient for REV1. A large closed Nano clearance opening would discard useful routing/ground area without eliminating the need for headers and standoffs. A U-shaped/open-edge board or larger central opening merits later comparison only if enclosure height, USB/RJ45 direct access, or field service proves more important than compact XY and structural continuity. No elaborate profile is justified solely by board-area ratio.

## 14. Remaining physical verification

**NEEDS PHYSICAL VERIFICATION before placement/outline/cable freeze:**

1. On the actual Nano, identify DISPLAY/J1 physical pin 1 by silkscreen or powered-off continuity and confirm the STEP-inferred bottom-contact face and inward cable exit.
2. Mate the exact ESW lead style to the Nano and measure pin insertion and PCB-to-PCB separation; confirm both socket rows seat without binding and that the proposed standoffs match the measured height.
3. Obtain the selected 15-way FFC and verify Type-B contact presentation, stiffener thickness, minimum bend radius and install/remove path through a 1:1 mock opening.
4. Continue the already-recorded LCD/touch flex sample checks and verify the J201 harness bend/latch envelope in the chosen architecture.

These checks do not reopen the corrected electrical mapping. No electrical issue blocks the pre-layout baseline, and this study does not authorize placement or routing.

## 15. Verification status

- Complete P1 and P2 pin tables match the Waveshare pinout chart and the header blocks in the official Waveshare schematic.
- All five controls use P1 GPIOs that are ordinary, non-strapping and free of Nano onboard connections in the official schematic.
- P2 has no daughterboard electrical connection.
- The schematic connector symbols retain every host power, ground and GPIO function even where the daughterboard leaves the pin open.
- Only J1001/J1002 symbol metadata, J1001 control/ground stubs, and the removal of the two former P2 ground stubs changed electrically in the Nano interface sheet; the DSI, panel, touch, power and sequencing nets were not altered.
- Native KiCad CLI ERC/netlist export was not available in this execution environment. Balanced-S-expression parsing, connector-coordinate/net extraction, complete symbol/library pin-map comparison, and a scoped textual connectivity diff were used instead; the existing all-zero ERC report remains the last native KiCad run and must be regenerated in KiCad 10 before PCB work begins.
