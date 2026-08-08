# Copyright (c) 2026, FadlTech team and contributors

"""Integration tests for `fadl_pos.core` — needs a real Frappe DB/session."""

from __future__ import annotations

import frappe
from frappe.tests import IntegrationTestCase

from fadl_pos.core.permission import BaseController, is_manager, require_session_user


class TestRequireSessionUser(IntegrationTestCase):
	TEST_EMAIL = "fadl_pos_core_test@example.com"

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("User", cls.TEST_EMAIL):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": cls.TEST_EMAIL,
					"first_name": "CoreTest",
					"send_welcome_email": 0,
				}
			)
			user.insert(ignore_permissions=True)
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

	def test_rejects_guest(self):
		with self.assertRaises(frappe.AuthenticationError):
			require_session_user("Guest")

	def test_accepts_administrator(self):
		"""Generic gate only rejects Guest; Administrator is fine here (unlike
		login's stricter `require_authenticated_session`, see `login/permission.py`)."""
		self.assertEqual(require_session_user("Administrator"), "Administrator")

	def test_accepts_real_user(self):
		self.assertEqual(require_session_user(self.TEST_EMAIL), self.TEST_EMAIL)

	def test_falls_back_to_session_user(self):
		frappe.set_user(self.TEST_EMAIL)
		self.assertEqual(require_session_user(), self.TEST_EMAIL)

	def test_base_controller_sets_user(self):
		controller = BaseController(self.TEST_EMAIL)
		self.assertEqual(controller.user, self.TEST_EMAIL)

	def test_base_controller_rejects_guest(self):
		with self.assertRaises(frappe.AuthenticationError):
			BaseController("Guest")


class TestIsManager(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	def test_administrator_is_manager(self):
		self.assertTrue(is_manager())
