"""
Item catalog: ERPNext POS search/list/scan wrappers.

SPA boot payload: :class:`fadl_pos.services.bootstrap_service.BootstrapService`.
"""

from collections import defaultdict

import frappe
from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_item_group, get_stock_availability
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups
from erpnext.stock.utils import scan_barcode
from frappe import _
from frappe.query_builder import DocType, Order
from frappe.utils import cint, get_datetime
from frappe.utils.nestedset import get_root_of

from fadl_pos.services._base import BaseService
from fadl_pos.services.bootstrap_service import BootstrapService


class CatalogService(BaseService):
	"""Catalog list/search; delegates ``boot`` to :class:`BootstrapService`."""

	# --- Public API ---

	def get(self, action: str, **kwargs) -> dict:
		"""RPC router: ``items`` | ``boot``."""
		if action == "items":
			return self.get_items(**kwargs)
		if action == "boot":
			pos_profile = (kwargs.get("pos_profile") or "").strip()
			if not pos_profile:
				frappe.throw(_("pos_profile is required for boot"))
			return BootstrapService().boot(pos_profile)
		frappe.throw(_("Invalid action: {0}").format(action))

	def get_items(
		self, start, page_length=15, price_list=None, item_group=None, pos_profile=None, search_term=""
	):
		warehouse, hide_unavailable_items = frappe.db.get_value(
			"POS Profile", pos_profile, ["warehouse", "hide_unavailable_items"]
		)

		result = []

		if search_term:
			result = self._search_by_term(search_term, warehouse, price_list) or []
			self._filter_result_items(result, pos_profile)
			if result:
				return result

		if not frappe.db.exists("Item Group", item_group):
			item_group = get_root_of("Item Group")

		condition = self._get_items_search_condition(search_term)
		condition += self._get_item_group_sql_filter(pos_profile)

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

		if not items_data:
			return {"items": []}

		current_date = frappe.utils.today()
		item_codes = [row.name for row in items_data]
		prices_by_item = self._fetch_item_prices_bulk(item_codes, price_list, current_date)
		uoms_by_item = self._fetch_uom_conversions_bulk(item_codes)

		for item in items_data:
			item.actual_qty, _, _is_negative_stock_allowed = get_stock_availability(item.name, warehouse)

			item_prices = prices_by_item.get(item.name, [])
			item_uom, item_uom_price = self._resolve_item_uom_price(item, item_prices)

			item_conversion_factor = self._conversion_factor_from_map(
				item.name, item_uom, item.stock_uom, uoms_by_item
			)

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
					"uoms": self._build_item_uoms(
						item.stock_uom, uoms_by_item.get(item.name, []), item_prices
					),
				}
			)

		return {"items": result}

	# --- Search (barcode / serial / batch / term) ---

	@staticmethod
	def _scan_barcode(search_value: str) -> dict[str, str | None]:
		return scan_barcode(search_value)

	def _filter_result_items(self, result, pos_profile):
		if result and result.get("items"):
			pos_profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
			pos_item_groups = get_item_group(pos_profile_doc)
			if not pos_item_groups:
				return
			result["items"] = [
				item for item in result.get("items") if item.get("item_group") in pos_item_groups
			]

	def _search_by_term(self, search_term, warehouse, price_list):
		result = self._scan_barcode(search_term) or {}

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

		item_prices_all = self._fetch_item_prices_bulk(
			[item_code], price_list, frappe.utils.today()
		).get(item_code, [])
		uom_rows = [
			{"uom": row.uom, "conversion_factor": row.conversion_factor} for row in item_doc.uoms
		]
		item["uoms"] = self._build_item_uoms(item_doc.stock_uom, uom_rows, item_prices_all)

		return {"items": [item]}

	# --- SQL fragments (items list) ---

	def _get_items_search_condition(self, search_term):
		condition = "("
		condition += """item.name like {search_term}
            or item.item_name like {search_term}""".format(
			search_term=frappe.db.escape("%" + search_term + "%")
		)
		condition += self._add_pos_search_fields(search_term)
		condition += ")"

		return condition

	def _add_pos_search_fields(self, search_term):
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

	def _get_item_group_sql_filter(self, pos_profile):
		cond = "and 1=1"
		item_groups = get_item_groups(pos_profile)
		if item_groups:
			cond = "and item.item_group in (%s)" % (", ".join(["%s"] * len(item_groups)))

		return cond % tuple(item_groups)

	# --- Pricing / UOM ---

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

	def _fetch_uom_conversions_bulk(self, item_codes):
		"""One query for UOM Conversion Detail rows; grouped per item."""
		if not item_codes:
			return {}

		UCD = DocType("UOM Conversion Detail")
		rows = (
			frappe.qb.from_(UCD)
			.select(UCD.parent, UCD.uom, UCD.conversion_factor, UCD.idx)
			.where(UCD.parent.isin(item_codes))
			.orderby(UCD.parent, order=Order.asc)
			.orderby(UCD.idx, order=Order.asc)
		).run(as_dict=True)

		uoms_by_item = defaultdict(list)
		for row in rows:
			uoms_by_item[row.parent].append(
				{"uom": row.uom, "conversion_factor": row.conversion_factor}
			)
		return uoms_by_item

	@staticmethod
	def _conversion_factor_from_map(item_code, uom, stock_uom, uoms_by_item):
		if not uom or uom == stock_uom:
			return 1.0
		for row in uoms_by_item.get(item_code, []):
			if row.get("uom") == uom:
				return row.get("conversion_factor") or 1.0
		return 1.0

	@staticmethod
	def _price_for_uom(uom, stock_uom, item_prices, conversion_factor):
		exact = next((d for d in item_prices if d.get("uom") == uom), None)
		if exact and exact.get("price_list_rate") is not None:
			return exact["price_list_rate"]

		stock_price = next((d for d in item_prices if d.get("uom") == stock_uom), None)
		if stock_price and stock_price.get("price_list_rate") is not None:
			return stock_price["price_list_rate"] * conversion_factor

		return None

	def _build_item_uoms(self, stock_uom, uom_rows, item_prices):
		uoms = []
		stock_cf = 1.0
		uoms.append(
			{
				"uom": stock_uom,
				"conversion_factor": stock_cf,
				"price": self._price_for_uom(stock_uom, stock_uom, item_prices, stock_cf),
			}
		)
		seen = {stock_uom}
		for row in uom_rows:
			uom = row.get("uom")
			if not uom or uom in seen:
				continue
			seen.add(uom)
			cf = row.get("conversion_factor") or 1.0
			uoms.append(
				{
					"uom": uom,
					"conversion_factor": cf,
					"price": self._price_for_uom(uom, stock_uom, item_prices, cf),
				}
			)
		return uoms

	def _resolve_item_uom_price(self, item, item_prices):
		"""
		Pick the default selling UOM and its price for a catalog row.

		Mirrors the native ERPNext ``point_of_sale.get_items`` logic
		(``erpnext/selling/page/point_of_sale/point_of_sale.py`` L228-L256).

		Resolution chain (same as ``get_item_details`` L441-443):

		1. **Base**: ``item_uom = stock_uom``, price = Item Price where uom == stock_uom.
		2. **Sales UOM override**: if ``sales_uom`` is set and differs from ``stock_uom``,
		   switch ``item_uom = sales_uom``.  If an Item Price row exists for ``sales_uom``,
		   use it directly.  Otherwise keep ``stock_uom`` price — the caller will
		   multiply it by ``conversion_factor`` (see ``get_items``, L343-344).
		3. **Fallback**: if *no* Item Price matched either UOM, take the first
		   available row (may have a third UOM like "Box").

		Barcode UOM is handled separately in ``_search_by_term``; it overrides
		``item["uom"]`` before price lookup.

		Args:
			item: row from the items SQL query (has ``stock_uom``, ``sales_uom``).
			item_prices: list of Item Price dicts, pre-sorted by ``valid_from`` desc.

		Returns:
			tuple[str, dict]: ``(resolved_uom, price_row_dict)``.
			``price_row_dict`` can be ``{}`` when no Item Price exists at all.
		"""
		stock_uom_price = next((d for d in item_prices if d.get("uom") == item.stock_uom), {})
		item_uom = item.stock_uom
		item_uom_price = stock_uom_price

		if item.sales_uom and item.sales_uom != item.stock_uom:
			item_uom = item.sales_uom
			sales_uom_price = next((d for d in item_prices if d.get("uom") == item.sales_uom), {})
			if sales_uom_price:
				item_uom_price = sales_uom_price
			# else: keep stock_uom price — caller multiplies by conversion_factor

		if item_prices and not item_uom_price:
			item_uom = item_prices[0].get("uom")
			item_uom_price = item_prices[0]

		return item_uom, item_uom_price
