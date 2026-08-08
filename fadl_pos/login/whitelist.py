# Copyright (c) 2026, FadlTech team and contributors

"""Fadl POS token endpoints for Frappe `/api/method/...` RPC calls."""

from __future__ import annotations

import frappe
from frappe.rate_limiter import rate_limit

from fadl_pos.core.serializer import dump_out, validate_in
from fadl_pos.login.controller import LoginController
from fadl_pos.login.serializer import (
	AuthTokenOut,
	LoginQuery,
	QRGenerateOut,
	QRGenerateQuery,
	QRLoginQuery,
)


def _controller() -> LoginController:
	return LoginController()


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60)
def login(usr: str | None = None, pwd: str | None = None) -> AuthTokenOut:
	"""
	Password authentication for POS API clients.

	**Route:** ``/api/method/fadl_pos.login.whitelist.login`` (POST, ``allow_guest``)

	**Input:**

	- ``usr`` (str, required): Frappe username / email (5-100 chars).
	- ``pwd`` (str, required): password (8-100 chars).

	**Output:**

	- ``{"token": "Basic <base64(api_key:api_secret)>"}`` -- ``AuthTokenOut``.
	"""
	body = validate_in(LoginQuery, {"usr": usr, "pwd": pwd})
	return dump_out(AuthTokenOut, _controller().login(login=body.usr, password=body.pwd))


@frappe.whitelist(methods=["POST"])
def clear_sessions() -> AuthTokenOut:
	"""
	Invalidate POS tokens by rotating API credentials for the logged-in user.

	**Route:** ``/api/method/fadl_pos.login.whitelist.clear_sessions`` (POST)

	**Input:** none (session user).

	**Output:** Same credential envelope shape as ``login`` (fresh secret).
	"""
	return dump_out(AuthTokenOut, _controller().clear_sessions())


@frappe.whitelist(methods=["POST"])
def generate_qr(pin_code: str | None = None) -> QRGenerateOut:
	"""
	Generate an encrypted QR payload bound to the current user (desk-stored ciphertext).

	**Route:** ``/api/method/fadl_pos.login.whitelist.generate_qr`` (POST)

	**Input:**

	- ``pin_code`` (str, required): 6-digit PIN used by cipher when generating payload.

	**Output:**

	- ``QRGenerateOut`` dict -- encrypted blob / metadata fields from ``LoginController``.
	"""
	body = validate_in(QRGenerateQuery, {"pin_code": pin_code})
	return dump_out(QRGenerateOut, _controller().generate_qr(pin_code=body.pin_code))


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60)
def login_qr(
	encrypted_qr: str | None = None,
	pin_code: str | None = None,
) -> AuthTokenOut:
	"""
	QR-based login using stored ciphertext + PIN.

	**Route:** ``/api/method/fadl_pos.login.whitelist.login_qr`` (POST, ``allow_guest``)

	**Input:**

	- ``encrypted_qr`` (str, required): ciphertext blob from ``generate_qr`` (10-512 chars).
	- ``pin_code`` (str, required): 6-digit PIN used to decrypt.

	**Output:** Same ``token`` Basic envelope as password ``login`` (``AuthTokenOut``).
	"""
	body = validate_in(QRLoginQuery, {"encrypted_qr": encrypted_qr, "pin_code": pin_code})
	return dump_out(
		AuthTokenOut,
		_controller().login_qr(encrypted_qr=body.encrypted_qr, pin_code=body.pin_code),
	)
