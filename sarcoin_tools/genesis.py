#!/usr/bin/env python3
"""Reproduce the Sarcoin DEVELOPMENT genesis using only Python's stdlib."""
import hashlib
import json
import struct
from pathlib import Path


def sha256d(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def compact_size(n):
    if n < 253:
        return bytes([n])
    if n <= 65535:
        return b"\xfd" + struct.pack("<H", n)
    return b"\xfe" + struct.pack("<I", n)


def generate():
    message = b"Sarcoin 20/Oct/2026 - Independent development chain"
    # Matches CScript() << 486604799 << CScriptNum(4) << message.
    script_sig = bytes.fromhex("04ffff001d0104") + bytes([len(message)]) + message
    tx = (struct.pack("<i", 1) + b"\x01" + b"\x00" * 32
          + b"\xff" * 4 + compact_size(len(script_sig)) + script_sig
          + b"\xff" * 4 + b"\x01" + struct.pack("<q", 50 * 100_000_000)
          + b"\x01\x6a" + b"\x00" * 4)  # OP_RETURN: unspendable genesis.
    merkle = sha256d(tx)
    timestamp = 1792454400  # 2026-10-20 00:00:00 UTC
    bits = 0x207fffff  # Deliberately trivial DEVELOPMENT PoW.
    target = (bits & 0x7fffff) << (8 * ((bits >> 24) - 3))
    for nonce in range(2**32):
        header = struct.pack("<i", 1) + b"\x00" * 32 + merkle + struct.pack("<III", timestamp, bits, nonce)
        digest = sha256d(header)
        if int.from_bytes(digest, "little") <= target:
            return {"network": "sarcoin-devnet-v1", "timestamp_message": message.decode(),
                    "time": timestamp, "bits": f"{bits:08x}", "nonce": nonce,
                    "version": 1, "reward_satoshis": 5_000_000_000,
                    "genesis_hash": digest[::-1].hex(), "merkle_root": merkle[::-1].hex(),
                    "header_hex": header.hex(), "coinbase_hex": tx.hex(),
                    "pow_valid": True, "production_ready": False}
    raise RuntimeError("Nonce space exhausted")


if __name__ == "__main__":
    result = generate()
    output = Path(__file__).with_name("genesis.json")
    if output.exists():
        assert json.loads(output.read_text(encoding="utf-8")) == result, "Genesis manifest mismatch"
    else:
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
