# Copyright (c) 2026, FadlTech team and contributors

"""QR payload v2: encrypt/decrypt and resolve user via native API token validation."""

from __future__ import annotations

import frappe
from frappe.auth import validate_api_key_secret
from frappe.model.document import Document
from pydantic import ValidationError as PydanticValidationError

from fadl_pos.core.errors import auth_error
from fadl_pos.login.constants import QR_PAYLOAD_VERSION
from fadl_pos.login.processing.pin_cipher import decrypt_with_pin, encrypt_with_pin
from fadl_pos.login.processing.token import BasicToken
from fadl_pos.login.serializer import QRPayloadRequest


def build_payload(token: BasicToken) -> dict[str, object]:
	return {
		"v": QR_PAYLOAD_VERSION,
		"api_key": token.api_key,
		"api_secret": token.api_secret,
	}


def encrypt_payload(pin_code: str, payload: dict[str, object]) -> str:
	try:
		return encrypt_with_pin(pin_code, payload)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "fadl_pos generate_qr encrypt")
		auth_error("Could not create encrypted QR payload")
		raise AssertionError("unreachable")


def resolve_user(encrypted_qr: str, pin_code: str) -> tuple[str, Document]:
	encrypted_qr = (encrypted_qr or "").strip()
	if not encrypted_qr:
		auth_error("Encrypted QR payload is required")

	try:
		raw = decrypt_with_pin(pin_code, encrypted_qr)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "fadl_pos login_qr decrypt")
		auth_error("Invalid PIN or encrypted QR payload")
		raise AssertionError("unreachable")

	payload = _parse_payload(raw)

	try:
		validate_api_key_secret(payload["api_key"], payload["api_secret"])
	except frappe.AuthenticationError:
		auth_error("Invalid PIN or encrypted QR payload")
		raise AssertionError("unreachable")

	user = frappe.db.get_value("User", {"api_key": payload["api_key"]}, "name")
	if not user:
		auth_error("Invalid PIN or encrypted QR payload")
		raise AssertionError("unreachable")

	return user, frappe.get_doc("User", user)


def _parse_payload(raw: dict[str, object]) -> dict[str, object]:
	try:
		payload = QRPayloadRequest.model_validate(raw)
	except PydanticValidationError:
		auth_error("Invalid PIN or encrypted QR payload")
		raise AssertionError("unreachable")
	return payload.model_dump()
