# References

This index records source documents and manufacturer links used by the project. Manufacturer and third-party PDFs are not stored in this repository unless deliberately approved.

## User-supplied project sources

| ID | Manufacturer / source | Document | Revision / identity | Repository status |
|---|---|---|---|---|
| S1 | Displayman (SZ) Technology Co., Ltd. | `KD068HDFID009-C009A` module datasheet | v1.0, 2024-11-25, 40 pages; SHA-256 `4c8394ac…03bcf` | External source; not committed |
| S2 | Displayman | `KD068HDFID009 -2LANE.txt` initialization file | SHA-256 `81ec9ab8…e6872c` | External source; not committed |
| S3 | Waveshare | `ESP32-P4-NANO-schematic.pdf` | PDF created 2024-10-25; SHA-256 `1e57b31f…10de1` | External source; not committed |
| S7 | Displayman, Anson Ho | Email reporting Displayman engineering confirmation that S2, including `RSOX(600)`, is correct for exact module | Received 2026-09-13 | External correspondence; summarized in PRD v0.2 |
| S8 | Displayman, Anson Ho | Detailed engineering response covering IOVCC, sequence, DSI, backlight, mapping, FPCs, and GT9271 | Received 2026-09-14; SHA-256 `76a9e53303412ff29189debf72a1f4c5dcf495e249f0ce86e32092063407ed4d` | User deliberately committed [email-chain PDF](design-notes/Re-%20Displayman%20%7C%20Datasheet%20%26%20Evaluation%20Units%20for%20KD068HDFID009-C009A.pdf); analyzed in PRD v0.3 |

Abbreviated hashes match `docs/PRD.md`. Full hashes should be retained in controlled project records if the source package is deliberately archived.

## Platform and board documentation

Checked 2026-09-14.

| Manufacturer | Document | Revision / date | Source |
|---|---|---|---|
| Espressif Systems | ESP32-P4 Series Datasheet | v0.7, 2026-07-14 | [Manufacturer documentation](https://documentation.espressif.com/esp32-p4_datasheet_en.html) |
| Espressif Systems | ESP32-P4 Hardware Design Guidelines | v1.9, 2026-07-21 | [Manufacturer PDF](https://documentation.espressif.com/esp-hardware-design-guidelines/en/latest/esp32p4/esp-hardware-design-guidelines-en-master-esp32p4.pdf) |
| Espressif Systems | ESP-IDF MIPI DSI LCD API | Current online documentation | [Manufacturer documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/peripherals/lcd/dsi_lcd.html) |
| Waveshare | ESP32-P4-NANO product documentation | Current online documentation; S3 remains the electrical source | [Manufacturer documentation](https://www.waveshare.com/wiki/ESP32-P4-NANO) |

## Power, sequencing, and interface components

Checked 2026-09-14. Status is the manufacturer product-page status where shown. Inclusion does not authorize schematic capture or substitution; `docs/PRD.md` remains controlling and `docs/design-notes/phase2-preparation.md` records recommendations.

| Manufacturer | Part number / family | Function | Status / document | Source |
|---|---|---|---|---|
| Texas Instruments | `LM76003RNPR` | 24 V to 5 V buck | ACTIVE; datasheet Rev. A | [LM76003](https://www.ti.com/product/LM76003) |
| Texas Instruments | `TLV75533PDBVR`, `TLV75528PDBVR`, `TLV75518PDBVR` | Touch 3.3 V / VCI 2.8 V / IOVCC 1.8 V LDOs | ACTIVE/production; datasheet Rev. D | [TLV755P](https://www.ti.com/product/TLV755P) |
| Texas Instruments | `TPS22919DCKR` | VCI load switch | ACTIVE; datasheet Rev. B | [TPS22919](https://www.ti.com/product/TPS22919) |
| Texas Instruments | `LM3880MF-1AA/NOPB` | Candidate three-stage sequencer | ACTIVE; fixed-function candidate | [LM3880](https://www.ti.com/product/LM3880) |
| Texas Instruments | `TPS3808G01DBVR` | Candidate power-fail supervisor | ACTIVE | [TPS3808](https://www.ti.com/product/TPS3808) |
| Texas Instruments | `SN74LVC1G07DBVR` | Open-drain reset buffer with Ioff | ACTIVE; datasheet Rev. AG | [SN74LVC1G07](https://www.ti.com/product/SN74LVC1G07) |
| Texas Instruments | `PCA9306DCTR` | Original I2C translator candidate | ACTIVE; superseded because it does not isolate INT/RESET | [PCA9306](https://www.ti.com/product/PCA9306) |
| Texas Instruments | `TMUX1574DYYR` / `TMUX1574PWR` | Recommended four-channel powered-off-protected touch switch | ACTIVE; datasheet Rev. C | [TMUX1574](https://www.ti.com/product/TMUX1574) |
| Texas Instruments | `TPD6E05U06RVZR` | Six-channel MIPI ESD | ACTIVE; TPDxE05U06 family | [TPD6E05U06](https://www.ti.com/product/TPD6E05U06) |
| Texas Instruments | `TPD4E05U06DQAR` | Four-channel touch ESD | ACTIVE; TPDxE05U06 family | [TPD4E05U06](https://www.ti.com/product/TPD4E05U06) |
| Texas Instruments | `TPS92511DDA` | Original buck backlight candidate | ACTIVE; superseded as baseline because full-temperature current spread is wider than project ±5% target | [TPS92511](https://www.ti.com/product/TPS92511) |
| Texas Instruments | `TPS922053DYYR` | Preferred 240 mA buck backlight driver | ACTIVE/production; datasheet Rev. B; 4.5–65 V, external 200 mV current sense, 100 ns minimum off-time, fast/hybrid PWM | [TPS922053](https://www.ti.com/product/TPS922053), [datasheet](https://www.ti.com/lit/ds/symlink/tps922053.pdf) |
| Analog Devices | `LT8391A` | Four-switch buck-boost LED contingency | Recommended for new designs; datasheet Rev. A; use only if completed buck headroom validation fails | [Product page](https://www.analog.com/en/products/lt8391a.html), [datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/lt8391a.pdf) |

## Input protection

Checked 2026-09-14.

| Manufacturer | Part number / family | Function | Validation note | Source |
|---|---|---|---|---|
| Same Sky | `PJ-044AH` | Original barrel-jack candidate | Manufacturer identifies 2.0 x 6.5 mm vertical through-hole; does not match PRD assumption | [Manufacturer page](https://www.sameskydevices.com/product/interconnect/connectors/dc-power-connectors/jacks/pj-044ah) |
| Switchcraft | `RAPC722X` | Recommended barrel-jack candidate | 24 V, 5 A, right-angle through-hole, 2.0 mm center-pin family | [Manufacturer page](https://www.switchcraft.com/right-angle-pc-mount-dc-power-jack-pin-size-0-080-2-0mm-open-frame/rapc722x/) |
| Littelfuse | `0451002.MRL`, 451 series | Input fuse | 2 A / 125 V very-fast-acting candidate; inrush coordination required | [Manufacturer series page](https://www.littelfuse.com/products/fuses-overcurrent-protection/fuses/surface-mount-fuses/451) |
| Littelfuse | `SMBJ30A`, SMBJ series | Input TVS | 30 V standoff / 600 W family | [Manufacturer page](https://www.littelfuse.com/products/tvs-diodes/surface-mount/smbj) |
| Vishay | `SS5P6-M3/86A` | Original Schottky reverse protection | Corrected product link; electrically valid but no longer preferred | [SS5P5/SS5P6](https://www.vishay.com/en/product/88988/) |
| Texas Instruments | `LM74700-Q1` plus external N-MOSFET | Recommended ideal-diode reverse protection | ACTIVE; 3.2–65 V, reverse-current blocking; datasheet Rev. G | [LM74700-Q1](https://www.ti.com/product/LM74700-Q1) |

## Vehicle-input and source-isolation components

Checked 2026-09-14. Automotive/AEC qualification of individual parts does not qualify the assembled evaluation board to ISO 7637 or ISO 16750.

| Manufacturer | Part number / family | Function | Status / validation note | Source |
|---|---|---|---|---|
| Texas Instruments | `LM74800QDRRRQ1` / LM7480-Q1 | Vehicle reverse-polarity, reverse-current, inrush, and overvoltage control with back-to-back N-FETs | ACTIVE; AEC-Q100; 3–65 V, −65 V reverse input, WSON-12; datasheet Rev. C | [Product page](https://www.ti.com/product/LM7480-Q1), [datasheet](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf) |
| Texas Instruments | `LM5176QPWPRQ1` | 12 V vehicle to nominal-24 V four-switch synchronous buck-boost controller | ACTIVE; AEC-Q100; 4.2–55 V operating, 60 V maximum, HTSSOP-28; datasheet Rev. B | [Product page](https://www.ti.com/product/LM5176-Q1), [datasheet](https://www.ti.com/lit/ds/symlink/lm5176-q1.pdf) |
| Texas Instruments | `LM51772-Q1` | Newer four-switch comparison candidate | ACTIVE; 55 V, optional I²C, VQFN-40; not selected because its added complexity is unnecessary for a fixed 24 V rail | [Product page](https://www.ti.com/product/LM51772-Q1) |
| Texas Instruments | `CSD19531Q5A` | Provisional 100 V N-MOSFET class for vehicle protection, conversion, and ORing | ACTIVE; 6.4 mΩ max at 10 V, 37 nC typical Qg, 5 × 6 mm SON | [Product page](https://www.ti.com/product/CSD19531Q5A), [datasheet](https://www.ti.com/lit/ds/symlink/csd19531q5a.pdf) |
| Texas Instruments | `TPS259470ARPWR` / TPS25947 | Nano 5 V current limiting, inrush control, and true reverse-current blocking | ACTIVE; 2.7–23 V, 5.5 A, 28 mΩ typical; datasheet Rev. C, May 2026 | [Product page](https://www.ti.com/product/TPS25947), [datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf) |
| Bourns | `SM8S24CA-Q` | Vehicle high-energy bidirectional TVS | Automotive/AEC-Q101 series; 24 V standoff, 38.9 V clamp class, 6.6 kW, DO-218; availability observed through authorized distribution | [Manufacturer datasheet](https://www.bourns.com/docs/product-datasheets/sm8s-q.pdf) |
| Coilcraft | `XAL7030-682MEC` class | Provisional buck-boost inductor | Current AEC-Q200 shielded series; 6.8 µH, 15 A typical Isat, 6.8 A 40 °C-rise Irms; manufacturer showed orderable stock | [Manufacturer series page](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal7030/) |
| Molex | `43045-0200` / `43025-0200` | Provisional keyed vehicle-evaluation connector pair | Micro-Fit 3.0, 2 circuits; header 8.5 A/contact, −40 to 105 °C, right-angle THT; not sealed/automotive-qualified | [Header](https://www.molex.com/en-us/products/part-detail/430450200), [housing](https://www.molex.com/en-us/products/part-detail/430250200) |
| Littelfuse | 451 series, 5 A class | Compact vehicle-branch fuse comparison | Current series; exact 5 A time-delay/serviceable implementation remains a schematic/mechanical choice because 451 is very-fast acting | [Manufacturer series page](https://www.littelfuse.com/products/fuses-overcurrent-protection/fuses/surface-mount-fuses/451) |

## Connectors and cables

Checked 2026-09-14.

| Manufacturer | Part number | Function | Documented configuration | Source |
|---|---|---|---|---|
| Molex | `505110-4096` | Panel LCD connector | 40 position, 0.50 mm, bottom contact, front flip, 1.90 mm height | [Manufacturer page](https://www.molex.com/en-us/products/part-detail/5051104096) |
| Molex | `0150200429` | Panel LCD FFC candidate | 40 circuit, 0.50 mm, type A same-side contacts, 76 mm | [Manufacturer page](https://www.molex.com/en-us/products/part-detail/150200429) |
| Molex | `0150200431` | Panel LCD FFC candidate | 40 circuit, 0.50 mm, type A same-side contacts, 102 mm | [Manufacturer page](https://www.molex.com/en-us/products/part-detail/150200431) |
| Amphenol Communications Solutions | `SFW15R-2STE1LF` | Nano DSI connector candidate | ACTIVE; 15 position, 1.00 mm, top contact, side-entry SMT ZIF | [Manufacturer page](https://www.amphenol-cs.com/product/sfw15r2ste1lf.html) |
| Hirose Electric | `FH12-8S-0.5SH(55)` | Touch connector candidate | 8 position, 0.50 mm, bottom contact, front ZIF, 2.0 mm height | [Manufacturer page](https://www.hirose.com/product/p/CL0586-0744-5-55) |
| Samtec | `SSW-113-02-G-D` family/configuration | Nano stacking sockets | 2 x 13, 2.54 mm; exact tail/body option remains mechanical | [Manufacturer family/configuration page](https://www.samtec.com/products/ssw-113-02-g-d-ll) |

Manufacturer electrical and mechanical documents control the design. Distributor availability is a procurement snapshot and must be rechecked before schematic freeze, prototype purchasing, and assembly release.
