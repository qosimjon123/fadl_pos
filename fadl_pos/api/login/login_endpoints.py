# Copyright (c) 2026, FadlTech team and contributors

"""Fadl POS token endpoints for Frappe `/api/method/...` RPC calls."""

from __future__ import annotations

import frappe
from frappe.rate_limiter import rate_limit

from fadl_pos.api.login.auth_service import TokenAuthService
from fadl_pos.api.login.rpc_params import optional_str_param
from fadl_pos.serializers.login import AuthTokenResponse, QRGenerateResponse


def _service() -> TokenAuthService:
	return TokenAuthService()


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60)
def login(usr: str | None = None, pwd: str | None = None) -> AuthTokenResponse:
	"""
	Password authentication for POS API clients.

	**Route:** ``/api/method/fadl_pos.api.login.login_endpoints.login`` (POST, ``allow_guest``)

	**Input:**

	- ``usr`` (str, required): Frappe username / email.
	- ``pwd`` (str, required): password.

	**Output:**

	- ``{"authorization": "Basic <base64(api_key:api_secret)>", ...}`` — see ``AuthTokenResponse``
	  serializer for full keys returned by ``TokenAuthService``.
	"""
	return _service().login(
		login=optional_str_param("usr", usr),
		password=optional_str_param("pwd", pwd),
	)


@frappe.whitelist(methods=["POST"])
def clear_sessions() -> AuthTokenResponse:
	"""
	Invalidate POS tokens by rotating API credentials for the logged-in user.

	**Route:** ``/api/method/fadl_pos.api.login.login_endpoints.clear_sessions`` (POST)

	**Input:** none (session user).

	**Output:** Same credential envelope shape as ``login`` (fresh secret).
	"""
	return _service().clear_sessions()


@frappe.whitelist(methods=["POST"])
def generate_qr(pin_code: str | None = None) -> QRGenerateResponse:
	"""
	Generate an encrypted QR payload bound to the current user (desk-stored ciphertext).

	**Route:** ``/api/method/fadl_pos.api.login.login_endpoints.generate_qr`` (POST)

	**Input:**

	- ``pin_code`` (str, optional): PIN used by cipher when generating payload.

	**Output:**

	- ``QRGenerateResponse`` dict — encrypted blob / metadata fields from ``TokenAuthService``.
	"""
	return _service().generate_qr(pin_code=optional_str_param("pin_code", pin_code))


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60)
def login_qr(
	encrypted_qr: str | None = None,
	pin_code: str | None = None,
) -> AuthTokenResponse:
	"""
	QR-based login using stored ciphertext + PIN.

	**Route:** ``/api/method/fadl_pos.api.login.login_endpoints.login_qr`` (POST, ``allow_guest``)

	**Input:**

	- ``encrypted_qr`` (str, required): payload from ``generate_qr``.
	- ``pin_code`` (str, optional): PIN used to decrypt.

	**Output:** Same ``authorization`` Basic envelope as password ``login``.
	"""
	return _service().login_qr(
		encrypted_qr=optional_str_param("encrypted_qr", encrypted_qr),
		pin_code=optional_str_param("pin_code", pin_code),
	)
