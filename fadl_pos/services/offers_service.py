"""
Promotions and coupon apply path for fadl POS.

**get(action, **kwargs)**

* ``active_offers`` → ``{\"offers\": [Pricing Rule field dicts within validity window]}``.
* ``coupons`` → ``{\"coupons\": [Coupon Code rows]}``.

**apply_offer(invoice_name, coupon_code=None)**

* *Input*: ``invoice_name`` — POS or Sales Invoice id; optional ``coupon_code`` sets ``doc.coupon_code``.
* *Output*: ``{\"status\": \"success\", \"invoice\": dict}`` after native ``set_missing_values``,
  ``calculate_taxes_and_totals``, and ``save`` (full validate + pricing rules).
"""
import frappe
from frappe import _
from frappe.utils import today, getdate

from fadl_pos.services._base import BaseService
from fadl_pos.services.invoice_service import InvoiceService
from fadl_pos.serializers.offers import OffersResponseSerializer

class OffersService(BaseService):
    """Read offers/coupons; apply coupon on draft invoice using ERPNext document controller."""

    def get(self, action: str, **kwargs) -> OffersResponseSerializer:
        if action == "active_offers":
            return self.get_active_offers(**kwargs)
        elif action == "coupons":
            return self.get_coupons(**kwargs)
        else:
            frappe.throw(_("Invalid action: {0}").format(action))

    def get_active_offers(self, pos_profile: str = None) -> OffersResponseSerializer:
        """
        Native logic: Get all active Pricing Rules.
        """
        # Filter for selling rules that are not disabled and within validity dates
        filters = {
            "selling": 1,
            "disable": 0,
        }
        
        # Add date validity
        current_date = today()
        
        rules = frappe.get_all(
            "Pricing Rule",
            filters=filters,
            fields=[
                "name", "title", "apply_on", "rate_or_discount", 
                "discount_percentage", "discount_amount", "priority"
            ]
        )
        
        # Filter by date in python to handle NULLs properly if needed, 
        # or use complex SQL. simpler:
        active_rules = []
        for r in rules:
            doc = frappe.get_cached_doc("Pricing Rule", r.name)
            if doc.valid_from and getdate(doc.valid_from) > getdate(current_date):
                continue
            if doc.valid_upto and getdate(doc.valid_upto) < getdate(current_date):
                continue
            active_rules.append(r)
            
        return {"offers": active_rules}

    def get_coupons(self, customer: str = None) -> OffersResponseSerializer:
        """
        Native logic: Get available Coupon Codes.
        """
        filters = {}
        if customer:
            # You could filter by customer-specific coupons if implemented in ERPNext
            pass
            
        coupons = frappe.get_all(
            "Coupon Code",
            filters=filters,
            fields=["name", "coupon_code", "pricing_rule", "valid_from", "valid_upto"]
        )
        return {"coupons": coupons}

    def apply_offer(self, invoice_name: str, coupon_code: str = None):
        """
        Set coupon on draft POS Invoice or Sales Invoice and save (native pricing / totals).
        """
        doc = InvoiceService._get_existing_invoice_doc(invoice_name)
        if doc.docstatus != 0:
            frappe.throw(
                _("Only draft invoices can apply coupons."),
                frappe.ValidationError,
            )
        if coupon_code:
            doc.coupon_code = coupon_code

        if hasattr(doc, "set_missing_values"):
            doc.set_missing_values()
        if hasattr(doc, "calculate_taxes_and_totals"):
            doc.calculate_taxes_and_totals()

        doc.save()
        return {"status": "success", "invoice": doc.as_dict()}
