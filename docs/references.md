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
| S9 | Displayman, Anson Ho | Follow-up email and reference LCD timing screenshot | Received 2026-09-15; email SHA-256 `8823097df6d8f23fd516d2b6e0f963860ce33b882156e1e74eb6324d2f1189f4`; screenshot SHA-256 `0e07dbbabf7c044b3f3cbf885d786e36a1ac6d44cc7af4ac6fe7aa517a8977d3` | User deliberately committed [email text](design-notes/email%20response%20from%20displayman%20on%209-15-2026.md) and [timing screenshot](design-notes/email%20response%20from%20displayman%20on%209-15-2026%20%5BIMAGE%5D.jpg) in `e98d2188f5f2b2ff797b6d45c06f2300e67c91f1`; analyzed in PRD v0.5 |

Abbreviated hashes match `docs/PRD.md`. Full hashes should be retained in controlled project records if the source package is deliberately archived.

## Platform and board documentation

Checked through 2026-09-15.

| Manufacturer | Document | Revision / date | Source |
|---|---|---|---|
| Espressif Systems | ESP32-P4 Series Datasheet | v0.7, 2026-07-14 | [Manufacturer documentation](https://documentation.espressif.com/esp32-p4_datasheet_en.html) |
| Espressif Systems | ESP32-P4 Hardware Design Guidelines | v1.9, 2026-07-21 | [Manufacturer PDF](https://documentation.espressif.com/esp-hardware-design-guidelines/en/latest/esp32p4/esp-hardware-design-guidelines-en-master-esp32p4.pdf) |
| Espressif Systems | ESP-IDF MIPI DSI LCD API | Current online documentation | [Manufacturer documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/peripherals/lcd/dsi_lcd.html) |
| Waveshare | ESP32-P4-NANO product documentation | Current online documentation; S3 remains the electrical source | [Manufacturer documentation](https://www.waveshare.com/wiki/ESP32-P4-NANO) |

## Display-module corroboration and evidence limits

Checked 2026-09-15. These public listings are secondary to the exact-module datasheet, initialization file, and direct Displayman correspondence. They support product identity/family plausibility only and do not establish a GC9703C HS lane-rate limit.

| Evidence class | Source | Supported observation | Explicit limitation |
|---|---|---|---|
| Manufacturer public listing | Displayman, KD068HDFID009-C009A | Exact module is listed as 480 × 1280, two-lane MIPI display, I²C touch, GT9271 | Does not publish D-PHY HS operating rate or controller maximum; [manufacturer page](https://displayman.com/bar-type-tft-lcd-displays/) |
| Third-party exact-family listing | Startek/TFT-TFT, KD068HDFID009 | Base module is listed as GC9703C, 480 × 1280, two-lane MIPI, 40-pin, 6S4P/19.2 V/240 mA | Not a substitute for exact C009A controlled documentation; [product page](https://en.tft-tft.com/product/1658-KD068HDFID009-6.8-inch-480x1280-2-Lane-MIPI-interface-GC9703C-Bar-Type-TFT-high-brightness-IPS-LCD-Module.html) |
| Third-party sibling-module listing | Startek/TFT-TFT, KD068HDFID020 | Closely related 480 × 1280 / 60.19 × 160.51 mm GC9703C platform is offered with 3/4-lane MIPI | Sibling evidence only; cannot prove C009A rate capability; [product page](https://www.tft-tft.com/product/detail?id=899) |

No authoritative independent GC9703C datasheet or manufacturer source substantiating the previously stated 500 Mb/s/lane maximum was located in this review. Accordingly, 500 Mb/s/lane is recorded as an unverified claim, not as a controller specification; absence of corroboration is not proof of a higher limit.

## Power, sequencing, and interface components

Checked through 2026-09-16. Status is the manufacturer product-page status where shown. `docs/PRD.md` remains controlling; the populated selections and calculations are recorded in `docs/design-notes/schematic-calculations.md`.

| Manufacturer | Part number / family | Function | Status / document | Source |
|---|---|---|---|---|
| Texas Instruments | `LM76003RNPR` | 24 V to 5 V buck | ACTIVE; datasheet Rev. A | [LM76003](https://www.ti.com/product/LM76003) |
| Texas Instruments | `TLV75533PDBVR`, `TLV75528PDBVR`, `TLV75518PDBVR` | Touch 3.3 V / VCI 2.8 V / IOVCC 1.8 V LDOs | ACTIVE/production; datasheet Rev. D | [TLV755P](https://www.ti.com/product/TLV755P) |
| Texas Instruments | `TPS22919DCKR` | VCI load switch | ACTIVE; datasheet Rev. B | [TPS22919](https://www.ti.com/product/TPS22919) |
| Texas Instruments | `LM3880MF-1AA/NOPB` | Candidate three-stage sequencer | ACTIVE; fixed-function candidate | [LM3880](https://www.ti.com/product/LM3880) |
| Texas Instruments | `TPS3808G01DBVR` | Candidate power-fail supervisor | ACTIVE | [TPS3808](https://www.ti.com/product/TPS3808) |
| Texas Instruments | `SN74LVC1G07DBVR` | Open-drain reset buffer with Ioff | ACTIVE; datasheet Rev. AG | [SN74LVC1G07](https://www.ti.com/product/SN74LVC1G07) |
| Texas Instruments | `SN74LVC1G11DCKR` | Three-input hardware backlight-enable gate | ACTIVE; partial-power-down/Ioff behavior | [SN74LVC1G11](https://www.ti.com/product/SN74LVC1G11) |
| Texas Instruments | `PCA9306DCTR` | Original I2C translator candidate | ACTIVE; superseded because it does not isolate INT/RESET | [PCA9306](https://www.ti.com/product/PCA9306) |
| Texas Instruments | `TMUX1574DYYR` / `TMUX1574PWR` | Recommended four-channel powered-off-protected touch switch | ACTIVE; datasheet Rev. C | [TMUX1574](https://www.ti.com/product/TMUX1574) |
| Texas Instruments | `TPD6E05U06RVZR` | Six-channel MIPI ESD | ACTIVE; TPDxE05U06 family | [TPD6E05U06](https://www.ti.com/product/TPD6E05U06) |
| Texas Instruments | `TPD4E05U06DQAR` | Four-channel touch ESD | ACTIVE; TPDxE05U06 family | [TPD4E05U06](https://www.ti.com/product/TPD4E05U06) |
| Texas Instruments | `TPS92511DDA` | Original buck backlight candidate | ACTIVE; superseded as baseline because full-temperature current spread is wider than project ±5% target | [TPS92511](https://www.ti.com/product/TPS92511) |
| Texas Instruments | `TPS922053DYYR` | Preferred 240 mA buck backlight driver | ACTIVE/production; datasheet Rev. B; 4.5–65 V, external 200 mV current sense, 100 ns minimum off-time, fast/hybrid PWM | [TPS922053](https://www.ti.com/product/TPS922053), [datasheet](https://www.ti.com/lit/ds/symlink/tps922053.pdf) |
| Vishay | `IHLP6767GZER680M11` | Selected 68 µH backlight inductor | IHLP-6767GZ-11 commercial low-DCR series; 6.1 A heat-rated and 4.5 A typical saturation current; manufacturer product page/datasheet checked 2026-09-16 | [Manufacturer product page](https://www.vishay.com/en/product/34282/) |
| Vishay | `SS2H10-E3/52T`, `SS34-E3/57T`, `BAT46W-E3-08` | Backlight catch diode, hold-up diode, and LM5176 bootstrap diodes | Current manufacturer families; 100 V bootstrap/catch selections preserve voltage margin | [SS2H10](https://www.vishay.com/en/product/88961/), [SS34](https://www.vishay.com/en/product/88751/), [BAT46W](https://www.vishay.com/en/product/85662/) |
| Murata | `BLM18KG601SN1D` | Backlight-anode EMI bead | 0603, 600 Ω at 100 MHz, 1 A class; headroom/temperature to be verified on prototype | [Manufacturer page](https://www.murata.com/en-us/products/productdetail?partno=BLM18KG601SN1%23) |
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

Checked through 2026-09-16. Automotive/AEC qualification of individual parts does not qualify the assembled evaluation board to ISO 7637 or ISO 16750.

| Manufacturer | Part number / family | Function | Status / validation note | Source |
|---|---|---|---|---|
| Texas Instruments | `LM74800QDRRRQ1` / LM7480-Q1 | Vehicle reverse-polarity, reverse-current, inrush, and overvoltage control with back-to-back N-FETs | ACTIVE; AEC-Q100; 3–65 V, −65 V reverse input, WSON-12; datasheet Rev. C | [Product page](https://www.ti.com/product/LM7480-Q1), [datasheet](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf) |
| Texas Instruments | `LM5176QPWPRQ1` | 12 V vehicle to nominal-24 V four-switch synchronous buck-boost controller | ACTIVE; AEC-Q100; 4.2–55 V operating, 60 V maximum, HTSSOP-28; datasheet Rev. B | [Product page](https://www.ti.com/product/LM5176-Q1), [datasheet](https://www.ti.com/lit/ds/symlink/lm5176-q1.pdf) |
| Texas Instruments | `LM51772-Q1` | Newer four-switch comparison candidate | ACTIVE; 55 V, optional I²C, VQFN-40; not selected because its added complexity is unnecessary for a fixed 24 V rail | [Product page](https://www.ti.com/product/LM51772-Q1) |
| Texas Instruments | `CSD19531Q5A` | Provisional 100 V N-MOSFET class for vehicle protection, conversion, and ORing | ACTIVE; 6.4 mΩ max at 10 V, 37 nC typical Qg, 5 × 6 mm SON | [Product page](https://www.ti.com/product/CSD19531Q5A), [datasheet](https://www.ti.com/lit/ds/symlink/csd19531q5a.pdf) |
| Texas Instruments | `TPS259470ARPWR` / TPS25947 | Nano 5 V current limiting, inrush control, and true reverse-current blocking | ACTIVE; 2.7–23 V, 5.5 A, 28 mΩ typical; datasheet Rev. C, May 2026 | [Product page](https://www.ti.com/product/TPS25947), [datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf) |
| Bourns | `SM8S24CA-Q` | Vehicle high-energy bidirectional TVS | Automotive/AEC-Q101 series; 24 V standoff, 38.9 V clamp class, 6.6 kW, DO-218; availability observed through authorized distribution | [Manufacturer datasheet](https://www.bourns.com/docs/product-datasheets/sm8s-q.pdf) |
| Coilcraft | `XAL7070-153MEC`, `XAL7070-103MEC` | Selected 15 µH LM5176 and 10 µH LM76003 inductors | Current shielded molded series; selected values and current ratings checked in the manufacturer table | [Manufacturer series page](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal7070/) |
| Bourns | `SRP1038A-2R2M` | Vehicle input-filter inductor | Shielded AEC-Q200 SRP1038A family; 2.2 µH, 8 A class | [Manufacturer product page](https://www.bourns.com/products/magnetic-products/power-inductors-smd-high-current-shielded/product/SRP1038A) |
| Molex | `43045-0218` / `43025-0200` | Selected keyed vehicle-evaluation connector pair | Micro-Fit 3.0, two circuits; vertical SMT board header with mating receptacle; not sealed/automotive-qualified | [Header](https://www.molex.com/en-us/products/part-detail/430450218), [housing](https://www.molex.com/en-us/products/part-detail/430250200) |
| Littelfuse / Keystone | `0297005.WXNV` / `3568` | Selected serviceable vehicle-branch fuse and PCB holder | 5 A MINI blade fuse in a through-hole PCB holder | [Littelfuse 297 series](https://www.littelfuse.com/products/fuses-overcurrent-protection/fuses/automotive-passenger-car/blade-fuses/297), [Keystone 3568](https://www.keyelco.com/product.cfm/product_id/14138) |

## Connectors and cables

Checked through 2026-09-16.

| Manufacturer | Part number | Function | Documented configuration | Source |
|---|---|---|---|---|
| Molex | `505110-4096` | Panel LCD connector | 40 position, 0.50 mm, bottom contact, front flip, 1.90 mm height | [Manufacturer page](https://www.molex.com/en-us/products/part-detail/5051104096) |
| Molex | `0150200429` | Panel LCD FFC candidate | 40 circuit, 0.50 mm, type A same-side contacts, 76 mm | [Manufacturer page](https://www.molex.com/en-us/products/part-detail/150200429) |
| Molex | `0150200431` | Panel LCD FFC candidate | 40 circuit, 0.50 mm, type A same-side contacts, 102 mm | [Manufacturer page](https://www.molex.com/en-us/products/part-detail/150200431) |
| Amphenol Communications Solutions | `SFW15R-2STE1LF` | Nano DSI connector candidate | ACTIVE; 15 position, 1.00 mm, top contact, side-entry SMT ZIF | [Manufacturer page](https://www.amphenol-cs.com/product/sfw15r2ste1lf.html) |
| Hirose Electric | `FH12-8S-0.5SH(55)` | Touch connector candidate | 8 position, 0.50 mm, bottom contact, front ZIF, 2.0 mm height | [Manufacturer page](https://www.hirose.com/product/p/CL0586-0744-5-55) |
| Samtec | `SSW-113-02-G-D` family/configuration | Nano stacking sockets | 2 x 13, 2.54 mm; exact tail/body option remains mechanical | [Manufacturer family/configuration page](https://www.samtec.com/products/ssw-113-02-g-d-ll) |

Manufacturer electrical and mechanical documents control the design. Distributor availability is a procurement snapshot and must be rechecked before schematic freeze, prototype purchasing, and assembly release.
