# Copyright (c) 2026, FadlTech team and contributors

"""Fadl POS token endpoints for Frappe `/api/method/...` RPC calls."""

from __future__ import annotations

import frappe
from frappe.rate_limiter import rate_limit

from fadl_pos.core.serializer import dump_out, validate_in
from fadl_pos.login.controller import LoginController
from fadl_pos.login.serializer import (
	AuthTokenResponse,
	LoginRequest,
	QRGenerateRequest,
	QRGenerateResponse,
	QRLoginRequest,
)


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60)
def login(usr: str | None = None, pwd: str | None = None) -> AuthTokenResponse:
	"""
	Password authentication for POS API clients.

	**Route:** ``/api/method/fadl_pos.login.whitelist.login`` (POST, ``allow_guest``)

	**Input:**

	- ``usr`` (str, required): Frappe username / email (5-100 chars).
	- ``pwd`` (str, required): password (8-100 chars).

	**Output:**

	- ``{"token": "Basic <base64(api_key:api_secret)>"}`` -- ``AuthTokenResponse``.
	"""
	body = validate_in(LoginRequest, {"usr": usr, "pwd": pwd})
	return dump_out(AuthTokenResponse, LoginController().login(usr=body.usr, pwd=body.pwd))


@frappe.whitelist(methods=["POST"])
def clear_sessions() -> AuthTokenResponse:
	"""
	Invalidate POS tokens by rotating API credentials for the logged-in user.

	**Route:** ``/api/method/fadl_pos.login.whitelist.clear_sessions`` (POST)

	**Input:** none (session user).

	**Output:** Same credential envelope shape as ``login`` (fresh secret).
	"""
	return dump_out(AuthTokenResponse, LoginController().clear_sessions())


@frappe.whitelist(methods=["POST"])
def generate_qr(pin_code: str | None = None) -> QRGenerateResponse:
	"""
	Generate an encrypted QR payload for the current user (client-held ciphertext).

	**Route:** ``/api/method/fadl_pos.login.whitelist.generate_qr`` (POST)

	**Input:**

	- ``pin_code`` (str, required): 6-digit PIN used by cipher when generating payload.

	**Output:**

	- ``QRGenerateResponse`` dict -- encrypted blob / metadata fields from ``LoginController``.
	"""
	body = validate_in(QRGenerateRequest, {"pin_code": pin_code})
	return dump_out(QRGenerateResponse, LoginController().generate_qr(pin_code=body.pin_code))


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60)
def login_qr(
	encrypted_qr: str | None = None,
	pin_code: str | None = None,
) -> AuthTokenResponse:
	"""
	QR-based login using client-held ciphertext + PIN.

	**Route:** ``/api/method/fadl_pos.login.whitelist.login_qr`` (POST, ``allow_guest``)

	**Input:**

	- ``encrypted_qr`` (str, required): ciphertext blob from ``generate_qr`` (10-512 chars).
	- ``pin_code`` (str, required): 6-digit PIN used to decrypt.

	**Output:** Same ``token`` Basic envelope as password ``login`` (``AuthTokenResponse``).
	"""
	body = validate_in(QRLoginRequest, {"encrypted_qr": encrypted_qr, "pin_code": pin_code})
	return dump_out(
		AuthTokenResponse,
		LoginController().login_qr(encrypted_qr=body.encrypted_qr, pin_code=body.pin_code),
	)
