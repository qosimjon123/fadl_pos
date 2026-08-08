# Copyright (c) 2026, FadlTech team and contributors

"""End-to-end happy path for the login feature.

The app has no HTTP/browser test harness (no Playwright/Cypress setup) yet, so
"e2e" here means driving every whitelisted RPC entry point in `whitelist.py`
back-to-back, in the same order and via the same `set_request` plumbing a real
POS client would hit, rather than calling internal helpers directly. This is
the template other feature modules should follow until a real HTTP-level
harness exists.
"""

from __future__ import annotations

import base64

import frappe
from frappe.auth import CookieManager, LoginManager, validate_api_key_secret
from frappe.tests import IntegrationTestCase
from frappe.utils import set_request
from frappe.utils.password import update_password

from fadl_pos.login.whitelist import clear_sessions, generate_qr, login, login_qr


class TestLoginHappyPathE2E(IntegrationTestCase):
	TEST_EMAIL = "fadl_pos_e2e_test@example.com"
	TEST_PASSWORD = "fadl-pos-e2e-pwd-3zR"
	PIN = "135790"

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if frappe.db.exists("User", cls.TEST_EMAIL):
			frappe.delete_doc("User", cls.TEST_EMAIL, force=True)
			frappe.db.commit()

		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": cls.TEST_EMAIL,
				"first_name": "E2E",
				"send_welcome_email": 0,
			}
		)
		user.insert(ignore_permissions=True)
		user.add_roles("Sales User")
		update_password(cls.TEST_EMAIL, cls.TEST_PASSWORD)
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		if frappe.db.exists("User", cls.TEST_EMAIL):
			frappe.delete_doc("User", cls.TEST_EMAIL, force=True)
			frappe.db.commit()
		super().tearDownClass()

	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	@staticmethod
	def _simulate_request(path: str) -> None:
		set_request(method="POST", path=path, environ_base={"REMOTE_ADDR": "127.0.0.1"})
		frappe.local.request_ip = "127.0.0.1"
		frappe.local.cookie_manager = CookieManager()
		frappe.local.login_manager = LoginManager()

	@staticmethod
	def _decode_basic_token(value: str) -> tuple[str, str]:
		decoded = base64.b64decode(value.removeprefix("Basic ")).decode("utf-8")
		api_key, api_secret = decoded.split(":", 1)
		return api_key, api_secret

	def test_login_then_qr_bootstrap_then_qr_login_then_clear_sessions(self):
		# 1. Password login (cashier opens the POS on a new device).
		frappe.set_user("Guest")
		self._simulate_request("/api/v2/method/fadl_pos.login.whitelist.login")
		password_token = login(self.TEST_EMAIL, self.TEST_PASSWORD)["token"]
		self.assertTrue(password_token.startswith("Basic "))

		# The token is only good as authentication once the client sends it back
		# (Authorization: Basic ...) on a subsequent request — simulate that here.
		api_key, api_secret = self._decode_basic_token(password_token)
		validate_api_key_secret(api_key, api_secret)
		self.assertEqual(frappe.session.user, self.TEST_EMAIL)

		# 2. Cashier enrolls a PIN-protected QR for fast re-login.
		encrypted_qr = generate_qr(self.PIN)["encrypted_qr"]
		self.assertTrue(encrypted_qr)

		# 3. A second device scans the QR + PIN to log in.
		frappe.set_user("Guest")
		self._simulate_request("/api/v2/method/fadl_pos.login.whitelist.login_qr")
		qr_token = login_qr(encrypted_qr, self.PIN)["token"]
		self.assertTrue(qr_token.startswith("Basic "))

		qr_api_key, qr_api_secret = self._decode_basic_token(qr_token)
		validate_api_key_secret(qr_api_key, qr_api_secret)
		self.assertEqual(frappe.session.user, self.TEST_EMAIL)

		# 4. Cashier signs out everywhere; the QR/token issued above must die with it.
		frappe.set_user(self.TEST_EMAIL)
		clear_sessions()
		self.assertFalse(frappe.db.get_value("User", self.TEST_EMAIL, "qr_encrypted_data"))
		with self.assertRaises(frappe.AuthenticationError):
			validate_api_key_secret(qr_api_key, qr_api_secret)
