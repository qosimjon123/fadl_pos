import frappe
from fadl_pos.services.payment_service import PaymentService

@frappe.whitelist()
def manage(action: str, **kwargs):
    """
    Unified payment and loyalty endpoint.
    Route: /api/method/fadl_pos.api.payment.manage
    """
    service = PaymentService()
    # If data is passed as JSON string, parse it
    if "payments" in kwargs and isinstance(kwargs["payments"], str):
        kwargs["payments"] = frappe.parse_json(kwargs["payments"])
        
    return service.manage(action, **kwargs)
