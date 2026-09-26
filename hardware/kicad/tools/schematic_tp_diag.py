#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import kicad_sch_api as ksa

ROOT = Path(__file__).resolve().parents[3]
SCH = ROOT / "hardware" / "kicad" / "ESP32-P4 Display Development Daughterboard.kicad_sch"
OUT = ROOT / "placement-artifacts" / "tp-schematic-diagnostic.json"
TPS = "TP103 TP201 TP202 TP301 TP302 TP501 TP502 TP503 TP504 TP601 TP602 TP603 TP604 TP605 TP606 TP607 TP801 TP802 TP803 TP804 TP805 TP901 TP902 TP903 TP904 TP905 TP1001 TP1002 TP1003 TP1004 TP1005 TP1006".split()


def serial(value, depth=0):
    if depth > 4:
        return repr(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple, set)):
        return [serial(v, depth + 1) for v in value]
    if isinstance(value, dict):
        return {str(k): serial(v, depth + 1) for k, v in value.items()}
    if hasattr(value, "__dict__"):
        return {"class": type(value).__name__, **{k: serial(v, depth + 1) for k, v in vars(value).items() if not k.startswith("_")}}
    return repr(value)


sch = ksa.Schematic.load(str(SCH))
report = {
    "schematic_class": type(sch).__name__,
    "schematic_attrs": sorted(a for a in dir(sch) if not a.startswith("_")),
    "collection_attrs": {},
    "testpoints": {},
}
for name in ("wires", "labels", "global_labels", "hierarchical_labels", "junctions", "components"):
    obj = getattr(sch, name, None)
    if obj is not None:
        report["collection_attrs"][name] = sorted(a for a in dir(obj) if not a.startswith("_"))

for ref in TPS:
    comp = sch.components.get(ref)
    rec = {"component": serial(comp)}
    try:
        pos = sch.get_component_pin_position(ref, "1")
    except Exception as exc:
        pos = None
        rec["pin_error"] = repr(exc)
    rec["pin_position"] = serial(pos)
    if pos is not None:
        try:
            wires = list(sch.wires.get_by_point((pos.x, pos.y), tolerance=0.02))
        except Exception as exc:
            wires = []
            rec["wire_error"] = repr(exc)
        rec["wires"] = [serial(w) for w in wires]
        for name in ("labels", "global_labels", "hierarchical_labels", "junctions"):
            collection = getattr(sch, name, None)
            if collection is None:
                continue
            matches = []
            try:
                for item in collection:
                    ipos = getattr(item, "position", None)
                    if ipos is not None and abs(float(ipos.x)-float(pos.x)) < 0.03 and abs(float(ipos.y)-float(pos.y)) < 0.03:
                        matches.append(serial(item))
            except Exception as exc:
                rec[name + "_error"] = repr(exc)
            rec[name] = matches
    report["testpoints"][ref] = rec

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"components": len(list(sch.components)), "testpoints": len(report["testpoints"]), "out": str(OUT)}, indent=2))
