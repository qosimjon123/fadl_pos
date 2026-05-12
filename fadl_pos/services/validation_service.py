import frappe
from frappe import _

class ValidationService:
    """
    Backend validation helpers that mirror native ERPNext POS checks.
    """
    
    @staticmethod
    def validate_cart_items(items: list, warehouse: str) -> dict:
        """
        Backend-side validation of prices and stock before submission.
        """
        errors = []
        from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_stock_availability
        
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
