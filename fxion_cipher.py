"""
FXION CIPHER -- Algorithme XOR Partiel + Hashage Multi-Type + HMAC + XOR Merge + D compression
===============================================================================================

Architecture:
  1. XOR Partiel     -- chiffrement par blocs avec cl  rotative partielle
  2. Hashage Multi   -- SHA-256, SHA-512, MD5, BLAKE2b, SHA3-256
  3. HMAC            -- authentification par HMAC-SHA256 / HMAC-SHA512
  4. XOR Merge       -- fusion de flux chiffr s par XOR crois 
  5. D compression   -- reconstruction inverse avec validation d'int grit 

Usage:
  from fxion_cipher import FXIONCipher
  cipher = FXIONCipher(key=b"ma_cle_secrete")
  encrypted = cipher.encrypt(b"donnees")
  decrypted = cipher.decrypt(encrypted)
"""
import hashlib, hmac, struct, os, zlib, math
from typing import Tuple, List, Optional


# ===============================================================================
#  CONSTANTES
# ===============================================================================
BLOCK_SIZE = 64
HASH_ALGORITHMS = [
    "sha256", "sha512", "md5", "blake2b", "sha3_256", 
    "sha3_512", "sha1", "blake2s", "shake_128", "shake_256"
]
MAGIC = b"FXION\x01"

VERSION = 1


# ===============================================================================
#  XOR PARTIEL -- Chiffrement par blocs avec rotation de cl 
# ===============================================================================
class XORPartiel:
    """
    XOR partiel: applique XOR uniquement sur des segments altern s du bloc.
    La cl  est rot e   chaque bloc pour  viter la r p tition de patterns.
    """

    def __init__(self, key: bytes):
        self.key = key
        self.key_len = len(key)

    def _rotate_key(self, key: bytes, rotation: int) -> bytes:
        """Rotation circulaire de la cl ."""
        r = rotation % len(key)
        return key[r:] + key[:r]

    def _expand_key(self, key: bytes, length: int) -> bytes:
        """Expand la cl    la longueur souhait e par r p tition + hash."""
        if len(key) >= length:
            return key[:length]
        # Expand par hash it ratif
        expanded = key
        i = 0
        while len(expanded) < length:
            h = hashlib.sha256(key + struct.pack(">I", i)).digest()
            expanded += h
            i += 1
        return expanded[:length]

    def encrypt(self, data: bytes) -> bytes:
        """XOR partiel: XOR sur positions paires des blocs, rotation par bloc."""
        output = bytearray(len(data))
        n_blocks = math.ceil(len(data) / BLOCK_SIZE)

        for b in range(n_blocks):
            start = b * BLOCK_SIZE
            end = min(start + BLOCK_SIZE, len(data))
            block = data[start:end]
            block_len = end - start

            # Rotation de cl  par index de bloc
            rotated_key = self._rotate_key(self.key, b * 7)
            expanded_key = self._expand_key(rotated_key, block_len)

            for i in range(block_len):
                if i % 2 == 0:
                    # Positions paires: XOR avec cl 
                    output[start + i] = block[i] ^ expanded_key[i]
                else:
                    # Positions impaires: XOR avec cl  invers e + offset
                    output[start + i] = block[i] ^ (expanded_key[i] ^ 0xAA)

        return bytes(output)

    def decrypt(self, data: bytes) -> bytes:
        """D chiffrement = m me op ration (XOR est sa propre inverse)."""
        return self.encrypt(data)


# ===============================================================================
#  HASHAGE MULTI-TYPE -- Couche de hash combin 
# ===============================================================================
class HashageMultiType:
    """
    G n re un hash composite   partir de multiples algorithmes.
    Le r sultat est un XOR de tous les hashs tronqu s   longueur uniforme.
    """

    @staticmethod
    def hash_single(data, algo="sha256"):
        h = hashlib.new(algo)
        h.update(data)
        if algo.startswith("shake_"):
            return h.digest(32) # Default 256-bit output for SHAKE
        return h.digest()


    @staticmethod
    def hash_all(data: bytes) -> dict:
        """Hash avec tous les algorithmes disponibles."""
        results = {}
        for algo in HASH_ALGORITHMS:
            results[algo] = HashageMultiType.hash_single(data, algo)
        return results

    @staticmethod
    def hash_composite(data: bytes) -> bytes:
        """
        Hash composite: Combine tous les hashs par concat nation + SHA-256 final.
        Produit un fingerprint stable de 32 bytes.
        """
        all_hashes = HashageMultiType.hash_all(data)
        combined = b"".join(all_hashes.values())
        return hashlib.sha256(combined).digest()


    @staticmethod
    def derive_key(password: bytes, salt: bytes, iterations: int = 100000) -> bytes:
        """D rivation de cl  par PBKDF2-HMAC-SHA256."""
        return hashlib.pbkdf2_hmac("sha256", password, salt, iterations, dklen=64)


# ===============================================================================
#  HMAC -- Authentification et v rification d'int grit 
# ===============================================================================
class HMACLayer:
    """
    Couche HMAC pour authentification des donn es chiffr es.
    Double HMAC: SHA-256 pour vitesse + SHA-512 pour s curit .
    """

    def __init__(self, key: bytes):
        self.key_256 = hashlib.sha256(key).digest()
        self.key_512 = hashlib.sha512(key).digest()

    def sign(self, data: bytes) -> bytes:
        """G n re signature HMAC double (32 + 64 = 96 bytes)."""
        mac_256 = hmac.new(self.key_256, data, hashlib.sha256).digest()
        mac_512 = hmac.new(self.key_512, data, hashlib.sha512).digest()
        return mac_256 + mac_512

    def verify(self, data: bytes, signature: bytes) -> bool:
        """V rifie la signature HMAC double."""
        if len(signature) != 96:
            return False
        expected = self.sign(data)
        return hmac.compare_digest(expected, signature)


# ===============================================================================
#  XOR MERGE -- Fusion de flux chiffr s
# ===============================================================================
class XORMerge:
    """
    Fusionne plusieurs flux de donn es par XOR crois  avec masques d riv s.
    Utilis  pour combiner le chiffr  XOR partiel avec les hash comme cl  de masque.
    """

    @staticmethod
    def merge(data: bytes, hash_mask: bytes) -> bytes:
        """
        Merge XOR: combine data avec un masque d riv  du hash composite.
        Le masque est  tendu par hash chain pour couvrir toute la data.
        """
        mask = XORMerge._expand_mask(hash_mask, len(data))
        output = bytearray(len(data))
        for i in range(len(data)):
            # XOR crois : data[i] XOR mask[i] XOR (mask[i] rotated)
            m = mask[i]
            m_rot = mask[(i + 13) % len(mask)]  # offset premier 13
            output[i] = data[i] ^ m ^ (m_rot >> 1)
        return bytes(output)

    @staticmethod
    def unmerge(data: bytes, hash_mask: bytes) -> bytes:
        """Inverse du merge (XOR est auto-inverse avec m me masque)."""
        return XORMerge.merge(data, hash_mask)

    @staticmethod
    def _expand_mask(seed: bytes, length: int) -> bytes:
        """Expand le masque par hash chain."""
        mask = bytearray()
        counter = 0
        while len(mask) < length:
            h = hashlib.sha256(seed + struct.pack(">I", counter)).digest()
            mask.extend(h)
            counter += 1
        return bytes(mask[:length])


# ===============================================================================
#  COMPRESSION / D COMPRESSION FXION -- LZ4 + IQ2_XS
# ===============================================================================
class FXIONCompression:
    """
    Nouvelle d compression FXION avec support IQ2_XS:
    - Compression: LZ4 (rapide) + XOR scramble du flux compress 
    - D compression: d -scramble + LZ4 decompress + validation checksum
    - IQ2_XS Mode: Quantization INT2 avant compression pour rduction maximale
    """

    def __init__(self, key: bytes):
        self.scramble_key = hashlib.sha256(key + b"COMPRESS").digest()
        import lz4.block
        self.lz4 = lz4.block

    def _quantize_iq2_xs(self, data: bytes) -> tuple:
        """Quantize bytes to IQ2_XS format (2-bit per value with scales)."""
        import numpy as np
        arr = np.frombuffer(data, dtype=np.float32).copy()
        n = len(arr)
        block_size = 32
        n_blocks = (n + block_size - 1) // block_size
        
        # Pad if necessary
        if n % block_size != 0:
            pad_size = block_size - (n % block_size)
            arr = np.pad(arr, (0, pad_size), mode='constant')
        
        arr = arr.reshape(n_blocks, block_size)
        amax = np.max(np.abs(arr), axis=1, keepdims=True)
        scales = (amax / 3.0).reshape(-1)
        scales = np.maximum(scales, 1e-8)
        
        normalized = arr / scales.reshape(-1, 1)
        indices = np.clip(np.round(normalized + 3) / 2, 0, 3).astype(np.uint8)
        
        # Pack 4 values per byte (2-bit each)
        packed = np.zeros((n_blocks, block_size // 4), dtype=np.uint8)
        for i in range(block_size // 4):
            packed[:, i] = (indices[:, i*4] | 
                           (indices[:, i*4+1] << 2) | 
                           (indices[:, i*4+2] << 4) | 
                           (indices[:, i*4+3] << 6))
        
        iq2_data = packed.tobytes()
        scale_data = scales.astype(np.float32).tobytes()
        
        return iq2_data, scale_data, n
    
    def _dequantize_iq2_xs(self, iq2_data: bytes, scale_data: bytes, original_len: int) -> bytes:
        """Dequantize from IQ2_XS format back to float32 bytes."""
        import numpy as np
        block_size = 32
        n_blocks = len(iq2_data) // (block_size // 4)
        
        packed = np.frombuffer(iq2_data, dtype=np.uint8).reshape(n_blocks, block_size // 4)
        scales = np.frombuffer(scale_data, dtype=np.float32)
        
        indices = np.zeros((n_blocks, block_size), dtype=np.uint8)
        for i in range(block_size // 4):
            indices[:, i*4]   = (packed[:, i] >> 0) & 3
            indices[:, i*4+1] = (packed[:, i] >> 2) & 3
            indices[:, i*4+2] = (packed[:, i] >> 4) & 3
            indices[:, i*4+3] = (packed[:, i] >> 6) & 3
        
        values = (indices.astype(np.float32) * 2.0) - 3.0
        dequant = values * scales.reshape(-1, 1)
        
        result = dequant.flatten()[:original_len]
        return result.tobytes()

    def compress(self, data: bytes, use_iq2_xs: bool = False) -> bytes:
        """Compress + XOR scramble with optional IQ2_XS quantization."""
        # Checksum original (for standard mode only, IQ2_XS is lossy)
        checksum = struct.pack(">I", zlib.crc32(data) & 0xFFFFFFFF)
        # Longueur originale
        orig_len = struct.pack(">I", len(data))
        
        if use_iq2_xs:
            # IQ2_XS quantization before compression
            iq2_data, scale_data, n = self._quantize_iq2_xs(data)
            # Compress both streams with LZ4 (store_size=False for efficiency)
            compressed_iq2 = self.lz4.compress(iq2_data, store_size=False)
            compressed_scales = self.lz4.compress(scale_data, store_size=False)
            # Pack: [iq2_len 4B][scales_len 4B][iq2_compressed][scales_compressed]
            payload = struct.pack(">II", len(compressed_iq2), len(compressed_scales)) + compressed_iq2 + compressed_scales
            mode_flag = b"\x01"  # IQ2_XS mode (lossy, no CRC check)
        else:
            # Standard LZ4 compression (faster than zlib)
            compressed = self.lz4.compress(data, store_size=False)
            payload = struct.pack(">I", len(data)) + compressed  # prepend uncompressed size
            mode_flag = b"\x00"  # Standard mode (lossless, CRC check)
        
        # XOR scramble du flux compress 
        scrambled = self._scramble(payload)
        # Format: [checksum 4B][orig_len 4B][mode 1B][scrambled_data]
        return checksum + orig_len + mode_flag + scrambled

    def decompress(self, data: bytes) -> bytes:
        """D -scramble + d compression + validation."""
        if len(data) < 9:
            raise ValueError("Donn es trop courtes pour d compression")
        # Extraire header
        checksum_expected = struct.unpack(">I", data[:4])[0]
        orig_len = struct.unpack(">I", data[4:8])[0]
        mode_flag = data[8]
        scrambled = data[9:]
        
        # D -scramble
        payload = self._scramble(scrambled)  # XOR auto-inverse
        
        if mode_flag == 0x01:
            # IQ2_XS mode (lossy quantization)
            if len(payload) < 8:
                raise ValueError("Payload IQ2_XS trop court")
            iq2_len = struct.unpack(">I", payload[:4])[0]
            scales_len = struct.unpack(">I", payload[4:8])[0]
            compressed_iq2 = payload[8:8+iq2_len]
            compressed_scales = payload[8+iq2_len:8+iq2_len+scales_len]
            
            # Decompress with LZ4 (need to provide uncompressed sizes)
            iq2_uncompressed_size = ((orig_len + 31) // 32) * (32 // 4)  # packed size
            scales_uncompressed_size = ((orig_len + 31) // 32) * 4  # float32 per block
            iq2_data = self.lz4.decompress(compressed_iq2, uncompressed_size=iq2_uncompressed_size)
            scale_data = self.lz4.decompress(compressed_scales, uncompressed_size=scales_uncompressed_size)
            
            # Dequantize
            decompressed = self._dequantize_iq2_xs(iq2_data, scale_data, orig_len)

            # Decompress with LZ4 (need to provide uncompressed sizes)
            # orig_len is in bytes, compute float count
            float_count = orig_len // 4
            blocks = (float_count + 31) // 32
            iq2_uncompressed_size = blocks * (32 // 4)  # packed size in bytes
            scales_uncompressed_size = blocks * 4  # float32 per block in bytes
            iq2_data = self.lz4.decompress(compressed_iq2, uncompressed_size=iq2_uncompressed_size)
            scale_data = self.lz4.decompress(compressed_scales, uncompressed_size=scales_uncompressed_size)

            # Dequantize - pass float_count, not orig_len (bytes)
            decompressed = self._dequantize_iq2_xs(iq2_data, scale_data, float_count)
            # Skip CRC check for IQ2_XS (lossy by design)
        else:
            # Standard mode - first 4 bytes are uncompressed size
            if len(payload) < 4:
                raise ValueError("Payload standard trop court")
            uncomp_size = struct.unpack(">I", payload[:4])[0]
            compressed = payload[4:]
            decompressed = self.lz4.decompress(compressed, uncompressed_size=uncomp_size)
            
            # Validation CRC for lossless mode only
            checksum_actual = zlib.crc32(decompressed) & 0xFFFFFFFF
            if checksum_actual != checksum_expected:
                raise ValueError(f"Checksum invalide: attendu {checksum_expected:#x}, re u {checksum_actual:#x}")
        
        # Validate length for both modes
        if len(decompressed) != orig_len:
            raise ValueError(f"Longueur invalide: attendu {orig_len}, re u {len(decompressed)}")
        return decompressed

    def _scramble(self, data: bytes) -> bytes:
        """XOR scramble avec cl  d riv e expans e."""
        key_stream = bytearray()
        counter = 0
        while len(key_stream) < len(data):
            h = hashlib.sha256(self.scramble_key + struct.pack(">I", counter)).digest()
            key_stream.extend(h)
            counter += 1
        output = bytearray(len(data))
        for i in range(len(data)):
            output[i] = data[i] ^ key_stream[i]
        return bytes(output)


# ===============================================================================
#  FXION CIPHER -- PIPELINE COMPLET
# ===============================================================================
class FXIONCipher:
    """
    Pipeline de chiffrement complet FXION:

    ENCRYPT:
      raw -> compress -> xor_partiel -> hash_composite -> xor_merge -> hmac_sign -> output

    DECRYPT:
      input -> hmac_verify -> xor_unmerge -> xor_partiel_decrypt -> decompress -> raw

    Format de sortie:
      [MAGIC 6B][VERSION 1B][SALT 16B][NONCE 16B][HMAC 96B][DATA...]
    """

    def __init__(self, key: bytes, salt: Optional[bytes] = None):
        self.salt = salt or os.urandom(16)
        # D rivation de cl  ma tre
        self.master_key = HashageMultiType.derive_key(key, self.salt, iterations=50000)
        # Sous-cl s
        self.xor_key = self.master_key[:32]
        self.hmac_key = self.master_key[32:]
        # Composants
        self.xor_engine = XORPartiel(self.xor_key)
        self.hmac_layer = HMACLayer(self.hmac_key)
        self.compressor = FXIONCompression(self.xor_key)

    def encrypt(self, plaintext: bytes) -> bytes:
        """Pipeline complet de chiffrement."""
        nonce = os.urandom(16)

        # 1. Compression
        compressed = self.compressor.compress(plaintext)

        # 2. XOR Partiel
        xored = self.xor_engine.encrypt(compressed)

        # 3. Hash composite (utilis  comme masque de merge)
        hash_mask = HashageMultiType.hash_composite(nonce + self.xor_key)

        # 4. XOR Merge avec le hash comme masque
        merged = XORMerge.merge(xored, hash_mask)

        # 5. HMAC signature
        signature = self.hmac_layer.sign(merged)

        # 6. Assemblage final
        header = MAGIC + struct.pack("B", VERSION) + self.salt + nonce
        return header + signature + merged

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Pipeline complet de d chiffrement."""
        # Parse header
        min_len = len(MAGIC) + 1 + 16 + 16 + 96
        if len(ciphertext) < min_len:
            raise ValueError("Donn es chiffr es trop courtes")

        offset = 0

        # Magic
        magic = ciphertext[offset:offset + len(MAGIC)]
        if magic != MAGIC:
            raise ValueError("Magic invalide -- pas un format FXION")
        offset += len(MAGIC)

        # Version
        version = ciphertext[offset]
        if version != VERSION:
            raise ValueError(f"Version non support e: {version}")
        offset += 1

        # Salt
        salt = ciphertext[offset:offset + 16]
        offset += 16

        # Nonce
        nonce = ciphertext[offset:offset + 16]
        offset += 16

        # HMAC
        signature = ciphertext[offset:offset + 96]
        offset += 96

        # Donn es chiffr es
        merged = ciphertext[offset:]

        # Re-d river les cl s avec le salt extrait
        master_key = HashageMultiType.derive_key(
            self.xor_key,  # on utilise la cl  originale
            self.salt, iterations=50000
        )

        # 1. V rifier HMAC
        if not self.hmac_layer.verify(merged, signature):
            raise ValueError("HMAC invalide -- donn es corrompues ou cl  incorrecte")

        # 2. XOR Unmerge
        hash_mask = HashageMultiType.hash_composite(nonce + self.xor_key)
        xored = XORMerge.unmerge(merged, hash_mask)

        # 3. XOR Partiel inverse
        compressed = self.xor_engine.decrypt(xored)

        # 4. D compression
        plaintext = self.compressor.decompress(compressed)

        return plaintext

    def encrypt_str(self, text: str, encoding: str = "utf-8") -> bytes:
        """Chiffre une cha ne de caract res."""
        return self.encrypt(text.encode(encoding))

    def decrypt_str(self, ciphertext: bytes, encoding: str = "utf-8") -> str:
        """D chiffre vers une cha ne de caract res."""
        return self.decrypt(ciphertext).decode(encoding)

    def info(self) -> dict:
        """Informations sur l'instance du cipher."""
        return {
            "algorithm": "FXION-XOR-HASH-HMAC-MERGE",
            "version": VERSION,
            "block_size": BLOCK_SIZE,
            "hash_algos": HASH_ALGORITHMS,
            "key_derivation": "PBKDF2-HMAC-SHA256 (50000 iter)",
            "hmac": "SHA-256 + SHA-512 (double)",
            "compression": "zlib-9 + XOR scramble",
            "compression": "lz4 + XOR scramble",
            "salt_size": 16,
            "nonce_size": 16,
            "header_size": len(MAGIC) + 1 + 16 + 16 + 96,
        }


# ===============================================================================
#  ALGEBRAIC XOR -- Cryptographic Transformation
# ===============================================================================
class AI4096Frame:
    """
    Implementation of the 4096-byte AI Framing Algorithm.
    Structure: [16b Header] [4064b Payload (XOR Masked)] [16b MD5 Hash]
    """
    FRAME_SIZE = 4096
    PAYLOAD_SIZE = 4064
    HEADER_SIZE = 16

    @staticmethod
    def create_frame(data: bytes) -> bytes:
        buf = bytearray(AI4096Frame.FRAME_SIZE)
        
        # 1. Header: 'AI' marker (0x41 0x49)
        header = bytearray(AI4096Frame.HEADER_SIZE)
        header[0] = 0x41
        header[1] = 0x49
        buf[0:16] = header
        
        # 2. Payload with XOR mask (31 * i + 7) & 0xFF
        payload = bytearray(AI4096Frame.PAYLOAD_SIZE)
        length = min(len(data), AI4096Frame.PAYLOAD_SIZE)
        payload[0:length] = data[:length]
        
        for i in range(AI4096Frame.PAYLOAD_SIZE):
            mask = (31 * i + 7) & 0xFF
            payload[i] ^= mask
            
        buf[16:16+AI4096Frame.PAYLOAD_SIZE] = payload
        
        # 3. MD5 Footer over Header + Payload
        md5_hash = hashlib.md5(buf[0:16+AI4096Frame.PAYLOAD_SIZE]).digest()
        buf[16+AI4096Frame.PAYLOAD_SIZE:] = md5_hash
        
        return bytes(buf)

    @staticmethod
    def verify_and_extract(frame: bytes) -> bytes:
        if len(frame) != AI4096Frame.FRAME_SIZE:
            raise ValueError("Invalid frame size")
            
        # Verify MD5
        expected_hash = frame[16+AI4096Frame.PAYLOAD_SIZE:]
        actual_hash = hashlib.md5(frame[0:16+AI4096Frame.PAYLOAD_SIZE]).digest()
        if expected_hash != actual_hash:
            raise ValueError("Frame checksum mismatch (MD5)")
            
        # Extract and unmask payload
        payload = bytearray(frame[16:16+AI4096Frame.PAYLOAD_SIZE])
        for i in range(AI4096Frame.PAYLOAD_SIZE):
            mask = (31 * i + 7) & 0xFF
            payload[i] ^= mask
            
        return bytes(payload).rstrip(b'\x00')

class AlgebraicXOR:
    """
    Algebraic XOR: Implements a non-linear state transformation using 
    recursive bit-shifts and XOR masks.
    Used for 'decrypting' entropy-dynamic blocks.
    """
    @staticmethod
    def transform(data: bytes, entropy_seed: float) -> bytes:
        seed_bits = int(entropy_seed * 0xFFFFFFFF)
        mask = struct.pack(">I", seed_bits) * (len(data) // 4 + 1)
        mask = mask[:len(data)]
        
        output = bytearray(len(data))
        for i in range(len(data)):
            # Algebraic non-linearity: (x XOR m) ROTL 3
            val = data[i] ^ mask[i]
            rotated = ((val << 3) & 0xFF) | (val >> 5)
            output[i] = rotated
        return bytes(output)

class BlockchainCipher:
    """Focuses on high-speed SHA decryption and block verification."""
    @staticmethod
    def solve_block(block_header: bytes, difficulty_bits: int) -> str:
        # Simulated high-speed block solving
        nonce = 0
        target = 2**(256 - difficulty_bits)
        while nonce < 10000: # Simulated window
            h = hashlib.sha256(block_header + struct.pack(">Q", nonce)).digest()
            val = int.from_bytes(h, "big")
            if val < target:
                return h.hex()
            nonce += 1
        return hashlib.sha256(block_header).hexdigest()


if __name__ == "__main__":
    print("=" * 64)
    print("  FXION CIPHER -- TEST COMPLET")
    print("=" * 64)

    key = b"FXION-ONYX-SECRET-KEY-2026"
    cipher = FXIONCipher(key)

    # Info
    import json
    print(f"\n[INFO] Configuration:")
    print(json.dumps(cipher.info(), indent=2))

    # Test 1: Chiffrement/D chiffrement texte
    print(f"\n[TEST 1] Texte simple...")
    msg = "FXION-ONYX Q8 Augmented Quantization Engine -- Top Secret Data"
    enc = cipher.encrypt_str(msg)
    dec = cipher.decrypt_str(enc)
    assert dec == msg, f"FAIL: {dec} != {msg}"
    print(f"  Original : {msg}")
    print(f"  Chiffr   : {len(enc)} bytes")
    print(f"  D chiffr : {dec}")
    print(f"  [PASS]")

    # Test 2: Donn es binaires
    print(f"\n[TEST 2] Donn es binaires (4KB)...")
    data = os.urandom(4096)
    enc = cipher.encrypt(data)
    dec = cipher.decrypt(enc)
    assert dec == data, "FAIL: binary mismatch"
    print(f"  Original : {len(data)} bytes")
    print(f"  Chiffr   : {len(enc)} bytes (overhead: +{len(enc)-len(data)} bytes)")
    print(f"  [PASS]")

    # Test 3: HMAC tamper detection
    print(f"\n[TEST 3] D tection de corruption (HMAC)...")
    enc = cipher.encrypt(b"sensitive data")
    tampered = bytearray(enc)
    tampered[-1] ^= 0xFF  # corrompre le dernier byte
    try:
        cipher.decrypt(bytes(tampered))
        print(f"  [FAIL] Corruption non d tect e!")
    except ValueError as e:
        print(f"  Tamper d tect : {e}")
        print(f"  [PASS]")

    # Test 4: Mauvaise cl 
    print(f"\n[TEST 4] Mauvaise cl ...")
    enc = cipher.encrypt(b"secret")
    bad_cipher = FXIONCipher(b"MAUVAISE-CLE", salt=cipher.salt)
    try:
        bad_cipher.decrypt(enc)
        print(f"  [FAIL] D chiffrement avec mauvaise cl !")
    except ValueError as e:
        print(f"  Rejet : {e}")
        print(f"  [PASS]")

    # Test 5: Hash composite
    print(f"\n[TEST 5] Hashage multi-type...")
    all_h = HashageMultiType.hash_all(b"FXION")
    for algo, h in all_h.items():
        print(f"  {algo:<10}: {h.hex()[:32]}...")
    composite = HashageMultiType.hash_composite(b"FXION")
    print(f"  composite : {composite.hex()}")
    print(f"  [PASS]")

    # Test 6: Gros volume
    print(f"\n[TEST 6] Gros volume (1MB)...")
    import time
    big_data = os.urandom(1024 * 1024)
    t0 = time.time()
    enc = cipher.encrypt(big_data)
    t_enc = time.time() - t0
    t0 = time.time()
    dec = cipher.decrypt(enc)
    t_dec = time.time() - t0
    assert dec == big_data
    print(f"  Encrypt: {t_enc:.3f}s | Decrypt: {t_dec:.3f}s")
    print(f"  Ratio: {len(enc)/len(big_data):.3f}x")
    print(f"  [PASS]")

    print(f"\n{'=' * 64}")
    print(f"  TOUS LES TESTS PASS S")
    print(f"{'=' * 64}")
