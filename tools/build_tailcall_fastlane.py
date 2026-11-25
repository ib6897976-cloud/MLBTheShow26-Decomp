#!/usr/bin/env python3
"""Stage exact-name forwarder labels for stripped functions that only tail-call a known callee.

This fast lane is deliberately narrow: after FN_ENTER the complete lifted body
must contain exactly one musttail return to an indexed semantic or exact ELF name.
No arguments, fields, or hidden behavior are inferred.
"""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARK = re.compile(r"^\s*FN_ENTER\(0x([0-9a-fA-F]+)ull\);\s*$")
DEFINITION = re.compile(r"^void f_([0-9a-fA-F]+)\(Cpu \*c\) \{")
TAIL = re.compile(r"^__attribute__\(\(musttail\)\) return f_([0-9a-fA-F]+)\(c\);$")

def read_tsv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))

def slug(value: str) -> str:
    value = value.strip()
    value = value.replace('operator delete', 'operator_delete').replace('operator new', 'operator_new')
    value = re.sub(r'\([^)]*\)', '', value)
    value = re.sub(r'[^A-Za-z0-9]+', '_', value).strip('_').lower()
    return value or ''

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--wave', type=int, required=True)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--limit', type=int, default=0, help='optional cap; zero means all eligible functions')
    args=ap.parse_args()
    decomp=ROOT/'decompiled'
    names={r['address'].lower():r for r in read_tsv(decomp/'function_name_index.tsv') if r['module']=='main'}
    known={r['address'].lower():r for r in read_tsv(ROOT/'tools/data/function_annotations.tsv') if r['module']=='main'}
    behavior={r['address'].lower():r for r in read_tsv(decomp/'function_behavior.tsv') if r['module']=='main'}
    lines_by_addr={}
    for path in sorted((decomp/'main').glob('main_[0-9][0-9][0-9][0-9].c')):
        lines=path.read_text(encoding='utf-8').splitlines()
        current=None; start=None; body=[]
        def save(end_line):
            if current is not None:
                lines_by_addr[current]=(path.name,start,end_line,body[:])
        for number,line in enumerate(lines,1):
            mdef=DEFINITION.match(line)
            if mdef:
                save(number-1)
                current='0x'+mdef.group(1).lower(); start=number; body=[]
                continue
            if current is not None:
                body.append((number,line))
        save(len(lines))
    proposals=[]
    for addr,(source,start,end,body_lines) in sorted(lines_by_addr.items()):
        indexed=names.get(addr,{})
        if addr in known or indexed.get('raw_elf_name'):
            continue
        actual=[]; marker_seen=False
        for number,line in body_lines:
            stripped=line.strip()
            if not stripped or stripped == '}' or stripped.startswith('/*') or stripped.startswith('//'):
                continue
            marker=MARK.match(line)
            if marker:
                marker_seen=True
                continue
            actual.append((number,stripped))
        if not marker_seen or len(actual)!=1:
            continue
        m=TAIL.match(actual[0][1])
        if not m:
            continue
        callee='0x'+m.group(1).lower()
        target=names.get(callee,{})
        target_sem=target.get('semantic_name','').strip()
        target_readable=target.get('readable_name','').strip()
        if target_sem:
            target_name=target_sem; target_evidence='accepted semantic annotation'
        elif target.get('raw_elf_name') and target_readable and target_readable != target.get('generated_name'):
            target_name=target_readable; target_evidence='exact exported ELF symbol demangling'
        else:
            continue
        callee_slug=slug(target_name)
        if not callee_slug:
            continue
        module_body=behavior.get(addr,{})
        direct={x.lower() for x in (module_body.get('direct_callee_addresses','').split(';')) if x}
        if direct and direct != {callee}:
            continue
        semantic=f'tailcall_forward_to_{callee_slug}'
        proposals.append({
          'module':'main','address':addr,'semantic_name':semantic,'confidence':'high',
          'evidence':f'Exact lifted body in decompiled/main/{source}:{start}-{end} contains FN_ENTER and only the musttail return to {callee}. The target is named {target_name!r} from {target_evidence} in decompiled/function_name_index.tsv. This label records the proven forwarding behavior; it does not infer source parameter or field types.'
        })
    if args.limit:
        proposals=proposals[:args.limit]
    out=args.output or ROOT/'tools/data/staging'/f'wave{args.wave:02d}_auto_tailcalls_wave{args.wave}.jsonl'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(''.join(json.dumps(p,separators=(',',':'))+'\n' for p in proposals),encoding='utf-8',newline='\n')
    print(f'Staged {len(proposals)} exact tail-call forwarders to {out}')

if __name__=='__main__': main()

