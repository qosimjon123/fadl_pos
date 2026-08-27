# Copyright (c) 2026, FadlTech team and contributors

"""Шифрование полезной нагрузки ключом, производным от PIN (каскад логина)."""

from __future__ import annotations

import base64
import json
import os
from hashlib import pbkdf2_hmac

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"FP1"
SALT_LEN = 16
NONCE_LEN = 12
PBKDF2_ITERS = 100_000


def derive_key(pin: str, salt: bytes) -> bytes:
	return pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, PBKDF2_ITERS, dklen=32)


def encrypt_with_pin(pin: str, payload: dict[str, object]) -> str:
	"""Сериализует dict в JSON, шифрует PIN-ом, возвращает url-safe base64 blob."""
	plaintext = json.dumps(payload, separators=(",", ":"), sort_keys=True)
	salt = os.urandom(SALT_LEN)
	key = derive_key(pin, salt)
	aes = AESGCM(key)
	nonce = os.urandom(NONCE_LEN)
	ciphertext = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
	raw = MAGIC + salt + nonce + ciphertext
	return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decrypt_with_pin(pin: str, blob_b64: str) -> dict[str, object]:
	"""Расшифровывает blob; при неверном PIN или порче данных бросает ValueError."""
	pad = "=" * (-len(blob_b64) % 4)
	raw = base64.urlsafe_b64decode(blob_b64 + pad)
	if len(raw) < len(MAGIC) + SALT_LEN + NONCE_LEN + 16:
		raise ValueError("truncated")
	if not raw.startswith(MAGIC):
		raise ValueError("bad_magic")
	salt = raw[len(MAGIC) : len(MAGIC) + SALT_LEN]
	nonce = raw[len(MAGIC) + SALT_LEN : len(MAGIC) + SALT_LEN + NONCE_LEN]
	ciphertext = raw[len(MAGIC) + SALT_LEN + NONCE_LEN :]
	key = derive_key(pin, salt)
	aes = AESGCM(key)
	plaintext = aes.decrypt(nonce, ciphertext, None)
	data = json.loads(plaintext.decode("utf-8"))
	if not isinstance(data, dict):
		raise ValueError("payload_not_object")
	return data
