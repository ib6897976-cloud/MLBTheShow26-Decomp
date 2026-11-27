from __future__ import annotations

import base64
import csv
import hashlib
import json
import os
import tempfile
import threading
import time
from collections import Counter, defaultdict, deque
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "tools" / "progress_site"
DATA_FILES = [
    ROOT / "decompiled" / "function_name_index.tsv",
    ROOT / "tools" / "data" / "function_annotations.tsv",
    ROOT / "tools" / "data" / "function_prototype_candidates.tsv",
    ROOT / "tools" / "data" / "field_annotations.tsv",
]
_CACHE_LOCK = threading.Lock()
_CACHE_STAMP = None
_CACHE_DATA = None
TIMELINE_STATE = ROOT / "tools" / "data" / "progress_timeline_state.json"
TIMELINE_EVENTS = ROOT / "tools" / "data" / "progress_timeline.jsonl"
_TIMELINE_LOCK = threading.Lock()
_TIMELINE_SCAN_STAMP = None
_TIMELINE_PENDING_STAMP = None
_TIMELINE_PENDING_SINCE = None
_TIMELINE_READ_LOCK = threading.Lock()
_TIMELINE_READ_STAMP = None
_TIMELINE_READ_DATA = None
TIMELINE_SCAN_FILES = [
    ROOT / "decompiled" / "function_name_index.tsv",
    ROOT / "decompiled" / "function_behavior.tsv",
    ROOT / "tools" / "data" / "function_annotations.tsv",
    ROOT / "tools" / "data" / "function_prototype_candidates.tsv",
    ROOT / "tools" / "data" / "field_annotations.tsv",
]


@contextmanager
def timeline_process_lock():
    """Serialize timeline scans across the live server and static exporter."""
    identity = hashlib.sha256(str(TIMELINE_STATE.resolve()).encode("utf-8")).hexdigest()[:20]
    lock_path = Path(tempfile.gettempdir()) / f"mlbts_progress_timeline_{identity}.lock"
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        if os.name == "nt":
            import msvcrt

            if os.fstat(descriptor).st_size == 0:
                os.write(descriptor, b"\0")
            os.lseek(descriptor, 0, os.SEEK_SET)
            msvcrt.locking(descriptor, msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(descriptor, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def read_tsv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def timeline_records():
    records = {}

    def add(key, kind, item, details, module="", address="", fingerprint=None):
        body = {
            "kind": kind,
            "item": item,
            "details": details,
            "module": module,
            "address": address,
        }
        serialized = json.dumps(body, sort_keys=True, ensure_ascii=False)
        records[key] = {**body, "fingerprint": fingerprint or hashlib.sha256(serialized.encode("utf-8")).hexdigest()}

    # New function-index addresses are tracked separately from later semantic-name edits.
    for row in read_tsv(ROOT / "decompiled" / "function_name_index.tsv"):
        module, address = row["module"], row["address"]
        add(
            f"function:{module}:{address}", "Function", row.get("semantic_name") or row.get("generated_name") or address,
            "New function address appeared in the generated function index.", module, address,
            fingerprint=f"{module}:{address}",
        )

    for row in read_tsv(ROOT / "tools" / "data" / "function_annotations.tsv"):
        module, address = row["module"], row["address"]
        add(
            f"annotation:{module}:{address}", "Function annotation", row["semantic_name"],
            f"{row.get('confidence', 'unknown')} confidence · {row.get('evidence', '')}", module, address,
        )

    for row in read_tsv(ROOT / "tools" / "data" / "function_prototype_candidates.tsv"):
        module, address = row["module"], row["address"]
        add(
            f"prototype:{module}:{address}", "Prototype", row["candidate_prototype"],
            f"{row.get('confidence', 'unknown')} confidence · {row.get('evidence', '')}", module, address,
        )

    for row in read_tsv(ROOT / "tools" / "data" / "field_annotations.tsv"):
        module = row["module"]
        structure = row["structure_name"]
        offset = row["offset"]
        field_name = row["field_name"]
        key = f"field:{module}:{structure}:{offset}:{field_name}"
        add(
            key, "Field / type", f"{structure}.{field_name}",
            f"{row.get('ctype', 'unknown')} at {offset} · {row.get('semantic_description', '')}", module, offset,
        )
    return records


def save_timeline_state(state):
    temporary = TIMELINE_STATE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    temporary.replace(TIMELINE_STATE)


def refresh_timeline():
    global _TIMELINE_SCAN_STAMP, _TIMELINE_PENDING_STAMP, _TIMELINE_PENDING_SINCE
    TIMELINE_STATE.parent.mkdir(parents=True, exist_ok=True)
    stamp = tuple((path.stat().st_mtime_ns, path.stat().st_size) for path in TIMELINE_SCAN_FILES)
    with _TIMELINE_LOCK, timeline_process_lock():
        if stamp == _TIMELINE_SCAN_STAMP:
            return
        now = time.monotonic()
        if stamp != _TIMELINE_PENDING_STAMP:
            _TIMELINE_PENDING_STAMP = stamp
            _TIMELINE_PENDING_SINCE = now
            return
        # The annotation refresh rewrites large TSVs in place. Let all source
        # files settle before reading them, so a transient partial index is not
        # mistaken for real additions/removals in the activity timeline.
        if now - _TIMELINE_PENDING_SINCE < 1.5:
            return
        with (ROOT / "decompiled" / "function_name_index.tsv").open("r", encoding="utf-8-sig", newline="") as stream:
            function_rows = sum(1 for _ in csv.DictReader(stream, delimiter="\t"))
        with (ROOT / "decompiled" / "function_behavior.tsv").open("r", encoding="utf-8-sig", newline="") as stream:
            behavior_rows = sum(1 for _ in csv.DictReader(stream, delimiter="\t"))
        if function_rows != behavior_rows:
            return
        current = timeline_records()
        after_stamp = tuple((path.stat().st_mtime_ns, path.stat().st_size) for path in TIMELINE_SCAN_FILES)
        if after_stamp != stamp:
            _TIMELINE_PENDING_STAMP = after_stamp
            _TIMELINE_PENDING_SINCE = time.monotonic()
            return
        if TIMELINE_STATE.exists():
            state = json.loads(TIMELINE_STATE.read_text(encoding="utf-8"))
        else:
            started = utc_now()
            state = {
                "tracking_since": started,
                "records": {key: row["fingerprint"] for key, row in current.items()},
            }
            if not TIMELINE_EVENTS.exists():
                TIMELINE_EVENTS.write_text(json.dumps({
                    "timestamp": started,
                    "action": "started",
                    "kind": "Timeline",
                    "item": "Activity tracking started",
                    "details": "Existing rows are the baseline; new and changed entries receive timestamps from this point forward.",
                    "module": "",
                    "address": "",
                }, ensure_ascii=False) + "\n", encoding="utf-8")
            save_timeline_state(state)
            _TIMELINE_SCAN_STAMP = stamp
            _TIMELINE_PENDING_STAMP = None
            _TIMELINE_PENDING_SINCE = None
            return

        known = state.setdefault("records", {})
        new_events = []
        for key, row in current.items():
            old_fingerprint = known.get(key)
            if old_fingerprint == row["fingerprint"]:
                continue
            action = "added" if old_fingerprint is None else "updated"
            new_events.append({
                "timestamp": utc_now(),
                "action": action,
                "kind": row["kind"],
                "item": row["item"],
                "details": row["details"],
                "module": row["module"],
                "address": row["address"],
            })
            known[key] = row["fingerprint"]
        removed = set(known) - set(current)
        kind_names = {
            "function": "Function",
            "annotation": "Function annotation",
            "prototype": "Prototype",
            "field": "Field / type",
        }
        for key in sorted(removed):
            parts = key.split(":", 2)
            prefix = parts[0] if parts else ""
            module = parts[1] if len(parts) > 1 else ""
            tail = parts[2] if len(parts) > 2 else key
            new_events.append({
                "timestamp": utc_now(),
                "action": "removed",
                "kind": kind_names.get(prefix, "Annotation"),
                "item": tail,
                "details": "Previously tracked row was removed from the current annotation index.",
                "module": module,
                "address": tail if prefix in {"function", "annotation", "prototype"} else "",
            })
            known.pop(key, None)
        if new_events:
            with TIMELINE_EVENTS.open("a", encoding="utf-8") as stream:
                for event in new_events:
                    stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        save_timeline_state(state)
        _TIMELINE_SCAN_STAMP = stamp
        _TIMELINE_PENDING_STAMP = None
        _TIMELINE_PENDING_SINCE = None


def read_timeline(limit=100):
    global _TIMELINE_READ_STAMP, _TIMELINE_READ_DATA
    try:
        stat = TIMELINE_EVENTS.stat()
        stamp = (stat.st_mtime_ns, stat.st_size)
    except FileNotFoundError:
        stamp = (0, 0)
    with _TIMELINE_READ_LOCK:
        if stamp == _TIMELINE_READ_STAMP and _TIMELINE_READ_DATA is not None:
            return _TIMELINE_READ_DATA
        events = deque(maxlen=limit)
        total_events = 0
        if stamp != (0, 0):
            with TIMELINE_EVENTS.open("r", encoding="utf-8") as stream:
                for line in stream:
                    if line.strip():
                        events.append(json.loads(line))
                        total_events += 1
        state = json.loads(TIMELINE_STATE.read_text(encoding="utf-8")) if TIMELINE_STATE.exists() else {}
        _TIMELINE_READ_DATA = {
            "trackingSince": state.get("tracking_since", ""),
            "trackedItems": len(state.get("records", {})),
            "totalEvents": total_events,
            "events": list(reversed(events)),
            "version": f"{stamp[0]}:{stamp[1]}",
        }
        _TIMELINE_READ_STAMP = stamp
        return _TIMELINE_READ_DATA


def timeline_monitor():
    while True:
        try:
            refresh_timeline()
        except Exception as error:
            print(f"Timeline scan error: {error}")
        time.sleep(2)


def subsystem(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ("pitch", "ball", "velocity_mph", "air_density")):
        return "Pitch & ball"
    if any(k in n for k in ("swing", "bunt")):
        return "Swing & contact"
    if any(k in n for k in ("hit", "timing", "bat_chance")):
        return "Hit & timing"
    if any(k in n for k in ("stamina", "fatigue")):
        return "Stamina"
    if any(k in n for k in ("stadium", "lighting", "probe")):
        return "Stadium lighting"
    if any(k in n for k in ("broadcast", "moments", "leader")):
        return "Broadcast & leaders"
    if any(k in n for k in ("attribute", "ranked", "player_configured", "nested_payload", "default_table")):
        return "Player attributes"
    if any(k in n for k in ("record", "row_", "payload", "decode", "section", "property_map", "table_lookup", "copy", "zero_fill", "zero_", "qsort", "top_n", "global_record")):
        return "Records & parsing"
    if any(k in n for k in ("linear", "range_remap", "metric_component", "metric_compute")):
        return "Math & metrics"
    if "exif" in n:
        return "EXIF"
    return "Other"


def snapshot():
    global _CACHE_STAMP, _CACHE_DATA
    stamp = tuple((p.stat().st_mtime_ns, p.stat().st_size) for p in DATA_FILES)
    with _CACHE_LOCK:
        if stamp == _CACHE_STAMP and _CACHE_DATA is not None:
            return _CACHE_DATA

        funcs = read_tsv(DATA_FILES[0])
        annotations = read_tsv(DATA_FILES[1])
        prototypes = read_tsv(DATA_FILES[2])
        fields = read_tsv(DATA_FILES[3])
        behavior_path = ROOT / "decompiled" / "function_behavior.tsv"
        behavior_count = sum(1 for _ in behavior_path.open("r", encoding="utf-8-sig")) - 1

        by_module = defaultdict(list)
        semantic_names = {}
        readable = 0
        exported = 0
        demangled = 0
        for row in funcs:
            module = row["module"]
            by_module[module].append(row)
            if row["readable_name"] != row["generated_name"]:
                readable += 1
            is_export = bool(row["raw_elf_name"])
            exported += int(is_export)
            demangled += int(row["prototype_status"].startswith("Itanium symbol encodes"))
            if row["semantic_name"]:
                semantic_names[row["address"]] = row["semantic_name"]

        modules = []
        for module in ("main", "sdk"):
            rows = sorted(by_module[module], key=lambda x: int(x["address"], 16))
            states = bytearray()
            exact = semantic = 0
            addresses = []
            for row in rows:
                is_semantic = bool(row["semantic_name"])
                is_export = bool(row["raw_elf_name"])
                state = 2 if is_semantic else 1 if is_export else 0
                states.append(state)
                addresses.append(row["address"])
                semantic += int(is_semantic)
                exact += int(is_export)
            modules.append({
                "name": module,
                "total": len(rows),
                "semantic": semantic,
                "exported": exact,
                "addresses": addresses,
                "stateMap": base64.b64encode(states).decode("ascii"),
            })

        categories = defaultdict(Counter)
        for row in annotations:
            categories[subsystem(row["semantic_name"])][row["confidence"]] += 1
        category_rows = [
            {"name": name, "total": sum(counts.values()), "high": counts["high"], "medium": counts["medium"], "low": counts["low"]}
            for name, counts in sorted(categories.items(), key=lambda kv: (-sum(kv[1].values()), kv[0]))
        ]

        structure_counts = defaultdict(Counter)
        for row in fields:
            structure_counts[row["structure_name"]][row["confidence"]] += 1
        structures = [
            {"name": name, "total": sum(counts.values()), "high": counts["high"], "medium": counts["medium"], "low": counts["low"]}
            for name, counts in sorted(structure_counts.items(), key=lambda kv: (-sum(kv[1].values()), kv[0]))
        ]

        proto_counts = Counter(row["confidence"] for row in prototypes)
        annotation_confidence = Counter(row["confidence"] for row in annotations)
        total = len(funcs)
        semantic_total = len(annotations)
        export_only = sum(bool(row["raw_elf_name"]) and not row["semantic_name"] for row in funcs)
        unknown = total - semantic_total - export_only
        data = {
            "sourceVersion": max(value[0] for value in stamp),
            "totalFunctions": total,
            "readableNames": readable,
            "exportedSymbols": exported,
            "demangledSymbols": demangled,
            "semanticFunctions": semantic_total,
            "exportOnly": export_only,
            "addressOnly": unknown,
            "prototypeCandidates": len(prototypes),
            "prototypeConfidence": {k: proto_counts[k] for k in ("high", "medium", "low")},
            "fieldRows": len(fields),
            "fieldConfidence": {k: Counter(row["confidence"] for row in fields)[k] for k in ("high", "medium", "low")},
            "candidateStructures": len(structures),
            "annotationConfidence": {k: annotation_confidence[k] for k in ("high", "medium", "low")},
            "behaviorIndexRows": max(0, behavior_count),
            "modules": modules,
            "subsystems": category_rows,
            "structures": structures,
            "semanticNames": semantic_names,
        }
        _CACHE_STAMP, _CACHE_DATA = stamp, data
        return data


def coverage_status():
    """Small polling response; the full coverage map is fetched only on change."""
    stamp = tuple((p.stat().st_mtime_ns, p.stat().st_size) for p in DATA_FILES)
    return {"sourceVersion": max(value[0] for value in stamp)}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE), **kwargs)

    def do_GET(self):
        endpoint = unquote(self.path.split("?", 1)[0])
        if endpoint == "/api/coverage-status":
            body = json.dumps(coverage_status(), separators=(",", ":")).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if endpoint == "/api/coverage":
            body = json.dumps(snapshot(), separators=(",", ":")).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if endpoint == "/api/timeline":
            body = json.dumps(read_timeline(), separators=(",", ":")).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


if __name__ == "__main__":
    host, port = "0.0.0.0", 8765
    snapshot()
    refresh_timeline()
    threading.Thread(target=timeline_monitor, daemon=True).start()
    print(f"MLB The Show recomp dashboard: http://{host}:{port}")
    print("Serving on all network interfaces; Ctrl+C stops the server.")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
