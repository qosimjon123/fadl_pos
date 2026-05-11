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
	If the user has an open shift, returns only that profile (status Open). Otherwise all assigned profiles with Close and payment_methods/checklists.
	Route: /api/method/fadl_pos.api.session.get_list
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
	Create a new POS Opening Entry.
	Only Cash balance_details rows from the POS Profile are used; non-Cash lines are ignored.
	Optional **comment** is saved like Desk “Add Comment” on the submitted POS Opening Entry (`Comment` doctype).
	Route: /api/method/fadl_pos.api.session.open_shift
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
	Close the shift and create POS Closing Entry.
	Cash MOPs need closing_amount in closing_data; non-Cash can be omitted (expected_amount is used).
	Optional **comment** is saved like Desk on the submitted POS Closing Entry (`Comment` doctype).
	Route: /api/method/fadl_pos.api.session.close_shift
	"""
	opening_entry_name = optional_str_param("opening_entry_name", opening_entry_name)
	comment = optional_str_param("comment", comment)
	if not opening_entry_name:
		frappe.throw(_("Opening Entry Name is required to close the shift."))

	service = SessionService()
	parsed_data = service.parse_closing_data_arg(closing_data)
	return service.close_shift(opening_entry_name, parsed_data, comment=comment)
