# Copyright (c) 2026, FadlTech team and contributors

"""Invoice list RPC."""

from __future__ import annotations

import frappe

from fadl_pos.api.rpc_boundary import dump_out, validate_in
from fadl_pos.schemas import InvoiceListHistoryIn, InvoiceListOut
from fadl_pos.services.invoice_list_service import InvoiceListService


@frappe.whitelist()
def history(search_term: str | None = None, status: str | None = None, limit: int | None = None):
	"""``/api/method/fadl_pos.api.invoice_list.history``"""
	body = validate_in(
		InvoiceListHistoryIn,
		{
			"search_term": search_term or "",
			"status": status or "Paid",
			"limit": limit if limit is not None else 20,
		},
	)
	return dump_out(
		InvoiceListOut,
		InvoiceListService().get_history(
			search_term=body.search_term, status=body.status, limit=body.limit
		),
	)
