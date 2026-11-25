"""Inspect and extract Switch NSP packages: PFS0 -> NCA -> (ExeFS PFS0 | RomFS | CNMT | NACP).

Usage:
    py -I tools/nxextract.py --keys PATH_TO_prod.keys [--titlekeys title.keys] NSP OUTDIR [--exefs] [--control] [--romfs-list]

Writes a JSON summary to OUTDIR/summary.json. Key material is read from the given files and never printed.
Patch (BKTR) RomFS sections are reported but not decoded.
"""
import argparse
import hashlib
import json
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from swcrypto import AesEcb, aes_ctr, aes_xts_nintendo_decrypt  # noqa: E402

CONTENT_TYPES = {0: "Program", 1: "Meta", 2: "Control", 3: "Manual", 4: "Data", 5: "PublicData"}
CNMT_TYPES = {0x80: "Application", 0x81: "Patch", 0x82: "AddOnContent", 0x83: "Delta"}
CNMT_CONTENT_TYPES = {0: "Meta", 1: "Program", 2: "Data", 3: "Control", 4: "HtmlDocument", 5: "LegalInformation",
                      6: "DeltaFragment"}


def load_keys(path):
    keys = {}
    if not path:
        return keys
    for line in Path(path).read_text(errors="ignore").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            k, v = k.strip().lower(), v.strip()
            try:
                keys[k] = bytes.fromhex(v)
            except ValueError:
                pass
    return keys


class File:
    """Bounded window into a file."""

    def __init__(self, fh, base, size):
        self.fh, self.base, self.size = fh, base, size

    def read(self, off, n):
        self.fh.seek(self.base + off)
        return self.fh.read(n)


def parse_pfs0(read, base=0):
    hdr = read(base, 16)
    magic, count, strsz = hdr[:4], *struct.unpack_from("<II", hdr, 4)
    if magic not in (b"PFS0", b"HFS0"):
        raise ValueError(f"bad PFS magic {magic!r}")
    esz = 0x18 if magic == b"PFS0" else 0x40
    entries_raw = read(base + 16, count * esz + strsz)
    strtab = entries_raw[count * esz:]
    data_off = base + 16 + count * esz + strsz
    out = []
    for i in range(count):
        off, size, noff = struct.unpack_from("<QQI", entries_raw, i * esz)
        name = strtab[noff:strtab.index(b"\0", noff)].decode()
        out.append((name, data_off + off, size))
    return out


def _bktr_info(fsh, off, hdr, phys):
    """Bucket-tree table descriptor inside an NCA fs header (sparse / compression / patch tables)."""
    toff, tsize = struct.unpack_from("<QQ", fsh, off)
    magic = fsh[hdr:hdr + 4]
    if magic != b"BKTR":
        return None
    ver, count = struct.unpack_from("<Ii", fsh, hdr + 4)
    d = {"table_offset": hex(toff), "table_size": hex(tsize), "entries": count}
    if phys is not None:
        d["physical_offset"] = hex(struct.unpack_from("<Q", fsh, phys)[0])
        d["generation"] = struct.unpack_from("<H", fsh, phys + 8)[0]
    return d


class Nca:
    def __init__(self, f: File, keys, titlekeys, tickets):
        self.f = f
        hk = keys.get("header_key")
        if not hk:
            raise SystemExit("header_key missing from keys file")
        self.hdr = aes_xts_nintendo_decrypt(hk, f.read(0, 0xC00))
        h = self.hdr
        self.magic = h[0x200:0x204]
        if self.magic not in (b"NCA3", b"NCA2"):
            raise ValueError(f"bad NCA magic {self.magic!r}")
        self.dist = h[0x204]
        self.content_type = h[0x205]
        kg_old = h[0x206]
        self.kaek_index = h[0x207]
        self.content_size, self.program_id = struct.unpack_from("<QQ", h, 0x208)
        self.content_index = struct.unpack_from("<I", h, 0x218)[0]
        sdk = struct.unpack_from("<I", h, 0x21C)[0]
        self.sdk_version = f"{(sdk >> 24) & 0xFF}.{(sdk >> 16) & 0xFF}.{(sdk >> 8) & 0xFF}.{sdk & 0xFF}"
        kg = max(kg_old, h[0x220])
        self.key_generation = kg
        self.rights_id = h[0x230:0x240]
        self.sections = []
        for i in range(4):
            start, end = struct.unpack_from("<II", h, 0x240 + i * 0x10)
            if start == 0 and end == 0:
                continue
            fsh = h[0x400 + i * 0x200: 0x600 + i * 0x200]
            self.sections.append({
                "index": i, "start": start * 0x200, "end": end * 0x200,
                "fs_type": fsh[2], "hash_type": fsh[3], "enc_type": fsh[4],
                "fsh": fsh,
                "ctr_upper": fsh[0x140:0x148].hex(),
                "sparse": _bktr_info(fsh, 0x148, 0x158, 0x168),
                "compression": _bktr_info(fsh, 0x178, 0x188, None),
                "patch_indirect": _bktr_info(fsh, 0x100, 0x110, None),
                "patch_aesctrex": _bktr_info(fsh, 0x120, 0x130, None),
            })
        # key derivation
        kidx = kg - 1 if kg > 0 else 0
        self.key = None
        if any(self.rights_id):
            rid = self.rights_id.hex()
            tk = titlekeys.get(rid) or tickets.get(rid)
            kek = keys.get(f"titlekek_{kidx:02x}")
            if tk and kek:
                self.key = AesEcb(kek).decrypt(tk)
            self.key_source = "titlekey" if self.key else "missing-titlekey"
        else:
            kak = keys.get(f"key_area_key_{['application', 'ocean', 'system'][self.kaek_index]}_{kidx:02x}")
            if kak:
                area = AesEcb(kak).decrypt(h[0x300:0x340])
                self.key = area[0x20:0x30]  # AES-CTR key slot
            self.key_source = "keyarea" if self.key else "missing-kak"

    def section_reader(self, sec):
        fsh = sec["fsh"]
        ctr_hi = fsh[0x140:0x148][::-1]
        start = sec["start"]

        def read(off, n):
            a = (off // 16) * 16
            b = ((off + n + 15) // 16) * 16
            raw = self.f.read(start + a, b - a)
            if sec["enc_type"] == 1:
                dec = raw
            elif sec["enc_type"] in (3, 4):
                dec = aes_ctr(self.key, ctr_hi, start + a, raw)
            else:
                raise ValueError(f"unsupported enc type {sec['enc_type']}")
            return dec[off - a: off - a + n]
        return read

    def pfs0_offset(self, sec):
        fsh = sec["fsh"]
        # HierarchicalSha256: master hash(0x20) blocksize layercount, then layer (offset,size) pairs
        hd = fsh[0x8:]
        layer_count = struct.unpack_from("<I", hd, 0x24)[0]
        layers = [struct.unpack_from("<QQ", hd, 0x28 + i * 16) for i in range(layer_count)]
        return layers[-1][0]

    def romfs_offset(self, sec):
        hd = sec["fsh"][0x8:]
        assert hd[:4] == b"IVFC", hd[:4]
        lvl6 = struct.unpack_from("<QQ", hd, 0x10 + 0x18 * 5)
        return lvl6[0], lvl6[1]


def parse_romfs(read, base):
    h = struct.unpack_from("<10Q", read(base, 0x50))
    _, dir_hash_off, dir_hash_sz, dir_meta_off, dir_meta_sz, file_hash_off, file_hash_sz, file_meta_off, file_meta_sz, data_off = h
    dmeta = read(base + dir_meta_off, dir_meta_sz)
    fmeta = read(base + file_meta_off, file_meta_sz)
    files = []

    def walk_dir(doff, path):
        parent, sibling, child, ffile, hsh, nlen = struct.unpack_from("<IIIIII", dmeta, doff)
        name = dmeta[doff + 0x18: doff + 0x18 + nlen].decode("utf-8", "replace")
        p = f"{path}/{name}" if name else path
        f = ffile
        while f != 0xFFFFFFFF:
            fparent, fsib, foff, fsize, fh, fnl = struct.unpack_from("<IIQQII", fmeta, f)
            fname = fmeta[f + 0x20: f + 0x20 + fnl].decode("utf-8", "replace")
            files.append((f"{p}/{fname}", base + data_off + foff, fsize))
            f = fsib
        c = child
        while c != 0xFFFFFFFF:
            walk_dir(c, p)
            c = struct.unpack_from("<I", dmeta, c + 4)[0]
    walk_dir(0, "")
    return files


def parse_cnmt(data):
    tid, ver, mtype, _, ext_sz, ccount, mcount = struct.unpack_from("<QIBBHHH", data, 0)
    out = {"title_id": f"{tid:016X}", "version": ver, "version_str": f"{ver >> 26}.{(ver >> 20) & 0x3F}.{(ver >> 16) & 0xF} (raw {ver})",
           "type": CNMT_TYPES.get(mtype, hex(mtype)), "contents": []}
    ext = data[0x20:0x20 + ext_sz]
    if mtype in (0x80, 0x81) and len(ext) >= 0x10:
        other, req = struct.unpack_from("<QI", ext, 0)
        out["patch_or_app_id"] = f"{other:016X}"
        out["required_system_version"] = req
        if mtype == 0x80:
            out["required_application_version"] = struct.unpack_from("<I", ext, 0xC)[0]
    off = 0x20 + ext_sz
    for i in range(ccount):
        rec = data[off + i * 0x38: off + (i + 1) * 0x38]
        size = int.from_bytes(rec[0x30:0x36], "little")
        out["contents"].append({"nca_id": rec[0x20:0x30].hex(), "size": size,
                                "type": CNMT_CONTENT_TYPES.get(rec[0x36], rec[0x36]), "id_offset": rec[0x37]})
    return out


def parse_nacp(d):
    langs = ["AmericanEnglish", "BritishEnglish", "Japanese", "French", "German", "LatinAmericanSpanish", "Spanish",
             "Italian", "Dutch", "CanadianFrench", "Portuguese", "Russian", "Korean", "TraditionalChinese",
             "SimplifiedChinese", "BrazilianPortuguese"]
    titles = {}
    for i, l in enumerate(langs):
        name = d[i * 0x300: i * 0x300 + 0x200].split(b"\0")[0].decode("utf-8", "replace")
        pub = d[i * 0x300 + 0x200: i * 0x300 + 0x300].split(b"\0")[0].decode("utf-8", "replace")
        if name:
            titles[l] = {"name": name, "publisher": pub}
    q = lambda o: struct.unpack_from("<Q", d, o)[0]  # noqa: E731
    return {
        "titles": titles,
        "display_version": d[0x3060:0x3070].split(b"\0")[0].decode(),
        "startup_user_account": d[0x3025],
        "supported_language_flag": hex(struct.unpack_from("<I", d, 0x302C)[0]),
        "screenshot": d[0x3034], "video_capture": d[0x3035],
        "presence_group_id": f"{q(0x3038):016X}",
        "add_on_content_base_id": f"{q(0x3070):016X}",
        "save_data_owner_id": f"{q(0x3078):016X}",
        "user_account_save_data_size": hex(q(0x3080)),
        "user_account_save_data_journal_size": hex(q(0x3088)),
        "device_save_data_size": hex(q(0x3090)),
        "device_save_data_journal_size": hex(q(0x3098)),
        "bcat_delivery_cache_storage_size": hex(q(0x30A0)),
        "local_communication_ids": [f"{q(0x30B0 + i * 8):016X}" for i in range(8) if q(0x30B0 + i * 8)],
        "logo_type": d[0x30F0], "logo_handling": d[0x30F1],
        "cache_storage_size": hex(q(0x3110)),
        "cache_storage_journal_size": hex(q(0x3118)),
        "cache_storage_data_and_journal_max": hex(q(0x3120)),
        "cache_storage_index_max": struct.unpack_from("<H", d, 0x3128)[0],
        "user_account_save_data_size_max": hex(q(0x3148)),
        "user_account_save_data_journal_size_max": hex(q(0x3150)),
        "device_save_data_size_max": hex(q(0x3158)),
        "temporary_storage_size": hex(q(0x3168)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", required=True)
    ap.add_argument("--titlekeys")
    ap.add_argument("nsp")
    ap.add_argument("outdir")
    ap.add_argument("--exefs", action="store_true")
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--romfs-list", action="store_true")
    a = ap.parse_args()
    keys = load_keys(a.keys)
    titlekeys = load_keys(a.titlekeys) if a.titlekeys else {}
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    summary = {"nsp": os.path.basename(a.nsp), "nsp_size": os.path.getsize(a.nsp), "entries": [], "ncas": []}
    fh = open(a.nsp, "rb")
    whole = File(fh, 0, summary["nsp_size"])
    entries = parse_pfs0(whole.read)
    tickets = {}
    for name, off, size in entries:
        summary["entries"].append({"name": name, "size": size})
        if name.endswith(".tik"):
            t = whole.read(off, size)
            rid = t[0x2A0:0x2B0].hex()
            tickets[rid] = t[0x180:0x190]
            summary.setdefault("tickets", []).append({"rights_id": rid, "title_key_type": t[0x241],
                                                      "key_generation": t[0x285]})
    for name, off, size in entries:
        if not name.endswith(".nca"):
            continue
        nca = Nca(File(fh, off, size), keys, titlekeys, tickets)
        info = {"file": name, "size": size, "content_type": CONTENT_TYPES.get(nca.content_type, nca.content_type),
                "program_id": f"{nca.program_id:016X}", "content_index": nca.content_index,
                "sdk_addon_version": nca.sdk_version, "key_generation": nca.key_generation,
                "rights_id": nca.rights_id.hex() if any(nca.rights_id) else None, "key_source": nca.key_source,
                "sections": [{k: v for k, v in s.items() if k != "fsh"} for s in nca.sections],
                "content_size": nca.content_size}
        summary["ncas"].append(info)
        if nca.key is None:
            continue
        for sec in nca.sections:
            sec_info = next(x for x in info["sections"] if x["index"] == sec["index"])
            if sec["sparse"] is not None:
                sec_info["note"] = ("sparse: data absent from this NCA" if sec["sparse"]["entries"] == 0
                                    else "sparse (+compressed) storage; not decoded by this tool")
                continue
            if sec["compression"] is not None:
                sec_info["note"] = "compressed storage; not decoded by this tool"
                continue
            rd = nca.section_reader(sec)
            if nca.content_type == 1 and sec["fs_type"] == 1:  # Meta
                po = nca.pfs0_offset(sec)
                for fn, foff, fsz in parse_pfs0(rd, po):
                    if fn.endswith(".cnmt"):
                        info["cnmt"] = parse_cnmt(rd(foff, fsz))
            elif nca.content_type == 0 and sec["fs_type"] == 1 and sec["index"] == 0:  # ExeFS
                po = nca.pfs0_offset(sec)
                ex = []
                for fn, foff, fsz in parse_pfs0(rd, po):
                    data = rd(foff, fsz)
                    ex.append({"name": fn, "size": fsz, "sha256": hashlib.sha256(data).hexdigest()})
                    if a.exefs:
                        (out / "exefs").mkdir(exist_ok=True)
                        (out / "exefs" / fn).write_bytes(data)
                info["exefs"] = ex
            elif sec["fs_type"] == 0 and sec["enc_type"] == 4:
                sec_info["note"] = "BKTR patch RomFS (needs base RomFS to decode)"
            elif nca.content_type == 2 and sec["fs_type"] == 0:  # Control RomFS
                ro, rs = nca.romfs_offset(sec)
                files = parse_romfs(rd, ro)
                info["control_files"] = [f for f, _, _ in files]
                for fn, foff, fsz in files:
                    if fn.endswith("control.nacp"):
                        info["nacp"] = parse_nacp(rd(foff, fsz))
                    if a.control:
                        p = out / "control" / fn.lstrip("/")
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_bytes(rd(foff, fsz))
            elif nca.content_type == 0 and sec["fs_type"] == 0 and a.romfs_list:  # Program RomFS (base)
                ro, rs = nca.romfs_offset(sec)
                files = parse_romfs(rd, ro)
                with open(out / "romfs_list.tsv", "w", encoding="utf-8") as lf:
                    for fn, foff, fsz in files:
                        lf.write(f"{fsz}\t{fn}\n")
                info["romfs_file_count"] = len(files)
                info["romfs_total_bytes"] = sum(s for _, _, s in files)
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    for n in summary["ncas"]:
        print(n["file"], n["content_type"], n["program_id"], n["key_source"], n.get("cnmt", {}).get("version_str", ""))


if __name__ == "__main__":
    main()
