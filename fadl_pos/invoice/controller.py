# Copyright (c) 2026, FadlTech team and contributors

"""invoice controller — wraps ported xpos business logic."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController

from fadl_pos.invoice.processing.creation import create_invoice as _create_invoice
from fadl_pos.invoice.processing.creation import finalize_fiscal_invoice as _finalize_fiscal_invoice
from fadl_pos.invoice.processing.creation import discard_draft_invoice as _discard_draft_invoice
from fadl_pos.invoice.processing.creation import save_draft_invoice as _save_draft_invoice
from fadl_pos.invoice.processing.creation import update_invoice as _update_invoice
from fadl_pos.invoice.processing.creation import submit_invoice as _submit_invoice
from fadl_pos.invoice.processing.creation import validate_cart_items as _validate_cart_items
from fadl_pos.invoice.processing.data import get_last_invoice_rates as _get_last_invoice_rates
from fadl_pos.invoice.processing.queries import get_draft_invoices as _get_draft_invoices
from fadl_pos.invoice.processing.queries import get_unsettled_invoices as _get_unsettled_invoices
from fadl_pos.invoice.processing.queries import get_past_orders as _get_past_orders
from fadl_pos.invoice.processing.queries import get_invoices as _get_invoices
from fadl_pos.invoice.processing.queries import get_invoice_details as _get_invoice_details
from fadl_pos.invoice.processing.queries import delete_draft_invoice as _delete_draft_invoice
from fadl_pos.invoice.processing.queries import search_invoices_for_return as _search_invoices_for_return
from fadl_pos.invoice.processing.queries import get_invoice_for_return as _get_invoice_for_return
from fadl_pos.invoice.processing.queries import search_invoices_for_repeat as _search_invoices_for_repeat
from fadl_pos.invoice.processing.queries import get_invoice_for_repeat as _get_invoice_for_repeat
from fadl_pos.invoice.processing.utils import fetch_exchange_rate as _fetch_exchange_rate


class InvoiceController(BaseController):
	def create_invoice(self, *args, **kwargs):
		return _create_invoice(*args, **kwargs)

	def finalize_fiscal_invoice(self, *args, **kwargs):
		return _finalize_fiscal_invoice(*args, **kwargs)

	def discard_draft_invoice(self, *args, **kwargs):
		return _discard_draft_invoice(*args, **kwargs)

	def save_draft_invoice(self, *args, **kwargs):
		return _save_draft_invoice(*args, **kwargs)

	def get_draft_invoices(self, *args, **kwargs):
		return _get_draft_invoices(*args, **kwargs)

	def get_unsettled_invoices(self, *args, **kwargs):
		return _get_unsettled_invoices(*args, **kwargs)

	def get_past_orders(self, *args, **kwargs):
		return _get_past_orders(*args, **kwargs)

	def get_invoices(self, *args, **kwargs):
		return _get_invoices(*args, **kwargs)

	def get_invoice_details(self, *args, **kwargs):
		return _get_invoice_details(*args, **kwargs)

	def delete_draft_invoice(self, *args, **kwargs):
		return _delete_draft_invoice(*args, **kwargs)

	def search_invoices_for_return(self, *args, **kwargs):
		return _search_invoices_for_return(*args, **kwargs)

	def get_invoice_for_return(self, *args, **kwargs):
		return _get_invoice_for_return(*args, **kwargs)

	def fetch_exchange_rate(self, *args, **kwargs):
		return _fetch_exchange_rate(*args, **kwargs)

	def get_last_invoice_rates(self, *args, **kwargs):
		return _get_last_invoice_rates(*args, **kwargs)

	def search_invoices_for_repeat(self, *args, **kwargs):
		return _search_invoices_for_repeat(*args, **kwargs)

	def get_invoice_for_repeat(self, *args, **kwargs):
		return _get_invoice_for_repeat(*args, **kwargs)

	def update_invoice(self, *args, **kwargs):
		return _update_invoice(*args, **kwargs)

	def submit_invoice(self, *args, **kwargs):
		return _submit_invoice(*args, **kwargs)

	def validate_cart_items(self, *args, **kwargs):
		return _validate_cart_items(*args, **kwargs)
