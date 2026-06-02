"""
Item catalog: native ``point_of_sale`` search/list/scan plus SPA ``boot`` payload.

See :meth:`CatalogService.boot_pos` for the large composite response (opening voucher, profile, item group
trees, warehouses, checklists).
"""

from collections import defaultdict

import frappe
from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_item_group, get_stock_availability
from erpnext.accounts.doctype.pos_profile.pos_profile import get_child_nodes, get_item_groups
from erpnext.stock.get_item_details import get_conversion_factor
from erpnext.stock.utils import scan_barcode
from frappe import _
from frappe.query_builder import DocType, Order
from frappe.utils import cint, get_datetime
from frappe.utils.nestedset import get_root_of

from fadl_pos.meta import POS_PROFILE_FIELDS
from fadl_pos.schemas import CatalogItemOut, CatalogResponseSerializer
from fadl_pos.services._base import BaseService
from fadl_pos.services.customer_service import CustomerService
from fadl_pos.services.session_service import SessionService
from fadl_pos.services.stock_service import StockService


class CatalogService(BaseService):
	"""Thin wrappers around ERPNext POS page controllers where possible."""

	def get(self, action: str, **kwargs) -> CatalogResponseSerializer:
		"""
		Unified entry point for catalog actions.
		"""
		if action == "items":
			return self.get_items(**kwargs)
		elif action == "boot":
			pos_profile = (kwargs.get("pos_profile") or "").strip()
			if not pos_profile:
				frappe.throw(_("pos_profile is required for boot"))
			return self.boot_pos(pos_profile)
		else:
			frappe.throw(_("Invalid action: {0}").format(action))

	def search_for_serial_or_batch_or_barcode_number(self, search_value: str) -> dict[str, str | None]:
		return scan_barcode(search_value)

	def filter_result_items(self, result, pos_profile):
		if result and result.get("items"):
			pos_profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
			pos_item_groups = get_item_group(pos_profile_doc)
			if not pos_item_groups:
				return
			result["items"] = [
				item for item in result.get("items") if item.get("item_group") in pos_item_groups
			]

	def search_by_term(self, search_term, warehouse, price_list):
		result = self.search_for_serial_or_batch_or_barcode_number(search_term) or {}

		item_code = result.get("item_code", search_term)
		serial_no = result.get("serial_no", "")
		batch_no = result.get("batch_no", "")
		barcode = result.get("barcode", "")

		if not result:
			return

		item_doc = frappe.get_doc("Item", item_code)

		if not item_doc:
			return

		item = {
			"barcode": barcode,
			"batch_no": batch_no,
			"description": item_doc.description or "",
			"is_stock_item": item_doc.is_stock_item,
			"name": item_doc.name,
			"item_group": item_doc.item_group,
			"item_image": item_doc.image,
			"item_name": item_doc.item_name,
			"serial_no": serial_no,
			"stock_uom": item_doc.stock_uom,
			"uom": item_doc.stock_uom,
			"has_serial_no": item_doc.has_serial_no,
			"has_batch_no": item_doc.has_batch_no,
			"tax_code": item_doc.get("tax_code"),
			"max_discount": item_doc.max_discount,
			"brand": item_doc.brand,
		}

		if barcode:
			barcode_info = next(filter(lambda x: x.barcode == barcode, item_doc.get("barcodes", [])), None)
			if barcode_info and barcode_info.uom:
				uom = next(filter(lambda x: x.uom == barcode_info.uom, item_doc.uoms), {})
				item.update(
					{
						"uom": barcode_info.uom,
						"conversion_factor": uom.get("conversion_factor", 1),
					}
				)

		item_stock_qty, _is_stock_item, _is_negative_stock_allowed = get_stock_availability(
			item_code, warehouse
		)
		item_stock_qty = item_stock_qty // item.get("conversion_factor", 1)
		item.update({"actual_qty": item_stock_qty})

		price_filters = {
			"price_list": price_list,
			"item_code": item_code,
		}

		if batch_no:
			price_filters["batch_no"] = ["in", [batch_no, ""]]

		if serial_no:
			price_filters["uom"] = item_doc.stock_uom

		price = frappe.get_list(
			doctype="Item Price",
			filters=price_filters,
			fields=["uom", "currency", "price_list_rate", "batch_no"],
		)

		def __sort(p):
			p_uom = p.get("uom")
			p_batch = p.get("batch_no")
			batch_no = item.get("batch_no")

			if batch_no and p_batch and p_batch == batch_no:
				if p_uom == item.get("uom"):
					return 0
				elif p_uom == item.get("stock_uom"):
					return 1
				else:
					return 2

			if p_uom == item.get("uom"):
				return 3
			elif p_uom == item.get("stock_uom"):
				return 4
			else:
				return 5

		# sort by fallback preference. always pick exact uom and batch number match if available
		price = sorted(price, key=__sort)

		if len(price) > 0:
			p = price.pop(0)
			item.update(
				{
					"currency": p.get("currency"),
					"price_list_rate": p.get("price_list_rate"),
				}
			)

		return {"items": [item]}

	def get_conditions(self, search_term):
		condition = "("
		condition += """item.name like {search_term}
            or item.item_name like {search_term}""".format(
			search_term=frappe.db.escape("%" + search_term + "%")
		)
		condition += self.add_search_fields_condition(search_term)
		condition += ")"

		return condition

	def add_search_fields_condition(self, search_term):
		condition = ""
		search_fields = frappe.get_all("POS Search Fields", fields=["fieldname"])
		if search_fields:
			for field in search_fields:
				if not field.get("fieldname"):
					continue
				condition += " or item.`{}` like {}".format(
					field["fieldname"], frappe.db.escape("%" + search_term + "%")
				)
		return condition

	def get_item_group_condition(self, pos_profile):
		cond = "and 1=1"
		item_groups = get_item_groups(pos_profile)
		if item_groups:
			cond = "and item.item_group in (%s)" % (", ".join(["%s"] * len(item_groups)))

		return cond % tuple(item_groups)

	def _fetch_item_prices_bulk(self, item_codes, price_list, current_date):
		"""One Item Price query for all item_codes; rows grouped per item, valid_from desc."""
		if not item_codes or not price_list:
			return {}

		ItemPrice = DocType("Item Price")
		rows = (
			frappe.qb.from_(ItemPrice)
			.select(
				ItemPrice.item_code,
				ItemPrice.price_list_rate,
				ItemPrice.currency,
				ItemPrice.uom,
				ItemPrice.batch_no,
				ItemPrice.valid_from,
				ItemPrice.valid_upto,
			)
			.where(ItemPrice.price_list == price_list)
			.where(ItemPrice.item_code.isin(item_codes))
			.where(ItemPrice.selling == 1)
			.where((ItemPrice.valid_from <= current_date) | (ItemPrice.valid_from.isnull()))
			.where((ItemPrice.valid_upto >= current_date) | (ItemPrice.valid_upto.isnull()))
			.orderby(ItemPrice.valid_from, order=Order.desc)
		).run(as_dict=True)

		prices_by_item = defaultdict(list)
		for row in rows:
			prices_by_item[row.item_code].append(row)

		# Global ORDER BY does not guarantee per-item ordering after grouping.
		for prices in prices_by_item.values():
			prices.sort(
				key=lambda d: (
					get_datetime(d["valid_from"]) if d.get("valid_from") else get_datetime("1900-01-01")
				),
				reverse=True,
			)

		return prices_by_item

	def _resolve_item_uom_price(self, item, item_prices):
		"""
		Pick uom, rate, currency, and Item Price.batch_no for catalog list rows.

		item_prices are pre-sorted by valid_from desc. batch_no here is the price-rule
		field on Item Price, not stock/line batch from barcode scan.
		"""
		stock_uom_price = next((d for d in item_prices if d.get("uom") == item.stock_uom), {})
		item_uom = item.stock_uom
		item_uom_price = stock_uom_price

		if item.sales_uom and item.sales_uom != item.stock_uom:
			item_uom = item.sales_uom
			sales_uom_price = next((d for d in item_prices if d.get("uom") == item.sales_uom), {})
			if sales_uom_price:
				item_uom_price = sales_uom_price

		if item_prices and not item_uom_price:
			item_uom = item_prices[0].get("uom")
			item_uom_price = item_prices[0]

		return item_uom, item_uom_price

	def get_items(
		self, start, page_length=15, price_list=None, item_group=None, pos_profile=None, search_term=""
	):
		warehouse, hide_unavailable_items = frappe.db.get_value(
			"POS Profile", pos_profile, ["warehouse", "hide_unavailable_items"]
		)

		result = []

		if search_term:
			result = self.search_by_term(search_term, warehouse, price_list) or []
			self.filter_result_items(result, pos_profile)
			if result:
				return {"items": [CatalogItemOut.model_validate(i).model_dump() for i in result["items"]]}

		if not frappe.db.exists("Item Group", item_group):
			item_group = get_root_of("Item Group")

		condition = self.get_conditions(search_term)
		condition += self.get_item_group_condition(pos_profile)

		lft, rgt = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"])

		bin_join_selection, bin_join_condition = "", ""
		if hide_unavailable_items:
			bin_join_selection = "LEFT JOIN `tabBin` bin ON bin.item_code = item.name"
			bin_join_condition = "AND (item.is_stock_item = 0 OR (item.is_stock_item = 1 AND bin.warehouse = %(warehouse)s AND bin.actual_qty > 0))"

		items_data = frappe.db.sql(
			"""
            SELECT
                item.name AS name,
                item.item_name,
                item.description,
                item.item_group,
                item.stock_uom,
                item.image AS item_image,
                item.is_stock_item,
                item.has_serial_no,
                item.has_batch_no,
                item.tax_code,
                item.max_discount,
                item.brand,
                item.sales_uom
            FROM
                `tabItem` item {bin_join_selection}
            WHERE
                item.disabled = 0
                AND item.has_variants = 0
                AND item.is_sales_item = 1
                AND item.is_fixed_asset = 0
                AND item.item_group in (SELECT name FROM `tabItem Group` WHERE lft >= {lft} AND rgt <= {rgt})
                AND {condition}
                {bin_join_condition}
            ORDER BY
                item.name asc
            LIMIT
                {page_length} offset {start}""".format(
				start=cint(start),
				page_length=cint(page_length),
				lft=cint(lft),
				rgt=cint(rgt),
				condition=condition,
				bin_join_selection=bin_join_selection,
				bin_join_condition=bin_join_condition,
			),
			{"warehouse": warehouse},
			as_dict=1,
		)

		# return (empty) list if there are no results
		if not items_data:
			return {"items": []}

		current_date = frappe.utils.today()
		item_codes = [row.name for row in items_data]
		prices_by_item = self._fetch_item_prices_bulk(item_codes, price_list, current_date)

		for item in items_data:
			item.actual_qty, _, _is_negative_stock_allowed = get_stock_availability(item.name, warehouse)

			item_prices = prices_by_item.get(item.name, [])
			item_uom, item_uom_price = self._resolve_item_uom_price(item, item_prices)

			item_conversion_factor = get_conversion_factor(item.name, item_uom).get("conversion_factor")

			if item.stock_uom != item_uom:
				item.actual_qty = item.actual_qty // item_conversion_factor

			if item_uom_price and item_uom != item_uom_price.get("uom"):
				item_uom_price.price_list_rate = item_uom_price.price_list_rate * item_conversion_factor

			result.append(
				{
					**item,
					"description": item.description or "",
					"price_list_rate": item_uom_price.get("price_list_rate"),
					"currency": item_uom_price.get("currency"),
					"uom": item_uom,
					"batch_no": item_uom_price.get("batch_no"),
				}
			)

		return {"items": [CatalogItemOut.model_validate(i).model_dump() for i in result]}

	def init_empty_invoice_template(self, invoice, pos_profile):
		"""
		Build an initialized POS invoice template on the server.

		JS uses ``frm.trigger("set_pos_data")`` on the client; server-side equivalent is
		``set_missing_values`` + ``calculate_taxes_and_totals`` on the document controller.
		"""
		profile = frappe._dict(pos_profile)
		common_values = {
			"company": profile.company,
			"pos_profile": profile.name,
			"items": [],
			"is_pos": 1,
			"allocate_advances_automatically": 0,
		}

		# In multi-warehouse carts, each row carries its own warehouse.
		# Keep set_warehouse unset in the template.
		common_values["set_warehouse"] = None

		# Doctype-specific payload blocks: frontend gets one clear template based on
		# POS Settings.invoice_type and does not need to infer mixed behavior.
		sales_invoice_values = {
			"is_created_using_pos": 1,
		}
		pos_invoice_values = {
			# Explicit for parity with POSInvoice defaults/flow.
			"is_return": 0,
		}

		for key, value in common_values.items():
			invoice.set(key, value)

		if invoice.doctype == "Sales Invoice":
			for key, value in sales_invoice_values.items():
				invoice.set(key, value)
		elif invoice.doctype == "POS Invoice":
			for key, value in pos_invoice_values.items():
				invoice.set(key, value)

		if hasattr(invoice, "set_missing_values"):
			invoice.set_missing_values(for_validate=bool(invoice.get("is_return")))
		if hasattr(invoice, "calculate_taxes_and_totals"):
			invoice.calculate_taxes_and_totals()

		return invoice

	def boot_pos(self, pos_profile: str):
		"""
		Собирает все необходимые данные для инициализации POS-приложения (SPA) за один запрос.
		"""
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

		# POS Payment Method: default / allow_in_returns. type (Cash|Bank) — в Mode of Payment, один JOIN.
		pay_by_mop = {
			row["mode_of_payment"]: row for row in SessionService()._fetch_payment_methods([pos_profile])
		}

		balance_details_out = []
		for row in opening.balance_details or []:
			pr = pay_by_mop.get(row.mode_of_payment) or {}
			balance_details_out.append(
				{
					"mode_of_payment": row.mode_of_payment,
					"opening_amount": row.opening_amount,
					"default": bool(pr.get("default", 0)),
					"allow_in_returns": bool(pr.get("allow_in_returns", 0)),
					"mop_type": pr.get("mop_type") or "Cash",
				}
			)

		stock = StockService()
		warehouses = stock.get_warehouses(profile_doc.company)

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

		item_groups_tree = self._build_item_group_tree(pos_profile)

		return {
			"opening_voucher": {
				"name": opening.name,
				"period_start_date": opening.period_start_date,
				"user_full_name": frappe.db.get_value("User", opening.user, "full_name") or opening.user,
				"balance_details": balance_details_out,
			},
			"pos_profile": pos_out,
			"item_groups": {
				"tree": item_groups_tree,
			},
			"warehouses": warehouses,
			"checklists": checklists_payload,
		}

	def _build_item_group_tree(self, pos_profile: str) -> list[dict]:
		"""
		Использует встроенную логику ERPNext для получения разрешенных групп
		и строит из них вложенное JSON-дерево для фронтенда.
		"""
		from erpnext.selling.page.point_of_sale.point_of_sale import get_item_groups

		# Получаем плоский список разрешенных групп из POS Profile (нативная функция)
		allowed_groups = get_item_groups(pos_profile)

		filters = {}
		if allowed_groups:
			filters["name"] = ["in", allowed_groups]

		# Запрашиваем информацию о группах
		groups = frappe.get_all(
			"Item Group",
			filters=filters,
			fields=["name", "item_group_name", "is_group", "parent_item_group"],
			order_by="lft asc",
		)

		# Строим словарь узлов
		by_name = {
			g.name: {
				"name": g.name,
				"label": g.item_group_name,
				"is_group": bool(g.is_group),
				"is_directory": bool(g.is_group),
				"children": [],
			}
			for g in groups
		}

		roots = []
		# Связываем дочерние элементы с родителями
		for g in groups:
			node = by_name[g.name]
			parent = g.parent_item_group
			if parent and parent in by_name:
				by_name[parent]["children"].append(node)
			else:
				roots.append(node)

		# Удаляем пустые массивы children для чистоты JSON
		def clean_empty(nodes):
			for n in nodes:
				if not n["children"]:
					del n["children"]
				else:
					clean_empty(n["children"])

		clean_empty(roots)
		return roots
