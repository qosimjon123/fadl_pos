import frappe
from frappe import _
from fadl_pos.services._base import BaseService
from fadl_pos.serializers.customer import CustomerResponseSerializer

class CustomerService(BaseService):
    
    def get(self, action: str, **kwargs) -> CustomerResponseSerializer:
        if action == "list":
            return self.get_list(**kwargs)
        elif action == "details":
            return self.get_details(**kwargs)
        elif action == "recent_transactions":
            return self.get_recent_transactions(**kwargs)
        else:
            frappe.throw(_("Invalid action: {0}").format(action))

    def manage(self, action: str, data: dict) -> CustomerResponseSerializer:
        if action == "create":
            return self.create(data)
        elif action == "update":
            return self.update(data)
        elif action == "set_info":
            return self.set_info(data)
        else:
            frappe.throw(_("Invalid action: {0}").format(action))

    def get_list(self, search_term: str = "", limit: int = 20) -> CustomerResponseSerializer:
        """
        Native: Search customers.
        """
        filters = []
        if search_term:
            filters.append([
                "Customer", "customer_name", "like", f"%{search_term}%", "or",
                "Customer", "name", "like", f"%{search_term}%", "or",
                "Customer", "mobile_no", "like", f"%{search_term}%"
            ])
            
        customers = frappe.get_all(
            "Customer",
            filters=filters,
            fields=["name", "customer_name", "email_id", "mobile_no", "customer_group", "territory"],
            limit=self._cap_limit(limit)
        )
        return {"customers": customers}

    def get_details(self, customer: str) -> CustomerResponseSerializer:
        """
        Native: Get full customer info.
        """
        doc = frappe.get_doc("Customer", customer)
        return {"customer": doc.as_dict()}

    def create(self, data: dict) -> CustomerResponseSerializer:
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

    def update(self, data: dict) -> CustomerResponseSerializer:
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

    def set_info(self, data: dict) -> CustomerResponseSerializer:
        """
        Native wrapper: Quickly update specific customer fields (email, mobile, loyalty).
        """
        from erpnext.selling.page.point_of_sale.point_of_sale import set_customer_info as native_set_info
        
        fieldname = data.get("fieldname")
        customer = data.get("customer")
        value = data.get("value", "")
        
        if not fieldname or not customer:
            frappe.throw(_("Fieldname and Customer are required."))
            
        native_set_info(fieldname, customer, value)
        
        return {
            "status": "success",
            "message": _("Updated {0} for {1}").format(fieldname, customer)
        }

    def get_recent_transactions(self, customer: str) -> CustomerResponseSerializer:
        """
        Native wrapper: Get last 20 transactions for a customer.
        """
        from erpnext.selling.page.point_of_sale.point_of_sale import get_customer_recent_transactions
        
        transactions = get_customer_recent_transactions(customer)
        return {"transactions": transactions}
