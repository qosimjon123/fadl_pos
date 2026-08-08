# Copyright (c) 2026, FadlTech team and contributors

"""Login feature Pydantic v2 contracts. Field-level rules that need more than
``Field(...)`` constraints (PIN format, QR payload version) are expressed as
``@field_validator`` methods on the class, per module template."""

from __future__ import annotations

import re

from pydantic import Field, field_validator

from fadl_pos.core.serializer import InputSchema, OutputSchema
from fadl_pos.login.constants import (
	ENCRYPTED_QR_MAX_LENGTH,
	ENCRYPTED_QR_MIN_LENGTH,
	PIN_CODE_LENGTH,
	PIN_CODE_PATTERN,
	PWD_MAX_LENGTH,
	PWD_MIN_LENGTH,
	QR_PAYLOAD_VERSION,
	QR_TOKEN_LENGTH,
	USR_MAX_LENGTH,
	USR_MIN_LENGTH,
)

_PIN_RE = re.compile(PIN_CODE_PATTERN)


class LoginQuery(InputSchema):
	usr: str = Field(min_length=USR_MIN_LENGTH, max_length=USR_MAX_LENGTH)
	pwd: str = Field(min_length=PWD_MIN_LENGTH, max_length=PWD_MAX_LENGTH)


class _PinCodeIn(InputSchema):
	pin_code: str = Field(min_length=PIN_CODE_LENGTH, max_length=PIN_CODE_LENGTH)

	@field_validator("pin_code")
	@classmethod
	def validate_pin_code(cls, value: str) -> str:
		if not _PIN_RE.match(value):
			raise ValueError(f"PIN must be a {PIN_CODE_LENGTH}-digit code")
		return value


class QRGenerateQuery(_PinCodeIn):
	pass


class QRLoginQuery(_PinCodeIn):
	encrypted_qr: str = Field(min_length=ENCRYPTED_QR_MIN_LENGTH, max_length=ENCRYPTED_QR_MAX_LENGTH)


class QRPayloadIn(InputSchema):
	"""Decrypted QR blob shape; validated by the controller after PIN decryption."""

	v: int
	api_key: str = Field(min_length=1)
	qr_token: str = Field(min_length=QR_TOKEN_LENGTH, max_length=QR_TOKEN_LENGTH)

	@field_validator("v")
	@classmethod
	def validate_version(cls, value: int) -> int:
		if value != QR_PAYLOAD_VERSION:
			raise ValueError(f"Unsupported QR payload version: {value}")
		return value


class AuthTokenOut(OutputSchema):
	token: str


class QRGenerateOut(OutputSchema):
	encrypted_qr: str


# --- Compat aliases (kept for anything still importing the old names) ---
AuthTokenResponse = AuthTokenOut
QRGenerateResponse = QRGenerateOut
QRPayloadPlain = QRPayloadIn
