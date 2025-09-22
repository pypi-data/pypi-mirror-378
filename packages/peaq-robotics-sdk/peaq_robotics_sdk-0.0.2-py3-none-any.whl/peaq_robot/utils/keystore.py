"""
Keystore utilities for persisting and loading wallet secrets.

This module provides a lightweight, professional-looking keystore format
that stores either a mnemonic or a private key. If the environment variable
PEAQ_ROBOT_KEY_PASSWORD is set, the keystore is encrypted using Fernet with
PBKDF2-HMAC key derivation; otherwise, it falls back to base64 encoding
to avoid storing raw plaintext.
"""

import os
import json
import base64
import secrets
from typing import Tuple, Literal

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


SecretType = Literal["mnemonic", "private_key"]


def _derive_fernet_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)


def _ensure_parent_perms(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, mode=0o700, exist_ok=True)


def save_keystore(path: str, payload: str, secret_type: SecretType) -> str:
    """Persist secret to keystore file. Returns the saved path.

    The file is created with 0600 permissions when possible.
    """
    _ensure_parent_perms(path)

    password = os.environ.get("PEAQ_ROBOT_KEY_PASSWORD")
    record = {
        "version": 1,
        "type": secret_type,
    }

    payload_bytes = payload.encode("utf-8")

    if password:
        salt = secrets.token_bytes(16)
        fkey = _derive_fernet_key(password, salt)
        token = Fernet(fkey).encrypt(payload_bytes)
        record.update({
            "encoding": "fernet",
            "salt": base64.b64encode(salt).decode("utf-8"),
            "data": token.decode("utf-8"),
        })
    else:
        record.update({
            "encoding": "base64",
            "data": base64.b64encode(payload_bytes).decode("utf-8"),
        })

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh)

    try:
        os.chmod(path, 0o600)
    except Exception:
        pass

    return path


def load_keystore(path: str) -> Tuple[SecretType, str]:
    """Load secret from keystore file. Returns (type, payload)."""
    with open(path, "r", encoding="utf-8") as fh:
        record = json.load(fh)

    secret_type = record.get("type", "mnemonic")
    encoding = record.get("encoding", "base64")
    data = record["data"]

    if encoding == "fernet":
        salt_b64 = record["salt"]
        salt = base64.b64decode(salt_b64)
        password = os.environ.get("PEAQ_ROBOT_KEY_PASSWORD")
        if not password:
            raise ValueError("Keystore is encrypted; set PEAQ_ROBOT_KEY_PASSWORD to decrypt")
        fkey = _derive_fernet_key(password, salt)
        payload_bytes = Fernet(fkey).decrypt(data.encode("utf-8"))
        return secret_type, payload_bytes.decode("utf-8")
    else:
        payload_bytes = base64.b64decode(data.encode("utf-8"))
        return secret_type, payload_bytes.decode("utf-8")


