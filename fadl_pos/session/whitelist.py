# Copyright (c) 2026, FadlTech team and contributors

"""POS shift session RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.core.serializer import dump_out, validate_in
from fadl_pos.session.controller import SessionController
from fadl_pos.session.serializer import (
	CloseShiftIn,
	CloseShiftOut,
	OpenShiftIn,
	SessionListEnvelopeOut,
	SessionListIn,
)


def _controller() -> SessionController:
	return SessionController()


@frappe.whitelist(methods=["GET", "POST"])
def get_list():
	"""``/api/method/fadl_pos.session.whitelist.get_list``"""
	validate_in(SessionListIn, {})
	result = _controller().get_list()
	if isinstance(result, list):
		return [dump_out(SessionListEnvelopeOut, block) for block in result]
	return dump_out(SessionListEnvelopeOut, result)


@frappe.whitelist(methods=["POST"])
def open_shift(
	pos_profile: str | None = None,
	company: str | None = None,
	balance_details: object | None = None,
	comment: str | None = None,
):
	"""``/api/method/fadl_pos.session.whitelist.open_shift``"""
	body = validate_in(
		OpenShiftIn,
		{
			"pos_profile": pos_profile or "",
			"company": company or "",
			"comment": comment,
			"balance_details": balance_details,
		},
	)
	result = _controller().open_shift(
		body.pos_profile,
		body.company,
		[row.model_dump() for row in body.balance_details],
		comment=body.comment,
	)
	if isinstance(result, list):
		return [dump_out(SessionListEnvelopeOut, block) for block in result]
	return dump_out(SessionListEnvelopeOut, result)


@frappe.whitelist(methods=["POST"])
def close_shift(
	opening_entry_name: str | None = None,
	closing_data: object | None = None,
	comment: str | None = None,
):
	"""``/api/method/fadl_pos.session.whitelist.close_shift``"""
	body = validate_in(
		CloseShiftIn,
		{
			"opening_entry_name": opening_entry_name or "",
			"comment": comment,
			"closing_data": closing_data,
		},
	)
	closing_rows = [row.model_dump() for row in body.closing_data] if body.closing_data is not None else None
	return dump_out(
		CloseShiftOut,
		_controller().close_shift(body.opening_entry_name, closing_rows, comment=body.comment),
	)
