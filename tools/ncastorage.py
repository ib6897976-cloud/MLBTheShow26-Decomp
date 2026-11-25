"""NCA storage layers needed for patched/sparse/compressed RomFS (behaviour as described by Atmosphere's fssystem;
independent implementation).

Layer order for a patch NCA RomFS section (NcaFileSystemDriver::OpenStorageImpl / CreateStorageByRawStorage):
    body -> AesCtrEx (patch data)                                          \
    original: base body -> Sparse -> AesCtr  (OpenIndirectableStorageAsOriginal) -> Indirect -> IVFC data level
    -> Compressed (LZ4) -> RomFS

All storages expose .size and .read(offset, length).
"""
import bisect
import struct
from collections import OrderedDict

import lz4.block
import numpy as np

from swcrypto import aes_ctr

NODE_SIZE = 0x4000


class FileStorage:
    def __init__(self, fh, base, size):
        self.fh, self.base, self.size = fh, base, size

    def read(self, off, n):
        if n <= 0:
            return b""
        self.fh.seek(self.base + off)
        d = self.fh.read(n)
        if len(d) != n:
            raise IOError(f"short read at {self.base + off:#x}: {len(d)} of {n}")
        return d


class SubStorage:
    def __init__(self, base, off, size):
        self.base, self.off, self.size = base, off, size

    def read(self, off, n):
        assert off >= 0 and off + n <= self.size, (hex(off), hex(n), hex(self.size))
        return self.base.read(self.off + off, n)


class ZeroStorage:
    size = 1 << 62

    def read(self, off, n):
        return bytes(n)


def make_iv(upper_u64):
    return upper_u64.to_bytes(8, "big")


class AesCtrStorage:
    """Counter = upper_iv (BE u64) || BE u64((counter_offset + offset) >> 4)."""

    def __init__(self, base, key, upper_u64, counter_offset):
        self.base, self.key, self.iv, self.counter_offset = base, key, make_iv(upper_u64), counter_offset
        self.size = base.size

    def read(self, off, n):
        a = off & ~0xF
        b = min((off + n + 15) & ~0xF, self.size)
        raw = self.base.read(a, b - a)
        pad = (-len(raw)) % 16
        dec = aes_ctr(self.key, self.iv, self.counter_offset + a, raw + bytes(pad))
        return dec[off - a: off - a + n]


def read_bucket_tree(meta, header16, entry_size):
    """Return (entries_bytes_list, end_offset). meta: storage holding node storage then entry storage."""
    magic, ver, count = header16[:4], *struct.unpack_from("<Ii", header16, 4)
    assert magic == b"BKTR", magic
    if count == 0:
        return [], 0
    per_set = (NODE_SIZE - 16) // entry_size
    set_count = -(-count // per_set)
    offset_count = (NODE_SIZE - 16) // 8
    if set_count <= offset_count:
        l2 = 0
    else:
        l2c = -(-set_count // offset_count)
        l2 = -(-(set_count - (offset_count - (l2c - 1))) // offset_count)
    node_storage_size = (1 + l2) * NODE_SIZE
    l1 = meta.read(0, 16)
    _, _, end_offset = struct.unpack("<iiq", l1)
    blob = meta.read(node_storage_size, set_count * NODE_SIZE)
    out = []
    for s in range(set_count):
        idx, cnt, set_end = struct.unpack_from("<iiq", blob, s * NODE_SIZE)
        base = s * NODE_SIZE + 16
        out.append(blob[base: base + cnt * entry_size])
    raw = b"".join(out)
    assert len(raw) == count * entry_size, (len(raw), count, entry_size)
    return raw, end_offset


class _Ranged:
    """Common logic: sorted virtual offsets, each entry covers [v[i], v[i+1])."""

    def _setup(self, virts, end):
        self.virts = virts
        self.end = end
        self.size = end

    def _spans(self, off, n):
        i = bisect.bisect_right(self.virts, off) - 1
        assert i >= 0, hex(off)
        cur, stop = off, off + n
        while cur < stop:
            e_start = self.virts[i]
            e_end = self.virts[i + 1] if i + 1 < len(self.virts) else self.end
            take = min(stop, e_end) - cur
            yield i, cur - e_start, take
            cur += take
            i += 1


class SparseStorage(_Ranged):
    """Indirect-style entries; storage index 0 = data, 1 = zeros."""

    def __init__(self, data, raw, end):
        a = np.frombuffer(raw, dtype=[("v", "<i8"), ("p", "<i8"), ("s", "<i4")])
        self._setup(a["v"].tolist(), end)
        self.phys, self.idx, self.data = a["p"].tolist(), a["s"].tolist(), data

    def read(self, off, n):
        parts = []
        for i, rel, take in self._spans(off, n):
            parts.append(self.data.read(self.phys[i] + rel, take) if self.idx[i] == 0 else bytes(take))
        return b"".join(parts)


class IndirectStorage(_Ranged):
    def __init__(self, storages, raw, end):
        a = np.frombuffer(raw, dtype=[("v", "<i8"), ("p", "<i8"), ("s", "<i4")])
        self._setup(a["v"].tolist(), end)
        self.phys, self.idx, self.storages = a["p"].tolist(), a["s"].tolist(), storages

    def read(self, off, n):
        return b"".join(self.storages[self.idx[i]].read(self.phys[i] + rel, take) for i, rel, take in self._spans(off, n))


class AesCtrExStorage(_Ranged):
    def __init__(self, data, key, secure_value, counter_offset, raw, end):
        a = np.frombuffer(raw, dtype=[("o", "<i8"), ("e", "u1"), ("r", "V3"), ("g", "<i4")])
        self._setup(a["o"].tolist(), end)
        self.enc, self.gen = a["e"].tolist(), a["g"].tolist()
        self.data, self.key, self.secure, self.counter_offset = data, key, secure_value, counter_offset
        self.size = data.size

    def read(self, off, n):
        parts = []
        for i, rel, take in self._spans(off, n):
            start = self.virts[i] + rel
            if self.enc[i] == 0:
                upper = (self.secure << 32) | (self.gen[i] & 0xFFFFFFFF)
                parts.append(AesCtrStorage(self.data, self.key, upper, self.counter_offset).read(start, take))
            else:
                parts.append(self.data.read(start, take))
        return b"".join(parts)


class CompressedStorage(_Ranged):
    def __init__(self, data, raw, end, cache_entries=64):
        a = np.frombuffer(raw, dtype=[("v", "<i8"), ("p", "<i8"), ("t", "u1"), ("l", "i1"), ("r", "V2"), ("ps", "<i4")])
        self._setup(a["v"].tolist(), end)
        self.phys, self.type, self.psize = a["p"].tolist(), a["t"].tolist(), a["ps"].tolist()
        self.data = data
        self.cache = OrderedDict()
        self.cache_entries = cache_entries
        self.type_counts = {int(k): int(v) for k, v in zip(*np.unique(a["t"], return_counts=True))}

    def _entry(self, i):
        if i in self.cache:
            self.cache.move_to_end(i)
            return self.cache[i]
        vsize = (self.virts[i + 1] if i + 1 < len(self.virts) else self.end) - self.virts[i]
        t = self.type[i]
        if t == 1:
            d = bytes(vsize)
        elif t == 0:
            d = self.data.read(self.phys[i], vsize)
        elif t == 3:
            d = lz4.block.decompress(self.data.read(self.phys[i], self.psize[i]), uncompressed_size=vsize)
        else:
            raise ValueError(f"unsupported compression type {t}")
        self.cache[i] = d
        if len(self.cache) > self.cache_entries:
            self.cache.popitem(last=False)
        return d

    def read(self, off, n):
        parts = []
        for i, rel, take in self._spans(off, n):
            if self.type[i] == 0:
                parts.append(self.data.read(self.phys[i] + rel, take))
            elif self.type[i] == 1:
                parts.append(bytes(take))
            else:
                parts.append(self._entry(i)[rel: rel + take])
        return b"".join(parts)


# ---------------------------------------------------------------- NCA section helpers

def fsh_fields(fsh):
    f = {}
    f["upper"] = struct.unpack_from("<Q", fsh, 0x140)[0]
    f["secure_value"] = struct.unpack_from("<I", fsh, 0x144)[0]
    f["indirect"] = struct.unpack_from("<QQ", fsh, 0x100) + (fsh[0x110:0x120],)
    f["aesctrex"] = struct.unpack_from("<QQ", fsh, 0x120) + (fsh[0x130:0x140],)
    f["sparse"] = struct.unpack_from("<QQ", fsh, 0x148) + (fsh[0x158:0x168],) + struct.unpack_from("<QH", fsh, 0x168)
    f["compression"] = struct.unpack_from("<QQ", fsh, 0x178) + (fsh[0x188:0x198],)
    hd = fsh[0x8:]
    if hd[:4] == b"IVFC":
        lv = [struct.unpack_from("<QQI", hd, 0x10 + 0x18 * i) for i in range(6)]
        f["ivfc_levels"] = lv
        f["ivfc_master_hash"] = hd[0xC0:0xE0]
    return f


def _has(bk):
    return bk[3 - 1][:4] == b"BKTR" if len(bk) >= 3 else False


def original_storage(nca, sec):
    """Base NCA section as the patch's 'original' (sparse + AesCtr, no integrity/compression)."""
    fsh = sec["fsh"]
    f = fsh_fields(fsh)
    fs_offset, fs_end = sec["start"], sec["end"]
    meta_off, meta_size, hdr, phys_off, gen = f["sparse"]
    if hdr[:4] == b"BKTR":
        count = struct.unpack_from("<i", hdr, 8)[0]
        if count == 0:
            return ZeroStorage()
        phys_size = meta_off + meta_size
        body = FileStorage(nca.f.fh, nca.f.base + phys_off, phys_size)
        sparse_upper = (f["secure_value"] << 32) | ((gen << 16) & 0xFFFFFFFF)
        meta = AesCtrStorage(SubStorage(body, meta_off, meta_size), nca.key, sparse_upper, phys_off + meta_off)
        raw, end = read_bucket_tree(meta, hdr, 0x14)
        sp = SparseStorage(body, raw, end)
        return AesCtrStorage(sp, nca.key, f["upper"], fs_offset)
    body = FileStorage(nca.f.fh, nca.f.base + fs_offset, fs_end - fs_offset)
    return AesCtrStorage(body, nca.key, f["upper"], fs_offset)


def patched_romfs(patch_nca, patch_sec, base_nca, base_sec):
    """Returns (romfs_storage, info) for a patch RomFS section over its base."""
    fsh = patch_sec["fsh"]
    f = fsh_fields(fsh)
    fs_offset, fs_end = patch_sec["start"], patch_sec["end"]
    body = FileStorage(patch_nca.f.fh, patch_nca.f.base + fs_offset, fs_end - fs_offset)
    ex_off, ex_size, ex_hdr = f["aesctrex"]
    ex_meta = AesCtrStorage(SubStorage(body, ex_off, (ex_size + 0x1FF) & ~0x1FF), patch_nca.key, f["upper"], fs_offset + ex_off)
    ex_raw, ex_end = read_bucket_tree(ex_meta, ex_hdr, 0x10)
    ex = AesCtrExStorage(SubStorage(body, 0, ex_off), patch_nca.key, f["secure_value"], fs_offset, ex_raw, ex_end)
    ind_off, ind_size, ind_hdr = f["indirect"]
    ind_raw, ind_end = read_bucket_tree(SubStorage(ex, ind_off, ind_size), ind_hdr, 0x14)
    orig = original_storage(base_nca, base_sec)
    ind = IndirectStorage([orig, SubStorage(ex, 0, ind_off)], ind_raw, ind_end)
    lv = f["ivfc_levels"]
    data_off, data_size = lv[5][0], lv[5][1]
    ivfc_data = SubStorage(ind, data_off, data_size)
    info = {"indirect_entries": len(ind.virts), "indirect_end": ind_end, "aesctrex_entries": len(ex.virts),
            "ivfc_data_offset": data_off, "ivfc_data_size": data_size, "ivfc": ind, "levels": lv}
    c_off, c_size, c_hdr = f["compression"]
    if c_hdr[:4] == b"BKTR" and struct.unpack_from("<i", c_hdr, 8)[0] > 0:
        c_raw, c_end = read_bucket_tree(SubStorage(ivfc_data, c_off, c_size), c_hdr, 0x18)
        cs = CompressedStorage(SubStorage(ivfc_data, 0, c_off), c_raw, c_end)
        info.update(compression_entries=len(cs.virts), compressed_virtual_size=c_end, compression_types=cs.type_counts)
        return cs, info
    return ivfc_data, info
