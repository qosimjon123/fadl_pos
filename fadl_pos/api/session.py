# Copyright (c) 2026, FadlTech team and contributors

"""POS shift session whitelisted RPC (`/api/method/...`)."""

from __future__ import annotations

import frappe
from frappe import _

from fadl_pos.api.login.rpc_params import optional_str_param
from fadl_pos.serializers.session import CloseShiftResponse, SessionListResponseSerializer
from fadl_pos.services.session_service import SessionService


@frappe.whitelist(methods=["GET", "POST"])
def get_list() -> list[SessionListResponseSerializer]:
	"""
	List POS profiles for the session user and detect an open shift.

	**Route:** ``/api/method/fadl_pos.api.session.get_list`` (GET or POST)

	**Input:** none (session user from Frappe).

	**Output:** ``[{"pos_profiles": [...]}]``.

	- If the user has an open **POS Opening Entry**, a single profile object with ``status: "Open"``,
	  ``opening_entry``, ``opening_entry_date``.
	- Otherwise each assigned profile includes ``status: "Close"``, ``payment_methods``, ``checklists``,
	  ``company``. Closing uses native ``make_closing_entry_from_opening`` elsewhere.
	"""
	return SessionService().get_list()


@frappe.whitelist(methods=["POST"])
def open_shift(
	pos_profile: str | None = None,
	company: str | None = None,
	balance_details: object | None = None,
	comment: str | None = None,
) -> list[SessionListResponseSerializer]:
	"""
	Open a POS shift via native ``erpnext...point_of_sale.create_opening_voucher`` (wrapped server-side).

	**Route:** ``/api/method/fadl_pos.api.session.open_shift`` (POST)

	**Input:**

	- ``pos_profile`` (str, required), ``company`` (str, required).
	- ``balance_details`` (JSON string or list, required): rows ``{"mode_of_payment": str, "opening_amount": number}``.
	  Cash modes must include an opening amount; others default to ``0``.
	- ``comment`` (str, optional): timeline comment after submit.

	**Output:** Same shape as :func:`get_list` after opening (typically one ``Open`` profile).
	"""
	pos_profile = optional_str_param("pos_profile", pos_profile)
	company = optional_str_param("company", company)
	comment = optional_str_param("comment", comment)
	if not pos_profile or not company:
		frappe.throw(_("POS Profile and Company are required to open a shift."))

	service = SessionService()
	parsed_balance = service.parse_balance_details_arg(balance_details)
	return service.open_shift(pos_profile, company, parsed_balance, comment=comment)


@frappe.whitelist(methods=["POST"])
def close_shift(
	opening_entry_name: str | None = None,
	closing_data: object | None = None,
	comment: str | None = None,
) -> CloseShiftResponse:
	"""
	Close a shift using native ``make_closing_entry_from_opening`` plus reconciliation merge.

	**Route:** ``/api/method/fadl_pos.api.session.close_shift`` (POST)

	**Input:**

	- ``opening_entry_name`` (str, required): submitted POS Opening Entry to close.
	- ``closing_data`` (optional JSON string or list): ``[{"mode_of_payment": str, "closing_amount": number}, ...]``.
	  Cash modes require ``closing_amount``; others fall back to expected totals when omitted.
	- ``comment`` (str, optional): timeline comment on the closing entry.

	**Output:**

	- ``{"status": "success"|"failed", "is_final": bool, "entry_status": str,
	  "closing_entry": "<name>", "error_message": str|null}``.
	"""
	opening_entry_name = optional_str_param("opening_entry_name", opening_entry_name)
	comment = optional_str_param("comment", comment)
	if not opening_entry_name:
		frappe.throw(_("Opening Entry Name is required to close the shift."))

	service = SessionService()
	parsed_data = service.parse_closing_data_arg(closing_data)
	return service.close_shift(opening_entry_name, parsed_data, comment=comment)
