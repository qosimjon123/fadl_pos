# Copyright (c) 2026, FadlTech team and contributors

"""Интеграционные тесты get_qr_data и login_with_qr (PIN — ровно 6 цифр)."""

from __future__ import annotations

import frappe
from frappe.auth import CookieManager, LoginManager
from frappe.tests import IntegrationTestCase
from frappe.utils import set_request
from frappe.utils.password import update_password

from fadl_pos.api.login.login_with_qr import get_qr_data, login_with_qr # type: ignore


class TestLoginWithQrAPI(IntegrationTestCase):
	"""См. https://docs.frappe.io/framework/user/en/guides/automation/testing — интеграционные тесты приложения."""

	TEST_EMAIL = "fadl_pos_api_test@example.com"
	TEST_PASSWORD = "fadl-pos-test-pwd-9xK"
	TEST_EMAIL_OTHER = "fadl_pos_api_test_other@example.com"
	TEST_PASSWORD_OTHER = "fadl-pos-other-pwd-7mQ"

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls._create_test_user(cls.TEST_EMAIL, cls.TEST_PASSWORD, "FadlPos")
		cls._create_test_user(cls.TEST_EMAIL_OTHER, cls.TEST_PASSWORD_OTHER, "Other")

	@classmethod
	def tearDownClass(cls):
		for email in (cls.TEST_EMAIL, cls.TEST_EMAIL_OTHER):
			if frappe.db.exists("User", email):
				frappe.delete_doc("User", email, force=True)
		frappe.db.commit()
		super().tearDownClass()

	@classmethod
	def _create_test_user(cls, email: str, password: str, first_name: str):
		if frappe.db.exists("User", email):
			frappe.delete_doc("User", email, force=True)
			frappe.db.commit()

		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": first_name,
				"send_welcome_email": 0,
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
		set_request(method="POST", path=path)
		frappe.local.cookie_manager = CookieManager()
		frappe.local.login_manager = LoginManager()

	# --- get_qr_data (5) ---

	def test_get_qr_data_success_for_self(self):
		frappe.set_user(self.TEST_EMAIL)
		out = get_qr_data(self.TEST_EMAIL, self.TEST_PASSWORD, "123456")
		self.assertIn("encrypted_blob", out)
		self.assertTrue(out["encrypted_blob"])

	def test_get_qr_data_rejects_wrong_password(self):
		frappe.set_user(self.TEST_EMAIL)
		with self.assertRaises(frappe.AuthenticationError):
			get_qr_data(self.TEST_EMAIL, "wrong-password", "123456")

	def test_get_qr_data_rejects_invalid_pin(self):
		frappe.set_user(self.TEST_EMAIL)
		for bad in ("", "12345", "1234567", "12ab34"):
			with self.subTest(pin=bad):
				with self.assertRaises(frappe.AuthenticationError):
					get_qr_data(self.TEST_EMAIL, self.TEST_PASSWORD, bad)

	def test_get_qr_data_non_manager_cannot_use_other_user_credentials(self):
		frappe.set_user(self.TEST_EMAIL)
		with self.assertRaises(frappe.PermissionError):
			get_qr_data(self.TEST_EMAIL_OTHER, self.TEST_PASSWORD_OTHER, "999999")

	def test_get_qr_data_system_manager_can_issue_blob_for_other_user(self):
		frappe.set_user("Administrator")
		out = get_qr_data(self.TEST_EMAIL, self.TEST_PASSWORD, "567890")
		self.assertIn("encrypted_blob", out)

	# --- login_with_qr (5) ---

	def _bootstrap_blob(self, pin: str = "424242") -> str:
		frappe.set_user(self.TEST_EMAIL)
		return get_qr_data(self.TEST_EMAIL, self.TEST_PASSWORD, pin)["encrypted_blob"]

	def test_login_with_qr_success_sets_session(self):
		blob = self._bootstrap_blob()
		frappe.set_user("Guest")
		self._post_request("/api/method/fadl_pos.api.login.login_with_qr.login_with_qr")
		res = login_with_qr(blob, "424242")
		self.assertTrue(res.get("ok"))
		self.assertEqual(res.get("user"), self.TEST_EMAIL)

	def test_login_with_qr_rejects_wrong_or_invalid_pin(self):
		blob = self._bootstrap_blob()
		frappe.set_user("Guest")
		self._post_request("/api/method/fadl_pos.api.login.login_with_qr.login_with_qr")
		for bad in ("000000", "42424"):
			with self.subTest(pin=bad):
				with self.assertRaises(frappe.AuthenticationError):
					login_with_qr(blob, bad)

	def test_login_with_qr_rejects_missing_blob(self):
		frappe.set_user("Guest")
		self._post_request("/api/method/fadl_pos.api.login.login_with_qr.login_with_qr")
		with self.assertRaises(frappe.AuthenticationError):
			login_with_qr("", "424242")

	def test_login_with_qr_rejects_tampered_blob(self):
		blob = self._bootstrap_blob()
		tampered = blob[:-3] + ("A" if blob[-3] != "A" else "B") + blob[-2:]
		frappe.set_user("Guest")
		self._post_request("/api/method/fadl_pos.api.login.login_with_qr.login_with_qr")
		with self.assertRaises(frappe.AuthenticationError):
			login_with_qr(tampered, "424242")

	def test_login_with_qr_rejects_stale_secret_after_regenerate(self):
		pin = "777777"
		blob = self._bootstrap_blob(pin)
		doc = frappe.get_doc("User", self.TEST_EMAIL)
		doc.api_secret = frappe.generate_hash(length=15)
		doc.save(ignore_permissions=True)
		frappe.db.commit()

		frappe.set_user("Guest")
		self._post_request("/api/method/fadl_pos.api.login.login_with_qr.login_with_qr")
		with self.assertRaises(frappe.AuthenticationError):
			login_with_qr(blob, pin)
