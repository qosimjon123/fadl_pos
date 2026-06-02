# Copyright (c) 2026, FadlTech team and contributors

"""POS shift session whitelisted RPC (`/api/method/...`)."""

from __future__ import annotations

import frappe
from frappe import _
from pydantic import ValidationError
from pydantic.type_adapter import TypeAdapter

from fadl_pos.schemas import (
	BalanceDetailItem,
	CloseShiftQuery,
	CloseShiftResponse,
	ClosingReconciliationItem,
	OpenShiftQuery,
	SessionListResponseSerializer,
)
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
	try:
		query = OpenShiftQuery.model_validate(
			{"pos_profile": pos_profile or "", "company": company or "", "comment": comment}
		)
	except ValidationError as exc:
		frappe.throw(str(exc.errors()), frappe.ValidationError)
	if not query.pos_profile or not query.company:
		frappe.throw(_("POS Profile and Company are required to open a shift."))

	try:
		if balance_details is None or (isinstance(balance_details, str) and not balance_details.strip()):
			parsed_balance: list[BalanceDetailItem] = []
		elif isinstance(balance_details, str):
			parsed_balance = TypeAdapter(list[BalanceDetailItem]).validate_json(balance_details)
		else:
			parsed_balance = TypeAdapter(list[BalanceDetailItem]).validate_python(balance_details)
	except ValidationError as exc:
		frappe.throw(str(exc.errors()), frappe.ValidationError)
	return SessionService().open_shift(
		query.pos_profile, query.company, parsed_balance, comment=query.comment
	)


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
	try:
		query = CloseShiftQuery.model_validate(
			{"opening_entry_name": opening_entry_name or "", "comment": comment}
		)
	except ValidationError as exc:
		frappe.throw(str(exc.errors()), frappe.ValidationError)
	if not query.opening_entry_name:
		frappe.throw(_("Opening Entry Name is required to close the shift."))

	try:
		if closing_data is None or (isinstance(closing_data, str) and not closing_data.strip()):
			parsed_data: list[ClosingReconciliationItem] | None = None
		elif isinstance(closing_data, str):
			parsed_data = TypeAdapter(list[ClosingReconciliationItem]).validate_json(closing_data)
		else:
			parsed_data = TypeAdapter(list[ClosingReconciliationItem]).validate_python(closing_data)
	except ValidationError as exc:
		frappe.throw(str(exc.errors()), frappe.ValidationError)
	return SessionService().close_shift(query.opening_entry_name, parsed_data, comment=query.comment)
