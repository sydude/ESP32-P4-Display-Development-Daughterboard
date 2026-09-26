#!/usr/bin/env python3
"""Focused, formatting-preserving edit of the consolidated KiCad root schematic."""
from pathlib import Path
import csv
import re

TESTPOINTS = set("TP103 TP201 TP202 TP301 TP302 TP501 TP502 TP503 TP504 TP601 TP602 TP603 TP604 TP605 TP606 TP607 TP801 TP802 TP803 TP804 TP805 TP901 TP902 TP903 TP904 TP905 TP1001 TP1002 TP1003 TP1004 TP1005 TP1006".split())
DNP = {"R505", "C907", "R907", "R1005"}
METADATA = {
    "D201": {"Datasheet":"https://www.bourns.com/docs/product-datasheets/sm8s-q.pdf"},
    "L201": {"Datasheet":"https://www.bourns.com/docs/product-datasheets/srp1038a.pdf"},
    "J201": {"Datasheet":"https://www.molex.com/en-us/products/part-detail/430450218", "Description":"Molex Micro-Fit 3.0, 2-circuit vertical SMT header, 3.00 mm pitch; vehicle-power input"},
    "J701": {"Datasheet":"https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/10172241.pdf", "Description":"15-position 1.00 mm-pitch top-contact FFC/FPC connector for Nano DSI"},
    "J702": {"Datasheet":"https://www.molex.com/en-us/products/part-detail/5051104096", "Description":"Molex 505110-4096, 40-position 0.50 mm-pitch bottom-contact FPC connector for Displayman LCD"},
    "J801": {"Value":"68710814022", "Manufacturer":"Würth Elektronik", "MPN":"68710814022", "Datasheet":"https://www.we-online.com/components/products/datasheet/68710814022.pdf", "Description":"Würth Elektronik 68710814022, 8-position 0.50 mm-pitch top-contact ZIF FPC connector for Displayman touch tail", "Footprint":"Phase2:Wurth_68710814022"},
}
MOSFETS = set("Q201 Q202 Q301 Q302 Q303 Q304".split())
MOSMETA = {"Value":"CSD19531Q5A", "Manufacturer":"Texas Instruments", "MPN":"CSD19531Q5A", "Datasheet":"https://www.ti.com/lit/ds/symlink/csd19531q5a.pdf", "Description":"100 V N-channel MOSFET, TI DQJ/VSONP-8; exposed drain pad is not a separate pin", "Footprint":"Phase2:Texas_DQJ0008A_VSONP-8"}


def block_end(s, start):
    depth=0; quoted=False; escaped=False
    for i in range(start, len(s)):
        c=s[i]
        if quoted:
            if escaped: escaped=False
            elif c=='\\': escaped=True
            elif c=='"': quoted=False
        else:
            if c=='"': quoted=True
            elif c=='(': depth+=1
            elif c==')':
                depth-=1
                if depth==0: return i+1
    raise ValueError(f"unbalanced block at {start}")


def top_blocks(s):
    root=s.find('(kicad_sch')
    if root<0: raise ValueError('not a KiCad schematic')
    depth=0; quoted=False; escaped=False; start=None; out=[]
    for i in range(root, len(s)):
        c=s[i]
        if quoted:
            if escaped: escaped=False
            elif c=='\\': escaped=True
            elif c=='"': quoted=False
            continue
        if c=='"': quoted=True; continue
        if c=='(':
            depth+=1
            if depth==2: start=i
        elif c==')':
            if depth==2 and start is not None:
                end=i+1
                m=re.match(r'\(([A-Za-z_]+)', s[start:end])
                out.append((start,end,m.group(1) if m else '',s[start:end]))
                start=None
            depth-=1
            if depth==0: break
    return out


def patch_property(block, name, value):
    pat=re.compile(r'(\(property\s+"'+re.escape(name)+r'"\s+")[^"]*(")')
    if pat.search(block):
        return pat.sub(lambda m:m.group(1)+value+m.group(2), block, count=1)
    insert_at=min([x for x in (block.find('\n\t\t(pin '), block.find('\n\t\t(instances')) if x>=0] or [len(block)-1])
    prop=(f'\n\t\t(property "{name}" "{value}"\n'
          f'\t\t\t(at 0 0 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n'
          f'\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)')
    return block[:insert_at]+prop+block[insert_at:]


def at_coord(block):
    m=re.search(r'\(at\s+(-?[\d.]+)\s+(-?[\d.]+)(?:\s+(-?[\d.]+))?\)', block)
    return None if not m else tuple(round(float(x),4) for x in m.groups() if x is not None)


def edit_root(path):
    p=Path(path); s=p.read_text(); blocks=top_blocks(s)
    removals=[]; tp_data={}; metadata_ids={}
    for st,en,typ,b in blocks:
        if typ!='symbol': continue
        rm=re.search(r'\(property\s+"Reference"\s+"([^"]+)"', b)
        if not rm: continue
        ref=rm.group(1)
        if ref in TESTPOINTS:
            at=at_coord(b); vm=re.search(r'\(property\s+"Value"\s+"([^"]*)"', b)
            if not (at and vm) or len(at)<3 or abs(at[2])>1e-9: raise RuntimeError(f'unexpected test point {ref}')
            tp_data[ref]={'pin':(round(at[0]-5.08,4),round(at[1],4)), 'value':vm.group(1)}
            removals.append((st,en))
        elif ref in METADATA or ref in MOSFETS:
            metadata_ids[ref]=(st,en,b)
    if set(tp_data)!=TESTPOINTS: raise RuntimeError(f'test-point symbol mismatch: {TESTPOINTS-set(tp_data)}')
    wire_far={}
    for st,en,typ,b in blocks:
        if typ!='wire': continue
        pts=re.findall(r'\(xy\s+(-?[\d.]+)\s+(-?[\d.]+)\)', b)
        if len(pts)!=2: continue
        points=[(round(float(x),4),round(float(y),4)) for x,y in pts]
        for ref,d in tp_data.items():
            if d['pin'] in points:
                wire_far[ref]=points[1] if points[0]==d['pin'] else points[0]
                removals.append((st,en))
    label_removed=set()
    for st,en,typ,b in blocks:
        if typ!='global_label': continue
        nm=re.match(r'\(global_label\s+"([^"]+)"', b); at=at_coord(b)
        if not (nm and at): continue
        point=(round(at[0],4),round(at[1],4))
        for ref,d in tp_data.items():
            if point==wire_far.get(ref,d['pin']) and nm.group(1)==d['value']:
                label_removed.add(ref); removals.append((st,en))
    if label_removed!=TESTPOINTS: raise RuntimeError(f'test-point label mismatch: {TESTPOINTS-label_removed}')
    replacements=[]
    for ref,(st,en,b) in metadata_ids.items():
        fields=MOSMETA if ref in MOSFETS else METADATA[ref]
        for name,value in fields.items(): b=patch_property(b,name,value)
        replacements.append((st,en,b))
    libspan=next((x for x in blocks if x[2]=='lib_symbols'),None)
    if not libspan: raise RuntimeError('lib_symbols missing')
    lst,len_,_,lb=libspan
    for libname,fields in [('Phase2:CSD19531Q5A',MOSMETA),('Phase2:Wurth_68710814022',METADATA['J801'])]:
        rel=lb.find(f'(symbol "{libname}"')
        if rel<0: raise RuntimeError(f'embedded lib missing {libname}')
        relend=block_end(lb,rel); sub=lb[rel:relend]
        for name,value in fields.items(): sub=patch_property(sub,name,value)
        lb=lb[:rel]+sub+lb[relend:]
    replacements.append((lst,len_,lb))
    ops=sorted([(a,b,'') for a,b in removals]+replacements,key=lambda x:x[0],reverse=True)
    last=len(s)+1
    for a,b,new in ops:
        if b>last: raise RuntimeError('overlapping edit operations')
        s=s[:a]+new+s[b:]; last=a
    p.write_text(s)
    print(f'root: removed {len(TESTPOINTS)} symbols, {len(wire_far)} wires, {len(TESTPOINTS)} labels; patched {len(metadata_ids)} instances')


def patch_lib(path):
    p=Path(path); s=p.read_text()
    for name,fields in [('CSD19531Q5A',MOSMETA),('Wurth_68710814022',METADATA['J801'])]:
        st=s.find(f'(symbol "{name}"')
        if st<0: raise RuntimeError(f'project library missing {name}')
        en=block_end(s,st); b=s[st:en]
        for field,value in fields.items(): b=patch_property(b,field,value)
        s=s[:st]+b+s[en:]
    p.write_text('\n'.join(line.rstrip() for line in s.splitlines())+'\n')


def natural_key(ref):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)',ref)]


def sheet_name(ref):
    m=re.search(r'\d+',ref); n=int(m.group()) if m else 0
    if 200<=n<600: return 'Power'
    if 600<=n<700 or 900<=n<1000: return 'Display Power & Backlight'
    return 'Interfaces & Nano'


def regenerate_bom(root_path,bom_path):
    s=Path(root_path).read_text(); rows=[]
    for _,_,typ,b in top_blocks(s):
        if typ!='symbol': continue
        props=dict(re.findall(r'\(property\s+"([^"]+)"\s+"([^"]*)"',b))
        ref=props.get('Reference',''); footprint=props.get('Footprint','')
        if not ref or ref.startswith('#') or not footprint or '(on_board no)' in b: continue
        rows.append({'Reference':ref,'Value':props.get('Value',''),'Manufacturer':props.get('Manufacturer',''),'MPN':props.get('MPN',''),'Footprint':footprint,'DNP':'DNP' if ref in DNP or '(dnp yes)' in b else 'POP','Sheet':sheet_name(ref),'Description':props.get('Description','')})
    rows.sort(key=lambda r:natural_key(r['Reference']))
    if len(rows)!=165: raise RuntimeError(f'expected 165 schematic BOM rows plus H101/H102, found {len(rows)}')
    if {r['Reference'] for r in rows}&TESTPOINTS: raise RuntimeError('test points remain in BOM')
    with Path(bom_path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Reference','Value','Manufacturer','MPN','Footprint','DNP','Sheet','Description'],lineterminator='\n')
        w.writeheader(); w.writerows(rows)
    print(f'BOM: {len(rows)} schematic rows; board-only H101/H102 excluded')


if __name__=='__main__':
    root=Path('hardware/kicad/ESP32-P4 Display Development Daughterboard.kicad_sch')
    edit_root(root); patch_lib('hardware/kicad/Phase2.kicad_sym'); regenerate_bom(root,'hardware/BOM.csv')
