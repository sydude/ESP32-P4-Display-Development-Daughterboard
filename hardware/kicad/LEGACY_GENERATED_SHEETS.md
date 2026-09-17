# Unreferenced legacy generated sheets

The ten numbered schematic files named from `01_bench_input.kicad_sch` through `10_headers_debug.kicad_sch` are retained as historical snapshots to avoid destructively removing prior project artifacts. They are **not** referenced by the canonical root sheet and are **not** part of the active schematic hierarchy.

The active, authoritative native KiCad 10 hierarchy is:

- `ESP32-P4 Display Development Daughterboard.kicad_sch`
- `01_power.kicad_sch`
- `02_display_power_backlight.kicad_sch`
- `03_interfaces_nano.kicad_sch`

`tools/generate_schematic.py` is likewise retained only as a historical implementation record and exits without writing files. Do not use the legacy sheets or generator as a design source.
