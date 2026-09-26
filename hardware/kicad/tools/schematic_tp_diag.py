#!/usr/bin/env python3
from __future__ import annotations

import inspect
import json
from pathlib import Path

import kicad_sch_api as ksa

ROOT = Path(__file__).resolve().parents[3]
SCH = ROOT / "hardware" / "kicad" / "ESP32-P4 Display Development Daughterboard.kicad_sch"
OUT = ROOT / "placement-artifacts" / "tp-schematic-diagnostic.json"
TPS = "TP103 TP201 TP202 TP301 TP302 TP501 TP502 TP503 TP504 TP601 TP602 TP603 TP604 TP605 TP606 TP607 TP801 TP802 TP803 TP804 TP805 TP901 TP902 TP903 TP904 TP905 TP1001 TP1002 TP1003 TP1004 TP1005 TP1006".split()


def serial(value, depth=0):
    if depth > 6:
        return repr(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple, set)):
        return [serial(v, depth + 1) for v in value]
    if isinstance(value, dict):
        return {str(k): serial(v, depth + 1) for k, v in value.items()}
    if hasattr(value, "__dict__"):
        return {"class": type(value).__name__, **{k: serial(v, depth + 1) for k, v in vars(value).items()}}
    return repr(value)


sch = ksa.Schematic.load(str(SCH))
report = {
    "schematic_class": type(sch).__name__,
    "schematic_attrs": sorted(a for a in dir(sch) if not a.startswith("_")),
    "collection_attrs": {},
    "method_signatures": {},
    "method_sources": {},
    "testpoints": {},
}
for meth in ("get_component_pin_position", "list_component_pins", "get_net_for_pin"):
    fn = getattr(sch, meth)
    try:
        report["method_signatures"][meth] = str(inspect.signature(fn))
    except Exception as exc:
        report["method_signatures"][meth] = repr(exc)
    try:
        report["method_sources"][meth] = inspect.getsource(fn)
    except Exception as exc:
        report["method_sources"][meth] = repr(exc)
for name in ("wires", "labels", "global_labels", "hierarchical_labels", "junctions", "components"):
    obj = getattr(sch, name, None)
    if obj is not None:
        report["collection_attrs"][name] = sorted(a for a in dir(obj) if not a.startswith("_"))

for ref in TPS:
    comp = sch.components.get(ref)
    rec = {
        "component": serial(comp),
        "component_dir": sorted(a for a in dir(comp) if not a.startswith("_")) if comp else [],
    }
    try:
        rec["listed_pins"] = serial(sch.list_component_pins(ref))
    except Exception as exc:
        rec["listed_pins_error"] = repr(exc)
    for pin_arg in ("1", 1):
        key = f"pin_position_{type(pin_arg).__name__}"
        try:
            pos = sch.get_component_pin_position(ref, pin_arg)
        except Exception as exc:
            pos = None
            rec[key + "_error"] = repr(exc)
        rec[key] = serial(pos)
        if pos is not None:
            try:
                rec[key + "_wires_by_point"] = serial(sch.wires.get_by_point((pos.x, pos.y), tolerance=0.02))
            except Exception as exc:
                rec[key + "_wire_error"] = repr(exc)
    try:
        rec["net"] = serial(sch.get_net_for_pin(ref, "1"))
    except Exception as exc:
        rec["net_error"] = repr(exc)
    report["testpoints"][ref] = rec

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"components": len(list(sch.components)), "testpoints": len(report["testpoints"]), "out": str(OUT)}, indent=2))
