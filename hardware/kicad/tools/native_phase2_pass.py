#!/usr/bin/env python3
"""KiCad-native diagnostic and placement pass for the consolidated Phase 2 design.

The diagnostic mode is read-only. The apply mode is deliberately left gated until
its placement plan has been reviewed from the diagnostic artifact.
"""
from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[3]
KICAD = ROOT / "hardware" / "kicad"
BOARD_PATH = KICAD / "ESP32-P4 Display Development Daughterboard.kicad_pcb"
SCH_PATH = KICAD / "ESP32-P4 Display Development Daughterboard.kicad_sch"
OUT = ROOT / "placement-artifacts"
OUT.mkdir(exist_ok=True)


def mm(value):
    return float(pcbnew.ToMM(value))


def point(v):
    return [mm(v.x), mm(v.y)]


def box_dict(box):
    return {
        "x": mm(box.GetX()),
        "y": mm(box.GetY()),
        "w": mm(box.GetWidth()),
        "h": mm(box.GetHeight()),
        "right": mm(box.GetRight()),
        "bottom": mm(box.GetBottom()),
    }


def footprint_record(board, fp):
    pads = []
    for pad in fp.Pads():
        pads.append({
            "number": str(pad.GetNumber()),
            "net": pad.GetNetname(),
            "position": point(pad.GetPosition()),
            "size": point(pad.GetSize()),
            "orientation": float(pad.GetOrientationDegrees()),
            "attribute": int(pad.GetAttribute()),
        })
    return {
        "reference": fp.GetReference(),
        "value": fp.GetValue(),
        "fpid": fp.GetFPID().Format(),
        "position": point(fp.GetPosition()),
        "orientation": float(fp.GetOrientationDegrees()),
        "layer": board.GetLayerName(fp.GetLayer()),
        "locked": bool(fp.IsLocked()),
        "bbox": box_dict(fp.GetBoundingBox(False, False)),
        "pads": pads,
    }


def edge_summary(board):
    edge = pcbnew.Edge_Cuts
    items = []
    xs, ys = [], []
    for item in board.GetDrawings():
        if item.GetLayer() != edge:
            continue
        rec = {"type": item.GetClass()}
        if hasattr(item, "GetStart"):
            rec["start"] = point(item.GetStart())
            xs.append(rec["start"][0]); ys.append(rec["start"][1])
        if hasattr(item, "GetEnd"):
            rec["end"] = point(item.GetEnd())
            xs.append(rec["end"][0]); ys.append(rec["end"][1])
        if hasattr(item, "GetMid"):
            rec["mid"] = point(item.GetMid())
            xs.append(rec["mid"][0]); ys.append(rec["mid"][1])
        if hasattr(item, "GetCenter"):
            rec["center"] = point(item.GetCenter())
            xs.append(rec["center"][0]); ys.append(rec["center"][1])
        items.append(rec)
    bbox = None
    if xs:
        bbox = {"min_x": min(xs), "min_y": min(ys), "max_x": max(xs), "max_y": max(ys),
                "width": max(xs)-min(xs), "height": max(ys)-min(ys)}
    return {"items": items, "bbox": bbox}


def group_summary(board):
    groups = []
    getter = getattr(board, "Groups", None) or getattr(board, "GetGroups", None)
    if getter:
        try:
            for group in getter():
                members = []
                for item in group.GetItems():
                    if isinstance(item, pcbnew.FOOTPRINT):
                        members.append(item.GetReference())
                    else:
                        members.append(item.GetClass())
                groups.append({"name": group.GetName(), "members": sorted(members)})
        except Exception as exc:
            groups.append({"error": repr(exc)})
    return groups


def parse_schematic_symbols(text):
    # Extract top-level symbol blocks with balanced parentheses. This is diagnostic only.
    blocks = []
    token = "\n\t(symbol"
    cursor = 0
    while True:
        start = text.find(token, cursor)
        if start < 0:
            break
        start += 2
        depth = 0; quoted = False; escaped = False
        end = start
        for end in range(start, len(text)):
            c = text[end]
            if quoted:
                if escaped: escaped = False
                elif c == "\\": escaped = True
                elif c == '"': quoted = False
            else:
                if c == '"': quoted = True
                elif c == "(": depth += 1
                elif c == ")":
                    depth -= 1
                    if depth == 0:
                        end += 1
                        break
        block = text[start:end]
        props = dict(re.findall(r'\(property\s+"([^"]+)"\s+"([^"]*)"', block))
        if props.get("Reference") and not props["Reference"].startswith("#"):
            at = re.search(r'^\(symbol\s+\(lib_id\s+"[^"]+"\)\s+\(at\s+([-0-9.]+)\s+([-0-9.]+)(?:\s+([-0-9.]+))?\)', block)
            blocks.append({
                "reference": props.get("Reference"),
                "value": props.get("Value", ""),
                "footprint": props.get("Footprint", ""),
                "manufacturer": props.get("Manufacturer", ""),
                "mpn": props.get("MPN", ""),
                "datasheet": props.get("Datasheet", ""),
                "description": props.get("Description", ""),
                "position": [float(at.group(1)), float(at.group(2)), float(at.group(3) or 0)] if at else None,
            })
        cursor = end
    return blocks


def render_svg(records, edge):
    all_boxes = [r["bbox"] for r in records]
    min_x = min([b["x"] for b in all_boxes] + ([edge["bbox"]["min_x"]] if edge["bbox"] else [])) - 5
    min_y = min([b["y"] for b in all_boxes] + ([edge["bbox"]["min_y"]] if edge["bbox"] else [])) - 5
    max_x = max([b["right"] for b in all_boxes] + ([edge["bbox"]["max_x"]] if edge["bbox"] else [])) + 5
    max_y = max([b["bottom"] for b in all_boxes] + ([edge["bbox"]["max_y"]] if edge["bbox"] else [])) + 5
    scale = 5
    width = (max_x-min_x)*scale; height = (max_y-min_y)*scale
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="{min_x} {min_y} {max_x-min_x} {max_y-min_y}">',
             '<rect x="-1000" y="-1000" width="4000" height="4000" fill="#101820"/>']
    if edge["bbox"]:
        b = edge["bbox"]
        parts.append(f'<rect x="{b["min_x"]}" y="{b["min_y"]}" width="{b["width"]}" height="{b["height"]}" fill="none" stroke="#ffffff" stroke-width="0.3"/>')
    for r in records:
        b = r["bbox"]
        color = "#43bff5" if r["layer"].startswith("F.") else "#d966ff"
        parts.append(f'<rect x="{b["x"]}" y="{b["y"]}" width="{b["w"]}" height="{b["h"]}" fill="{color}" fill-opacity="0.18" stroke="{color}" stroke-width="0.15"/>')
        parts.append(f'<text x="{r["position"][0]}" y="{r["position"][1]}" fill="#fff" font-size="1.2" text-anchor="middle" dominant-baseline="middle">{r["reference"]}</text>')
    parts.append('</svg>')
    (OUT / "placement.svg").write_text("\n".join(parts))


def diagnostic():
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    footprints = [footprint_record(board, fp) for fp in board.GetFootprints()]
    edge = edge_summary(board)
    groups = group_summary(board)
    schematic = parse_schematic_symbols(SCH_PATH.read_text())
    report = {
        "kicad_version": pcbnew.GetBuildVersion(),
        "board": str(BOARD_PATH.relative_to(ROOT)),
        "footprint_count": len(footprints),
        "tracks": len(list(board.GetTracks())),
        "zones": board.GetAreaCount(),
        "footprints": sorted(footprints, key=lambda r: r["reference"]),
        "edge": edge,
        "groups": groups,
        "schematic_symbols": sorted(schematic, key=lambda r: r["reference"]),
    }
    (OUT / "diagnostic.json").write_text(json.dumps(report, indent=2))
    render_svg(footprints, edge)
    print(json.dumps({
        "kicad_version": report["kicad_version"],
        "footprints": report["footprint_count"],
        "tracks": report["tracks"],
        "zones": report["zones"],
        "edge_bbox": edge["bbox"],
        "groups": groups,
        "symbols": len(schematic),
    }, indent=2))
    for rec in sorted(footprints, key=lambda r: r["reference"]):
        print(f"FP {rec['reference']:7s} {rec['layer']:5s} {rec['position'][0]:9.3f} {rec['position'][1]:9.3f} {rec['orientation']:7.2f} {rec['fpid']} {rec['value']}")


def apply_pass():
    raise SystemExit("Apply mode is intentionally gated pending diagnostic review")


if __name__ == "__main__":
    mode = os.environ.get("PLACEMENT_MODE", "diagnostic")
    diagnostic() if mode == "diagnostic" else apply_pass()
