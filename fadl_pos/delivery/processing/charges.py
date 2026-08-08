# Copyright (c) 2026, FadlTech team and contributors

"""Delivery charges listing and applicability."""

from __future__ import annotations

import frappe


def get_delivery_charges(pos_profile: str):
	"""List delivery charge rules applicable to a POS Profile."""
	from fadl_pos.fadl_pos.doctype.delivery_charges.delivery_charges import (
		get_applicable_delivery_charges as _get_applicable_delivery_charges,
	)

	company = frappe.db.get_value("POS Profile", pos_profile, "company")
	if not company:
		return []
	charges = _get_applicable_delivery_charges(company, pos_profile=pos_profile, restrict=False)
	return [
		{
			"name": c.name,
			"label": c.label,
			"default_rate": c.get("default_rate"),
			"rate": c.get("rate") if c.get("rate") is not None else c.get("default_rate"),
			"company": c.get("company"),
		}
		for c in charges
	]


def get_applicable_delivery_charges(
	company: str,
	pos_profile: str,
	customer: str | None = None,
	shipping_address_name: str | None = None,
):
	from fadl_pos.fadl_pos.doctype.delivery_charges.delivery_charges import (
		get_applicable_delivery_charges as _get_applicable_delivery_charges,
	)

	return _get_applicable_delivery_charges(company, pos_profile, customer, shipping_address_name)
