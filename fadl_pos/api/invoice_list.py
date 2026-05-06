import frappe
from fadl_pos.services.invoice_list_service import InvoiceListService

@frappe.whitelist()
def get(action: str, **kwargs):
    """
    Unified invoice list query endpoint.
    Route: /api/method/fadl_pos.api.invoice_list.get
    """
    return InvoiceListService().get(action, **kwargs)
