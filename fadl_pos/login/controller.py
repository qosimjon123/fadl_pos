# Copyright (c) 2026, FadlTech team and contributors

"""POS token and QR authentication actions (create/rotate token, generate/verify QR)."""

from __future__ import annotations

import frappe
from frappe.sessions import clear_sessions
from frappe.twofactor import authenticate_for_2factor, confirm_otp_token, should_run_2fa

from fadl_pos.core.errors import auth_error
from fadl_pos.login import events
from fadl_pos.login.permission import require_session_user
from fadl_pos.login.processing import qr as qr_processing
from fadl_pos.login.processing import token as token_processing


class LoginController:
	"""Centralized API-token and QR-token actions for Fadl POS."""

	def login(self, usr: str, pwd: str) -> dict:
		lm = frappe.local.login_manager
		lm.run_trigger("before_login")

		if frappe.get_system_settings("disable_user_pass_login"):
			auth_error("Login with username and password is not allowed.")

		frappe.clear_cache(user=usr)
		lm.authenticate(user=usr, pwd=pwd)

		if lm.force_user_to_reset_password():
			auth_error("Password Reset")

		if should_run_2fa(lm.user):
			authenticate_for_2factor(lm.user)
			if not confirm_otp_token(lm):
				auth_error("Two-factor authentication required")

		frappe.form_dict.pop("pwd", None)
		lm.post_login()

		doc = frappe.get_doc("User", lm.user)
		token = token_processing.ensure_basic_token(doc)
		events.login_succeeded(user=lm.user, method="password")
		return {"token": token.as_authorization_header()}

	def clear_sessions(self) -> dict:
		user = require_session_user()
		doc = frappe.get_doc("User", user)
		token = token_processing.rotate_api_secret(doc)
		clear_sessions(user, keep_current=True, force=True)
		events.sessions_cleared(user=user)
		return {"token": token.as_authorization_header()}

	def generate_qr(self, pin_code: str) -> dict:
		user = require_session_user()
		doc = frappe.get_doc("User", user)
		token = token_processing.ensure_basic_token(doc)
		payload = qr_processing.build_payload(token)
		encrypted_qr = qr_processing.encrypt_payload(pin_code, payload)
		events.qr_generated(user=user)
		return {"encrypted_qr": encrypted_qr}

	def login_qr(self, encrypted_qr: str, pin_code: str) -> dict:
		user, doc = qr_processing.resolve_user(encrypted_qr, pin_code)
		frappe.local.login_manager.login_as(user)
		token = token_processing.ensure_basic_token(doc)
		events.login_succeeded(user=user, method="qr")
		return {"token": token.as_authorization_header()}