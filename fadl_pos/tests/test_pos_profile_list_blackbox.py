# Copyright (c) 2026, FadlTech team and contributors

"""Black-box негативные и награничные сценарии для get_pos_profile_list (без опоры на внутреннюю реализацию)."""

from __future__ import annotations

import unittest

import frappe
from frappe.tests import IntegrationTestCase
from fadl_pos.api.pos_profile_list import get_pos_profile_list  # type: ignore


def _any_company() -> str | None:
	"""Первая компания в сайте, если ERPNext-данные есть (иначе тесты, которым нужна компания, пропускаются)."""
	names = frappe.get_all("Company", pluck="name", limit=1)
	return names[0] if names else None


@unittest.skipUnless(_any_company(), "В сайте нет Company — пропуск сценариев с валидной компанией")
class TestGetPosProfileListBlackbox(IntegrationTestCase):
	"""Попытки «сломать» или вывести API из стабильного поведения снаружи."""

	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	# 1. неаутентифицированный клиент
	def test_01_guest_is_rejected(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.AuthenticationError):
			get_pos_profile_list()

	# 2. вымышленная компания
	def test_02_unknown_company_name_is_rejected(self):
		frappe.set_user("Administrator")
		with self.assertRaises(frappe.DoesNotExistError):
			get_pos_profile_list(company="COMPANY_DOES_NOT_EXIST_9f2b7c1e")

	# 3. строка, похожая на SQL-инъекцию, не должна валить процесс с неожиданной ошибкой
	def test_03_sqlish_company_string_does_not_cause_unhandled_error(self):
		frappe.set_user("Administrator")
		crafty = "x'; DELETE FROM `tabUser`; --"
		with self.assertRaises(frappe.DoesNotExistError):
			get_pos_profile_list(company=crafty)

	# 4. логическое True как company (как при десериализации JSON «неожиданный тип»)
	def test_04_bool_true_for_company_does_not_silently_succeed(self):
		frappe.set_user("Administrator")
		with self.assertRaises((TypeError, AttributeError)):
			get_pos_profile_list(company=True)  # type: ignore[arg-type]

	# 5. очень длинное имя компании
	def test_05_extremely_long_company_does_not_crash_process(self):
		frappe.set_user("Administrator")
		huge = "A" * 8000
		with self.assertRaises(frappe.DoesNotExistError):
			get_pos_profile_list(company=huge)

	# 6. нулевой байт и «битая» Unicode в параметре
	def test_06_nul_and_obscure_unicode_in_company_rejected_safely(self):
		frappe.set_user("Administrator")
		for bad in ("C\x00ompanyX", "شركة\x00", "\u200e\u200fT"):
			with self.subTest(company=repr(bad)):
				with self.assertRaises(frappe.DoesNotExistError):
					get_pos_profile_list(company=bad)

	# 7. стабильная форма ответа при валидном вызове
	def test_07_success_payload_has_user_company_and_profiles_list(self):
		company = _any_company()
		assert company
		frappe.set_user("Administrator")
		out = get_pos_profile_list(company=company)
		self.assertIsInstance(out, dict)
		self.assertIn("user", out)
		self.assertIn("company", out)
		self.assertIn("profiles", out)
		self.assertEqual(out["company"], company)
		self.assertIsInstance(out["profiles"], list)
		for row in out["profiles"]:
			self.assertIn("name", row)
			self.assertIn("shift", row)
			self.assertIsInstance(row["shift"], dict)
			if row["shift"]:
				self.assertIn("is_open", row["shift"])

	# 8. передача не-строки как company (частый баг в HTTP-слоях)
	def test_08_non_string_company_must_not_succeed_silently(self):
		frappe.set_user("Administrator")
		company = _any_company()
		assert company
		try:
			out = get_pos_profile_list(company=123)  # type: ignore[arg-type]
		except (TypeError, AttributeError) as e:
			self.assertIsNotNone(e)
			return
		if isinstance(out, dict) and out.get("company") == company:
			self.fail("нестроковый company не должен тихо превращаться в успешный ответ с default company")
		self.assertIsInstance(out, dict)

	# 9. «параметр-коллекция» вместо строки
	def test_09_collection_as_company_does_not_return_normal_success(self):
		frappe.set_user("Administrator")
		try:
			out = get_pos_profile_list(company=["A"])  # type: ignore[arg-type]
		except (TypeError, AttributeError) as e:
			self.assertIsNotNone(e)
			return
		self.assertNotIn("profiles", out or {}, msg="коллекция в company — не валидный успешный ответ")

	# 10. двойной вызов — тот же состав ключей (идемпотентность формы ответа)
	def test_10_double_call_same_shape(self):
		company = _any_company()
		assert company
		frappe.set_user("Administrator")
		a = get_pos_profile_list(company=company)
		b = get_pos_profile_list(company=company)
		self.assertEqual(set(a.keys()), set(b.keys()))
		self.assertIsInstance(a["profiles"], list)
		self.assertIsInstance(b["profiles"], list)
