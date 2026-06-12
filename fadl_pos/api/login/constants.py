# Copyright (c) 2026, FadlTech team and contributors

"""Shared login API field limits (Pydantic + auth_service)."""

from __future__ import annotations

PIN_CODE_LENGTH = 6
PIN_CODE_PATTERN = rf"^\d{{{PIN_CODE_LENGTH}}}$"

ENCRYPTED_QR_MIN_LENGTH = 10
# AES-GCM url-safe base64 blob from encrypt_with_pin is ~170+ chars.
ENCRYPTED_QR_MAX_LENGTH = 512

USR_MIN_LENGTH = 5
USR_MAX_LENGTH = 100
PWD_MIN_LENGTH = 8
PWD_MAX_LENGTH = 100
