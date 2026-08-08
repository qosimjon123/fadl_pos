# Copyright (c) 2026, FadlTech team and contributors

"""purchasing controller — wraps ported xpos business logic."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController

from fadl_pos.purchasing.processing.orders import create_supplier as _create_supplier
from fadl_pos.purchasing.processing.orders import search_suppliers as _search_suppliers
from fadl_pos.purchasing.processing.orders import create_purchase_item as _create_purchase_item
from fadl_pos.purchasing.processing.orders import create_purchase_order as _create_purchase_order
from fadl_pos.purchasing.processing.orders import create_purchase_invoice_direct as _create_purchase_invoice_direct
from fadl_pos.purchasing.processing.orders import search_items as _search_items
from fadl_pos.purchasing.processing.orders import search_item_by_barcode as _search_item_by_barcode
from fadl_pos.purchasing.processing.orders import get_pending_receipts as _get_pending_receipts
from fadl_pos.purchasing.processing.orders import get_purchase_order_detail as _get_purchase_order_detail
from fadl_pos.purchasing.processing.orders import receive_stock as _receive_stock
from fadl_pos.purchasing.processing.orders import get_stock_and_transit as _get_stock_and_transit
from fadl_pos.purchasing.processing.orders import get_category_items as _get_category_items
from fadl_pos.purchasing.processing.orders import save_po_draft as _save_po_draft
from fadl_pos.purchasing.processing.orders import load_po_draft as _load_po_draft
from fadl_pos.purchasing.processing.orders import delete_po_draft as _delete_po_draft
from fadl_pos.purchasing.processing.orders import list_po_drafts as _list_po_drafts
from fadl_pos.purchasing.processing.orders import save_pi_draft as _save_pi_draft
from fadl_pos.purchasing.processing.orders import load_pi_draft as _load_pi_draft
from fadl_pos.purchasing.processing.orders import delete_pi_draft as _delete_pi_draft
from fadl_pos.purchasing.processing.orders import list_pi_drafts as _list_pi_drafts
from fadl_pos.purchasing.processing.orders import submit_pi_draft as _submit_pi_draft
from fadl_pos.purchasing.processing.orders import get_purchase_orders_for_invoice as _get_purchase_orders_for_invoice
from fadl_pos.purchasing.processing.orders import get_item_purchase_details as _get_item_purchase_details
from fadl_pos.purchasing.processing.orders import get_purchase_tax_template as _get_purchase_tax_template

class PurchasingController(BaseController):
	def create_supplier(self, *args, **kwargs):
		return _create_supplier(*args, **kwargs)

	def search_suppliers(self, *args, **kwargs):
		return _search_suppliers(*args, **kwargs)

	def create_purchase_item(self, *args, **kwargs):
		return _create_purchase_item(*args, **kwargs)

	def create_purchase_order(self, *args, **kwargs):
		return _create_purchase_order(*args, **kwargs)

	def create_purchase_invoice_direct(self, *args, **kwargs):
		return _create_purchase_invoice_direct(*args, **kwargs)

	def search_items(self, *args, **kwargs):
		return _search_items(*args, **kwargs)

	def search_item_by_barcode(self, *args, **kwargs):
		return _search_item_by_barcode(*args, **kwargs)

	def get_pending_receipts(self, *args, **kwargs):
		return _get_pending_receipts(*args, **kwargs)

	def get_purchase_order_detail(self, *args, **kwargs):
		return _get_purchase_order_detail(*args, **kwargs)

	def receive_stock(self, *args, **kwargs):
		return _receive_stock(*args, **kwargs)

	def get_stock_and_transit(self, *args, **kwargs):
		return _get_stock_and_transit(*args, **kwargs)

	def get_category_items(self, *args, **kwargs):
		return _get_category_items(*args, **kwargs)

	def save_po_draft(self, *args, **kwargs):
		return _save_po_draft(*args, **kwargs)

	def load_po_draft(self, *args, **kwargs):
		return _load_po_draft(*args, **kwargs)

	def delete_po_draft(self, *args, **kwargs):
		return _delete_po_draft(*args, **kwargs)

	def list_po_drafts(self, *args, **kwargs):
		return _list_po_drafts(*args, **kwargs)

	def save_pi_draft(self, *args, **kwargs):
		return _save_pi_draft(*args, **kwargs)

	def load_pi_draft(self, *args, **kwargs):
		return _load_pi_draft(*args, **kwargs)

	def delete_pi_draft(self, *args, **kwargs):
		return _delete_pi_draft(*args, **kwargs)

	def list_pi_drafts(self, *args, **kwargs):
		return _list_pi_drafts(*args, **kwargs)

	def submit_pi_draft(self, *args, **kwargs):
		return _submit_pi_draft(*args, **kwargs)

	def get_purchase_orders_for_invoice(self, *args, **kwargs):
		return _get_purchase_orders_for_invoice(*args, **kwargs)

	def get_item_purchase_details(self, *args, **kwargs):
		return _get_item_purchase_details(*args, **kwargs)

	def get_purchase_tax_template(self, *args, **kwargs):
		return _get_purchase_tax_template(*args, **kwargs)
