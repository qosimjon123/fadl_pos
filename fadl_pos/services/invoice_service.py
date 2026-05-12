import frappe
from frappe import _

from fadl_pos.services._base import BaseService
from fadl_pos.serializers.invoice import InvoiceResponseSerializer

class InvoiceService(BaseService):
    
    def sync(self, action: str, data: dict) -> InvoiceResponseSerializer:
        """
        Unified entry point for invoice synchronization.
        """
        if action == "save":
            return self.save(data)
        elif action == "submit":
            return self.submit(data)
        elif action == "return":
            return self.make_return(data)
        elif action == "void":
            return self.void(data)
        elif action == "validate":
            return self.validate_cart(data)
        else:
            frappe.throw(_("Invalid action: {0}").format(action))

    def save(self, data: dict) -> InvoiceResponseSerializer:
        """
        Create or update a POS Invoice draft.
        """
        if data.get("name"):
            doc = frappe.get_doc("POS Invoice", data["name"])
            if doc.docstatus != 0:
                frappe.throw(_("Cannot update a submitted or cancelled invoice."))
            doc.update(data)
        else:
            data["doctype"] = "POS Invoice"
            doc = frappe.get_doc(data)

        if hasattr(doc, "set_missing_values"):
            doc.set_missing_values()

        doc.save()
        
        return {
            "status": "success",
            "name": doc.name,
            "invoice": doc.as_dict()
        }

    def submit(self, data: dict) -> InvoiceResponseSerializer:
        """
        Save and submit a POS Invoice.
        """
        # First save to ensure all fields are correct and validation passes
        save_res = self.save(data)
        doc = frappe.get_doc("POS Invoice", save_res["name"])
        
        doc.submit()
        
        return {
            "status": "success",
            "name": doc.name,
            "message": _("Invoice {0} submitted successfully").format(doc.name)
        }

    def make_return(self, data: dict) -> InvoiceResponseSerializer:
        """
        Create a return invoice from an existing one.
        """
        from erpnext.accounts.doctype.pos_invoice.pos_invoice import make_sales_return
        
        source_name = data.get("return_against")
        if not source_name:
            frappe.throw(_("Original invoice name is required for return."))
            
        return_doc = make_sales_return(source_name)
        
        # Add any specific return data if provided
        if data.get("items"):
            # Logic to filter items for partial return if needed
            pass
            
        if hasattr(return_doc, "set_missing_values"):
            return_doc.set_missing_values()

        return_doc.insert()
        
        return {
            "status": "success",
            "name": return_doc.name,
            "invoice": return_doc.as_dict()
        }

    def void(self, data: dict) -> InvoiceResponseSerializer:
        """
        Cancel or delete an invoice.
        """
        name = data.get("name")
        doc = frappe.get_doc("POS Invoice", name)
        
        if doc.docstatus == 1:
            doc.cancel()
        elif doc.docstatus == 0:
            frappe.delete_doc("POS Invoice", name)
            
        return {
            "status": "success",
            "name": name,
            "message": _("Invoice {0} voided").format(name)
        }

    def validate_cart(self, data: dict):
        from fadl_pos.services.validation_service import ValidationService
        return ValidationService.validate_cart_items(data.get("items", []), data.get("warehouse"))
