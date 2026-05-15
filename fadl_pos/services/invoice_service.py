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

    @staticmethod
    def _invoice_doctype_from_settings() -> str:
        dt = frappe.db.get_single_value("POS Settings", "invoice_type") or "POS Invoice"
        return dt if dt in ("POS Invoice", "Sales Invoice") else "POS Invoice"

    @staticmethod
    def _get_existing_invoice_doc(name: str):
        if frappe.db.exists("POS Invoice", name):
            return frappe.get_doc("POS Invoice", name)
        if frappe.db.exists("Sales Invoice", name):
            return frappe.get_doc("Sales Invoice", name)
        frappe.throw(_("Invoice {0} not found").format(name))

    def save(self, data: dict) -> InvoiceResponseSerializer:
        """
        Create or update a POS/Sales Invoice draft (doctype from POS Settings).
        """
        name = data.get("name")
        if name:
            doc = self._get_existing_invoice_doc(name)
            if doc.docstatus != 0:
                frappe.throw(_("Cannot update a submitted or cancelled invoice."))
            doc.update(data)
        else:
            dt = self._invoice_doctype_from_settings()
            payload = dict(data)
            payload.pop("doctype", None)
            payload["doctype"] = dt
            payload.setdefault("is_pos", 1)
            if dt == "Sales Invoice":
                payload.setdefault("is_created_using_pos", 1)
            doc = frappe.get_doc(payload)

        if hasattr(doc, "set_missing_values"):
            doc.set_missing_values()

        doc.save()

        return {
            "status": "success",
            "name": doc.name,
            "invoice": doc.as_dict(),
        }

    def submit(self, data: dict) -> InvoiceResponseSerializer:
        """
        Save and submit invoice (POS Invoice or Sales Invoice per POS Settings).
        """
        save_res = self.save(data)
        name = save_res["name"]
        inv = save_res.get("invoice") or {}
        dt = inv.get("doctype")
        if dt not in ("POS Invoice", "Sales Invoice"):
            dt = self._get_existing_invoice_doc(name).doctype

        doc = frappe.get_doc(dt, name)
        doc.submit()

        return {
            "status": "success",
            "name": doc.name,
            "message": _("Invoice {0} submitted successfully").format(doc.name),
        }

    def make_return(self, data: dict) -> InvoiceResponseSerializer:
        """
        Create a return invoice from POS Invoice or POS-created Sales Invoice.
        """
        from erpnext.accounts.doctype.pos_invoice.pos_invoice import make_sales_return
        from erpnext.controllers.sales_and_purchase_return import make_return_doc

        source_name = data.get("return_against")
        if not source_name:
            frappe.throw(_("Original invoice name is required for return."))

        if frappe.db.exists("POS Invoice", source_name):
            return_doc = make_sales_return(source_name)
        elif frappe.db.exists("Sales Invoice", source_name):
            return_doc = make_return_doc("Sales Invoice", source_name)
        else:
            frappe.throw(_("Invoice {0} not found").format(source_name))

        if hasattr(return_doc, "set_missing_values"):
            return_doc.set_missing_values()

        return_doc.insert()

        return {
            "status": "success",
            "name": return_doc.name,
            "invoice": return_doc.as_dict(),
        }

    def void(self, data: dict) -> InvoiceResponseSerializer:
        """
        Cancel or delete an invoice (draft POS/Sales Invoice).
        """
        name = data.get("name")
        if not name:
            frappe.throw(_("Invoice name is required."))

        doc = self._get_existing_invoice_doc(name)

        if doc.docstatus == 1:
            doc.cancel()
        elif doc.docstatus == 0:
            frappe.delete_doc(doc.doctype, name)

        return {
            "status": "success",
            "name": name,
            "message": _("Invoice {0} voided").format(name),
        }

    def validate_cart(self, data: dict):
        from fadl_pos.services.validation_service import ValidationService

        return ValidationService.validate_cart_items(data.get("items", []), data.get("warehouse"))
