#!/usr/bin/env python3
"""
Copyright 2025 Jeyashree narayanan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
dtp_core.py
Core cryptographic and steganographic library for the Decoy-Trap Protocol (DTP).
This module is designed to be imported into other applications and is independent of any user interface.
"""

import json
import base64
import hmac
import hashlib
import secrets
import random
from typing import Tuple, Optional, Dict
import os

try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Hash import SHA256
except ImportError:
    raise RuntimeError("pycryptodome is not installed. Please install it with: pip install pycryptodome")

# ----- Config -----
PBKDF2_ITER = 200_000
KDF_SALT_BYTES = 16
AES_KEY_BYTES = 32
GCM_NONCE_BYTES = 12
HMAC_CONTEXT = b"DTP-v1-secondary"

ZW_0 = '\u200b'  # zero-width space -> '0'
ZW_1 = '\u200c'  # zero-width non-joiner -> '1'


# ----- Crypto primitives -----
def derive_k1(password: str, salt: bytes, iterations: int = PBKDF2_ITER) -> bytes:
    return PBKDF2(password, salt, dkLen=AES_KEY_BYTES, count=iterations, hmac_hash_module=SHA256)

def derive_k2(k1: bytes, context: bytes = HMAC_CONTEXT) -> bytes:
    return hmac.new(k1, context, hashlib.sha256).digest()[:AES_KEY_BYTES]

def aes_gcm_encrypt(key: bytes, plaintext: bytes, aad: bytes = b'') -> Tuple[bytes, bytes, bytes]:
    nonce = get_random_bytes(GCM_NONCE_BYTES)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    if aad:
        cipher.update(aad)
    ct, tag = cipher.encrypt_and_digest(plaintext)
    return nonce, ct, tag

def aes_gcm_decrypt(key: bytes, nonce: bytes, ct: bytes, tag: bytes, aad: bytes = b'') -> bytes:
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    if aad:
        cipher.update(aad)
    return cipher.decrypt_and_verify(ct, tag)

# ----- Stego helpers -----
def bytes_to_zw_payload(data: bytes) -> str:
    b64 = base64.b64encode(data)
    bits = ''.join(f'{b:08b}' for b in b64)
    return ''.join(ZW_0 if bit == '0' else ZW_1 for bit in bits)

def zw_payload_to_bytes(text: str) -> bytes:
    filtered = [c for c in text if c == ZW_0 or c == ZW_1]
    if not filtered:
        return b''
    bits = ''.join('0' if c == ZW_0 else '1' for c in filtered)
    rem = len(bits) % 8
    if rem:
        bits = bits[:-rem]
    ba = bytearray()
    for i in range(0, len(bits), 8):
        ba.append(int(bits[i:i+8], 2))
    try:
        return base64.b64decode(bytes(ba))
    except Exception:
        return b''

def embed_payload_in_decoy(decoy: str, payload_bytes: bytes) -> str:
    zw = bytes_to_zw_payload(payload_bytes)
    return decoy + zw

def extract_payload_from_decoy(decoy_text: str) -> bytes:
    return zw_payload_to_bytes(decoy_text)

# ----- Decoy generator -----
def load_decoy_data(template_path: Optional[str] = None) -> Dict:
    """Loads decoy generation data from a JSON file."""
    if template_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, 'decoy_template.json')
    
    try:
        with open(template_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Decoy template not found at: {template_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in decoy template: {template_path}")

def generate_decoy(decoy_data: Optional[Dict] = None) -> str:
    """Generates a decoy string from the provided data."""
    if decoy_data is None:
        decoy_data = load_decoy_data()

    tpl = random.choice(decoy_data['templates'])
    return tpl.format(
        adj=random.choice(decoy_data['adjectives']),
        subj=random.choice(decoy_data['subjects']),
        sym=random.choice(decoy_data['symbols']),
        verb=random.choice(decoy_data['verbs']),
        obj=random.choice(decoy_data['objects']),
        adv=random.choice(decoy_data['adverbs']),
        time=random.choice(decoy_data['times'])
    )

# ----- High level DTP functions -----
def encrypt_dtp(plaintext: bytes, password: str, secret_key: bytes, decoy_template_path: Optional[str] = None) -> bytes:
    """
    Encrypts plaintext using the DTP protocol.

    Args:
        plaintext: The secret data to encrypt.
        password: The user's primary password.
        secret_key: A separate, high-entropy secret key for inner encryption.
        decoy_template_path: Optional path to a custom decoy template JSON.

    Returns:
        The DTP envelope as bytes.
    """
    salt = secrets.token_bytes(KDF_SALT_BYTES)
    k1 = derive_k1(password, salt)
    
    # Inner encrypt (true secret) with the separate secret_key
    nonce2, ct2, tag2 = aes_gcm_encrypt(secret_key, plaintext)
    inner_blob = json.dumps({"nonce": b64(nonce2), "ct": b64(ct2), "tag": b64(tag2)}).encode('utf-8')
    
    # Decoy + zero-width embed
    decoy_data = load_decoy_data(decoy_template_path)
    decoy = generate_decoy(decoy_data)
    decoy_with_zw = embed_payload_in_decoy(decoy, inner_blob)
    decoy_bytes = decoy_with_zw.encode('utf-8')
    
    # Outer encrypt decoy container
    nonce1, ct1, tag1 = aes_gcm_encrypt(k1, decoy_bytes)
    envelope = {
        "kdf": "pbkdf2_sha256",
        "kdf_iter": PBKDF2_ITER,
        "salt": b64(salt),
        "outer": {"nonce": b64(nonce1), "ct": b64(ct1), "tag": b64(tag1)},
        "meta": {"algo": "AES-256-GCM", "stego": "zero-width-u200b-u200c"}
    }
    return json.dumps(envelope).encode('utf-8')

def decrypt_decoy(envelope_bytes: bytes, password: str) -> str:
    """
    Decrypts the outer layer of a DTP envelope to reveal the decoy text.
    This step only requires the user's password.

    Args:
        envelope_bytes: The DTP envelope.
        password: The user's primary password.

    Returns:
        The decoy text, which may contain a hidden payload.
    """
    env = json.loads(envelope_bytes.decode('utf-8'))
    salt = ub64(env['salt'])
    o = env['outer']
    nonce1 = ub64(o['nonce']); ct1 = ub64(o['ct']); tag1 = ub64(o['tag'])
    
    k1 = derive_k1(password, salt)
    decoy_bytes = aes_gcm_decrypt(k1, nonce1, ct1, tag1)
    return decoy_bytes.decode('utf-8', errors='ignore')

def extract_secret(decoy_with_zw: str, secret_key: bytes) -> bytes:
    """
    Extracts and decrypts the hidden secret from a decoy text.
    This step requires the separate secret_key.

    Args:
        decoy_with_zw: The decoy text containing the hidden payload.
        secret_key: The high-entropy secret key for inner decryption.

    Returns:
        The original plaintext.
    """
    inner_blob = extract_payload_from_decoy(decoy_with_zw)
    if not inner_blob:
        raise ValueError("No hidden payload found — stego missing or stripped.")
    
    inner = json.loads(inner_blob.decode('utf-8'))
    nonce2 = ub64(inner['nonce']); ct2 = ub64(inner['ct']); tag2 = ub64(inner['tag'])
    
    pt = aes_gcm_decrypt(secret_key, nonce2, ct2, tag2)
    return pt

def decrypt_dtp(envelope_bytes: bytes, password: str) -> bytes:
    env = json.loads(envelope_bytes.decode('utf-8'))
    salt = ub64(env['salt'])
    o = env['outer']
    nonce1 = ub64(o['nonce']); ct1 = ub64(o['ct']); tag1 = ub64(o['tag'])
    
    k1 = derive_k1(password, salt)
    decoy_bytes = aes_gcm_decrypt(k1, nonce1, ct1, tag1)
    decoy_with_zw = decoy_bytes.decode('utf-8', errors='ignore')
    
    inner_blob = extract_payload_from_decoy(decoy_with_zw)
    if not inner_blob:
        raise ValueError("No hidden payload found — stego missing or stripped.")
    
    inner = json.loads(inner_blob.decode('utf-8'))
    nonce2 = ub64(inner['nonce']); ct2 = ub64(inner['ct']); tag2 = ub64(inner['tag'])
    
    k2 = derive_k2(k1)
    pt = aes_gcm_decrypt(k2, nonce2, ct2, tag2)
    return pt

# ----- Custom Exceptions -----
class DTPError(Exception):
    """Base exception for DTP-related errors."""
    pass

class DTPDecryptionError(DTPError):
    """Raised when decryption fails due to wrong key or tampered data."""
    pass

# ----- Decoy Detection Functions -----
def is_decoy_password(submitted_password: str, known_decoy_hashes: set) -> bool:
    """
    Check if a submitted password is a known decoy.
    
    Args:
        submitted_password: The password to check.
        known_decoy_hashes: Set of SHA-256 hashes of known decoy passwords.
    
    Returns:
        True if the password is a decoy, False otherwise.
    """
    submitted_hash = hash_password(submitted_password)
    return submitted_hash in known_decoy_hashes

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    
    Args:
        password: The password to hash.
    
    Returns:
        The SHA-256 hash of the password as a hex string.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def generate_client_secret() -> str:
    """
    Generate a cryptographically secure client secret.
    
    Returns:
        A URL-safe base64-encoded random string.
    """
    return secrets.token_urlsafe(32)

# ----- Enhanced Encryption Functions with Client Secret -----
def encrypt_dtp_with_client_secret(plaintext: bytes, password: str, client_secret: str, decoy_template_path: Optional[str] = None) -> bytes:
    """
    Encrypts plaintext using DTP protocol with an additional client secret.
    
    Args:
        plaintext: The secret data to encrypt.
        password: The user's primary password.
        client_secret: A device-specific secret for additional security.
        decoy_template_path: Optional path to a custom decoy template JSON.
    
    Returns:
        The DTP envelope as bytes.
    """
    # Combine password and client_secret for enhanced security
    combined_key_material = f"{password}:{client_secret}"
    
    salt = secrets.token_bytes(KDF_SALT_BYTES)
    k1 = derive_k1(combined_key_material, salt)
    k2 = derive_k2(k1)
    
    # Inner encrypt (true secret) with k2
    nonce2, ct2, tag2 = aes_gcm_encrypt(k2, plaintext)
    inner_blob = json.dumps({"nonce": b64(nonce2), "ct": b64(ct2), "tag": b64(tag2)}).encode('utf-8')
    
    # Decoy + zero-width embed
    decoy_data = load_decoy_data(decoy_template_path)
    decoy = generate_decoy(decoy_data)
    decoy_with_zw = embed_payload_in_decoy(decoy, inner_blob)
    decoy_bytes = decoy_with_zw.encode('utf-8')
    
    # Outer encrypt decoy container with k1
    nonce1, ct1, tag1 = aes_gcm_encrypt(k1, decoy_bytes)
    envelope = {
        "kdf": "pbkdf2_sha256",
        "kdf_iter": PBKDF2_ITER,
        "salt": b64(salt),
        "outer": {"nonce": b64(nonce1), "ct": b64(ct1), "tag": b64(tag1)},
        "meta": {"algo": "AES-256-GCM", "stego": "zero-width-u200b-u200c", "version": "1.0"}
    }
    return json.dumps(envelope).encode('utf-8')

def decrypt_dtp_with_client_secret(envelope_bytes: bytes, password: str, client_secret: str) -> bytes:
    """
    Decrypts a DTP envelope using password and client secret.
    
    Args:
        envelope_bytes: The DTP envelope.
        password: The user's primary password.
        client_secret: The device-specific secret.
    
    Returns:
        The original plaintext.
    
    Raises:
        DTPDecryptionError: If decryption fails.
    """
    try:
        # Combine password and client_secret
        combined_key_material = f"{password}:{client_secret}"
        
        env = json.loads(envelope_bytes.decode('utf-8'))
        salt = ub64(env['salt'])
        o = env['outer']
        nonce1 = ub64(o['nonce']); ct1 = ub64(o['ct']); tag1 = ub64(o['tag'])
        
        k1 = derive_k1(combined_key_material, salt)
        decoy_bytes = aes_gcm_decrypt(k1, nonce1, ct1, tag1)
        decoy_with_zw = decoy_bytes.decode('utf-8', errors='ignore')
        
        inner_blob = extract_payload_from_decoy(decoy_with_zw)
        if not inner_blob:
            raise DTPDecryptionError("No hidden payload found — steganography missing or stripped.")
        
        inner = json.loads(inner_blob.decode('utf-8'))
        nonce2 = ub64(inner['nonce']); ct2 = ub64(inner['ct']); tag2 = ub64(inner['tag'])
        
        k2 = derive_k2(k1)
        pt = aes_gcm_decrypt(k2, nonce2, ct2, tag2)
        return pt
        
    except Exception as e:
        raise DTPDecryptionError(f"Decryption failed: {str(e)}")

# ----- Small helpers -----
def b64(x: bytes) -> str:
    return base64.b64encode(x).decode('ascii')

def ub64(s: str) -> bytes:
    return base64.b64decode(s.encode('ascii'))
