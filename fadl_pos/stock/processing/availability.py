import frappe
from erpnext.stock.doctype.batch.batch import get_batch_qty
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum
from frappe.utils import cstr, flt, json

from fadl_pos.utilities import get_invoice_type


def get_stock_availability(item_code: str, warehouse: str) -> float:
	"""Return total available quantity for an item in the given warehouse.

	``warehouse`` can be either a single warehouse or a warehouse group.
	In case of a group, quantities from all child warehouses are summed up
	to provide an accurate availability figure.
	"""

	if not warehouse:
		return 0.0

	warehouses = [warehouse]
	if frappe.db.get_value("Warehouse", warehouse, "is_group"):
		warehouses = frappe.db.get_descendants("Warehouse", warehouse) or []

	bin_doctype = DocType("Bin")
	rows = (
		frappe.qb.from_(bin_doctype)
		.select(Sum(bin_doctype.actual_qty).as_("actual_qty"))
		.where(bin_doctype.item_code == item_code)
		.where(bin_doctype.warehouse.isin(warehouses))
		.run(as_dict=True)
	)

	return flt(rows[0].actual_qty) if rows else 0.0


def lock_bins_for_update(items: list[dict]) -> None:
	"""
	Take a row lock on the Bin rows an invoice is about to consume.

	Availability checks are read-then-write: without a lock two terminals can
	both read the last unit as available and both sell it.  Locking the bins
	before validating serialises those transactions so the second one sees the
	first one's deduction.

	Rows are locked in a deterministic ``(item_code, warehouse)`` order so two
	carts sharing items acquire them in the same sequence and cannot deadlock.
	The lock is held until the surrounding transaction commits.
	"""

	targets = set()
	for d in items or []:
		item_code = d.get("item_code")
		warehouse = d.get("warehouse")
		if not item_code or not warehouse:
			continue

		warehouses = [warehouse]
		if frappe.db.get_value("Warehouse", warehouse, "is_group"):
			warehouses = frappe.db.get_descendants("Warehouse", warehouse) or []

		for wh in warehouses:
			targets.add((item_code, wh))

	if not targets:
		return

	bin_doctype = DocType("Bin")
	for item_code, warehouse in sorted(targets):
		(
			frappe.qb.from_(bin_doctype)
			.select(bin_doctype.name)
			.where(bin_doctype.item_code == item_code)
			.where(bin_doctype.warehouse == warehouse)
			.for_update()
			.run()
		)


def get_bulk_stock_availability(items: list[dict]) -> dict[tuple[str, str, str], float]:
	"""
	Fetch available stock for a list of items.

	Args:
	    items: List of dicts/objects with 'item_code', 'warehouse', and optional 'batch_no'.

	Returns:
	    dict: key=(item_code, warehouse, batch_no), value=qty
	"""
	if not items:
		return {}

	regular_items_map = {}
	results = {}

	for d in items:
		item_code = d.get("item_code")
		warehouse = d.get("warehouse")
		batch_no = cstr(d.get("batch_no"))

		if not item_code or not warehouse:
			continue

		if batch_no:
			results[(item_code, warehouse, batch_no)] = flt(get_batch_qty(batch_no, warehouse))
		else:
			if warehouse not in regular_items_map:
				regular_items_map[warehouse] = set()
			regular_items_map[warehouse].add(item_code)

	if not regular_items_map:
		return results

	all_warehouses = list(regular_items_map.keys())
	group_warehouses = set(
		frappe.get_all("Warehouse", filters={"name": ["in", all_warehouses], "is_group": 1}, pluck="name")
	)

	bin_doctype = DocType("Bin")

	for warehouse, item_codes in regular_items_map.items():
		if not item_codes:
			continue

		target_warehouses = [warehouse]
		if warehouse in group_warehouses:
			target_warehouses = frappe.db.get_descendants("Warehouse", warehouse) or []

		if not target_warehouses:
			for code in item_codes:
				results[(code, warehouse, "")] = 0.0
			continue

		item_code_list = list(item_codes)

		query = (
			frappe.qb.from_(bin_doctype)
			.select(bin_doctype.item_code, Sum(bin_doctype.actual_qty).as_("actual_qty"))
			.where(bin_doctype.item_code.isin(item_code_list))
			.where(bin_doctype.warehouse.isin(target_warehouses))
			.groupby(bin_doctype.item_code)
		)

		rows = query.run(as_dict=True)
		qty_map = {r.item_code: flt(r.actual_qty) for r in rows}

		for code in item_codes:
			results[(code, warehouse, "")] = qty_map.get(code, 0.0)

	return results


def get_available_qty(items: str | list[dict]) -> list[dict]:
	"""Return available stock quantity for given items.

	Args:
	    items (str | list[dict]): JSON string or list of dicts with
	        item_code, warehouse and optional batch_no.

	Returns:
	    list: List of dicts with item_code, warehouse and available_qty
	        in stock UOM.
	"""

	if isinstance(items, str):
		items = json.loads(items)

	result = []
	for it in items or []:
		item_code = it.get("item_code")
		warehouse = it.get("warehouse")
		batch_no = it.get("batch_no")

		if not item_code or not warehouse:
			continue

		if batch_no:
			available_qty = get_batch_qty(batch_no, warehouse) or 0
		else:
			available_qty = get_stock_availability(item_code, warehouse)

		result.append(
			{
				"item_code": item_code,
				"warehouse": warehouse,
				"available_qty": flt(available_qty),
			}
		)

	return result

def get_pos_stock_availability(items: str | list, warehouse: str | None = None, pos_profile: str | None = None):
	"""Bulk-fetch stock for multiple items.

	Accepts two calling conventions:
	1. items = JSON list of item-code strings + warehouse as a separate param.
	2. items = JSON list of dicts with item_code, warehouse, and optional batch_no.

	Returns:
	        list of {"item_code": str, "actual_qty": float}
	"""
	if isinstance(items, str):
		items = json.loads(items)
	if not items:
		return []

	use_pos_deduction = bool(pos_profile and get_invoice_type() == "POS Invoice")
	pending_map: dict[str, float] = {}
	if use_pos_deduction and warehouse:
		wh_list = [warehouse]
		if frappe.db.get_value("Warehouse", warehouse, "is_group"):
			wh_list = frappe.db.get_descendants("Warehouse", warehouse) or []
		all_item_codes = []
		for d in items:
			if isinstance(d, str):
				all_item_codes.append(d)
			elif d.get("item_code"):
				all_item_codes.append(d.get("item_code"))
		pending_map = _get_pending_pos_qty_map(wh_list, item_codes=all_item_codes)

	results = []
	for d in items:
		if isinstance(d, str):
			item_code = d
			item_warehouse = warehouse
			batch_no = ""
		else:
			item_code = d.get("item_code")
			item_warehouse = d.get("warehouse") or warehouse
			batch_no = d.get("batch_no", "")

		if not item_code or not item_warehouse:
			continue

		if batch_no:
			from erpnext.stock.doctype.batch.batch import get_batch_qty

			qty = flt(get_batch_qty(batch_no, item_warehouse))
			if use_pos_deduction:
				qty -= get_pending_batch_qty(item_warehouse, pos_profile).get(batch_no, 0.0)
		else:
			qty = flt(get_stock_qty(item_code, item_warehouse))
			if use_pos_deduction:
				qty -= pending_map.get(item_code, 0.0)

		results.append({"item_code": item_code, "actual_qty": qty})

	return results

def get_stock_qty(item_code: str, warehouse: str, pos_profile: str | None = None):
	"""Get actual qty from Bin, supporting warehouse groups."""
	if not warehouse:
		return 0

	warehouses = [warehouse]
	if frappe.db.get_value("Warehouse", warehouse, "is_group"):
		warehouses = frappe.db.get_descendants("Warehouse", warehouse) or []

	from frappe.query_builder import DocType
	from frappe.query_builder.functions import Sum

	Bin = DocType("Bin")
	rows = (
		frappe.qb.from_(Bin)
		.select(Sum(Bin.actual_qty).as_("actual_qty"))
		.where(Bin.item_code == item_code)
		.where(Bin.warehouse.isin(warehouses))
		.run(as_dict=True)
	)
	bin_qty = flt(rows[0].actual_qty) if rows else 0

	if pos_profile and get_invoice_type() == "POS Invoice":
		pending_map = _get_pending_pos_qty_map(warehouses, item_codes=[item_code])
		bin_qty -= pending_map.get(item_code, 0.0)

	return bin_qty

def get_pending_batch_qty(warehouse: str, pos_profile: str | None) -> dict[str, float]:
	"""Return batch_no -> qty already sold on unconsolidated POS Invoices."""

	if not warehouse or not pos_profile or get_invoice_type() != "POS Invoice":
		return {}

	warehouses = [warehouse]
	if frappe.db.get_value("Warehouse", warehouse, "is_group"):
		warehouses = frappe.db.get_descendants("Warehouse", warehouse) or []

	pending: dict[str, float] = {}
	for (batch_no, _wh), qty in get_pending_pos_batch_qty_map(warehouses).items():
		pending[batch_no] = pending.get(batch_no, 0.0) + qty

	return pending

def _get_pending_pos_qty_map(
	warehouses: list[str],
	item_codes: list[str] | None = None,
) -> dict[str, float]:
	"""Return qty sold in submitted but unconsolidated POS Invoices.

	Returns a dict mapping item_code -> total pending qty across the
	given warehouses.  Only submitted (docstatus=1) POS Invoices that
	have not yet been consolidated are considered.
	"""
	from frappe.query_builder import DocType
	from frappe.query_builder.functions import Sum

	POSInv = DocType("POS Invoice")
	POSItem = DocType("POS Invoice Item")

	query = (
		frappe.qb.from_(POSItem)
		.join(POSInv)
		.on(POSItem.parent == POSInv.name)
		.select(
			POSItem.item_code,
			Sum(POSItem.stock_qty).as_("total_qty"),
		)
		.where(POSInv.docstatus == 1)
		.where((POSInv.consolidated_invoice == "") | (POSInv.consolidated_invoice.isnull()))
		.where(POSItem.warehouse.isin(warehouses))
		.groupby(POSItem.item_code)
	)

	if item_codes:
		query = query.where(POSItem.item_code.isin(item_codes))

	rows = query.run(as_dict=True)
	return {r.item_code: flt(r.total_qty) for r in rows}

def get_pending_pos_batch_qty_map(
	warehouses: list[str],
	batch_nos: list[str] | None = None,
) -> dict[tuple[str, str], float]:
	"""
	Return qty sold per batch in submitted but unconsolidated POS Invoices.
	"""

	if not warehouses:
		return {}

	POSInv = DocType("POS Invoice")
	POSItem = DocType("POS Invoice Item")

	query = (
		frappe.qb.from_(POSItem)
		.join(POSInv)
		.on(POSItem.parent == POSInv.name)
		.select(
			POSItem.batch_no,
			POSItem.warehouse,
			Sum(POSItem.stock_qty).as_("total_qty"),
		)
		.where(POSInv.docstatus == 1)
		.where((POSInv.consolidated_invoice == "") | (POSInv.consolidated_invoice.isnull()))
		.where(POSItem.warehouse.isin(warehouses))
		.where(POSItem.batch_no.notnull())
		.where(POSItem.batch_no != "")
		.groupby(POSItem.batch_no, POSItem.warehouse)
	)

	if batch_nos:
		query = query.where(POSItem.batch_no.isin(batch_nos))

	rows = query.run(as_dict=True)
	return {(r.batch_no, r.warehouse): flt(r.total_qty) for r in rows}

