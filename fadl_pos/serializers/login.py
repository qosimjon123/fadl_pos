# Copyright (c) 2026, FadlTech team and contributors
"""Typed API contracts for POS login, QR, and token responses."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class LoginRequest(TypedDict, total=False):
	"""Password login RPC args (`usr` / `pwd`, legacy Frappe names)."""

	usr: NotRequired[str]
	pwd: NotRequired[str]


class QRLoginRequest(TypedDict, total=False):
	"""QR + PIN guest login RPC args."""

	encrypted_qr: NotRequired[str]
	pin_code: NotRequired[str]


class QRGenerateRequest(TypedDict, total=False):
	"""Authenticated QR generation RPC args."""

	pin_code: NotRequired[str]


class AuthTokenResponse(TypedDict):
	"""JSON body: Basic auth header value for API key/secret."""

	token: str


class QRGenerateResponse(TypedDict):
	"""JSON body: url-safe encrypted blob for QR."""

	encrypted_qr: str


class QRPayloadPlain(TypedDict):
	"""Structured payload serialized inside the encrypted QR blob."""

	v: int
	api_key: str
	qr_token: str
