# Copyright (c) 2026, FadlTech team and contributors

"""Stock RPC — one whitelist per operation."""

from __future__ import annotations

import frappe
from frappe import _

from fadl_pos.api.rpc_boundary import dump_out, validate_in
from fadl_pos.schemas import (
	StockAutoSerialIn,
	StockAutoSerialOut,
	StockBatchIn,
	StockBatchOut,
	StockBundleIn,
	StockBundleOut,
	StockReservedSerialsIn,
	StockReservedSerialsOut,
	StockSingleIn,
	StockSingleOut,
	StockUpdateWarehouseIn,
	StockUpdateWarehouseOut,
	StockWarehousesIn,
	StockWarehousesListOut,
)
from fadl_pos.services.stock_service import StockService


def _resolve_company(body: StockWarehousesIn) -> str:
	if body.company:
		return body.company
	if body.pos_profile:
		company = frappe.db.get_value("POS Profile", body.pos_profile, "company")
		if company:
			return company
	frappe.throw(_("Company or pos_profile is required."))


@frappe.whitelist()
def single(item_code: str | None = None, warehouse: str | None = None):
	body = validate_in(StockSingleIn, {"item_code": item_code or "", "warehouse": warehouse or ""})
	return dump_out(StockSingleOut, StockService().get_single(body.item_code, body.warehouse))


@frappe.whitelist()
def batch(item_codes: object | None = None, warehouse: str | None = None):
	body = validate_in(StockBatchIn, {"item_codes": item_codes or [], "warehouse": warehouse or ""})
	return dump_out(StockBatchOut, StockService().get_batch(body.item_codes, body.warehouse))


@frappe.whitelist()
def warehouses(company: str | None = None, pos_profile: str | None = None):
	body = validate_in(StockWarehousesIn, {"company": company, "pos_profile": pos_profile})
	co = _resolve_company(body)
	# Service returns list for get_warehouses — wrap for Out
	rows = StockService().get_warehouses(co)
	if isinstance(rows, list):
		return StockWarehousesListOut.dump({"warehouses": rows})
	return dump_out(StockWarehousesListOut, rows)


@frappe.whitelist()
def bundle(item_code: str | None = None, warehouse: str | None = None):
	body = validate_in(StockBundleIn, {"item_code": item_code or "", "warehouse": warehouse or ""})
	return dump_out(StockBundleOut, StockService().get_bundle(body.item_code, body.warehouse))


@frappe.whitelist()
def auto_serial(
	qty: int | float | None = None,
	item_code: str | None = None,
	warehouse: str | None = None,
	batch_nos: object | None = None,
):
	body = validate_in(
		StockAutoSerialIn,
		{
			"qty": qty if qty is not None else 0,
			"item_code": item_code or "",
			"warehouse": warehouse or "",
			"batch_nos": batch_nos,
		},
	)
	return dump_out(
		StockAutoSerialOut,
		StockService().auto_fetch_serial(body.qty, body.item_code, body.warehouse, batch_nos=body.batch_nos),
	)


@frappe.whitelist()
def reserved_serials(item_code: str | None = None, warehouse: str | None = None):
	body = validate_in(
		StockReservedSerialsIn,
		{"item_code": item_code or "", "warehouse": warehouse or ""},
	)
	return dump_out(
		StockReservedSerialsOut,
		StockService().get_reserved_serials(body.item_code, body.warehouse),
	)


@frappe.whitelist()
def update_warehouse(pos_profile: str | None = None, warehouse: str | None = None):
	body = validate_in(
		StockUpdateWarehouseIn,
		{"pos_profile": pos_profile or "", "warehouse": warehouse or ""},
	)
	return dump_out(
		StockUpdateWarehouseOut,
		StockService().update_warehouse(body.pos_profile, body.warehouse),
	)
