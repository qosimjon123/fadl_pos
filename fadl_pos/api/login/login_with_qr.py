# Copyright (c) 2026, FadlTech team and contributors

"""Каскад: bootstrap (логин + пароль + PIN → blob), verify (blob + PIN → сессия)."""

from __future__ import annotations

import re

import frappe
from frappe import _
from frappe.auth import LoginManager, validate_api_key_secret
from frappe.core.doctype.user.user import User
from frappe.utils import cint

from fadl_pos.api.login.pin_cipher import decrypt_with_pin, encrypt_with_pin


def _bad_creds():
	frappe.throw(_("Invalid login, password or PIN"), frappe.AuthenticationError)


def _bad_blob():
	frappe.throw(_("Invalid PIN or encrypted payload"), frappe.AuthenticationError)


def _can_generate_keys_for(target_user: str) -> bool:
	su = frappe.session.user
	if su == target_user:
		return True
	return "System Manager" in frappe.get_roles(su)


_PIN_RE = re.compile(r"^\d{6}$")


def _require_pin(pin_code: str | None) -> str:
	"""PIN: ровно 6 цифр (код для POS)."""
	pin = (pin_code or "").strip()
	if not _PIN_RE.match(pin):
		frappe.throw(_("PIN must be a 6-digit code"), frappe.AuthenticationError)
	return pin


@frappe.whitelist(allow_guest=False, methods=["POST"])
def get_qr_data(login: str, password: str, pin_code: str):
	"""Генерация api_key/api_secret и отдача в encrypted_blob. SM — для любого; иначе только себе."""
	pin_code = _require_pin(pin_code)
	login = (login or "").strip()
	password = password or ""
	if not login or not password:
		frappe.throw(_("Login and password are required"), frappe.AuthenticationError)

	row = User.find_by_credentials(login, password)
	if not row or not row.get("is_authenticated"):
		_bad_creds()

	name = row["name"]
	if name in frappe.STANDARD_USERS or not cint(row.get("enabled")):
		_bad_creds()

	if not _can_generate_keys_for(name):
		frappe.throw(_("Not permitted to generate keys for this user"), frappe.PermissionError)

	doc = frappe.get_doc("User", name)
	secret = frappe.generate_hash(length=15)
	if not doc.api_key:
		doc.api_key = frappe.generate_hash(length=15)
	doc.api_secret = secret
	doc.save(ignore_permissions=True)

	try:
		blob = encrypt_with_pin(pin_code, {"api_key": doc.api_key, "api_secret": secret})
	except Exception:
		frappe.log_error(frappe.get_traceback(), "fadl_pos cascade_bootstrap encrypt")
		frappe.throw(_("Could not create encrypted payload"), frappe.AuthenticationError)

	return {"encrypted_blob": blob}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def login_with_qr(encrypted_blob: str, pin_code: str):
	"""Вход без сессии: кто угодно может вызвать, но успех только при верной паре blob+PIN и валидных api_key/api_secret.

	Так устройство после offline-хранения blob получает cookie (sid) при первом обращении.
	"""
	if not (encrypted_blob or "").strip():
		frappe.throw(_("Encrypted payload is required"), frappe.AuthenticationError)

	pin_code = _require_pin(pin_code)

	try:
		data = decrypt_with_pin(pin_code, str(encrypted_blob).strip())
	except Exception:
		_bad_blob()

	api_key, api_secret = data.get("api_key"), data.get("api_secret")
	if not api_key or not api_secret:
		_bad_blob()

	try:
		validate_api_key_secret(api_key, api_secret)
	except frappe.AuthenticationError:
		_bad_blob()

	user = frappe.session.user
	if not user or user == "Guest":
		user = frappe.db.get_value("User", {"api_key": api_key, "enabled": 1}, "name")
	if not user or user == "Guest":
		_bad_blob()

	LoginManager().login_as(user)
	frappe.db.commit()

	return {"ok": True, "user": user, "message": _("Logged In")}
