#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
KDIR = ROOT / "hardware" / "kicad"
PCB = KDIR / "ESP32-P4 Display Development Daughterboard.kicad_pcb"
SCH = KDIR / "ESP32-P4 Display Development Daughterboard.kicad_sch"
TARGETS = {
    "Q201","Q202","Q301","Q302","Q303","Q304","U201","U301","U501","U502",
    "J201","J701","J702","J801","L201","U901",
}
TESTPOINTS = {
    "TP103","TP201","TP202","TP301","TP302","TP501","TP502","TP503","TP504",
    "TP601","TP602","TP603","TP604","TP605","TP606","TP607",
    "TP801","TP802","TP803","TP804","TP805",
    "TP901","TP902","TP903","TP904","TP905",
    "TP1001","TP1002","TP1003","TP1004","TP1005","TP1006",
}

def mm(v):
    return pcbnew.ToMM(v)

def point(p):
    return [round(mm(p.x), 5), round(mm(p.y), 5)]

def balanced_blocks(text: str, token: str):
    pos = 0
    while True:
        start = text.find(token, pos)
        if start < 0:
            return
        depth = 0; quoted = False; escaped = False
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
                    if depth == 0:
                        yield text[start:i+1]
                        pos = i + 1
                        break
        else:
            raise RuntimeError(f"Unbalanced block at {start}")

def schematic_symbols(path: Path):
    text = path.read_text()
    out = {}
    for block in balanced_blocks(text, "(symbol"):
        props = dict(re.findall(r'\(property\s+"([^"]+)"\s+"([^"]*)"', block))
        ref = props.get("Reference", "")
        if not ref or ref.startswith("#"):
            continue
        if ref not in out or len(block) < out[ref][0]:
            out[ref] = (len(block), props)
    return {k:v[1] for k,v in out.items()}

def group_info(board):
    groups = []
    candidates = []
    for name in ("Groups", "GetGroups"):
        if hasattr(board, name):
            try: candidates = list(getattr(board, name)()); break
            except Exception: pass
    for g in candidates:
        try: name = g.GetName()
        except Exception: name = ""
        members = []
        for meth in ("GetItems", "GetMembers"):
            if hasattr(g, meth):
                try:
                    for item in getattr(g, meth)():
                        if isinstance(item, pcbnew.FOOTPRINT): members.append(item.GetReference())
                    break
                except Exception: pass
        groups.append({"name":name,"members":sorted(members)})
    return groups

def main():
    board = pcbnew.LoadBoard(str(PCB))
    fps = []
    for fp in board.GetFootprints():
        pos = fp.GetPosition(); box = fp.GetBoundingBox()
        try: fpid = fp.GetFPID().Format()
        except Exception: fpid = str(fp.GetFPID())
        try: props = {k:fp.GetProperty(k) for k in fp.GetProperties()}
        except Exception:
            props = {}
        fps.append({
            "ref":fp.GetReference(), "value":fp.GetValue(), "fpid":fpid,
            "position":point(pos), "orientation_deg":round(fp.GetOrientationDegrees(),3),
            "side":"B" if fp.IsFlipped() else "F",
            "bbox":[round(mm(box.GetX()),5),round(mm(box.GetY()),5),round(mm(box.GetWidth()),5),round(mm(box.GetHeight()),5)],
            "properties":props,
        })
    fps.sort(key=lambda x:x["ref"])
    drawings = list(board.GetDrawings())
    edge = [x for x in drawings if x.GetLayer() == pcbnew.Edge_Cuts]
    edge_boxes = [x.GetBoundingBox() for x in edge]
    if edge_boxes:
        eb = edge_boxes[0]
        for b in edge_boxes[1:]: eb.Merge(b)
        edge_bbox=[round(mm(eb.GetX()),5),round(mm(eb.GetY()),5),round(mm(eb.GetWidth()),5),round(mm(eb.GetHeight()),5)]
    else: edge_bbox=[]
    sch = schematic_symbols(SCH)
    phase2 = {r:p for r,p in sch.items() if p.get("Footprint","").startswith("Phase2:")}
    report = {
        "kicad_version":pcbnew.GetBuildVersion(),
        "footprint_count":len(fps),
        "tracks":len(list(board.GetTracks())),
        "zones":len(list(board.Zones())),
        "edge_item_count":len(edge), "edge_bbox":edge_bbox,
        "groups":group_info(board),
        "testpoints_board":sorted(set(TESTPOINTS)&{f["ref"] for f in fps}),
        "testpoints_schematic":sorted(set(TESTPOINTS)&set(sch)),
        "targets":{"board":{f["ref"]:f for f in fps if f["ref"] in TARGETS},
                   "schematic":{r:sch.get(r,{}) for r in sorted(TARGETS)}},
        "phase2_symbols":phase2,
        "footprints":fps,
    }
    out = ROOT / "audit-output"
    out.mkdir(exist_ok=True)
    (out/"current-audit.json").write_text(json.dumps(report,indent=2,sort_keys=True))
    lines=[]
    lines.append(f"KiCad {report['kicad_version']}")
    lines.append(f"footprints={len(fps)} tracks={report['tracks']} zones={report['zones']} edge_items={len(edge)} edge_bbox={edge_bbox}")
    lines.append("testpoints board="+",".join(report["testpoints_board"]))
    lines.append("testpoints schematic="+",".join(report["testpoints_schematic"]))
    lines.append("GROUPS:")
    for g in report["groups"]: lines.append(f"  {g['name']}: {','.join(g['members'])}")
    lines.append("TARGET BOARD:")
    for r in sorted(TARGETS):
        f=report["targets"]["board"].get(r)
        lines.append(f"  {r}: {f}")
    lines.append("TARGET SCHEMATIC:")
    for r in sorted(TARGETS): lines.append(f"  {r}: {report['targets']['schematic'].get(r)}")
    lines.append("PHASE2 SYMBOLS:")
    for r,p in sorted(phase2.items()): lines.append(f"  {r}: {p}")
    (out/"current-audit.txt").write_text("\n".join(lines)+"\n")
    print("\n".join(lines))

if __name__ == "__main__": main()
