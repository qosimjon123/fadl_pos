"""Past orders list — wrapper for ``erpnext...point_of_sale.get_past_order_list``."""
import frappe
from frappe import _
from fadl_pos.services._base import BaseService
from fadl_pos.serializers.invoice_list import InvoiceListResponseSerializer

# Native Import
from erpnext.selling.page.point_of_sale.point_of_sale import get_past_order_list

class InvoiceListService(BaseService):
    """Returns merged POS + POS Sales Invoice history rows."""

    def get(self, action: str, **kwargs) -> InvoiceListResponseSerializer:
        if action == "history":
            return self.get_history(**kwargs)
        else:
            frappe.throw(_("Invalid action: {0}").format(action))

    def get_history(self, search_term: str = "", status: str = "Paid", limit: int = 20) -> InvoiceListResponseSerializer:
        """
        Native: Get past order list (POS Invoices + Sales Invoices).
        """
        invoices = get_past_order_list(
            search_term=search_term,
            status=status,
            limit=self._cap_limit(limit)
        )
        return {"invoices": invoices}
