"""Refuse commits that carry game data, generated code or key material.

    python tools/check_content.py --staged      (pre-commit hook; .githooks/pre-commit)
    python tools/check_content.py --all         (all git-tracked files, e.g. CI)
    python tools/check_content.py FILE...

Checks every file: forbidden paths/extensions, size limit, Switch container magics (NCA/NSO/PFS0/NPDM/RomFS image
headers), the marker the code generator writes into game-derived C, and key-file lines. Standard library only.
"""
import re
import subprocess
import sys
from pathlib import Path

# recomp/gen.py writes GENERATED_MARKER into every file it emits; split so this file does not contain it.
GENERATED_MARKER = 'MLBTS_RECOMP_' + 'GENERATED_FROM_GAME_CODE'
MARKERS = (GENERATED_MARKER, 'TOTK_RECOMP_' + 'GENERATED_FROM_GAME_CODE')  # also refuse TotK-generator output
MAX_BYTES = 2 * 1024 * 1024
MAGICS = {b'NSO0': 'NSO module', b'PFS0': 'PFS0 container', b'HFS0': 'HFS0 container', b'META': 'NPDM',
          b'NCA3': 'NCA', b'IVFC': 'IVFC image', b'FXB\0': 'FXB shader bank', b'TX12': 'TEX texture'}
KEY_LINE = re.compile(rb'^\s*(header_key|key_area_key_\w+|titlekek_\w+|master_key_\w+|[0-9a-f]{32})\s*=\s*[0-9a-fA-F]{32,64}\s*$',
                      re.M)
ALLOWED_BIG = set()
FORBIDDEN_PREFIXES = ('work/', 'gamefiles/', 'refs/')
FORBIDDEN_SUFFIXES = ('.keys', '.nsp', '.xci', '.nca', '.nso', '.nro', '.npdm', '.romfs', '.bktr')
FORBIDDEN_NAMES = ('prod.keys', 'title.keys')


def problems(path, data):
    out = []
    norm = path.replace('\\', '/')
    if any(norm.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        out.append('under forbidden local-only directory')
    base = norm.rsplit('/', 1)[-1].lower()
    if base in FORBIDDEN_NAMES or base.endswith(FORBIDDEN_SUFFIXES):
        out.append('forbidden game/key file type')
    if len(data) > MAX_BYTES and path not in ALLOWED_BIG:
        out.append(f'larger than {MAX_BYTES} bytes')
    head = data[:4]
    if head in MAGICS:
        out.append(f'starts with {MAGICS[head]} magic')
    if any(m.encode() in data for m in MARKERS):
        out.append('contains the generated-code marker')
    if KEY_LINE.search(data):
        out.append('looks like a key file line')
    return out


def staged():
    names = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z'],
                           check=True, capture_output=True).stdout.split(b'\0')
    for n in filter(None, names):
        name = n.decode()
        blob = subprocess.run(['git', 'show', f':{name}'], check=True, capture_output=True).stdout
        yield name, blob


def tracked():
    names = subprocess.run(['git', '-c', 'safe.directory=*', 'ls-files', '-z'],
                           check=True, capture_output=True).stdout.split(b'\0')
    for n in filter(None, names):
        name = n.decode()
        p = Path(name)
        if p.is_file():
            yield name, p.read_bytes()


def main():
    args = sys.argv[1:]
    if args == ['--staged']:
        items = staged()
    elif args == ['--all']:
        items = tracked()
    else:
        items = ((a, Path(a).read_bytes()) for a in args)
    bad = 0
    for name, data in items:
        for p in problems(name.replace('\\', '/'), data):
            print(f'{name}: {p}', file=sys.stderr)
            bad += 1
    if bad:
        print(f'check_content: {bad} problem(s); game data, generated code and keys stay out of git', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
