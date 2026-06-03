# Copyright (c) 2026, FadlTech team and contributors

"""POS shift session whitelisted RPC."""

from __future__ import annotations

import frappe
from frappe import _
from pydantic import TypeAdapter, ValidationError

from fadl_pos.api.rpc_boundary import dump_out, raise_validation_error, validate_in
from fadl_pos.schemas import (
	BalanceDetailItem,
	CloseShiftIn,
	CloseShiftOut,
	ClosingReconciliationItem,
	OpenShiftIn,
	SessionListEnvelopeOut,
	SessionListIn,
)
from fadl_pos.services.session_service import SessionService


def _parse_balance_details(raw: object | None) -> list[BalanceDetailItem]:
	if raw is None or (isinstance(raw, str) and not raw.strip()):
		return []
	if isinstance(raw, str):
		return TypeAdapter(list[BalanceDetailItem]).validate_json(raw)
	return TypeAdapter(list[BalanceDetailItem]).validate_python(raw)


def _parse_closing_data(raw: object | None) -> list[ClosingReconciliationItem] | None:
	if raw is None or (isinstance(raw, str) and not raw.strip()):
		return None
	if isinstance(raw, str):
		return TypeAdapter(list[ClosingReconciliationItem]).validate_json(raw)
	return TypeAdapter(list[ClosingReconciliationItem]).validate_python(raw)


@frappe.whitelist(methods=["GET", "POST"])
def get_list():
	"""``/api/method/fadl_pos.api.session.get_list``"""
	validate_in(SessionListIn, {})
	result = SessionService().get_list()
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
	"""``/api/method/fadl_pos.api.session.open_shift``"""
	try:
		query = validate_in(
			OpenShiftIn,
			{"pos_profile": pos_profile or "", "company": company or "", "comment": comment},
		)
		parsed_balance = _parse_balance_details(balance_details)
	except ValidationError as exc:
		raise_validation_error(exc)

	result = SessionService().open_shift(
		query.pos_profile,
		query.company,
		[row.model_dump() for row in parsed_balance],
		comment=query.comment,
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
	"""``/api/method/fadl_pos.api.session.close_shift``"""
	try:
		query = validate_in(
			CloseShiftIn,
			{"opening_entry_name": opening_entry_name or "", "comment": comment},
		)
		parsed_data = _parse_closing_data(closing_data)
	except ValidationError as exc:
		raise_validation_error(exc)

	closing_rows = [row.model_dump() for row in parsed_data] if parsed_data else None
	return dump_out(
		CloseShiftOut,
		SessionService().close_shift(
			query.opening_entry_name, closing_rows, comment=query.comment
		),
	)
