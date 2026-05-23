"""
Customer CRUD/search and Desk POS field patches.

**CustomerService.get / manage** mirror ``fadl_pos.api.customer`` — list, details, recent transactions;
create/update via standard **Customer** documents; ``set_info`` delegates to
``erpnext...point_of_sale.set_customer_info``.
"""
import frappe
from frappe import _
from fadl_pos.services._base import BaseService
from fadl_pos.serializers.customer import CustomerResponseSerializer

class CustomerService(BaseService):
    """Customer documents + native POS helpers."""

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
        customer_dict = doc.as_dict()

        # 1. Интеграция программы лояльности
        if customer_dict.get("loyalty_program"):
            try:
                from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_program_details_with_points
                loyalty_info = get_loyalty_program_details_with_points(
                    customer, 
                    customer_dict["loyalty_program"], 
                    silent=True
                )
                customer_dict["loyalty_points"] = loyalty_info.get("loyalty_points", 0)
                customer_dict["conversion_factor"] = loyalty_info.get("conversion_factor", 1)
            except Exception:
                customer_dict["loyalty_points"] = 0
                customer_dict["conversion_factor"] = 1

        # 2. Эксклюзив: Текущий баланс (долг) клиента
        try:
            from erpnext.accounts.utils import get_balance_on
            # Отрицательный баланс в дебиторке означает, что клиент нам должен (или наоборот, зависит от плана счетов)
            # Узнаем валюту и баланс
            company = frappe.defaults.get_user_default("Company")
            if company:
                balance = get_balance_on(party_type="Customer", party=customer, company=company)
                customer_dict["outstanding_balance"] = balance
        except Exception:
            pass

        # 3. Эксклюзив: Последние транзакции клиента (для быстрой истории покупок на кассе)
        try:
            from erpnext.selling.page.point_of_sale.point_of_sale import get_customer_recent_transactions
            customer_dict["recent_transactions"] = get_customer_recent_transactions(customer)
        except Exception:
            pass

        return {"customer": customer_dict}

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
