"""
Customer CRUD/search and Desk POS field patches.

**CustomerService.get / manage** mirror ``fadl_pos.api.customer`` — list, details, recent transactions;
create/update via standard **Customer** documents; ``set_info`` delegates to
``erpnext...point_of_sale.set_customer_info``.
"""
import frappe
from frappe import _
from fadl_pos.meta import CUSTOMER_FIELDS
from fadl_pos.services._base import BaseService
from fadl_pos.serializers.customer import serialize_customers

class CustomerService(BaseService):
    """Customer documents + native POS helpers."""

    def get(self, action: str, **kwargs):
        if action == "list":
            return self.get_list(**kwargs)
        elif action == "details":
            return self.get_details(**kwargs)
        elif action == "recent_transactions":
            return self.get_recent_transactions(**kwargs)
        else:
            frappe.throw(_("Invalid action: {0}").format(action))

    def manage(self, action: str, data: dict):
        if action == "create":
            return self.create(data)
        elif action == "update":
            return self.update(data)
        elif action == "set_info":
            return self.set_info(data)
        else:
            frappe.throw(_("Invalid action: {0}").format(action))

    def _query_customers(self, mode: str, search_term: str = "", limit: int = 10, customer: str = ""):
        filters = {"disabled": 0, "is_frozen": 0}
        if mode == "details":
            if not customer:
                frappe.throw(_("Customer is required"))
            raw = frappe.db.get_value("Customer", customer, CUSTOMER_FIELDS, as_dict=True)
            if not raw:
                frappe.throw(_("Customer {0} not found").format(customer))
            return raw
        term = (search_term or "").strip()
        kwargs = {"filters": filters, "fields": CUSTOMER_FIELDS, "limit": self._cap_limit(limit)}
        if term:
            kwargs["or_filters"] = {f: ["like", f"%{term}%"] for f in CUSTOMER_FIELDS}
        return frappe.get_all("Customer", **kwargs)

    def get_list(self, search_term: str = "", limit: int = 10):
        rows = self._query_customers("list", search_term=search_term, limit=limit)
        return {"customers": serialize_customers(rows)}

    def get_details(self, customer: str):
        raw = self._query_customers("details", customer=customer)
        return {"customer": serialize_customers([raw])[0]}

    def create(self, data: dict):
        """
        Create a Customer from the POS API using ERPNext's Customer DocType.
        """
        # Ensure default group/territory if not provided
        if not data.get("customer_group"):
            data["customer_group"] = frappe.db.get_default("Customer Group") or "All Customer Groups"
        if not data.get("territory"):
            data["territory"] = frappe.db.get_default("Territory") or "All Territories"
            
        data["doctype"] = "Customer"
        doc = frappe.get_doc(data)
        doc.insert()
        
        return {
            "status": "success",
            "customer": doc.as_dict(),
            "message": _("Customer {0} created").format(doc.customer_name)
        }

    def update(self, data: dict):
        """
        Update existing customer.
        """
        name = data.get("name")
        if not name:
            frappe.throw(_("Customer name is required for update."))
            
        doc = frappe.get_doc("Customer", name)
        doc.update(data)
        doc.save()
        
        return {
            "status": "success",
            "customer": doc.as_dict()
        }

    def get_recent_transactions(self, customer: str):
        """
        Native wrapper: Get last 20 transactions for a customer.
        """
        from erpnext.selling.page.point_of_sale.point_of_sale import get_customer_recent_transactions
        
        transactions = get_customer_recent_transactions(customer)
        return {"transactions": transactions}
