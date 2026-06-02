"""Past orders list — wrapper for ``erpnext...point_of_sale.get_past_order_list``."""

import frappe

# Native Import
from erpnext.selling.page.point_of_sale.point_of_sale import get_past_order_list
from frappe import _

from fadl_pos.schemas import InvoiceListQuery, InvoiceListResponseSerializer
from fadl_pos.services._base import BaseService


class InvoiceListService(BaseService):
	"""Returns merged POS + POS Sales Invoice history rows."""

	def get(self, action: str, **kwargs) -> InvoiceListResponseSerializer:
		if action == "history":
			return self.get_history(**kwargs)
		else:
			frappe.throw(_("Invalid action: {0}").format(action))

	def get_history(
		self, search_term: str = "", status: str = "Paid", limit: int = 20
	) -> InvoiceListResponseSerializer:
		"""
		Native: Get past order list (POS Invoices + Sales Invoices).
		"""
		query = InvoiceListQuery.model_validate(
			{"search_term": search_term, "status": status, "limit": limit}
		)
		invoices = get_past_order_list(search_term=query.search_term, status=query.status, limit=query.limit)
		return InvoiceListResponseSerializer.dump({"invoices": invoices})
