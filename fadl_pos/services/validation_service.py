import frappe
from frappe import _
from frappe.utils import now_datetime, getdate, add_days

from fadl_pos.services.invoice_service import InvoiceService

class ValidationService:
    """
    Backend validation logic to ensure PWA stability and data integrity.
    """
    
    @staticmethod
    def validate_cart_items(items: list, warehouse: str) -> dict:
        """
        Backend-side validation of prices and stock before submission.
        """
        errors = []
        from erpnext.selling.page.point_of_sale.point_of_sale import get_stock_availability
        
        for item in items:
            item_code = item.get("item_code")
            qty = item.get("qty", 0)
            
            # 1. Stock Check
            availability, is_stock_item, allow_negative = get_stock_availability(item_code, warehouse)
            if is_stock_item and not allow_negative and availability < qty:
                errors.append(_("Item {0} has insufficient stock ({1} available, {2} requested)").format(
                    item_code, availability, qty
                ))
                
            # 2. Price Check (Optional but good for security)
            # Here we could verify if the rate matches the Price List rate
            
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    @staticmethod
    def check_offline_sync(offline_id: str) -> bool:
        """
        Check if an invoice with this offline ID (e.g., a custom field or naming convention)
        has already been synced to prevent duplicates.
        """
        # In fadl_pos, we should ideally have a custom field 'offline_id' on POS Invoice.
        # For now, let's assume we use a naming pattern or a field if it exists.
        return frappe.db.exists("POS Invoice", {"offline_id": offline_id})

    @staticmethod
    def cleanup_old_drafts(days: int = 7):
        """
        Delete POS Invoice drafts older than X days to keep the database clean.
        """
        cutoff_date = add_days(now_datetime(), -days)
        drafts = frappe.get_all(
            "POS Invoice",
            filters={
                "docstatus": 0,
                "modified": ["<", cutoff_date]
            },
            fields=["name"]
        )
        
        for d in drafts:
            frappe.delete_doc("POS Invoice", d.name, ignore_permissions=True)
            
        return len(drafts)
