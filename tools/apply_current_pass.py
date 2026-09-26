#!/usr/bin/env python3
"""Apply the focused schematic-metadata and KiCad-native parked-block placement pass."""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KDIR = ROOT / "hardware" / "kicad"
SCH = KDIR / "ESP32-P4 Display Development Daughterboard.kicad_sch"
PCB = KDIR / "ESP32-P4 Display Development Daughterboard.kicad_pcb"
SYMLIB = KDIR / "Phase2.kicad_sym"
BOM = ROOT / "hardware" / "BOM.csv"

TESTPOINTS = [
    "TP103",
    "TP201", "TP202",
    "TP301", "TP302",
    "TP501", "TP502", "TP503", "TP504",
    "TP601", "TP602", "TP603", "TP604", "TP605", "TP606", "TP607",
    "TP801", "TP802", "TP803", "TP804", "TP805",
    "TP901", "TP902", "TP903", "TP904", "TP905",
    "TP1001", "TP1002", "TP1003", "TP1004", "TP1005", "TP1006",
]
DNP = {"R505", "C907", "R907", "R1005"}

METADATA = {
    "D201": {"Datasheet": "https://www.bourns.com/docs/product-datasheets/sm8s-q.pdf"},
    "L201": {"Datasheet": "https://www.bourns.com/docs/product-datasheets/srp1038a.pdf"},
    "J201": {
        "Datasheet": "https://www.molex.com/en-us/products/part-detail/430450218",
        "Description": "Molex Micro-Fit 3.0, 2-circuit vertical SMT header, 3.00 mm pitch; vehicle-power input",
    },
    "J701": {
        "Datasheet": "https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/10172241.pdf",
        "Description": "15-position 1.00 mm-pitch top-contact FFC/FPC connector for Nano DSI",
    },
    "J702": {
        "Datasheet": "https://www.molex.com/en-us/products/part-detail/5051104096",
        "Description": "Molex 505110-4096, 40-position 0.50 mm-pitch bottom-contact FPC connector for Displayman LCD",
    },
    "J801": {
        "Value": "68710814022",
        "Manufacturer": "Würth Elektronik",
        "MPN": "68710814022",
        "Datasheet": "https://www.we-online.com/components/products/datasheet/68710814022.pdf",
        "Description": "Würth Elektronik 68710814022, 8-position 0.50 mm-pitch top-contact ZIF FPC connector for Displayman touch tail",
        "Footprint": "Phase2:Wurth_68710814022",
    },
}

MOSFETS = ["Q201", "Q202", "Q301", "Q302", "Q303", "Q304"]
MOSFET_META = {
    "Value": "CSD19531Q5A",
    "Manufacturer": "Texas Instruments",
    "MPN": "CSD19531Q5A",
    "Datasheet": "https://www.ti.com/lit/ds/symlink/csd19531q5a.pdf",
    "Description": "100 V N-channel MOSFET, TI DQJ/VSONP-8; exposed drain pad is not a separate pin",
    "Footprint": "Phase2:Texas_DQJ0008A_VSONP-8",
}

GROUPS = {
    "VEHICLE_INPUT_PROTECTION": "J201 F201 L201 C201 C202 D201 R201 C204 Q201 Q202 U201 C205 C206 C207 R202 R203 R204 R205 R206 C203".split(),
    "LM5176_24V": "C309 C310 Q301 Q302 L301 Q303 Q304 C312 C313 C311 R301 R302 R309 C301 U301 C307 D301 C308 D302 C306 R303 R304 C302 C303 R305 C304 C305 R306 R307 R308".split(),
    "LM76003_5V_EFUSE": "C505 C506 C507 U501 C501 L501 C503 C508 C509 C510 C511 C502 C504 R501 R502 R503 R504 R510 C513 U502 C514 C512 R505 R506 R507 R508 R509 R511 R512 J501".split(),
    "DISPLAY_SEQUENCE": "D601 R601 C601 U601 R602 R603 C607 C602 C603 R604 U602 R605 R606 R607 R608 R609 D602 U603 C604 U604 C605 U605 C606 U606 U607 U608 R610 R611".split(),
    "BACKLIGHT_DRIVER": "C901 U901 C902 C903 D901 L901 R901 R902 R903 C904 R904 R905 C906 C907 R906 R907 R908 R909 U902 J901 R910 FB901 C905 C908".split(),
}

PLACEMENT = {
    "J201": (-82.0, -50.0, 0), "F201": (-73.0, -44.85, 180), "L201": (-56.0, -44.85, 0),
    "C201": (-49.5, -41.5, 90), "C202": (-48.0, -49.5, 0), "D201": (-44.0, -35.0, 90),
    "R201": (-55.0, -34.0, 90), "C204": (-51.5, -34.0, 90), "Q201": (-37.0, -45.0, 0),
    "Q202": (-29.0, -45.0, 180), "U201": (-33.0, -55.0, 0), "C205": (-29.2, -51.6, 90),
    "C206": (-29.0, -58.5, 90), "R206": (-25.5, -54.0, 90), "C207": (-22.5, -54.0, 90),
    "R202": (-39.0, -57.0, 90), "R203": (-41.8, -57.0, 90), "R204": (-39.0, -61.0, 90),
    "R205": (-41.8, -61.0, 90), "C203": (-17.0, -45.0, 0),

    "C309": (13.0, -48.0, 0), "C310": (20.0, -42.0, 90), "Q301": (28.0, -40.0, -90),
    "Q302": (28.0, -50.0, -90), "L301": (43.0, -45.0, 0), "Q303": (58.0, -40.0, -90),
    "Q304": (58.0, -50.0, -90), "C312": (66.0, -41.5, 90), "C313": (70.5, -41.5, 90),
    "C311": (77.0, -48.0, 0), "R301": (28.0, -59.0, 90), "U301": (45.0, -60.0, -90),
    "C307": (34.0, -55.5, 0), "D301": (34.0, -60.0, 90), "C308": (55.0, -55.5, 0),
    "D302": (56.0, -60.0, 90), "C306": (46.0, -54.5, 90), "R302": (35.0, -63.5, 90),
    "R309": (38.0, -63.5, 90), "C301": (36.5, -67.0, 90), "C303": (41.0, -68.0, 90),
    "C302": (44.0, -68.0, 90), "R303": (47.0, -68.0, 90), "R304": (50.0, -68.0, 90),
    "R305": (53.0, -68.0, 90), "C304": (53.0, -71.2, 90), "C305": (56.0, -68.0, 90),
    "R306": (59.0, -68.0, 90), "R307": (62.0, -68.0, 90), "R308": (41.0, -55.0, 90),

    "C505": (-144.0, -48.0, 90), "C506": (-144.0, -55.0, 90), "C507": (-137.0, -51.5, 90),
    "U501": (-132.0, -52.0, 180), "C501": (-127.0, -48.0, 90), "L501": (-124.0, -52.0, 0),
    "C503": (-118.0, -52.0, 0), "C508": (-113.0, -48.0, 90), "C509": (-113.0, -55.0, 90),
    "C510": (-106.0, -48.0, 0), "C511": (-106.0, -55.0, 0), "C502": (-133.0, -44.0, 90),
    "C504": (-129.5, -44.0, 90), "R501": (-123.0, -43.0, 0), "R502": (-119.5, -43.0, 0),
    "R503": (-138.0, -43.0, 90), "R504": (-141.0, -43.0, 90), "R510": (-116.0, -43.0, 90),
    "C513": (-112.0, -31.0, 0), "U502": (-107.0, -31.0, 0), "C514": (-102.0, -31.0, 0),
    "J501": (-95.5, -31.0, 0), "C512": (-105.0, -26.5, 90), "R505": (-112.0, -26.5, 90),
    "R506": (-109.0, -26.5, 90), "R507": (-114.5, -34.5, 90), "R508": (-111.5, -34.5, 90),
    "R509": (-100.0, -26.5, 90), "R511": (-108.0, -36.0, 90), "R512": (-105.0, -36.0, 90),

    "D601": (101.0, 9.0, 0), "R601": (108.0, 9.0, 0), "C601": (116.0, 9.0, 0),
    "U601": (104.0, 21.0, 0), "R602": (99.0, 19.0, 90), "R603": (99.0, 23.0, 90),
    "C607": (101.5, 25.0, 90), "C602": (108.0, 24.0, 90), "C603": (108.0, 19.0, 90),
    "R604": (111.0, 24.0, 90), "U602": (116.0, 30.0, 0), "R605": (110.0, 29.0, 90),
    "R606": (107.0, 32.0, 90), "R607": (122.0, 27.0, 90), "R608": (122.0, 31.0, 90),
    "R609": (122.0, 35.0, 90), "D602": (110.0, 36.0, 0), "U603": (101.0, 42.0, 0),
    "C604": (106.0, 42.0, 90), "U604": (113.0, 42.0, 0), "C605": (118.0, 42.0, 90),
    "U605": (125.0, 42.0, 0), "C606": (130.0, 42.0, 90), "U606": (101.0, 49.0, 0),
    "U607": (109.0, 49.0, 0), "U608": (117.0, 49.0, 0), "R610": (124.0, 48.0, 90),
    "R611": (128.0, 48.0, 90),

    "C901": (251.0, 91.0, 90), "U901": (260.0, 92.0, 0), "C902": (256.5, 90.0, 90),
    "C903": (256.5, 95.0, 90), "D901": (265.0, 87.0, 180), "L901": (273.0, 92.0, 0),
    "R901": (284.0, 89.5, 180), "R902": (284.0, 94.5, 180), "R903": (267.0, 98.0, 90),
    "C904": (270.0, 98.0, 90), "R904": (255.0, 101.0, 90), "R905": (258.0, 104.0, 90),
    "C906": (261.0, 104.0, 90), "C907": (264.0, 104.0, 90), "R906": (255.0, 107.0, 90),
    "R907": (258.0, 107.0, 90), "R908": (261.0, 107.0, 90), "R909": (264.0, 107.0, 90),
    "U902": (257.0, 113.0, 0), "J901": (265.0, 113.0, 90), "R910": (291.0, 92.0, 0),
    "FB901": (299.0, 87.0, 0), "C905": (303.0, 92.0, 90), "C908": (308.0, 92.0, 90),
}


def natural_key(ref: str):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", ref)]


def prop(component, name: str) -> str:
    try:
        value = component.get_property(name)
        if isinstance(value, str): return value
        if value is not None and hasattr(value, "value"): return str(value.value)
    except Exception: pass
    try:
        raw = component.properties.get(name)
        if isinstance(raw, dict): return str(raw.get("value", ""))
        if isinstance(raw, str): return raw
    except Exception: pass
    return ""


def set_prop(component, name: str, value: str):
    try: component.set_property(name, value); return
    except Exception: pass
    try: component.add_property(name, value); return
    except Exception as exc: raise RuntimeError(f"Could not set {component.reference}.{name}: {exc}")


def patch_project_symbol_library(j801_lib_id: str):
    name = j801_lib_id.split(":", 1)[-1]
    text = SYMLIB.read_text(); token = f'(symbol "{name}"'; start = text.find(token)
    if start < 0: raise RuntimeError(f"J801 library symbol {name} not found")
    depth = 0; quoted = False; escaped = False; end = None
    for i in range(start, len(text)):
        c = text[i]
        if quoted:
            if escaped: escaped = False
            elif c == "\\": escaped = True
            elif c == '"': quoted = False
        else:
            if c == '"': quoted = True
            elif c == '(': depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0: end = i + 1; break
    if end is None: raise RuntimeError("Unbalanced J801 library symbol")
    block = text[start:end]; values = METADATA["J801"]
    for field in ("Value", "Footprint", "Datasheet", "Description", "Manufacturer", "MPN"):
        value = values[field]; pattern = re.compile(r'(\(property\s+"' + re.escape(field) + r'"\s+")[^"]*(")')
        if pattern.search(block): block = pattern.sub(lambda m: m.group(1) + value + m.group(2), block, count=1)
        else:
            insertion = f'\n\t\t(property "{field}" "{value}"\n\t\t\t(at 0 0 0)\n\t\t\t(effects (font (size 1.27 1.27)) hide)\n\t\t)'
            block = block[:-1] + insertion + "\n\t)"
    SYMLIB.write_text(text[:start] + block + text[end:])


def sheet_name(ref: str) -> str:
    m = re.search(r"\d+", ref); n = int(m.group()) if m else 0
    if 200 <= n < 600: return "Power"
    if 600 <= n < 700 or 900 <= n < 1000: return "Display Power & Backlight"
    return "Interfaces & Nano"


def run_schematic():
    from kicad_sch_api import Schematic, get_symbol_cache
    cache = get_symbol_cache(); cache.add_library_path(str(SYMLIB))
    schematic = Schematic.load(str(SCH)); before = {c.reference for c in schematic.components}
    missing = sorted(set(TESTPOINTS) - before, key=natural_key)
    if missing: raise RuntimeError(f"Missing schematic test points: {missing}")
    for ref in TESTPOINTS:
        component = schematic.components.get(ref)
        if component is None: raise RuntimeError(f"Missing component {ref}")
        schematic.components.remove_component(component)
    for ref, fields in METADATA.items():
        c = schematic.components.get(ref)
        if c is None: raise RuntimeError(f"Missing metadata target {ref}")
        for name, value in fields.items(): set_prop(c, name, value)
    for ref in MOSFETS:
        c = schematic.components.get(ref)
        if c is None: raise RuntimeError(f"Missing MOSFET {ref}")
        for name, value in MOSFET_META.items(): set_prop(c, name, value)
    j801 = schematic.components.get("J801"); patch_project_symbol_library(str(j801.lib_id))
    schematic.save()

    check = Schematic.load(str(SCH)); after = {c.reference for c in check.components}
    leftovers = sorted(set(TESTPOINTS) & after, key=natural_key)
    if leftovers: raise RuntimeError(f"Test points remain in schematic: {leftovers}")
    for ref in MOSFETS:
        c = check.components.get(ref)
        if prop(c, "Footprint") != MOSFET_META["Footprint"]: raise RuntimeError(f"{ref} footprint mismatch")
        if "DQK" in json.dumps(c.to_dict()): raise RuntimeError(f"{ref} retains DQK metadata")
    j801 = check.components.get("J801")
    if prop(j801, "MPN") != "68710814022" or "top-contact" not in prop(j801, "Description"):
        raise RuntimeError("J801 metadata correction did not persist")

    rows=[]
    for c in check.components:
        ref=str(c.reference); footprint=str(c.footprint or prop(c,"Footprint"))
        if not ref or ref.startswith("#") or not footprint or not getattr(c,"on_board",True): continue
        rows.append({"Reference":ref,"Value":str(c.value),"Manufacturer":prop(c,"Manufacturer"),"MPN":prop(c,"MPN"),
                     "Footprint":footprint,"DNP":"DNP" if ref in DNP else "POP","Sheet":sheet_name(ref),"Description":prop(c,"Description")})
    rows.sort(key=lambda row:natural_key(row["Reference"])); refs={r["Reference"] for r in rows}
    # The PCB has 167 footprints after deletion: 165 schematic components plus
    # board-only mounting holes H101/H102, which correctly do not appear in BOM.csv.
    if len(rows) != 165: raise RuntimeError(f"Expected 165 BOM rows plus two board-only mounting holes, found {len(rows)}")
    if refs & set(TESTPOINTS): raise RuntimeError("Test points remain in BOM")
    if not DNP <= refs: raise RuntimeError(f"Missing retained DNP parts: {sorted(DNP-refs)}")
    with BOM.open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=["Reference","Value","Manufacturer","MPN","Footprint","DNP","Sheet","Description"])
        w.writeheader(); w.writerows(rows)
    report={"removed":TESTPOINTS,"component_count_before":len(before),"component_count_after":len(after),"bom_rows":len(rows),
            "board_only_footprints":["H101","H102"],
            "j801":{k:prop(check.components.get("J801"),k) for k in ("Value","Manufacturer","MPN","Datasheet","Description","Footprint")},
            "mosfets":{r:{k:prop(check.components.get(r),k) for k in ("Value","Manufacturer","MPN","Datasheet","Description","Footprint")} for r in MOSFETS}}
    out=ROOT/"audit-output"; out.mkdir(exist_ok=True); (out/"schematic-apply.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps(report,indent=2,ensure_ascii=False))


def mm(value: float):
    import pcbnew
    return pcbnew.FromMM(value)


def position_signature(fp):
    return (round(fp.GetPosition().x/1e6,6),round(fp.GetPosition().y/1e6,6),round(fp.GetOrientationDegrees(),6),fp.IsFlipped())


def track_signature(board):
    sig=[]
    for item in board.GetTracks():
        entry=[type(item).__name__,item.GetNetname(),item.GetLayerName()]
        for meth in ("GetStart","GetEnd"):
            if hasattr(item,meth):
                p=getattr(item,meth)(); entry.extend([p.x,p.y])
        if hasattr(item,"GetWidth"): entry.append(item.GetWidth())
        sig.append(tuple(entry))
    return sorted(sig)


def edge_signature(board):
    import pcbnew
    sig=[]
    for item in board.GetDrawings():
        if item.GetLayer()!=pcbnew.Edge_Cuts: continue
        entry=[type(item).__name__]
        for meth in ("GetStart","GetEnd","GetMid","GetCenter"):
            if hasattr(item,meth):
                try:
                    p=getattr(item,meth)(); entry.extend([p.x,p.y])
                except Exception: pass
        sig.append(tuple(entry))
    return sorted(sig)


def courtyard_box(fp):
    import pcbnew
    for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        try:
            shape=fp.GetCourtyard(layer)
            if shape and not shape.IsEmpty(): return shape.BBox()
        except Exception: pass
    return fp.GetBoundingBox()


def merge_box(box, other):
    if box is None: return other
    box.Merge(other); return box


def run_pcb():
    import pcbnew
    board=pcbnew.LoadBoard(str(PCB)); before_tracks=track_signature(board); before_edges=edge_signature(board); before_zones=len(list(board.Zones()))
    refs={fp.GetReference():fp for fp in board.GetFootprints()}
    if len(refs)!=199: raise RuntimeError(f"Expected baseline 199 footprints, got {len(refs)}")
    missing=sorted(set(TESTPOINTS)-set(refs),key=natural_key)
    if missing: raise RuntimeError(f"Missing PCB test points: {missing}")
    moved=set(PLACEMENT); fixed={r:position_signature(fp) for r,fp in refs.items() if r not in moved and r not in TESTPOINTS}
    for ref in TESTPOINTS: board.Remove(refs[ref])
    refs={fp.GetReference():fp for fp in board.GetFootprints()}
    for ref,(x,y,angle) in PLACEMENT.items():
        fp=refs.get(ref)
        if fp is None: raise RuntimeError(f"Placement reference not found: {ref}")
        fp.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y))); fp.SetOrientationDegrees(angle)
    refs["J801"].SetValue("68710814022")
    existing=[]
    for meth in ("Groups","GetGroups"):
        if hasattr(board,meth):
            try: existing=list(getattr(board,meth)()); break
            except Exception: pass
    for group in existing:
        try: name=group.GetName()
        except Exception: continue
        if name in GROUPS: board.Remove(group)
    refs={fp.GetReference():fp for fp in board.GetFootprints()}
    for name,members in GROUPS.items():
        absent=sorted(set(members)-set(refs),key=natural_key)
        if absent: raise RuntimeError(f"{name} missing members: {absent}")
        group=pcbnew.PCB_GROUP(board); group.SetName(name); board.Add(group)
        for ref in members: group.AddItem(refs[ref])
    pcbnew.SaveBoard(str(PCB),board)
    check=pcbnew.LoadBoard(str(PCB)); refs={fp.GetReference():fp for fp in check.GetFootprints()}
    if len(refs)!=167: raise RuntimeError(f"Expected 167 PCB footprints, got {len(refs)}")
    leftovers=sorted(set(TESTPOINTS)&set(refs),key=natural_key)
    if leftovers: raise RuntimeError(f"Test points remain on PCB: {leftovers}")
    if track_signature(check)!=before_tracks: raise RuntimeError("Existing track geometry changed")
    if edge_signature(check)!=before_edges: raise RuntimeError("Edge.Cuts changed")
    if len(list(check.Zones()))!=before_zones: raise RuntimeError("Zone count changed")
    for ref,sig in fixed.items():
        if position_signature(refs[ref])!=sig: raise RuntimeError(f"Fixed placement changed: {ref}")
    groups=[]; candidates=[]
    for meth in ("Groups","GetGroups"):
        if hasattr(check,meth):
            try: candidates=list(getattr(check,meth)()); break
            except Exception: pass
    for g in candidates:
        try: name=g.GetName()
        except Exception: continue
        if name not in GROUPS: continue
        members=[]; box=None; items=[]
        for meth in ("GetItems","GetMembers"):
            if hasattr(g,meth):
                try: items=list(getattr(g,meth)()); break
                except Exception: items=[]
        for item in items:
            if isinstance(item,pcbnew.FOOTPRINT): members.append(item.GetReference()); box=merge_box(box,courtyard_box(item))
        groups.append({"name":name,"members":sorted(members,key=natural_key),
                       "bbox_mm":[round(box.GetX()/1e6,3),round(box.GetY()/1e6,3),round(box.GetWidth()/1e6,3),round(box.GetHeight()/1e6,3)] if box else []})
    report={"footprints":len(refs),"tracks":len(before_tracks),"zones":before_zones,"groups":sorted(groups,key=lambda x:x["name"]),
            "fixed_count":len(fixed),"removed":TESTPOINTS}
    out=ROOT/"audit-output"; out.mkdir(exist_ok=True); (out/"pcb-apply.json").write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("mode",choices=["schematic","pcb"]); args=parser.parse_args()
    if args.mode=="schematic": run_schematic()
    else: run_pcb()

if __name__=="__main__": main()
