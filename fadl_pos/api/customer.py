import frappe
from fadl_pos.services.customer_service import CustomerService

@frappe.whitelist()
def get(action: str, **kwargs):
    """
    Unified customer query endpoint.
    Route: /api/method/fadl_pos.api.customer.get
    """
    return CustomerService().get(action, **kwargs)

@frappe.whitelist(methods=["POST"])
def manage(action: str, data: str):
    """
    Unified customer management endpoint.
    Route: /api/method/fadl_pos.api.customer.manage
    """
    service = CustomerService()
    parsed_data = service._parse_json(data)
    return service.manage(action, parsed_data)
