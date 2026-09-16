# Canonical KiCad project

This directory contains the canonical KiCad project for the ESP32-P4 Displayman Development Daughterboard. The existing project names are preserved.

## Current phase

The schematic is populated for Phase 2 review as a root sheet plus ten hierarchical sheets. The PCB file remains the original unpopulated project; layout has not begun.

The generated schematic is reproducible from:

```sh
python3 hardware/kicad/tools/generate_schematic.py
```

The script validates physical pin sets, connector mappings, key IC pin/net assignments, unique references, and BOM generation before writing the KiCad files. Generated sheets and `Phase2.kicad_sym` are committed so the project opens without running the script. If a generated sheet is edited, update the generator as the authoritative source and regenerate the complete hierarchy.

## Verification commands

These checks were run with KiCad 9.0.9:

```sh
kicad-cli sch export netlist -o /tmp/phase2.net "hardware/kicad/ESP32-P4 Display Development Daughterboard.kicad_sch"
kicad-cli sch export pdf -o /tmp/phase2.pdf "hardware/kicad/ESP32-P4 Display Development Daughterboard.kicad_sch"
kicad-cli sch erc --severity-all -o hardware/kicad/erc-report.txt "hardware/kicad/ESP32-P4 Display Development Daughterboard.kicad_sch"
kicad-cli sch erc --severity-error --exit-code-violations -o /tmp/phase2-errors.rpt "hardware/kicad/ESP32-P4 Display Development Daughterboard.kicad_sch"
```

The current result is zero ERC errors and ten warnings. Every warning is an intentionally unresolved `Phase2:` footprint. See `docs/design-notes/schematic-review.md` and `Phase2.pretty/README.md` before PCB placement.

## Phase boundary

Do not begin PCB layout until:

1. the schematic receives an independent electrical review;
2. the physical connector/cable presentation is inspected;
3. the ten custom manufacturer-specific footprints are created and checked;
4. the owner separately authorizes PCB layout.
