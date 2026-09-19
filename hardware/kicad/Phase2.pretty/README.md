# Phase2 project-local footprints

These committed KiCad 10 footprints cover manufacturer-specific packages and cases where the stock KiCad footprint/model pair was incomplete for the selected component.

| Footprint | Basis |
|---|---|
| `Amphenol_SFW15R-2STE1LF` | Amphenol drawing 10172241 Rev. A; official manufacturer STEP |
| `Bourns_DO-218AB` | Bourns SM8S-Q package and recommended-land drawing |
| `L_Bourns_SRP1038A_10.0x10.0mm` | KiCad land pattern checked against Bourns SRP1038A dimensions; local model link |
| `Molex_505110-4096` | Molex sales drawing; official manufacturer STEP |
| `Molex_Micro-Fit_3.0_43045-0218_2x01-1MP_P3.00mm_Vertical` | KiCad land pattern checked against Molex drawing; local model link; `MP` is the mechanical hold-down pad |
| `Texas_DRR0012E_WSON-12_3x3mm_P0.5mm_EP1.3x2.5mm` | TI DRR0012E package drawing |
| `Texas_DYY0014A_TSOT-23-14` | TI DYY0014A package drawing |
| `Texas_PWP0028V_TSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP3.4x9.7mm_Mask2.94x5.62mm_ThermalVias` | KiCad/TI PWP0028V land pattern with exposed-pad mask and thermal vias; local model link |
| `Texas_RNP0030B_WQFN-30-1EP_4x6mm_P0.5mm_EP1.8x4.5mm_ThermalVias` | KiCad/TI RNP0030B land pattern with exposed-pad thermal vias; local model link |
| `Texas_RPW0010A_VQFN-HR-10_2x2mm` | TI RPW0010A package drawing |

Manufacturer drawings remain controlling. Connector contact presentation and all critical custom land patterns require an independent review before placement freeze.
