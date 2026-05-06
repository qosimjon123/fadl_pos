import frappe
from fadl_pos.services.invoice_service import InvoiceService

@frappe.whitelist(methods=["POST"])
def sync(action: str, data: str):
    """
    Unified invoice sync endpoint.
    Route: /api/method/fadl_pos.api.invoice.sync
    Params: action (save|submit|return|void), data (JSON string of invoice data).
    """
    service = InvoiceService()
    parsed_data = service._parse_json(data)
    return service.sync(action, parsed_data)
