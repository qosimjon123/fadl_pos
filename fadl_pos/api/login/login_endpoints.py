# Copyright (c) 2026, FadlTech team and contributors

"""Fadl POS token endpoints for Frappe `/api/v2/method/...` RPC calls."""

from __future__ import annotations

import frappe

from fadl_pos.api.login.auth_service import TokenAuthService
from fadl_pos.serializers.login import AuthTokenResponse, QRGenerateResponse


def _service() -> TokenAuthService:
	return TokenAuthService()


@frappe.whitelist(allow_guest=True, methods=["POST"])
def login(usr: str | None = None, pwd: str | None = None) -> AuthTokenResponse:
	"""Password login: returns `Basic base64(api_key:api_secret)`."""
	return _service().login(login=usr, password=pwd)


@frappe.whitelist(methods=["POST"])
def clear_sessions() -> AuthTokenResponse:
	"""Rotate the current user's API secret and clear the stored QR key."""
	return _service().clear_sessions()


@frappe.whitelist(methods=["POST"])
def generate_qr(pin_code: str | None = None) -> QRGenerateResponse:
	"""Generate and store a fresh encrypted QR payload for the current user."""
	return _service().generate_qr(pin_code=pin_code)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def login_qr(
	encrypted_qr: str | None = None,
	pin_code: str | None = None,
) -> AuthTokenResponse:
	"""QR login: decrypt payload with PIN and return `Basic base64(api_key:api_secret)`."""
	return _service().login_qr(encrypted_qr=encrypted_qr, pin_code=pin_code)
