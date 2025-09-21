# Copyright © 2025, Alexander Suvorov
import hmac
import hashlib
import base64


class HMAC_DRBG:
    def __init__(self, seed_material: bytes):
        self.K = b'\x00' * 32
        self.V = b'\x01' * 32
        self._update(seed_material)

    def _update(self, provided_data: bytes = None):
        data = provided_data if provided_data else b''
        self.K = hmac.new(self.K, self.V + b'\x00' + data, hashlib.sha256).digest()
        self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()
        if provided_data:
            self.K = hmac.new(self.K, self.V + b'\x01' + data, hashlib.sha256).digest()
            self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()

    def generate(self, num_bytes: int) -> bytes:
        temp = b''
        while len(temp) < num_bytes:
            self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()
            temp += self.V
        return temp[:num_bytes]

def encrypt_decrypt(data: bytes, key: bytes) -> bytes:
    return bytes([d ^ k for d, k in zip(data, key)])

def generate_key(master_seed: str, epoch_index: int, nonce: str, length: int) -> bytes:
    seed_material = f"{master_seed}_{epoch_index}_{nonce}".encode()
    seed_hash = hashlib.sha256(seed_material).digest()
    drbg = HMAC_DRBG(seed_hash)
    return drbg.generate(length)

def generate_nonce(signed_message: str, epoch_index: int) -> str:
    nonce_source = f"{signed_message}_{epoch_index}".encode()
    hash_bytes = hashlib.sha256(nonce_source).digest()
    nonce_b64 = base64.b64encode(hash_bytes).decode('ascii')
    nonce_clean = nonce_b64.replace('+', '-').replace('/', '_').replace('=', '')
    return nonce_clean[:16]
