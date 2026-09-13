# References

This index records the source documents and manufacturer links used by the project. Third-party PDFs are not stored in this repository unless deliberately approved for inclusion.

## User-supplied project sources

| ID | Manufacturer / source | Document | Revision / identity | Repository status |
|---|---|---|---|---|
| S1 | Displayman (SZ) Technology Co., Ltd. | `KD068HDFID009-C009A` module datasheet | v1.0, 2024-11-25, 40 pages; SHA-256 `4c8394ac…03bcf` | External source; not committed |
| S2 | Displayman | `KD068HDFID009 -2LANE.txt` initialization file | SHA-256 `81ec9ab8…e6872c` | External source; not committed |
| S3 | Waveshare | `ESP32-P4-NANO-schematic.pdf` | PDF created 2024-10-25; SHA-256 `1e57b31f…10de1` | External source; not committed |

The abbreviated hashes above match the Phase 1 PRD. Full source-file hashes should be recorded when the source package is deliberately placed under controlled project storage.

## Platform documentation

Checked 2026-09-13.

| Manufacturer | Document | Revision / status | Source |
|---|---|---|---|
| Espressif Systems | ESP32-P4 Series Datasheet | v0.7, 2026-07-14 | [Manufacturer documentation](https://documentation.espressif.com/esp32-p4_datasheet_en.html) |
| Espressif Systems | ESP-IDF MIPI DSI LCD API | Current online documentation as checked | [Manufacturer documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/peripherals/lcd/dsi_lcd.html) |
| Espressif Systems | ESP32-P4 Hardware Design Guidelines | Current online documentation as checked | [Manufacturer documentation](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32p4/schematic-checklist-esp32p4.html) |

## Candidate component manufacturer pages

Checked 2026-09-13. Candidate status is controlled by the PRD; inclusion here does not authorize schematic capture or substitution.

| Manufacturer | Part number / family | Function | Source |
|---|---|---|---|
| Texas Instruments | LM76003RNPR | 24 V to 5 V buck regulator | [LM76003](https://www.ti.com/product/LM76003) |
| Texas Instruments | TPS92511DDA | Constant-current backlight driver | [TPS92511](https://www.ti.com/product/TPS92511) |
| Texas Instruments | LM3880MF-1AA/NOPB | Power sequencer | [LM3880](https://www.ti.com/product/LM3880) |
| Texas Instruments | TPS3808G01DBVR | Power-fail supervisor | [TPS3808](https://www.ti.com/product/TPS3808) |
| Texas Instruments | TPS22919DCKR | VCI load switch | [TPS22919](https://www.ti.com/product/TPS22919) |
| Texas Instruments | TLV75533PDBVR / TLV75518PDBVR | 3.3 V / 1.8 V LDOs | [TLV755P](https://www.ti.com/product/TLV755P) |
| Texas Instruments | PCA9306DCTR | I²C domain isolation / translation | [PCA9306](https://www.ti.com/product/PCA9306) |
| Texas Instruments | SN74LVC1G07DBVR | LCD reset buffer | [SN74LVC1G07](https://www.ti.com/product/SN74LVC1G07) |
| Texas Instruments | TPD6E05U06RVZR | MIPI ESD protection | [TPD6E05U06](https://www.ti.com/product/TPD6E05U06) |
| Texas Instruments | TPD4E05U06DQAR | Touch-interface ESD protection | [TPD4E05U06](https://www.ti.com/product/TPD4E05U06) |
| Molex | 505110-4096 | 40-position panel LCD connector | [Manufacturer page](https://www.molex.com/en-us/products/part-detail/5051104096) |
| Amphenol Communications Solutions | SFW15R-2STE1LF | 15-position Nano DSI connector candidate | [Manufacturer page](https://www.amphenol-cs.com/product/sfw15r2ste1lf.html) |
| Hirose Electric | FH12-8S-0.5SH(55) | 8-position touch connector candidate | [Manufacturer page](https://www.hirose.com/product/p/CL0586-0744-5-55) |
| Same Sky | PJ-044AH | 24 V barrel jack candidate | [Manufacturer page](https://www.sameskydevices.com/product/interconnect/connectors/dc-power-connectors/jacks/pj-044ah) |
| Littelfuse | SMBJ series / SMBJ30A | Input TVS protection | [Manufacturer page](https://www.littelfuse.com/products/tvs-diodes/surface-mount/smbj) |
| Vishay | SS5P6-M3/86A | Reverse-polarity Schottky diode | [Manufacturer page](https://www.vishay.com/en/product/88721/) |

Manufacturer electrical documentation controls the design. Distributor availability is a procurement snapshot and must be rechecked before schematic freeze and assembly release.
