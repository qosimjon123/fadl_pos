"""
Customer CRUD/search and Desk POS field patches.

**CustomerService.get / manage** mirror ``fadl_pos.api.customer`` — list, details, recent transactions;
create/update via standard **Customer** documents; ``set_info`` delegates to
``erpnext...point_of_sale.set_customer_info``.
"""

import frappe
from frappe import _
from frappe.utils import flt, nowdate
from pydantic import TypeAdapter

from fadl_pos.meta import CUSTOMER_FIELDS
from fadl_pos.schemas import CustomerDetailsQuery, CustomerListQuery, CustomerOut
from fadl_pos.services._base import BaseService


class CustomerService(BaseService):
	"""Customer documents + native POS helpers."""

	_customer_out_list = TypeAdapter(list[CustomerOut])

	@staticmethod
	def _fetch_outstanding_balances(parties: list[str], company: str | None = None) -> dict[str, float]:
		company = company or frappe.defaults.get_user_default("Company")
		if not parties or not company:
			return {}
		from erpnext.accounts.utils import get_currency_precision

		precision = get_currency_precision()
		rows = frappe.db.sql(
			"""
			SELECT party,
				sum(round(debit_in_account_currency, %(p)s))
					- sum(round(credit_in_account_currency, %(p)s)) AS balance
			FROM `tabGL Entry`
			WHERE is_cancelled = 0
				AND company = %(company)s
				AND party_type = 'Customer'
				AND party IN %(parties)s
				AND posting_date <= %(date)s
			GROUP BY party
			""",
			{"company": company, "parties": parties, "date": nowdate(), "p": precision},
			as_dict=True,
		)
		return {r.party: flt(r.balance) for r in rows}

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
		kwargs = {"filters": filters, "fields": CUSTOMER_FIELDS, "limit": limit}
		if term:
			kwargs["or_filters"] = {f: ["like", f"%{term}%"] for f in CUSTOMER_FIELDS}
		return frappe.get_all("Customer", **kwargs)

	def get_list(self, search_term: str = "", limit: int = 10):
		query = CustomerListQuery.model_validate({"search_term": search_term, "limit": limit})
		rows = self._query_customers("list", search_term=query.search_term, limit=query.limit)
		parties = [r["name"] for r in rows if r.get("name")]
		balances = self._fetch_outstanding_balances(parties)
		payloads = [
			{
				**{f: r.get(f) for f in CUSTOMER_FIELDS},
				"outstanding_balance": balances.get(r.get("name", ""), 0.0),
			}
			for r in rows
		]
		customers = self._customer_out_list.dump_python(self._customer_out_list.validate_python(payloads))
		return {"customers": customers}

	def get_details(self, customer: str):
		query = CustomerDetailsQuery.model_validate({"customer": customer})
		raw = self._query_customers("details", customer=query.customer)
		parties = [raw["name"]] if raw.get("name") else []
		balances = self._fetch_outstanding_balances(parties)
		payload = {
			**{f: raw.get(f) for f in CUSTOMER_FIELDS},
			"outstanding_balance": balances.get(raw.get("name", ""), 0.0),
		}
		customer_out = CustomerOut.model_validate(payload).model_dump()
		return {"customer": customer_out}

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
			"message": _("Customer {0} created").format(doc.customer_name),
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

		return {"status": "success", "customer": doc.as_dict()}

	def get_recent_transactions(self, customer: str):
		"""
		Native wrapper: Get last 20 transactions for a customer.
		"""
		from erpnext.selling.page.point_of_sale.point_of_sale import get_customer_recent_transactions

		transactions = get_customer_recent_transactions(customer)
		return {"transactions": transactions}
