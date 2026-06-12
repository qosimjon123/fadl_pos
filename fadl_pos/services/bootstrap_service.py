"""
POS SPA bootstrap: opening voucher, profile, item group tree, warehouses, taxes, precision.

Invoked via ``fadl_pos.api.catalog.boot`` → :class:`BootstrapService`.
"""

import frappe
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups
from frappe import _
from frappe.query_builder import DocType, Order

from fadl_pos.meta import POS_PROFILE_FIELDS
from fadl_pos.services._base import BaseService
from fadl_pos.services.customer_service import CustomerService
from fadl_pos.services.session_service import SessionService
from fadl_pos.services.stock_service import StockService


class BootstrapService(BaseService):
	"""Single-request payload for POS SPA initialization."""

	def boot(self, pos_profile: str) -> dict:
		"""Collect opening voucher, profile, groups, warehouses, checklists, taxes."""
		if not pos_profile:
			frappe.throw(_("Invalid POS Profile"))

		profile_doc = frappe.get_doc("POS Profile", pos_profile)
		if profile_doc.disabled:
			frappe.throw(_("Invalid POS Profile"))

		open_rows = frappe.get_all(
			"POS Opening Entry",
			filters={
				"user": frappe.session.user,
				"pos_profile": pos_profile,
				"docstatus": 1,
				"pos_closing_entry": ["in", ["", None]],
			},
			fields=["name"],
			order_by="period_start_date desc",
			limit_page_length=1,
		)
		if not open_rows:
			frappe.throw(
				_("No open POS Opening Entry for user {0} and profile {1}").format(
					frappe.session.user, pos_profile
				)
			)
		opening = frappe.get_doc("POS Opening Entry", open_rows[0].name)

		pay_by_mop = {
			pm["mode_of_payment"]: pm
			for pm in SessionService()._fetch_payment_methods([pos_profile])
		}
		returns_by_mop = {
			p.mode_of_payment: p.allow_in_returns for p in (profile_doc.payments or [])
		}

		balance_details_out = []
		for row in opening.balance_details or []:
			pr = pay_by_mop.get(row.mode_of_payment)
			balance_details_out.append(
				{
					"mode_of_payment": row.mode_of_payment,
					"opening_amount": row.opening_amount,
					"default": bool(pr.get("default")) if pr else False,
					"allow_in_returns": bool(returns_by_mop.get(row.mode_of_payment, 0)),
				}
			)

		checklists_payload = {
			"opening": [
				{"title": row.title}
				for row in (profile_doc.custom_opening_checklist or [])
				if not row.disabled
			],
			"closing": [
				{"title": row.title}
				for row in (profile_doc.custom_closing_checklists or [])
				if not row.disabled
			],
		}
		default_customer_doc = None
		if profile_doc.customer:
			try:
				default_customer_doc = CustomerService().get_details(profile_doc.customer)["customer"]
			except frappe.DoesNotExistError:
				pass

		pos_out = {field: profile_doc.get(field) for field in POS_PROFILE_FIELDS}
		pos_out["customer"] = default_customer_doc

		return {
			"opening_voucher": {
				"name": opening.name,
				"period_start_date": opening.period_start_date,
				"user_full_name": frappe.db.get_value("User", opening.user, "full_name") or opening.user,
				"balance_details": balance_details_out,
			},
			"pos_profile": pos_out,
			"precision": self._get_precision(),
			"item_groups": self._build_item_group_tree(pos_profile),
			"warehouses": StockService().get_warehouses(profile_doc.company),
			"checklists": checklists_payload,
			"taxes": self._get_taxes(profile_doc.company),
		}

	@staticmethod
	def _get_precision() -> dict[str, object]:
		"""
		Number formatting / rounding settings from System Settings.

		The frontend must use them for all arithmetic to match server-side
		``flt()`` / ``rounded()`` results exactly.
		"""
		settings = frappe.db.get_value(
			"System Settings",
			"System Settings",
			["currency_precision", "float_precision", "rounding_method", "number_format"],
			as_dict=True,
		)
		return {
			"currency": int(settings.currency_precision) if settings.currency_precision else 2,
			"float": int(settings.float_precision) if settings.float_precision else 3,
			"rounding_method": settings.rounding_method,
			"number_format": settings.number_format,
		}

	def _get_taxes(self, company: str) -> list[dict[str, object]]:
		"""Company tax templates: title + taxes; only if all rows are On Net Total."""
		if not company:
			return []

		Template = DocType("Sales Taxes and Charges Template")
		Tax = DocType("Sales Taxes and Charges")

		rows = (
			frappe.qb.from_(Template)
			.left_join(Tax)
			.on((Tax.parent == Template.name) & (Tax.parenttype == "Sales Taxes and Charges Template"))
			.select(
				Template.name.as_("template_name"),
				Template.title,
				Tax.account_head,
				Tax.charge_type,
				Tax.rate,
				Tax.description,
				Tax.included_in_print_rate,
				Tax.idx,
			)
			.where(Template.company == company)
			.where(Template.disabled == 0)
			.orderby(Template.name, order=Order.asc)
			.orderby(Tax.idx, order=Order.asc)
		).run(as_dict=True)

		buckets: dict[str, dict[str, object]] = {}
		order: list[str] = []

		for row in rows:
			key = row.template_name
			if key not in buckets:
				buckets[key] = {"title": row.title, "taxes": [], "valid": True}
				order.append(key)
			if not row.account_head:
				continue
			if row.charge_type != "On Net Total":
				buckets[key]["valid"] = False
				continue
			if buckets[key]["valid"]:
				buckets[key]["taxes"].append(
					{
						"account_head": row.account_head,
						"charge_type": row.charge_type,
						"rate": row.rate,
						"included_in_print_rate": row.included_in_print_rate or 0,
						"idx": row.idx,
					}
				)

		return [
			{"title": buckets[key]["title"], "taxes": buckets[key]["taxes"]}
			for key in order
			if buckets[key]["valid"]
		]

	def _build_item_group_tree(self, pos_profile: str) -> dict:
		"""Allowed item groups from POS Profile as nested JSON tree for the SPA."""
		allowed_groups = get_item_groups(pos_profile)

		filters = {}
		if allowed_groups:
			filters["name"] = ["in", allowed_groups]

		groups = frappe.get_all(
			"Item Group",
			filters=filters,
			fields=["name", "is_group", "parent_item_group"],
			order_by="lft asc",
		)

		item_tax_template_by_group: dict[str, str] = {}
		if groups:
			group_names = [g.name for g in groups]
			for row in frappe.get_all(
				"Item Tax",
				filters={
					"parent": ["in", group_names],
					"parenttype": "Item Group",
					"parentfield": "taxes",
				},
				fields=["parent", "item_tax_template"],
				order_by="parent asc, idx asc",
			):
				if row.parent not in item_tax_template_by_group:
					item_tax_template_by_group[row.parent] = row.item_tax_template

		by_name = {
			g.name: {
				"name": g.name,
				"tax": item_tax_template_by_group.get(g.name),
				"is_group": bool(g.is_group),
				"children": [],
			}
			for g in groups
		}

		roots = []
		for g in groups:
			node = by_name[g.name]
			parent = g.parent_item_group
			if parent and parent in by_name:
				by_name[parent]["children"].append(node)
			else:
				roots.append(node)

		def clean_empty(nodes):
			for n in nodes:
				if not n.get("tax"):
					n.pop("tax", None)
				if not n["children"]:
					del n["children"]
				else:
					clean_empty(n["children"])

		clean_empty(roots)
		return {"tree": roots}
