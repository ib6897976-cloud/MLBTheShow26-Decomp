"""Interactive read-only MPH value scanner for the MLBTS recomp on Windows."""

from __future__ import annotations

import ctypes
import math
import os
import struct
import sys
import time
from ctypes import wintypes


PROCESS_NAME = "mlb.exe"
POLL_SECONDS = 0.1
GUEST_START = 0x100000000  # dynamic guest allocations are below the fixed modules
GUEST_END = 1 << 39  # runtime/core/host.h: RT_ADDRESS_LIMIT
CHUNK_SIZE = 8 * 1024 * 1024
RECORD_SIZE = 0x490

PITCH_FLAG = int(os.environ.get("MLBTS_PITCH_FLAG", "0x482"), 0)
SPEED_X = int(os.environ.get("MLBTS_SPEED_X_OFFSET", "0x454"), 0)
SPEED_Y = int(os.environ.get("MLBTS_SPEED_Y_OFFSET", "0x458"), 0)
POSITION = int(os.environ.get("MLBTS_POSITION_OFFSET", "0x420"), 0)
AIM = int(os.environ.get("MLBTS_AIM_OFFSET", "0x42c"), 0)

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
MEM_PRIVATE = 0x20000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100
WRITABLE_PROTECTIONS = {0x04, 0x08, 0x40, 0x80}
TH32CS_SNAPPROCESS = 0x00000002


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG),
                ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260)]


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
OpenProcess.restype = wintypes.HANDLE
ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                              ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = wintypes.BOOL
VirtualQueryEx = kernel32.VirtualQueryEx
VirtualQueryEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                           ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t]
VirtualQueryEx.restype = ctypes.c_size_t
CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
CreateToolhelp32Snapshot.restype = wintypes.HANDLE
Process32FirstW = kernel32.Process32FirstW
Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
Process32FirstW.restype = wintypes.BOOL
Process32NextW = kernel32.Process32NextW
Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
Process32NextW.restype = wintypes.BOOL


def find_process_id(name: str):
    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == wintypes.HANDLE(-1).value:
        return None
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        if Process32FirstW(snapshot, ctypes.byref(entry)):
            while True:
                if entry.szExeFile.lower() == name.lower():
                    return entry.th32ProcessID
                if not Process32NextW(snapshot, ctypes.byref(entry)):
                    break
    finally:
        CloseHandle(snapshot)
    return None


def read_bytes(handle: int, address: int, size: int) -> bytes | None:
    buf = ctypes.create_string_buffer(size)
    received = ctypes.c_size_t()
    ok = ReadProcessMemory(handle, ctypes.c_void_p(address), buf, size,
                           ctypes.byref(received))
    if not ok or received.value != size:
        return None
    return buf.raw


def readable_regions(handle: int, low=GUEST_START, high=GUEST_END):
    mbi = MEMORY_BASIC_INFORMATION()
    addr = low
    while addr < high:
        if not VirtualQueryEx(handle, ctypes.c_void_p(addr), ctypes.byref(mbi),
                              ctypes.sizeof(mbi)):
            break
        base = int(mbi.BaseAddress or 0)
        size = int(mbi.RegionSize)
        end = base + size
        if end <= addr:  # protect against an invalid query result
            break
        protect = int(mbi.Protect)
        if (mbi.State == MEM_COMMIT and mbi.Type == MEM_PRIVATE
                and (protect & 0xFF) in WRITABLE_PROTECTIONS
                and not (protect & (PAGE_NOACCESS | PAGE_GUARD))
                and base < high and end > low):
            yield max(base, low), min(end, high)
        addr = end


def parse_record(data: bytes, offset: int):
    if data[offset + PITCH_FLAG] == 0:
        return None
    sx, sy = struct.unpack_from("<ff", data, offset + SPEED_X)
    pos = struct.unpack_from("<fff", data, offset + POSITION)
    aim = struct.unpack_from("<fff", data, offset + AIM)
    if not all(math.isfinite(v) for v in (sx, sy, *pos, *aim)):
        return None
    if any(abs(v) > 10000.0 for v in (*pos, *aim)):
        return None
    return sx, sy, pos, aim


def speed_offset_for_address(address: int):
    # The guest actor can be 8-byte aligned rather than 16-byte aligned.
    possible = [offset for offset in (SPEED_X, SPEED_Y)
                if (address - offset) % 8 == 0]
    if len(possible) == 1:
        return possible[0]
    return None


def scan_mph_candidates(handle: int, target: float, tolerance: float):
    """Find aligned float values near target in writable guest memory."""
    # Keep the probe count bounded even when the user enters a wide tolerance.
    # For HUD speeds shown to one decimal place, 0.05 mph steps cover every
    # displayed tenth while avoiding hundreds of full-memory passes.
    step = max(0.01, tolerance / 20.0)
    steps = max(0, int(math.ceil(tolerance / step)))
    patterns = {struct.pack("<f", target + n * step)
                for n in range(-steps, steps + 1)}
    found = set()
    scanned = 0
    last_status = 0
    print(f"Scanning for {target:.2f} +/- {tolerance:.2f} mph "
          f"({len(patterns)} float probes across writable guest memory)...")

    for start, end in readable_regions(handle):
        cursor = start
        while cursor + RECORD_SIZE <= end:
            amount = min(CHUNK_SIZE, end - cursor)
            block = read_bytes(handle, cursor, amount)
            if block is None:
                cursor += amount
                continue
            is_last = cursor + amount >= end
            unique_bases = amount if is_last else amount - RECORD_SIZE + 1
            for pattern in patterns:
                pos = block.find(pattern)
                while pos >= 0:
                    address = cursor + pos
                    if address % 4 == 0 and pos < unique_bases:
                        found.add(address)
                    pos = block.find(pattern, pos + 1)
            scanned += amount
            if scanned - last_status >= 64 * 1024 * 1024:
                print(f"\rInitial mph scan: {scanned / (1024 * 1024):,.0f} MiB; "
                      f"{len(found)} matching address(es)...", end="", flush=True)
                last_status = scanned
            if is_last:
                break
            cursor += unique_bases

    print(f"\rInitial scan complete: {len(found)} matching address(es).                    ")
    return found


def refine_mph_candidates(handle: int, candidates, target: float, tolerance: float):
    kept = set()
    for address in candidates:
        data = read_bytes(handle, address, 4)
        if data is None:
            continue
        value = struct.unpack("<f", data)[0]
        if math.isfinite(value) and abs(value - target) <= tolerance:
            kept.add(address)
    return kept


def candidate_record(handle: int, speed_address: int):
    offset = speed_offset_for_address(speed_address)
    if offset is None:
        return None
    base = speed_address - offset
    data = read_bytes(handle, base, RECORD_SIZE)
    if data is None:
        return None
    flag = data[PITCH_FLAG]
    record = parse_record(data, 0) if data else None
    return base, offset, flag, record


def actor_context(handle: int, speed_address: int):
    candidate = candidate_record(handle, speed_address)
    if candidate is None:
        return None
    base, offset, flag, record = candidate
    if flag == 0 or record is None:
        return None
    return base, offset, record


def show_candidates(handle: int, candidates, maximum=20):
    print(f"Survivors: {len(candidates)}")
    rows = []
    for address in candidates:
        data = read_bytes(handle, address, 4)
        if data is None:
            continue
        speed = struct.unpack("<f", data)[0]
        candidate = candidate_record(handle, address)
        if candidate and candidate[3] is not None:
            base, offset, _, record = candidate
            _, _, pos, aim = record
            delta = tuple(p - a for p, a in zip(pos, aim))
            detail = (f"actor 0x{base:X} +0x{offset:X}; break "
                      f"{delta[0]:+.3f}, {delta[1]:+.3f}, {delta[2]:+.3f}")
        else:
            if candidate:
                base, offset, flag, _ = candidate
                state = "inactive" if flag == 0 else "coordinates not ready"
                detail = f"possible base 0x{base:X} +0x{offset:X}; flag={flag}, {state}"
            else:
                detail = "no aligned pitch-field base"
        has_context = bool(candidate and candidate[3] is not None)
        rows.append((not has_context, address, speed, detail))
    rows.sort(key=lambda row: (row[0], row[1]))
    contextual = sum(1 for row in rows if not row[0])
    print(f"Pitch-record context matches: {contextual}")
    for _, address, speed, detail in rows[:maximum]:
        print(f"  0x{address:X} {speed:.3f} mph | {detail}")
    if len(rows) > maximum:
        print(f"  ... {len(rows) - maximum} more")


def watch_single_candidate(handle: int, address: int):
    offset = speed_offset_for_address(address)
    base = address - offset if offset is not None else None
    base_text = f"0x{base:X} (+0x{offset:X})" if base is not None else "not aligned"
    print(f"Watching 0x{address:X}; candidate base {base_text}; "
          "Ctrl+C returns to the value filter.")
    try:
        while True:
            data = read_bytes(handle, address, 4)
            if data:
                speed = struct.unpack("<f", data)[0]
                candidate = candidate_record(handle, address)
                if candidate and candidate[3] is not None:
                    _, _, _, record = candidate
                    _, _, pos, aim = record
                    delta = tuple(p - a for p, a in zip(pos, aim))
                    break_text = (f"{delta[0]:+8.3f}, {delta[1]:+8.3f}, "
                                  f"{delta[2]:+8.3f} world units")
                elif candidate:
                    cbase, coffset, flag, _ = candidate
                    state = "inactive" if flag == 0 else "coordinates not ready"
                    break_text = f"waiting for live pitch record (base 0x{cbase:X}, flag={flag} {state})"
                else:
                    break_text = "no aligned pitch-record base"
                print(f"\rSPEED X: {speed:6.2f} mph | BREAK X/Y/Z: "
                      f"{break_text}",
                      end="", flush=True)
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("\nBack to the value filter.")


def main():
    if sys.platform != "win32":
        print("This monitor needs Windows and the MLBTS recomp.")
        return 2
    print("MLBTS pitch speed value scanner (read-only)")
    print(f"Waiting for {PROCESS_NAME}...")
    handle = None
    try:
        pid = None
        while pid is None:
            pid = find_process_id(PROCESS_NAME)
            if pid is None:
                time.sleep(1)
        handle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if not handle:
            print(f"Could not open {PROCESS_NAME}; run this console as the same user.")
            return 1
        print(f"Attached to {PROCESS_NAME} (PID {pid}).")

        while True:
            first = input("Enter a known pitch speed in mph (q quits): ").strip()
            if first.lower() == "q":
                break
            try:
                target = float(first)
                if not math.isfinite(target) or target <= 0:
                    raise ValueError
            except ValueError:
                print("Enter a positive mph number.")
                continue
            tol_text = input("Tolerance in mph [0.10]: ").strip()
            try:
                tolerance = float(tol_text) if tol_text else 0.10
                if not math.isfinite(tolerance) or tolerance < 0:
                    raise ValueError
            except ValueError:
                print("Tolerance must be zero or greater.")
                continue

            candidates = scan_mph_candidates(handle, target, tolerance)
            show_candidates(handle, candidates)
            while candidates:
                prompt = ("Next pitch mph to narrow | w=watch survivor | "
                          "r=restart | q=quit: ")
                command = input(prompt).strip()
                if command.lower() == "q":
                    return 0
                if command.lower() == "r":
                    break
                if command.lower() == "w":
                    if len(candidates) != 1:
                        print("Narrow to one address first by entering more known pitch speeds.")
                    else:
                        address = next(iter(candidates))
                        watch_single_candidate(handle, address)
                    continue
                try:
                    next_speed = float(command)
                    if not math.isfinite(next_speed) or next_speed <= 0:
                        raise ValueError
                except ValueError:
                    print("Enter the next pitch's mph, w, r, or q.")
                    continue
                candidates = refine_mph_candidates(handle, candidates, next_speed, tolerance)
                target = next_speed
                show_candidates(handle, candidates)
            if not candidates:
                print("No addresses survived. Restart with the observed mph and a wider tolerance.")
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if handle:
            CloseHandle(handle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
