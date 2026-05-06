import frappe
from fadl_pos.services.offers_service import OffersService

@frappe.whitelist()
def get(action: str, **kwargs):
    """
    Unified offers and coupons endpoint.
    Route: /api/method/fadl_pos.api.offers.get
    """
    return OffersService().get(action, **kwargs)

@frappe.whitelist(methods=["POST"])
def apply(invoice_name: str, coupon_code: str = None):
    """
    Apply a coupon or force offer calculation on an invoice.
    Route: /api/method/fadl_pos.api.offers.apply
    """
    return OffersService().apply_offer(invoice_name, coupon_code)
