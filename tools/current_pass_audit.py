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
BLOCK_REFS = {
    "VEHICLE_INPUT_PROTECTION": "J201 F201 L201 C201 C202 D201 R201 C204 Q201 Q202 U201 C205 C206 C207 R202 R203 R204 R205 R206 C203".split(),
    "LM5176_24V": "C309 C310 Q301 Q302 L301 Q303 Q304 C312 C313 C311 R301 R302 R309 C301 U301 C307 D301 C308 D302 C306 R303 R304 C302 C303 R305 C304 C305 R306 R307 R308".split(),
    "LM76003_5V_EFUSE": "C505 C506 C507 U501 C501 L501 C503 C508 C509 C510 C511 C502 C504 R501 R502 R503 R504 R510 C513 U502 C514 C512 R505 R506 R507 R508 R509 R511 R512 J501".split(),
    "DISPLAY_SEQUENCE": "D601 R601 C601 U601 R602 R603 C607 C602 C603 R604 U602 R605 R606 R607 R608 R609 D602 U603 C604 U604 C605 U605 C606 U606 U607 U608 R610 R611".split(),
    "BACKLIGHT_DRIVER": "C901 U901 C902 C903 D901 L901 R901 R902 R903 C904 R904 R905 C906 C907 R906 R907 R908 R909 U902 J901 R910 FB901 C905 C908".split(),
}

def mm(v): return pcbnew.ToMM(v)
def point(p): return [round(mm(p.x), 5), round(mm(p.y), 5)]

def balanced_blocks(text: str, token: str):
    pos = 0
    while True:
        start = text.find(token, pos)
        if start < 0: return
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
                        yield text[start:i+1]; pos = i + 1; break
        else: raise RuntimeError(f"Unbalanced block at {start}")

def schematic_symbols(path: Path):
    text = path.read_text(); out = {}
    for block in balanced_blocks(text, "(symbol"):
        props = dict(re.findall(r'\(property\s+"([^"]+)"\s+"([^"]*)"', block))
        ref = props.get("Reference", "")
        if not ref or ref.startswith("#"): continue
        if ref not in out or len(block) < out[ref][0]: out[ref] = (len(block), props)
    return {k:v[1] for k,v in out.items()}

def group_info(board):
    groups=[]; candidates=[]
    for name in ("Groups", "GetGroups"):
        if hasattr(board,name):
            try: candidates=list(getattr(board,name)()); break
            except Exception: pass
    for g in candidates:
        try: name=g.GetName()
        except Exception: name=""
        members=[]
        for meth in ("GetItems","GetMembers"):
            if hasattr(g,meth):
                try:
                    for item in getattr(g,meth)():
                        if isinstance(item,pcbnew.FOOTPRINT): members.append(item.GetReference())
                    break
                except Exception: pass
        groups.append({"name":name,"members":sorted(members)})
    return groups

def fpid_string(fp):
    try:
        x=fp.GetFPID(); return f"{x.GetLibNickname()}:{x.GetLibItemName()}"
    except Exception: return str(fp.GetFPID())

def main():
    board=pcbnew.LoadBoard(str(PCB)); fps=[]
    for fp in board.GetFootprints():
        pos=fp.GetPosition(); box=fp.GetBoundingBox()
        try: props={k:fp.GetProperty(k) for k in fp.GetProperties()}
        except Exception: props={}
        pads=[]
        for pad in fp.Pads():
            sz=pad.GetSize(); p=pad.GetPosition()
            pads.append({"number":pad.GetNumber(),"net":pad.GetNetname(),"position":point(p),
                         "size":[round(mm(sz.x),5),round(mm(sz.y),5)],"orientation_deg":round(pad.GetOrientationDegrees(),3)})
        fps.append({"ref":fp.GetReference(),"value":fp.GetValue(),"fpid":fpid_string(fp),
                    "position":point(pos),"orientation_deg":round(fp.GetOrientationDegrees(),3),
                    "side":"B" if fp.IsFlipped() else "F",
                    "bbox":[round(mm(box.GetX()),5),round(mm(box.GetY()),5),round(mm(box.GetWidth()),5),round(mm(box.GetHeight()),5)],
                    "properties":props,"pads":pads})
    fps.sort(key=lambda x:x["ref"]); byref={f["ref"]:f for f in fps}
    drawings=list(board.GetDrawings()); edge=[x for x in drawings if x.GetLayer()==pcbnew.Edge_Cuts]
    edge_boxes=[x.GetBoundingBox() for x in edge]
    if edge_boxes:
        eb=edge_boxes[0]
        for b in edge_boxes[1:]: eb.Merge(b)
        edge_bbox=[round(mm(eb.GetX()),5),round(mm(eb.GetY()),5),round(mm(eb.GetWidth()),5),round(mm(eb.GetHeight()),5)]
    else: edge_bbox=[]
    sch=schematic_symbols(SCH); phase2={r:p for r,p in sch.items() if p.get("Footprint","").startswith("Phase2:")}
    tracks=[]
    for t in board.GetTracks():
        try:
            tracks.append({"type":type(t).__name__,"net":t.GetNetname(),"start":point(t.GetStart()),"end":point(t.GetEnd()),"width":round(mm(t.GetWidth()),5)})
        except Exception: tracks.append({"type":type(t).__name__})
    report={"kicad_version":pcbnew.GetBuildVersion(),"footprint_count":len(fps),"tracks":tracks,
            "zones":len(list(board.Zones())),"edge_item_count":len(edge),"edge_bbox":edge_bbox,
            "groups":group_info(board),"testpoints_board":sorted(set(TESTPOINTS)&set(byref)),
            "testpoints_schematic":sorted(set(TESTPOINTS)&set(sch)),
            "targets":{"board":{r:byref.get(r) for r in sorted(TARGETS)},"schematic":{r:sch.get(r,{}) for r in sorted(TARGETS)}},
            "phase2_symbols":phase2,"blocks":{n:{r:byref.get(r) for r in refs} for n,refs in BLOCK_REFS.items()},"footprints":fps}
    out=ROOT/"audit-output"; out.mkdir(exist_ok=True)
    (out/"current-audit.json").write_text(json.dumps(report,indent=2,sort_keys=True))
    lines=[f"KiCad {report['kicad_version']}",f"footprints={len(fps)} tracks={len(tracks)} zones={report['zones']} edge_items={len(edge)} edge_bbox={edge_bbox}",
           "testpoints board="+",".join(report["testpoints_board"]),"testpoints schematic="+",".join(report["testpoints_schematic"]),"GROUPS:"]
    for g in report["groups"]: lines.append(f"  {g['name']}: {','.join(g['members'])}")
    lines.append("TRACKS:")
    for t in tracks: lines.append("  "+str(t))
    lines.append("TARGET BOARD:")
    for r in sorted(TARGETS): lines.append(f"  {r}: {report['targets']['board'].get(r)}")
    lines.append("TARGET SCHEMATIC:")
    for r in sorted(TARGETS): lines.append(f"  {r}: {report['targets']['schematic'].get(r)}")
    lines.append("PHASE2 SYMBOLS:")
    for r,p in sorted(phase2.items()): lines.append(f"  {r}: {p}")
    (out/"current-audit.txt").write_text("\n".join(lines)+"\n"); print("\n".join(lines))

if __name__=="__main__": main()
