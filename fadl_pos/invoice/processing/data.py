# Copyright (c) 2026, FadlTech team and contributors

"""Invoice data helpers (rates history, etc.)."""

from __future__ import annotations

import json

import frappe


def get_last_invoice_rates(customer: str, item_codes: str | list, company: str):
	"""Get the most recent invoice rates for items by customer."""
	if isinstance(item_codes, str):
		item_codes = json.loads(item_codes)

	if not item_codes:
		return []

	item_params = {}
	for idx, code in enumerate(item_codes):
		item_params[f"item_{idx}"] = code
	item_placeholders = ", ".join([f"%(item_{i})s" for i in range(len(item_codes))])
	results = frappe.db.sql(  # nosemgrep: frappe-sql-format-injection — item_placeholders is built from %(name)s named params, all values parameterized
		f"""
		SELECT
			sii.item_code,
			sii.rate,
			si.currency,
			sii.uom,
			si.posting_date
		FROM `tabSales Invoice Item` sii
		INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
		WHERE si.customer = %(customer)s
			AND si.company = %(company)s
			AND si.docstatus = 1
			AND si.is_return = 0
			AND sii.item_code IN ({item_placeholders})
		ORDER BY si.posting_date DESC, si.creation DESC
		""",
		{"customer": customer, "company": company, **item_params},
		as_dict=True,
	)

	seen = set()
	latest = []
	for r in results:
		if r.item_code not in seen:
			seen.add(r.item_code)
			latest.append(r)

	return latest

