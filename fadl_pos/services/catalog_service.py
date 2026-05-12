import frappe
from frappe import _

from fadl_pos.services._base import BaseService
from fadl_pos.serializers.catalog import CatalogResponseSerializer

# Native Imports
from erpnext.selling.page.point_of_sale.point_of_sale import (
    get_items as native_get_items,
    search_by_term as native_search_by_term,
    search_for_serial_or_batch_or_barcode_number as native_scan_barcode,
    item_group_query as native_item_group_query
)
from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_stock_availability as native_get_stock

class CatalogService(BaseService):
    
    def get(self, action: str, **kwargs) -> CatalogResponseSerializer:
        """
        Unified entry point for catalog actions.
        """
        if action == "items":
            return self.get_items(**kwargs)
        elif action == "search":
            return self.search(**kwargs)
        elif action == "barcode":
            return self.scan_barcode(**kwargs)
        elif action == "groups":
            return self.get_groups(**kwargs)
        elif action == "brands":
            return self.get_brands(**kwargs)
        elif action == "variants":
            return self.get_variants(**kwargs)
        elif action == "details":
            return self.get_details(**kwargs)
        else:
            frappe.throw(_("Invalid action: {0}").format(action))

    def get_items(self, start=0, limit=20, price_list=None, item_group=None, pos_profile=None, search_term=""):
        """
        Native wrapper for listing items.
        """
        result = native_get_items(
            start=start,
            page_length=limit,
            price_list=price_list,
            item_group=item_group,
            pos_profile=pos_profile,
            search_term=search_term
        )
        return result

    def search(self, search_term, warehouse, price_list):
        """
        Native wrapper for searching items.
        """
        return native_search_by_term(search_term, warehouse, price_list)

    def scan_barcode(self, search_value):
        """
        Native wrapper for barcode/serial/batch scan.
        """
        return native_scan_barcode(search_value)

    def get_groups(self, pos_profile=None, txt="", start=0, limit=20):
        """
        Native wrapper for item groups.
        """
        filters = {"pos_profile": pos_profile} if pos_profile else {}
        return native_item_group_query(
            doctype="Item Group",
            txt=txt,
            searchfield="name",
            start=start,
            page_len=limit,
            filters=filters
        )

    def get_brands(self, pos_profile: str):
        """
        Native-only Brand list.
        """
        brands = frappe.get_all(
            "Brand",
            fields=["name"],
            order_by="name asc",
            limit_page_length=0,
        )
        return {"brands": brands}

    def get_variants(self, template_item: str, pos_profile: str):
        """
        Read variants from native Item data and enrich with profile price/stock.
        """
        context = self._get_profile_context(pos_profile)
        variants = frappe.get_all(
            "Item",
            filters={
                "variant_of": template_item,
                "disabled": 0,
                "is_sales_item": 1,
                "is_fixed_asset": 0,
            },
            fields=["name as item_code", "item_name", "stock_uom", "image", "item_group", "brand", "is_stock_item"],
            order_by="name asc",
        )

        for v in variants:
            self._enrich_item(v, context)

        return {"items": variants}

    def get_details(self, item_code: str, pos_profile: str, warehouse: str = None, price_list: str = None):
        """
        Native ERPNext item details for online POS use.
        """
        context = self._get_profile_context(pos_profile)
        if warehouse:
            context["warehouse"] = warehouse
        if price_list:
            context["price_list"] = price_list

        items = frappe.get_all(
            "Item",
            filters={"name": item_code},
            fields=[
                "name as item_code",
                "item_name",
                "description",
                "stock_uom",
                "image",
                "is_stock_item",
                "has_batch_no",
                "has_serial_no",
                "item_group",
                "brand",
                "has_variants",
                "variant_of",
                "max_discount",
            ],
            limit=1,
        )
        item = items[0] if items else None
        if not item:
            frappe.throw(_("Item {0} not found").format(item_code))

        self._enrich_item(item, context)
        item["item_uoms"] = frappe.get_all(
            "UOM Conversion Detail",
            filters={"parent": item_code, "parenttype": "Item"},
            fields=["uom", "conversion_factor"],
            order_by="idx asc",
        )
        item["prices"] = self._get_item_prices(item_code, context.get("price_list"))

        return {"item": item}

    def _get_profile_context(self, pos_profile: str) -> dict:
        if not pos_profile:
            return {}
        profile = frappe.get_cached_doc("POS Profile", pos_profile)
        return {
            "warehouse": profile.get("warehouse"),
            "price_list": profile.get("selling_price_list"),
        }

    def _enrich_item(self, item: dict, context: dict) -> None:
        warehouse = context.get("warehouse")
        if warehouse:
            item["actual_qty"], _, _ = native_get_stock(item.get("item_code"), warehouse)

        price = self._get_default_item_price(item.get("item_code"), context.get("price_list"))
        if price:
            item["price_list_rate"] = price.get("price_list_rate")
            item["currency"] = price.get("currency")
            item["uom"] = price.get("uom") or item.get("stock_uom")

    def _get_default_item_price(self, item_code: str, price_list: str | None):
        prices = self._get_item_prices(item_code, price_list)
        return prices[0] if prices else None

    def _get_item_prices(self, item_code: str, price_list: str | None):
        if not price_list:
            return []
        today = frappe.utils.today()
        prices = frappe.get_all(
            "Item Price",
            filters={
                "item_code": item_code,
                "price_list": price_list,
                "selling": 1,
            },
            fields=["uom", "currency", "price_list_rate", "batch_no", "valid_from", "valid_upto"],
            order_by="valid_from desc",
        )
        return [
            price
            for price in prices
            if (not price.get("valid_from") or str(price.get("valid_from")) <= today)
            and (not price.get("valid_upto") or str(price.get("valid_upto")) >= today)
        ]
