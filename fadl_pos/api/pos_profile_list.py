# Copyright (c) 2026, FadlTech team and contributors
"""Список POS Profile для текущей смены/кассы: как нативный POS, плюс статус смены."""

from __future__ import annotations

import frappe
from frappe import _


def _require_logged_in_user() -> str:
	"""Сессия как в нативном POS: guest не допускается, user только из сессии."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Log in to continue."), frappe.AuthenticationError)
	return user


@frappe.whitelist(allow_guest=False)
def get_pos_profile_list(company: str | None = None) -> dict:
	"""Список POS Profile, где текущий пользователь в Applicable for Users, плюс признак открытой смены.

	Логика «кто в списке» повторяет `erpnext...pos_profile_query` (без fallback
	для пустого Applicable for Users — у нас только явное совпадение user).

	Статус смены по документу **POS Opening Entry** (как `check_opening_entry`, но
	для **профиля**: открыт = субмит, status=Open, нет `pos_closing_entry`).

	:API: ``POST/GET /api/method/fadl_pos.api.pos_profile_list.get_pos_profile_list``
	:param company: Не доверять без проверки прав; по умолчанию — user default.
	:returns: ``{ "user", "company", "profiles": [ { name, pos_profile fields..., shift } ] }``
	"""
	user = _require_logged_in_user()
	company = (company or "").strip() or frappe.defaults.get_user_default("Company")
	if not company:
		frappe.throw(_("Please set a default Company or pass company in the request."))

	if not frappe.db.exists("Company", company):
		frappe.throw(_("Company {0} not found.").format(company), frappe.DoesNotExistError)

	# Как pos_profile: только профили, где в child table есть текущий user
	profiles = frappe.db.sql(
		"""
		select
			pf.name,
			pf.company,
			pf.disabled,
			pf.warehouse,
			pf.letter_head
		from `tabPOS Profile` pf
		inner join `tabPOS Profile User` pfu
			on pfu.parent = pf.name and pfu.user = %(user)s
		where
			pf.company = %(company)s
			and ifnull(pf.disabled, 0) = 0
		order by pf.name
		""",
		{"user": user, "company": company},
		as_dict=True,
	)

	for row in profiles:
		row["shift"] = _shift_status_for_profile(row["name"])

	return {"user": user, "company": company, "profiles": profiles}


def _shift_status_for_profile(pos_profile: str) -> dict:
	"""Одна открытая смена на профиль (как валидация POS Opening Entry)."""
	oe_name = frappe.db.sql(
		"""
		select name
		from `tabPOS Opening Entry`
		where
			pos_profile = %(pos_profile)s
			and docstatus = 1
			and ifnull(status, '') = 'Open'
			and (pos_closing_entry is null or pos_closing_entry = '')
		limit 1
		""",
		{"pos_profile": pos_profile},
	)
	if not oe_name:
		return {
			"is_open": False,
			"opening_entry": None,
			"cashier": None,
			"period_start_date": None,
			"status": None,
		}

	data = frappe.db.get_value(
		"POS Opening Entry",
		oe_name[0][0],
		["name", "user", "period_start_date", "status", "pos_closing_entry"],
		as_dict=True,
	)
	return {
		"is_open": True,
		"opening_entry": data.name,
		"cashier": data.user,
		"period_start_date": data.period_start_date,
		"status": data.status,
	}
