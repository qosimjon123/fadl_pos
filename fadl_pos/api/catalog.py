# Copyright (c) 2026, FadlTech team and contributors

"""Catalog RPC — items search and boot."""

from __future__ import annotations

import frappe

from fadl_pos.api.rpc_boundary import dump_out, validate_in
from fadl_pos.schemas import BootPosOut, CatalogBootIn, CatalogItemsIn, CatalogOut
from fadl_pos.services.bootstrap_service import BootstrapService
from fadl_pos.services.catalog_service import CatalogService


@frappe.whitelist()
def items(
	start: int | None = None,
	page_length: int | None = None,
	price_list: str | None = None,
	item_group: str | None = None,
	pos_profile: str | None = None,
	search_term: str | None = None,
):
	"""``/api/method/fadl_pos.api.catalog.items``"""
	body = validate_in(
		CatalogItemsIn,
		{
			"start": start if start is not None else 0,
			"page_length": page_length if page_length is not None else 15,
			"price_list": price_list,
			"item_group": item_group,
			"pos_profile": pos_profile or "",
			"search_term": search_term or "",
		},
	)
	return dump_out(
		CatalogOut,
		CatalogService().get_items(
			body.start,
			page_length=body.page_length,
			price_list=body.price_list,
			item_group=body.item_group,
			pos_profile=body.pos_profile,
			search_term=body.search_term,
		),
	)


@frappe.whitelist()
def boot(pos_profile: str | None = None):
	"""``/api/method/fadl_pos.api.catalog.boot``"""
	body = validate_in(CatalogBootIn, {"pos_profile": pos_profile or ""})
	return dump_out(BootPosOut, BootstrapService().boot(body.pos_profile))
