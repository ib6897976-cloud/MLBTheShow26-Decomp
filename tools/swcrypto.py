"""Minimal AES primitives for Switch container parsing, backed by Windows CNG (bcrypt.dll).

No third-party dependencies. Provides AES-128-ECB, AES-128-CTR and the Nintendo
variant of AES-128-XTS (big-endian sector tweak) used for NCA headers.
"""
import ctypes
import ctypes.wintypes as wt
import numpy as np

_bcrypt = ctypes.WinDLL("bcrypt.dll")
_BCRYPT_ALG = ctypes.c_void_p


def _check(status, what):
    if status != 0:
        raise OSError(f"{what} failed: NTSTATUS 0x{status & 0xFFFFFFFF:08X}")


_alg = _BCRYPT_ALG()
_check(_bcrypt.BCryptOpenAlgorithmProvider(ctypes.byref(_alg), ctypes.c_wchar_p("AES"), None, 0), "OpenAlg")
_mode = ctypes.create_unicode_buffer("ChainingModeECB")
_check(_bcrypt.BCryptSetProperty(_alg, ctypes.c_wchar_p("ChainingMode"), _mode,
                                 ctypes.sizeof(_mode), 0), "SetProperty")


class AesEcb:
    def __init__(self, key: bytes):
        assert len(key) in (16, 32)
        self._h = ctypes.c_void_p()
        kb = ctypes.create_string_buffer(key, len(key))
        _check(_bcrypt.BCryptGenerateSymmetricKey(_alg, ctypes.byref(self._h), None, 0, kb, len(key), 0),
               "GenerateKey")

    def _run(self, fn, data: bytes) -> bytes:
        assert len(data) % 16 == 0
        n = len(data)
        inp = ctypes.create_string_buffer(bytes(data), n)
        out = ctypes.create_string_buffer(n)
        res = wt.ULONG()
        _check(fn(self._h, inp, n, None, None, 0, out, n, ctypes.byref(res), 0), "Crypt")
        return out.raw[:n]

    def encrypt(self, data: bytes) -> bytes:
        return self._run(_bcrypt.BCryptEncrypt, data)

    def decrypt(self, data: bytes) -> bytes:
        return self._run(_bcrypt.BCryptDecrypt, data)

    def __del__(self):
        try:
            _bcrypt.BCryptDestroyKey(self._h)
        except Exception:
            pass


def aes_ctr(key: bytes, iv_high8: bytes, offset: int, data: bytes) -> bytes:
    """AES-CTR as used in NCA sections: counter = iv_high8 || be64(offset >> 4)."""
    assert offset % 16 == 0
    n = len(data)
    nblocks = (n + 15) // 16
    start = offset >> 4
    ctrs = np.zeros((nblocks, 16), dtype=np.uint8)
    ctrs[:, :8] = np.frombuffer(iv_high8, dtype=np.uint8)
    idx = np.arange(start, start + nblocks, dtype=np.uint64)
    ctrs[:, 8:] = idx.astype(">u8").view(np.uint8).reshape(-1, 8)
    ks = np.frombuffer(AesEcb(key).encrypt(ctrs.tobytes()), dtype=np.uint8)[:n]
    return (np.frombuffer(data, dtype=np.uint8) ^ ks).tobytes()


def _gf_mul_x(t: np.ndarray) -> np.ndarray:
    # multiply 128-bit little-endian value by x in GF(2^128)
    v = int.from_bytes(t.tobytes(), "little")
    v <<= 1
    if v >> 128:
        v = (v & ((1 << 128) - 1)) ^ 0x87
    return np.frombuffer(v.to_bytes(16, "little"), dtype=np.uint8)


def aes_xts_nintendo_decrypt(key32: bytes, data: bytes, sector: int = 0, sector_size: int = 0x200) -> bytes:
    k1, k2 = AesEcb(key32[:16]), AesEcb(key32[16:])
    out = bytearray()
    for s in range(len(data) // sector_size):
        tweak = np.frombuffer(k2.encrypt((sector + s).to_bytes(16, "big")), dtype=np.uint8)
        chunk = np.frombuffer(data[s * sector_size:(s + 1) * sector_size], dtype=np.uint8).reshape(-1, 16)
        tw = np.empty_like(chunk)
        t = tweak.copy()
        for i in range(chunk.shape[0]):
            tw[i] = t
            t = _gf_mul_x(t)
        pt = np.frombuffer(k1.decrypt((chunk ^ tw).tobytes()), dtype=np.uint8).reshape(-1, 16) ^ tw
        out += pt.tobytes()
    return bytes(out)
