# Copyright (c) 2026, FadlTech team and contributors

"""POS token and QR authentication service."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass

import frappe
from frappe import _
from frappe.core.doctype.user.user import User
from frappe.model.document import Document
from frappe.utils import cint

from fadl_pos.api.login.pin_cipher import decrypt_with_pin, encrypt_with_pin
from fadl_pos.serializers.login import AuthTokenResponse, QRGenerateResponse, QRPayloadPlain


PIN_RE = re.compile(r"^\d{6}$")
QR_PAYLOAD_VERSION = 1
QR_TOKEN_LENGTH = 32


def _auth_error(message: str) -> None:
	frappe.throw(_(message), frappe.AuthenticationError)


@dataclass(frozen=True)
class BasicToken:
	api_key: str
	api_secret: str

	def as_authorization_header(self) -> str:
		raw = f"{self.api_key}:{self.api_secret}".encode("utf-8")
		encoded = base64.b64encode(raw).decode("ascii")
		return f"Basic {encoded}"


class TokenAuthService:
	"""Centralized API-token and QR-token workflow for Fadl POS."""

	qr_fieldname = "qr_encrypted_data"

	def login(self, login: str | None = None, password: str | None = None) -> AuthTokenResponse:
		user = self._authenticate_password(login, password)
		return AuthTokenResponse(token=self._ensure_basic_token(user).as_authorization_header())

	def clear_sessions(self) -> AuthTokenResponse:
		user = self._require_session_user()
		doc = frappe.get_doc("User", user)
		token = self._rotate_api_secret(doc)
		self._set_qr_blob(doc, None)
		doc.save(ignore_permissions=True)
		return AuthTokenResponse(token=token.as_authorization_header())

	def generate_qr(self, pin_code: str | None = None) -> QRGenerateResponse:
		pin = self._require_pin(pin_code)
		user = self._require_session_user()
		doc = frappe.get_doc("User", user)
		token = self._ensure_basic_token_for_doc(doc)
		payload: QRPayloadPlain = {
			"v": QR_PAYLOAD_VERSION,
			"api_key": token.api_key,
			"qr_token": frappe.generate_hash(length=QR_TOKEN_LENGTH),
		}
		try:
			encrypted_qr = encrypt_with_pin(pin, payload)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "fadl_pos generate_qr encrypt")
			_auth_error("Could not create encrypted QR payload")

		self._set_qr_blob(doc, encrypted_qr)
		doc.save(ignore_permissions=True)
		return QRGenerateResponse(encrypted_qr=encrypted_qr)

	def login_qr(self, encrypted_qr: str | None = None, pin_code: str | None = None) -> AuthTokenResponse:
		_, doc = self.verify_qr_user(encrypted_qr=encrypted_qr, pin_code=pin_code)
		return AuthTokenResponse(token=self._ensure_basic_token_for_doc(doc).as_authorization_header())

	def verify_qr_user(
		self,
		encrypted_qr: str | None = None,
		pin_code: str | None = None,
	) -> tuple[str, Document]:
		"""Resolve QR + PIN to the enabled User name and live User document."""
		encrypted_qr = (encrypted_qr or "").strip()
		if not encrypted_qr:
			_auth_error("Encrypted QR payload is required")

		pin = self._require_pin(pin_code)
		try:
			raw_payload = decrypt_with_pin(pin, encrypted_qr)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "fadl_pos login_qr decrypt")
			_auth_error("Invalid PIN or encrypted QR payload")

		payload = self._parse_qr_payload(raw_payload)
		api_key = payload["api_key"]
		qr_token = payload["qr_token"]

		user = frappe.db.get_value("User", {"api_key": api_key, "enabled": 1}, "name")
		if not user or user in frappe.STANDARD_USERS:
			_auth_error("Invalid PIN or encrypted QR payload")

		doc = frappe.get_doc("User", user)
		if (doc.get(self.qr_fieldname) or "").strip() != encrypted_qr:
			_auth_error("QR token has expired or was regenerated")

		return user, doc

	def _parse_qr_payload(self, raw: dict[str, object]) -> QRPayloadPlain:
		v = raw.get("v")
		api_key_raw = raw.get("api_key")
		qr_token_raw = raw.get("qr_token")
		if not isinstance(v, int) or v != QR_PAYLOAD_VERSION:
			_auth_error("Invalid PIN or encrypted QR payload")
		if not isinstance(api_key_raw, str) or not isinstance(qr_token_raw, str):
			_auth_error("Invalid PIN or encrypted QR payload")
		api_key = api_key_raw.strip()
		qr_token = qr_token_raw.strip()
		if not api_key or len(qr_token) != QR_TOKEN_LENGTH:
			_auth_error("Invalid PIN or encrypted QR payload")
		return QRPayloadPlain(v=QR_PAYLOAD_VERSION, api_key=api_key, qr_token=qr_token)

	def _authenticate_password(self, login: str | None, password: str | None) -> str:
		login = (login or "").strip()
		password = password or ""
		if not login or not password:
			_auth_error("Login and password are required")

		row = User.find_by_credentials(login, password)
		if not row or not row.get("is_authenticated"):
			_auth_error("Invalid login credentials")

		user = row["name"]
		if user in frappe.STANDARD_USERS or not cint(row.get("enabled")):
			_auth_error("Invalid login credentials")
		return user

	def _require_pin(self, pin_code: str | None) -> str:
		pin = (pin_code or "").strip()
		if not PIN_RE.match(pin):
			_auth_error("PIN must be a 6-digit code")
		return pin

	def _require_session_user(self, user: str | None = None) -> str:
		user = user or frappe.session.user
		if not user or user == "Guest" or user in frappe.STANDARD_USERS:
			_auth_error("Log in to continue")
		return user

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
