# Copyright (c) 2026, FadlTech team and contributors

"""Integration tests for the Fadl POS token/QR login API (needs Frappe DB/session)."""

from __future__ import annotations

import base64

import frappe
from frappe.auth import CookieManager, LoginManager, validate_api_key_secret
from frappe.tests import IntegrationTestCase
from frappe.utils import set_request
from frappe.utils.password import update_password

from fadl_pos.login.controller import TokenAuthService
from fadl_pos.login.serializer import AuthTokenResponse
from fadl_pos.login.whitelist import clear_sessions, generate_qr, login, login_qr


class TestLoginWithQrAPI(IntegrationTestCase):
	"""POS token API integration tests."""

	TEST_EMAIL = "fadl_pos_api_test@example.com"
	TEST_PASSWORD = "fadl-pos-test-pwd-9xK"
	TEST_EMAIL_OTHER = "fadl_pos_api_test_other@example.com"
	TEST_PASSWORD_OTHER = "fadl-pos-other-pwd-7mQ"
	TEST_EMAIL_DISABLED = "fadl_pos_api_disabled@example.com"
	TEST_PASSWORD_DISABLED = "fadl-pos-disabled-pwd-4nP"

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls._create_test_user(cls.TEST_EMAIL, cls.TEST_PASSWORD, "FadlPos")
		cls._create_test_user(cls.TEST_EMAIL_OTHER, cls.TEST_PASSWORD_OTHER, "Other")
		cls._create_test_user(cls.TEST_EMAIL_DISABLED, cls.TEST_PASSWORD_DISABLED, "Disabled", enabled=0)

	@classmethod
	def tearDownClass(cls):
		for email in (
			cls.TEST_EMAIL,
			cls.TEST_EMAIL_OTHER,
			cls.TEST_EMAIL_DISABLED,
		):
			if frappe.db.exists("User", email):
				frappe.delete_doc("User", email, force=True)
		frappe.db.commit()
		super().tearDownClass()

	@classmethod
	def _create_test_user(cls, email: str, password: str, first_name: str, *, enabled: int = 1):
		if frappe.db.exists("User", email):
			frappe.delete_doc("User", email, force=True)
			frappe.db.commit()

		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": first_name,
				"send_welcome_email": 0,
				"enabled": enabled,
			}
		)
		user.insert(ignore_permissions=True)
		user.add_roles("Sales User")
		update_password(email, password)
		frappe.db.commit()

	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	@staticmethod
	def _post_request(path: str) -> None:
		set_request(method="POST", path=path, environ_base={"REMOTE_ADDR": "127.0.0.1"})
		frappe.local.request_ip = "127.0.0.1"
		frappe.local.cookie_manager = CookieManager()
		frappe.local.login_manager = LoginManager()

	@staticmethod
	def _basic_header(payload: str | AuthTokenResponse | dict) -> str:
		if isinstance(payload, dict):
			return payload["token"]
		return payload

	@staticmethod
	def _decode_basic_token(value: str) -> tuple[str, str]:
		assert value.startswith("Basic ")
		decoded = base64.b64decode(value.removeprefix("Basic ")).decode("utf-8")
		api_key, api_secret = decoded.split(":", 1)
		return api_key, api_secret

	def _assert_basic_token_valid_for_user(
		self, value: str | AuthTokenResponse | dict, user: str
	) -> tuple[str, str]:
		api_key, api_secret = self._decode_basic_token(self._basic_header(value))
		self.assertEqual(frappe.db.get_value("User", user, "api_key"), api_key)
		validate_api_key_secret(api_key, api_secret)
		self.assertEqual(frappe.session.user, user)
		return api_key, api_secret

	def test_login_returns_basic_token_and_session(self):
		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login")
		token = login(self.TEST_EMAIL, self.TEST_PASSWORD)
		self._assert_basic_token_valid_for_user(token, self.TEST_EMAIL)

	def test_login_accepts_legacy_usr_pwd_names(self):
		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login")
		token = login(usr=self.TEST_EMAIL, pwd=self.TEST_PASSWORD)
		self._assert_basic_token_valid_for_user(token, self.TEST_EMAIL)

	def test_login_rejects_bad_password(self):
		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login")
		with self.assertRaises(frappe.AuthenticationError):
			login(self.TEST_EMAIL, "not-the-password")

	def test_login_rejects_disabled_user(self):
		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login")
		with self.assertRaises(frappe.AuthenticationError):
			login(self.TEST_EMAIL_DISABLED, self.TEST_PASSWORD_DISABLED)

	def test_generate_qr_allows_administrator_session(self):
		frappe.set_user("Administrator")
		result = generate_qr("123456")
		self.assertTrue(result["encrypted_qr"])

	def test_clear_sessions_allows_administrator_session(self):
		frappe.set_user("Administrator")
		result = clear_sessions()
		self.assertTrue(result["token"].startswith("Basic "))

	def test_generate_qr_returns_encrypted_payload_without_persisting(self):
		frappe.set_user(self.TEST_EMAIL)
		first = generate_qr("123456")["encrypted_qr"]
		self.assertTrue(first)

		second = generate_qr("123456")["encrypted_qr"]
		self.assertTrue(second)
		self.assertNotEqual(first, second)

	def test_generate_qr_rejects_invalid_pin(self):
		frappe.set_user(self.TEST_EMAIL)
		for bad in ("", "12345", "1234567", "12ab34"):
			with self.subTest(pin=bad):
				with self.assertRaises((frappe.AuthenticationError, frappe.ValidationError)):
					generate_qr(bad)

	def _bootstrap_blob(self, pin: str = "424242") -> str:
		frappe.set_user(self.TEST_EMAIL)
		return generate_qr(pin)["encrypted_qr"]

	def test_login_qr_success_returns_basic_token(self):
		blob = self._bootstrap_blob()
		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login_qr")
		token = login_qr(blob, "424242")
		self._assert_basic_token_valid_for_user(token, self.TEST_EMAIL)

	def test_login_qr_rejects_wrong_or_invalid_pin(self):
		blob = self._bootstrap_blob()
		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login_qr")
		for bad in ("000000", "42424"):
			with self.subTest(pin=bad):
				with self.assertRaises((frappe.AuthenticationError, frappe.ValidationError)):
					login_qr(blob, bad)

	def test_login_qr_rejects_missing_blob(self):
		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login_qr")
		with self.assertRaises((frappe.AuthenticationError, frappe.ValidationError)):
			login_qr("", "424242")

	def test_login_qr_rejects_tampered_blob(self):
		blob = self._bootstrap_blob()
		tampered = blob[:-3] + ("A" if blob[-3] != "A" else "B") + blob[-2:]
		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login_qr")
		with self.assertRaises(frappe.AuthenticationError):
			login_qr(tampered, "424242")

	def test_login_qr_still_works_after_regenerate(self):
		pin = "777777"
		blob = self._bootstrap_blob(pin)
		frappe.set_user(self.TEST_EMAIL)
		generate_qr(pin)

		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login_qr")
		token = login_qr(blob, pin)
		self._assert_basic_token_valid_for_user(token, self.TEST_EMAIL)

	def test_login_qr_rejects_stale_qr_after_clear_sessions(self):
		pin = "888888"
		blob = self._bootstrap_blob(pin)
		frappe.set_user(self.TEST_EMAIL)
		clear_sessions()

		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login_qr")
		with self.assertRaises(frappe.AuthenticationError):
			login_qr(blob, pin)

	def test_clear_sessions_rotates_secret(self):
		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login")
		old_token = login(self.TEST_EMAIL, self.TEST_PASSWORD)
		old_api_key, old_api_secret = self._decode_basic_token(self._basic_header(old_token))

		frappe.set_user(self.TEST_EMAIL)
		generate_qr("123456")
		new_token = clear_sessions()
		new_api_key, new_api_secret = self._decode_basic_token(self._basic_header(new_token))

		self.assertEqual(old_api_key, new_api_key)
		self.assertNotEqual(old_api_secret, new_api_secret)

		with self.assertRaises(frappe.AuthenticationError):
			validate_api_key_secret(old_api_key, old_api_secret)

	def test_legacy_controller_alias_still_delegates_to_v2_contract(self):
		"""`TokenAuthService` is a backward-compat alias for `LoginController`."""
		frappe.set_user("Guest")
		self._post_request("/api/v2/method/fadl_pos.login.whitelist.login")
		token = TokenAuthService().login(self.TEST_EMAIL, self.TEST_PASSWORD)
		self._assert_basic_token_valid_for_user(token, self.TEST_EMAIL)
