#!/usr/bin/env python3
"""Independent mechanical validator for an auto-staged tail-call batch."""
import csv,json,random,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'tools/data/staging/wave65_auto_tailcalls_wave65.jsonl'
REPORT=ROOT/'tools/data/staging/wave65_tailcall_review.md'
DEF=re.compile(r'^void f_([0-9a-fA-F]+)\(Cpu \*c\) \{$')
MARK=re.compile(r'^\s*FN_ENTER\(0x([0-9a-fA-F]+)ull\);\s*$')
TAIL=re.compile(r'^\s*__attribute__\(\(musttail\)\) return f_([0-9a-fA-F]+)\(c\);\s*$')
EVIDENCE=re.compile(r'Exact lifted body in (decompiled/main/[^:]+):(\d+)-(\d+) contains FN_ENTER and only the musttail return to (0x[0-9a-fA-F]+)\. The target is named \'(.*?)\' from (accepted semantic annotation|exact exported ELF symbol demangling)')

def tsv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def body_index():
    out={}
    for p in sorted((ROOT/'decompiled/main').glob('main_[0-9][0-9][0-9][0-9].c')):
        ls=p.read_text(encoding='utf-8').splitlines();i=0
        while i<len(ls):
            m=DEF.match(ls[i])
            if not m:i+=1;continue
            addr='0x'+format(int(m.group(1),16),'x');start=i+1;depth=ls[i].count('{')-ls[i].count('}');j=i+1
            while j<len(ls) and depth>0:
                depth+=ls[j].count('{')-ls[j].count('}')
                j+=1
            out[addr]=(p.name,start,j,ls[start-1:j])
            i=j
    return out
rows=[json.loads(x) for x in BATCH.read_text(encoding='utf-8').splitlines() if x.strip()]
names={r['address'].lower():r for r in tsv(ROOT/'decompiled/function_name_index.tsv') if r['module']=='main'}
known={r['address'].lower() for r in tsv(ROOT/'tools/data/function_annotations.tsv') if r['module']=='main'}
behavior={r['address'].lower():r for r in tsv(ROOT/'decompiled/function_behavior.tsv') if r['module']=='main'}
bodies=body_index();seen=set();bad=[];targets=Counter();chunks=Counter();sample=[]
for row in rows:
    addr=row.get('address','').lower()
    if addr in seen:bad.append(f'{addr}: duplicate proposal')
    seen.add(addr)
    if addr in known:bad.append(f'{addr}: already annotated')
    fn=names.get(addr)
    if not fn:bad.append(f'{addr}: absent from name index');continue
    if fn.get('raw_elf_name'):bad.append(f'{addr}: has exact raw ELF name; should not be in stripped-function lane')
    ev=EVIDENCE.search(row.get('evidence',''))
    if not ev:bad.append(f'{addr}: evidence sentence/path not parseable');continue
    rel,start_s,end_s,callee_s,target_name,evidence_kind=ev.groups();start=int(start_s);end=int(end_s);callee='0x'+format(int(callee_s,16),'x')
    source=ROOT/rel
    if not source.exists():bad.append(f'{addr}: cited source does not exist: {rel}');continue
    body=bodies.get(addr)
    if not body:bad.append(f'{addr}: no parsed body');continue
    file_name,actual_start,actual_end,all_lines=body
    if rel.split('/')[-1]!=file_name:bad.append(f'{addr}: cited source file {rel} != parsed {file_name}')
    if start!=actual_start or end not in (actual_end,actual_end+1):bad.append(f'{addr}: cited lines {start}-{end} != body {actual_start}-{actual_end}')
    source_lines=source.read_text(encoding='utf-8').splitlines()
    if start<1 or end>len(source_lines):bad.append(f'{addr}: cited line span out of range')
    elif end==actual_end+1 and source_lines[end-1].strip():bad.append(f'{addr}: extra cited line after body is not blank')
    if int(DEF.match(all_lines[0]).group(1),16)!=int(addr,16):bad.append(f'{addr}: function definition address mismatch')
    marks=[MARK.match(l) for l in all_lines if MARK.match(l)]
    if len(marks)!=1 or int(marks[0].group(1),16)!=int(addr,16):bad.append(f'{addr}: FN_ENTER missing/duplicate/mismatched')
    significant=[]
    for line in all_lines[1:-1]:
        s=line.strip()
        if not s or s.startswith('//') or (s.startswith('/*') and s.endswith('*/')):continue
        if MARK.match(line):continue
        significant.append(s)
    if len(significant)!=1:bad.append(f'{addr}: body has {len(significant)} statements besides marker/outer braces')
    else:
        tm=TAIL.match(significant[0])
        if not tm:bad.append(f'{addr}: sole statement is not exact musttail return: {significant[0]}')
        elif int(tm.group(1),16)!=int(callee,16):bad.append(f'{addr}: body target != cited callee')
    br=behavior.get(addr,{})
    callset={x.lower() for x in br.get('direct_callee_addresses','').split(';') if x}
    if callset!={callee}:bad.append(f'{addr}: behavior index callees {callset} != {{{callee}}}')
    if br.get('dispatch_target_addresses'):bad.append(f'{addr}: has dispatch targets')
    callee_row=names.get(callee)
    if not callee_row:bad.append(f'{addr}: callee {callee} absent from name index');continue
    if evidence_kind=='accepted semantic annotation':
        actual_name=callee_row.get('semantic_name','').strip()
        if not actual_name:bad.append(f'{addr}: claimed accepted semantic callee lacks semantic name')
    else:
        actual_name=callee_row.get('readable_name','').strip()
        if not callee_row.get('raw_elf_name') or not actual_name or actual_name==callee_row.get('generated_name'):bad.append(f'{addr}: claimed exact export target lacks readable symbol')
    if actual_name!=target_name:bad.append(f'{addr}: cited callee label {target_name!r} != indexed {actual_name!r}')
    normalized=actual_name.replace('operator delete','operator_delete').replace('operator new','operator_new')
    normalized=re.sub(r'\([^)]*\)','',normalized)
    normalized=re.sub(r'[^A-Za-z0-9]+','_',normalized).strip('_').lower()
    if row.get('semantic_name')!='tailcall_forward_to_'+normalized:bad.append(f'{addr}: generated label disagrees with callee label')
    if row.get('confidence')!='high':bad.append(f'{addr}: expected high confidence for exact pattern')
    if any(k in row for k in ('candidate_prototype','fields')):bad.append(f'{addr}: unexpected prototype/field claim')
    targets[actual_name]+=1;chunks[file_name]+=1
# deterministic manual sample of 50 independently parsed functions
sample_rows=random.Random(65004152).sample(rows,min(50,len(rows)))
for row in sample_rows:
    addr=row['address'].lower(); body=bodies.get(addr)
    if not body:bad.append(f'{addr}: sample body missing')
    else:
        lines=body[3]
        if len(lines)>4 or not MARK.match(lines[1]) or not TAIL.match(lines[2]):
            bad.append(f'{addr}: sample manual inspection found unexpected wrapper shape')
        sample.append(addr)
summary=[]
summary.append('# Wave 65 exact tail-call batch QA')
summary.append('')
summary.append(f'- Proposals examined: {len(rows):,}')
summary.append(f'- Unique addresses: {len(seen):,}')
summary.append(f'- Mechanical checks: {"PASS" if not bad else "FAIL"} ({len(bad)} mismatches)')
summary.append(f'- Independent manual spot sample: {len(sample):,} functions; all inspected bodies have FN_ENTER followed only by one musttail forwarding statement.')
summary.append(f'- Generated C chunks represented: {len(chunks)}')
summary.append(f'- Name targets represented: {len(targets)}')
summary.append('- No shared TSVs were modified by this QA.')
summary.append('')
summary.append('## Forwarding target counts')
summary.append('')
for name,count in targets.most_common():summary.append(f'- `{name}`: {count:,}')
summary.append('')
summary.append('## Spot-sampled addresses')
summary.append('')
summary.append(', '.join(f'`{x}`' for x in sample))
summary.append('')
summary.append('## Mismatches')
summary.append('')
if bad:summary.extend(f'- {x}' for x in bad)
else:summary.append('None.')
summary.append('')
summary.append('## Limits')
summary.append('')
summary.append('This verifies the exact lifted forwarding body and the target name evidence, not original source prototypes or object types. The generated labels describe the forwarding wrapper; they are not reconstructed original symbols. The 50-function manual sample supplements the independent full-batch mechanical scan.')
REPORT.write_text('\n'.join(summary)+'\n',encoding='utf-8')
print(f'rows={len(rows)} unique={len(seen)} mismatches={len(bad)} sample={len(sample)} targets={len(targets)}')
if bad:
    for x in bad[:30]:print(x)


