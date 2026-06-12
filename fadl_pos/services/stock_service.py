"""
Stock availability, serial helpers, and POS Profile warehouse updates.

All read paths delegate to ERPNext stock/POS helpers (``get_stock_availability``,
``auto_fetch_serial_number``, ``get_pos_reserved_serial_nos``).

Called from ``fadl_pos.api.stock`` — one method per whitelist endpoint.
``update_warehouse`` mutates **POS Profile** after permission + company checks.
"""

import frappe

# Native Imports
from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_stock_availability as native_get_stock
from frappe import _
from frappe.utils import cint, flt

from fadl_pos.services._base import BaseService


class StockService(BaseService):
	"""Wrap native POS stock queries and profile warehouse maintenance."""

	def get_single(self, item_code, warehouse):
		"""
		Native: Get stock availability for a single item in a warehouse.
		"""
		actual_qty, _is_stock_item, _is_negative_stock_allowed = native_get_stock(item_code, warehouse)
		return {"item_code": item_code, "warehouse": warehouse, "actual_qty": actual_qty}

	def get_batch(self, item_codes, warehouse):
		"""
		Get native POS availability for multiple items.
		"""
		final_results = []
		for code in item_codes:
			actual_qty, _, _ = native_get_stock(code, warehouse)
			final_results.append({"item_code": code, "actual_qty": actual_qty})

		return {"stocks": final_results}

	def get_item_by_warehouses(self, item_code, company=None):
		"""
		Get raw Bin availability across warehouses for a company.
		"""
		filters = {"item_code": item_code}
		if company:
			filters["company"] = company

		warehouses = frappe.get_all(
			"Bin", filters=filters, fields=["warehouse", "actual_qty", "reserved_qty", "projected_qty"]
		)
		return {"warehouses": warehouses}

	def get_bundle(self, item_code, warehouse):
		"""
		Native POS availability for a Product Bundle or stock item.
		"""
		actual_qty, _, _ = native_get_stock(item_code, warehouse)
		return {"bundle_availability": actual_qty}

	def auto_fetch_serial(self, qty, item_code, warehouse, batch_nos=None):
		"""
		Native wrapper: Auto-fetch available serial numbers for an item.
		"""
		from erpnext.stock.doctype.serial_no.serial_no import auto_fetch_serial_number

		serials = auto_fetch_serial_number(
			qty=cint(qty),
			item_code=item_code,
			warehouse=warehouse,
			batch_nos=batch_nos,
			for_doctype="POS Invoice",
		)
		return {"serial_nos": serials}

	def get_reserved_serials(self, item_code, warehouse):
		"""
		Native wrapper: Get serial numbers reserved in other open POS Invoices.
		"""
		from erpnext.stock.doctype.serial_no.serial_no import get_pos_reserved_serial_nos

		filters = {"item_code": item_code, "warehouse": warehouse}
		serials = get_pos_reserved_serial_nos(filters)
		return {"reserved_serial_nos": serials}

	def update_warehouse(self, pos_profile: str, warehouse: str):
		"""
		Update the warehouse for the POS Profile.
		"""

		# Check if user has access to this POS Profile
		has_access = frappe.db.exists(
			"POS Profile User", {"parent": pos_profile, "user": frappe.session.user}
		)

		if not has_access and not frappe.has_permission("POS Profile", "write", pos_profile):
			return {"status": False, "message": _("You don't have permission to update this POS Profile")}

		# Get POS Profile to check company
		profile_doc = frappe.get_doc("POS Profile", pos_profile)
		# Validate warehouse exists and is active
		warehouse_doc = frappe.get_doc("Warehouse", warehouse)
		if warehouse_doc.disabled and not warehouse_doc.is_group_warehouse:
			frappe.throw(_("Warehouse {0} is disabled").format(warehouse))

		# Validate warehouse belongs to same company
		if warehouse_doc.company != profile_doc.company:
			return {
				"status": False,
				"message": _("Warehouse {0} belongs to {1}, but POS Profile belongs to {2}").format(
					warehouse, warehouse_doc.company, profile_doc.company
				),
			}

		# Update the POS Profile
		profile_doc.warehouse = warehouse
		profile_doc.save()

		return {
			"status": True,
			"message": _("Warehouse updated successfully"),
			"warehouse": warehouse,
		}

	def get_warehouses(self, company: str | None = None, pos_profile: str | None = None) -> list:
		"""
		Get all active leaf warehouses for the company.
		"""
		if not company and pos_profile:
			company = frappe.db.get_value("POS Profile", pos_profile, "company")
		if not company:
			frappe.throw(_("Company or pos_profile is required."))

		warehouses = frappe.get_list(
			"Warehouse",
			filters={"company": company, "disabled": 0, "is_group": 0},
			fields=["name", "warehouse_name"],
			order_by="warehouse_name",
			limit_page_length=0,
		)
		return warehouses
