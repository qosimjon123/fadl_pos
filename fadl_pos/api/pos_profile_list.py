# Copyright (c) 2026, FadlTech team and contributors
"""Список POS Profile для текущей смены/кассы: как нативный POS, плюс статус смены."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, flt

from fadl_pos.api.login.auth_service import TokenAuthService


OPEN_ACTION = "open_shift"
CLOSE_ACTION = "close_shift"
ACTION_TO_CAPABILITY = {
	OPEN_ACTION: "custom_can_open",
	CLOSE_ACTION: "custom_can_close",
}


def _require_logged_in_user() -> str:
	"""Сессия как в нативном POS: guest не допускается, user только из сессии."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Log in to continue."), frappe.AuthenticationError)
	return user


@frappe.whitelist(allow_guest=False)
def get_pos_profile_list() -> dict:
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
	company = frappe.defaults.get_user_default("Company") or None
	if not company:
		frappe.throw(_("Please set a default Company or pass company in the request."))

	# Как pos_profile: только неотключенные профили, где в child table есть текущий user.
	profiles = frappe.db.sql(
		"""
		select
			pf.name,
			pf.company,
			pf.disabled,
			pf.warehouse,
			pf.letter_head,
			pf.selling_price_list,
			pf.currency,
			ifnull(pfu.custom_can_open, 0) as can_open,
			ifnull(pfu.custom_can_close, 0) as can_close
		from `tabPOS Profile` pf
		inner join `tabPOS Profile User` pfu
			on pfu.parent = pf.name and pfu.user = %(user)s
		where
			ifnull(pf.disabled, 0) = 0
			and pf.company = %(company)s
		order by pf.name
		""",
		{"user": user, "company": company},
		as_dict=True,
	)

	for row in profiles:
		row["shift"] = _shift_status_for_profile(row["name"])
		row["permissions"] = {
			"can_open": bool(cint(row.pop("can_open", 0))),
			"can_close": bool(cint(row.pop("can_close", 0))),
		}
		row["checklists"] = _checklists_for_profile(row["name"])
		row["payment_methods"] = _payment_methods_for_profile(row["name"])
		row["ui_status"] = "open" if row["shift"]["is_open"] else "closed"

	return {
		"user": {
			"name": user,
			"full_name": frappe.db.get_value("User", user, "full_name"),
		},
		"company": frappe.defaults.get_user_default("Company"),
		"profiles": profiles,
	}


@frappe.whitelist(allow_guest=False, methods=["POST"])
def open_pos_shift(
	pos_profile: str | None = None,
	opening_amount: str | float | int | None = None,
	comment: str | None = None,
	encrypted_qr: str | None = None,
	pin_code: str | None = None,
) -> dict:
	"""Open a POS shift after current-user or QR+PIN manager authorization."""
	user = _require_logged_in_user()
	pos_profile = _require_pos_profile(pos_profile)
	_assert_profile_access(user, pos_profile)

	shift = _shift_status_for_profile(pos_profile)
	if shift["is_open"]:
		return {
			"ok": True,
			"already_open": True,
			"pos_profile": pos_profile,
			"opening_entry": shift["opening_entry"],
			"comment": (comment or "").strip(),
			"shift": shift,
		}

	opening_user = _assert_actor_or_approval(
		user=user,
		pos_profile=pos_profile,
		action=OPEN_ACTION,
		encrypted_qr=encrypted_qr,
		pin_code=pin_code,
	)

	profile = frappe.get_doc("POS Profile", pos_profile)
	balance_details = _opening_balance_details(profile, opening_amount)
	if not balance_details:
		frappe.throw(_("Please add Mode of payments and opening balance details."))

	doc = frappe.get_doc(
		{
			"doctype": "POS Opening Entry",
			"period_start_date": frappe.utils.get_datetime(),
			"posting_date": frappe.utils.getdate(),
			"user": opening_user,
			"pos_profile": pos_profile,
			"company": profile.company,
		}
	)
	doc.set("balance_details", balance_details)
	doc.submit()

	return {
		"ok": True,
		"pos_profile": pos_profile,
		"opening_entry": doc.name,
		"comment": (comment or "").strip(),
		"shift": _shift_status_for_profile(pos_profile),
	}


@frappe.whitelist(allow_guest=False, methods=["POST"])
def close_pos_shift(
	pos_profile: str | None = None,
	closing_amount: str | float | int | None = None,
	comment: str | None = None,
	encrypted_qr: str | None = None,
	pin_code: str | None = None,
) -> dict:
	"""Close the open POS shift after current-user or QR+PIN manager authorization."""
	user = _require_logged_in_user()
	pos_profile = _require_pos_profile(pos_profile)
	_assert_profile_access(user, pos_profile)
	_assert_shift_state(pos_profile, CLOSE_ACTION)
	_assert_actor_or_approval(
		user=user,
		pos_profile=pos_profile,
		action=CLOSE_ACTION,
		encrypted_qr=encrypted_qr,
		pin_code=pin_code,
	)

	shift = _shift_status_for_profile(pos_profile)
	opening_entry = frappe.get_doc("POS Opening Entry", shift["opening_entry"])

	from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import (
		make_closing_entry_from_opening,
	)

	closing = make_closing_entry_from_opening(opening_entry)
	closing_amount_value = flt(closing_amount or 0)
	for row in closing.get("payment_reconciliation") or []:
		row.closing_amount = closing_amount_value if _is_cash_payment(row.mode_of_payment) else row.expected_amount
	if comment and hasattr(closing, "remarks"):
		closing.remarks = comment.strip()
	closing.submit()

	return {
		"ok": True,
		"pos_profile": pos_profile,
		"closing_entry": closing.name,
		"comment": (comment or "").strip(),
		"shift": _shift_status_for_profile(pos_profile),
	}


def _shift_status_for_profile(pos_profile: str) -> dict:
	"""Вернуть текущую открытую и незакрытую смену профиля, если она есть.
	status: "Draft", "Open", "Closed", "Cancelled"
	"""
	opening_entries = frappe.db.sql(
		"""
		select
			name,
			user,
			period_start_date,
			status
		from `tabPOS Opening Entry`
		where
			pos_profile = %(pos_profile)s
			and docstatus = 1
			and ifnull(status, '') = 'Open'
			and (pos_closing_entry is null or pos_closing_entry = '')
		limit 1
		""",
		{"pos_profile": pos_profile},
		as_dict=True,
	)
	if not opening_entries:
		return {
			"is_open": False,
			"opening_entry": None,
			"cashier": None,
			"period_start_date": None,
			"status": None,
		}

	data = opening_entries[0]
	return {
		"is_open": True,
		"opening_entry": data.name,
		"cashier": data.user,
		"period_start_date": data.period_start_date,
		"status": data.status,
	}


def _checklists_for_profile(pos_profile: str) -> dict:
	doc = frappe.get_cached_doc("POS Profile", pos_profile)
	return {
		"opening": _checklist_rows(doc.get("custom_opening_checklist") or []),
		"closing": _checklist_rows(doc.get("custom_closing_checklists") or []),
	}


def _checklist_rows(rows) -> list[dict]:
	out = []
	for row in rows:
		if cint(row.get("disabled")):
			continue
		out.append(
			{
				"name": row.get("name"),
				"title": row.get("title"),
				"idx": row.get("idx"),
			}
		)
	return out


def _payment_methods_for_profile(pos_profile: str) -> list[dict]:
	doc = frappe.get_cached_doc("POS Profile", pos_profile)
	return [
		{
			"mode_of_payment": row.mode_of_payment,
			"default": bool(cint(row.get("default"))),
			"allow_in_returns": bool(cint(row.get("allow_in_returns"))),
		}
		for row in doc.get("payments") or []
	]


def _require_pos_profile(pos_profile: str | None) -> str:
	pos_profile = (pos_profile or "").strip()
	if not pos_profile:
		frappe.throw(_("POS Profile is required."), frappe.ValidationError)
	if not frappe.db.exists("POS Profile", pos_profile):
		frappe.throw(_("POS Profile {0} not found.").format(pos_profile), frappe.DoesNotExistError)
	if cint(frappe.db.get_value("POS Profile", pos_profile, "disabled")):
		frappe.throw(_("POS Profile {0} is disabled.").format(pos_profile), frappe.PermissionError)
	return pos_profile


def _profile_user_row(user: str, pos_profile: str) -> dict | None:
	rows = frappe.db.get_all(
		"POS Profile User",
		filters={"parent": pos_profile, "user": user},
		fields=["user", "custom_can_open", "custom_can_close"],
		limit=1,
	)
	return rows[0] if rows else None


def _assert_profile_access(user: str, pos_profile: str) -> dict:
	row = _profile_user_row(user, pos_profile)
	if not row:
		frappe.throw(
			_("User {0} is not assigned to POS Profile {1}.").format(user, pos_profile),
			frappe.PermissionError,
		)
	return row


def _assert_profile_capability(user: str, pos_profile: str, action: str) -> None:
	row = _assert_profile_access(user, pos_profile)
	fieldname = ACTION_TO_CAPABILITY[action]
	if not cint(row.get(fieldname)):
		frappe.throw(
			_("User {0} is not allowed to perform this POS action.").format(user),
			frappe.PermissionError,
		)


def _assert_actor_or_approval(
	user: str,
	pos_profile: str,
	action: str,
	encrypted_qr: str | None,
	pin_code: str | None,
) -> str:
	try:
		_assert_profile_capability(user, pos_profile, action)
		return user
	except frappe.PermissionError:
		if not (encrypted_qr or "").strip() or not (pin_code or "").strip():
			raise

	approver = TokenAuthService().verify_qr_user(encrypted_qr=encrypted_qr, pin_code=pin_code)
	_assert_profile_capability(approver, pos_profile, action)
	return approver


def _assert_shift_state(pos_profile: str, action: str) -> None:
	is_open = bool(_shift_status_for_profile(pos_profile)["is_open"])
	if action == OPEN_ACTION and is_open:
		frappe.throw(
			_("POS Profile {0} already has an open shift.").format(pos_profile),
			frappe.ValidationError,
		)
	if action == CLOSE_ACTION and not is_open:
		frappe.throw(
			_("POS Profile {0} does not have an open shift.").format(pos_profile),
			frappe.ValidationError,
		)


def _opening_balance_details(profile, opening_amount: str | float | int | None) -> list[dict]:
	payments = profile.get("payments") or []
	default_payment = next((p for p in payments if cint(p.get("default"))), None)
	cash_payment = next((p for p in payments if _is_cash_payment(p.mode_of_payment)), None)
	target_payment = cash_payment or default_payment or (payments[0] if payments else None)
	amount = flt(opening_amount or 0)

	out = []
	for payment in payments:
		out.append(
			{
				"mode_of_payment": payment.mode_of_payment,
				"opening_amount": amount
				if target_payment and payment.mode_of_payment == target_payment.mode_of_payment
				else 0,
			}
		)
	return out


def _is_cash_payment(mode_of_payment: str | None) -> bool:
	mode_of_payment = (mode_of_payment or "").strip()
	if not mode_of_payment:
		return False
	return frappe.db.get_value("Mode of Payment", mode_of_payment, "type") == "Cash"
