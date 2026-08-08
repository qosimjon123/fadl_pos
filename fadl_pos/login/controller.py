# Copyright (c) 2026, FadlTech team and contributors

"""POS token and QR authentication actions (create/rotate token, generate/verify QR)."""

from __future__ import annotations

import base64
from dataclasses import dataclass

import frappe
from frappe import _
from frappe.core.doctype.user.user import User
from frappe.model.document import Document
from pydantic import ValidationError as PydanticValidationError

from fadl_pos.core.errors import auth_error
from fadl_pos.login import events
from fadl_pos.login.constants import QR_PAYLOAD_VERSION, QR_TOKEN_LENGTH
from fadl_pos.login.permission import (
	require_authenticated_session,
	require_enabled_login_user,
	require_qr_bound_user,
)
from fadl_pos.login.pin_cipher import decrypt_with_pin, encrypt_with_pin
from fadl_pos.login.serializer import QRPayloadIn


@dataclass(frozen=True)
class BasicToken:
	api_key: str
	api_secret: str

	def as_authorization_header(self) -> str:
		raw = f"{self.api_key}:{self.api_secret}".encode()
		encoded = base64.b64encode(raw).decode("ascii")
		return f"Basic {encoded}"


class LoginController:
	"""Centralized API-token and QR-token actions for Fadl POS."""

	qr_fieldname = "qr_encrypted_data"

	def login(self, login: str | None = None, password: str | None = None) -> dict:
		user = self._authenticate_password(login, password)
		token = self._ensure_basic_token(user)
		events.login_succeeded(user=user, method="password")
		return {"token": token.as_authorization_header()}

	def clear_sessions(self) -> dict:
		user = require_authenticated_session()
		doc = frappe.get_doc("User", user)
		token = self._rotate_api_secret(doc)
		self._set_qr_blob(doc, None)
		doc.save(ignore_permissions=True)
		events.sessions_cleared(user=user)
		return {"token": token.as_authorization_header()}

	def generate_qr(self, pin_code: str | None = None) -> dict:
		user = require_authenticated_session()
		doc = frappe.get_doc("User", user)
		token = self._ensure_basic_token_for_doc(doc)
		payload = {
			"v": QR_PAYLOAD_VERSION,
			"api_key": token.api_key,
			"qr_token": frappe.generate_hash(length=QR_TOKEN_LENGTH),
		}
		try:
			encrypted_qr = encrypt_with_pin(pin_code, payload)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "fadl_pos generate_qr encrypt")
			auth_error("Could not create encrypted QR payload")

		self._set_qr_blob(doc, encrypted_qr)
		doc.save(ignore_permissions=True)
		events.qr_generated(user=user)
		return {"encrypted_qr": encrypted_qr}

	def login_qr(self, encrypted_qr: str | None = None, pin_code: str | None = None) -> dict:
		user, doc = self.verify_qr_user(encrypted_qr=encrypted_qr, pin_code=pin_code)
		token = self._ensure_basic_token_for_doc(doc)
		events.login_succeeded(user=user, method="qr")
		return {"token": token.as_authorization_header()}

	def verify_qr_user(
		self,
		encrypted_qr: str | None = None,
		pin_code: str | None = None,
	) -> tuple[str, Document]:
		"""Resolve QR + PIN to the enabled User name and live User document."""
		encrypted_qr = (encrypted_qr or "").strip()
		if not encrypted_qr:
			auth_error("Encrypted QR payload is required")

		try:
			raw_payload = decrypt_with_pin(pin_code, encrypted_qr)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "fadl_pos login_qr decrypt")
			auth_error("Invalid PIN or encrypted QR payload")

		payload = self._parse_qr_payload(raw_payload)
		api_key = payload["api_key"]

		user = frappe.db.get_value("User", {"api_key": api_key, "enabled": 1}, "name")
		user = require_qr_bound_user(user)

		doc = frappe.get_doc("User", user)
		if (doc.get(self.qr_fieldname) or "").strip() != encrypted_qr:
			auth_error("QR token has expired or was regenerated")

		return user, doc

	def _parse_qr_payload(self, raw: dict[str, object]) -> dict[str, object]:
		try:
			payload = QRPayloadIn.model_validate(raw)
		except PydanticValidationError:
			auth_error("Invalid PIN or encrypted QR payload")
			raise AssertionError("unreachable")
		return payload.model_dump()

	def _authenticate_password(self, login: str | None, password: str | None) -> str:
		login = (login or "").strip()
		password = password or ""
		if not login or not password:
			auth_error("Login and password are required")

		row = User.find_by_credentials(login, password)
		if not row or not row.get("is_authenticated"):
			auth_error("Invalid login credentials")

		return require_enabled_login_user(row["name"], enabled=row.get("enabled"))

	def _ensure_basic_token(self, user: str) -> BasicToken:
		doc = frappe.get_doc("User", user)
		return self._ensure_basic_token_for_doc(doc)

	def _ensure_basic_token_for_doc(self, doc: Document) -> BasicToken:
		changed = False
		if not doc.api_key:
			doc.api_key = frappe.generate_hash(length=15)
			changed = True

		api_secret = doc.get_password("api_secret", raise_exception=False)
		if not api_secret:
			api_secret = frappe.generate_hash(length=15)
			doc.api_secret = api_secret
			changed = True

		if changed:
			doc.save(ignore_permissions=True)

		return BasicToken(api_key=doc.api_key, api_secret=api_secret)

	def _rotate_api_secret(self, doc: Document) -> BasicToken:
		if not doc.api_key:
			doc.api_key = frappe.generate_hash(length=15)
		api_secret = frappe.generate_hash(length=15)
		doc.api_secret = api_secret
		return BasicToken(api_key=doc.api_key, api_secret=api_secret)

	def _set_qr_blob(self, doc: Document, value: str | None) -> None:
		if self.qr_fieldname not in frappe.db.get_table_columns("User"):
			frappe.throw(
				_("Missing User custom field {0}. Run bench migrate.").format(self.qr_fieldname),
				frappe.ValidationError,
			)
		doc.set(self.qr_fieldname, value)


# Compat alias for callers/tests still referring to the pre-redesign name.
TokenAuthService = LoginController
