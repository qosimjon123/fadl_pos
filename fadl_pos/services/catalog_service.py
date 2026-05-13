from collections import defaultdict

import frappe
from frappe import _

from fadl_pos.services._base import BaseService
from fadl_pos.services.stock_service import StockService
from fadl_pos.serializers.catalog import CatalogResponseSerializer

# Native Imports
from erpnext.selling.page.point_of_sale.point_of_sale import (
    get_items as native_get_items,
    search_by_term as native_search_by_term,
    search_for_serial_or_batch_or_barcode_number as native_scan_barcode,
    item_group_query as native_item_group_query,
)
from erpnext.accounts.doctype.pos_invoice.pos_invoice import (
    get_stock_availability as native_get_stock,
)
from frappe.utils.nestedset import get_root_of

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
        elif action == "boot":
            pos_profile = (kwargs.get("pos_profile") or "").strip()
            if not pos_profile:
                frappe.throw(_("pos_profile is required for boot"))
            return self.boot_pos(pos_profile)
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

    def boot_pos(self, pos_profile: str):
        """Initial payload for SPA; mirrors ERPNext Desk POS behaviour where noted.

        Native parity notes (ERPNext):

        - Listing uses ``point_of_sale.get_items``: warehouse + ``hide_unavailable_items`` come
          from POS Profile; when the profile **has no** Item Group rows, SQL applies no whitelist
          (``AND 1=1``)—same as Desk: all Items still respect the **selected** group branch in
          ``get_items`` (``lft``/``rgt`` sub-tree), not "whole DB without group filter".
        - When the profile **has** Item Group rows, ``get_item_groups`` expands each row to all
          descendants (nested set); items must be in that flat set (``item.item_group IN (...)``).
        - User Permissions on Item Group are applied in native ``get_item_groups``; this boot
          builds trees from data the user can read—tighten further if you replicate permission SQL.
        - Item Group "folder" flag in ERPNext is ``is_group`` (label *Is Group*). In JSON below
          we expose ``is_directory`` as the same boolean for UI trees.
        - **Items** should use **leaf** groups (``is_group == 0``); the Item Group doctype says
          *Only leaf nodes are allowed in transaction*. Parent groups are containers for the tree
          and POS filtering, not the normal place to hang stock items.
        - Item groups marked ``disabled`` (Custom Field / column ``disabled`` on **Item Group**)
          are omitted; any descendant under a disabled group is omitted (nested-set rule).

        Example response shape (illustrative)::

            {
                "opening_voucher": {
                    "name": "POS-OPE-2026-00001",
                    "period_start_date": "...",
                    "user": "user@example.com",
                    "user_full_name": "...",
                    "balance_details": [
                        {
                            "mode_of_payment": "Cash",
                            "opening_amount": 1000.0,
                            "default": true,
                            "allow_in_returns": true,
                            "mop_type": "Cash"
                        },
                        ...
                    ]
                },
                "pos_profile": {
                    "name": "...",
                    "company": "...",
                    "warehouse": "...",
                    "currency": "...",
                    "selling_price_list": "...",
                    "customer": "...",
                    "hide_images": false,
                    "hide_unavailable_items": false,
                    "auto_add_item_to_cart": false,
                    "validate_stock_on_save": false,
                    "print_receipt_on_order_complete": false,
                    "action_on_new_invoice": "Always Ask",
                    "allow_rate_change": false,
                    "allow_discount_change": false,
                    "allow_partial_payment": false,
                    "set_grand_total_to_default_mop": true,
                    "ignore_pricing_rule": false,
                    "apply_discount_on": "Grand Total",
                    "taxes_and_charges": "Tax on Sales",
                    "tax_category": "",
                },
                "item_groups": {
                    "restriction": "none | profile_whitelist",
                    "allowlist_names": null,
                    "tree": [...]
                },
                "warehouses": [
                    {"name": "Stores - FT", "warehouse_name": "Stores - FT"},
                    ...
                ]
            }

        ``warehouses`` — from :meth:`fadl_pos.services.stock_service.StockService.get_warehouses`
        (active leaf warehouses of the profile company).

        ``opening_voucher.balance_details`` rows are enriched from POS Profile payments
        (``default``, ``allow_in_returns``) and ``Mode of Payment.type`` as ``mop_type``.
        Invoice save still re-validates on the server.
        """
        if not pos_profile:
            frappe.throw(_("Invalid POS Profile"))

        try:
            profile = frappe.get_doc("POS Profile", pos_profile)
        except frappe.DoesNotExistError:
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
        pay_by_mop = {row.mode_of_payment: row for row in (profile.payments or [])}

        mop_keys = [r.mode_of_payment for r in (opening.balance_details or []) if r.mode_of_payment]
        mop_types: dict[str, str | None] = {}
        if mop_keys:
            uniq = list(dict.fromkeys(mop_keys))
            for mop in frappe.get_all(
                "Mode of Payment",
                filters={"name": ["in", uniq]},
                fields=["name", "type"],
            ):
                mop_types[mop.name] = mop.get("type")

        balance_details_out = []
        for row in opening.balance_details or []:
            pr = pay_by_mop.get(row.mode_of_payment)
            balance_details_out.append(
                {
                    "mode_of_payment": row.mode_of_payment,
                    "opening_amount": row.opening_amount,
                    "default": bool(getattr(pr, "default", 0)) if pr else False,
                    "allow_in_returns": bool(getattr(pr, "allow_in_returns", 0)) if pr else False,
                    "mop_type": mop_types.get(row.mode_of_payment) or "Cash",
                }
            )

        allow_names = self._pos_profile_item_group_allowlist(profile)

        stock = StockService()
        warehouses = stock.get_warehouses(pos_profile)

        pos_out = {
            "name": profile.name,
            "company": profile.company,
            "warehouse": profile.warehouse,
            "currency": profile.currency,
            "selling_price_list": profile.selling_price_list,
            "customer": profile.customer,
            "hide_images": bool(profile.hide_images),
            "hide_unavailable_items": bool(profile.hide_unavailable_items),
            "auto_add_item_to_cart": bool(profile.auto_add_item_to_cart),
            "validate_stock_on_save": bool(profile.validate_stock_on_save),
            "print_receipt_on_order_complete": bool(profile.print_receipt_on_order_complete),
            "action_on_new_invoice": profile.action_on_new_invoice,
            "allow_rate_change": bool(profile.allow_rate_change),
            "allow_discount_change": bool(profile.allow_discount_change),
            "allow_partial_payment": bool(profile.allow_partial_payment),
            "set_grand_total_to_default_mop": bool(profile.set_grand_total_to_default_mop),
            "ignore_pricing_rule": bool(profile.ignore_pricing_rule),
            "apply_discount_on": profile.apply_discount_on,
            "taxes_and_charges": profile.taxes_and_charges or None,
            "tax_category": profile.tax_category or None,
        }

        return {
            "opening_voucher": {
                "name": opening.name,
                "period_start_date": opening.period_start_date,
                "user": opening.user,
                "user_full_name": frappe.db.get_value(
                    "User", opening.user, "full_name"
                )
                or opening.user,
                "balance_details": balance_details_out,
            },
            "pos_profile": pos_out,
            "item_groups": {
                "restriction": "none" if allow_names is None else "profile_whitelist",
                "allowlist_names": sorted(allow_names) if allow_names is not None else None,
                "tree": self._item_group_boot_tree(profile, allow_names),
            },
            "warehouses": warehouses,
        }

    @staticmethod
    def _item_group_disabled_supported() -> bool:
        """If False, ERPNext vanilla Item Group is used (no active/inactive semantics here)."""
        return frappe.db.has_column("Item Group", "disabled")

    @staticmethod
    def _item_group_sql_active_fragment(table_alias: str) -> str:
        """Drop disabled nodes and every descendant under a disabled ancestor (nested set)."""
        if not CatalogService._item_group_disabled_supported():
            return ""
        ta = table_alias.strip()
        return f"""
AND COALESCE({ta}.disabled, 0) = 0
AND NOT EXISTS (
    SELECT 1 FROM `tabItem Group` anc
    WHERE COALESCE(anc.disabled, 0) = 1
    AND anc.lft < {ta}.lft AND {ta}.rgt < anc.rgt
)"""

    def _item_group_filter_active_nodes(self, names: set[str]) -> set[str]:
        if not names or not self._item_group_disabled_supported():
            return set(names)
        out: set[str] = set()
        names_list = list(names)
        frag = CatalogService._item_group_sql_active_fragment("ig")
        chunk_size = 400
        for i in range(0, len(names_list), chunk_size):
            chunk = names_list[i : i + chunk_size]
            ph = ", ".join(["%s"] * len(chunk))
            rows = frappe.db.sql(
                f"SELECT ig.name FROM `tabItem Group` ig WHERE ig.name IN ({ph}) {frag}",
                chunk,
            )
            out.update(row[0] for row in rows)
        return out

    @staticmethod
    def _item_group_nested_set_union(root_names: list[str]) -> set[str]:
        """Union of Item Group nested-set subtrees for the given roots (single batched read)."""
        if not root_names:
            return set()

        uniq_roots = list(dict.fromkeys(root_names))
        roots = frappe.get_all(
            "Item Group",
            filters={"name": ["in", uniq_roots]},
            fields=["lft", "rgt"],
        )
        if not roots:
            return set()

        conds = ["(lft >= %s AND rgt <= %s)"] * len(roots)
        params: list = []
        for r in roots:
            params.extend([r.lft, r.rgt])

        rows = frappe.db.sql(
            f"SELECT name FROM `tabItem Group` WHERE {' OR '.join(conds)}",
            params,
        )
        return {r[0] for r in rows}

    def _pos_profile_item_group_allowlist(self, profile) -> set | None:
        """ERPNext POS: empty table ⇒ no whitelist in SQL (`get_item_groups` ⇒ [])."""
        rows = getattr(profile, "item_groups", None) or []
        if not rows:
            return None
        root_names = [r.item_group for r in rows]
        raw = self._item_group_nested_set_union(root_names)
        return self._item_group_filter_active_nodes(raw)

    def _item_group_boot_tree(self, profile, allowlist: set | None) -> list[dict]:
        if allowlist is None:
            root = get_root_of("Item Group")
            if not root:
                return []
            bounds = frappe.db.get_value("Item Group", root, ["lft", "rgt"])
            if not bounds:
                return []
            lft, rgt = bounds
            frag = CatalogService._item_group_sql_active_fragment("ig")
            rows = frappe.db.sql(
                f"""
                SELECT ig.name, ig.item_group_name, ig.is_group, ig.parent_item_group
                FROM `tabItem Group` ig
                WHERE ig.lft >= %s AND ig.rgt <= %s
                {frag}
                ORDER BY ig.lft
                """,
                (lft, rgt),
                as_dict=True,
            )
            by_name, children = self._item_group_link_rows(rows)
            node = self._item_group_boot_node_from_cache(root, by_name, children)
            return [node] if node else []

        if not allowlist:
            return []

        rows = frappe.get_all(
            "Item Group",
            filters={"name": ["in", list(allowlist)]},
            fields=["name", "item_group_name", "is_group", "parent_item_group"],
        )
        by_name, children = self._item_group_link_rows(rows)

        forests: list[dict] = []
        for row in getattr(profile, "item_groups", None) or []:
            if row.item_group in by_name:
                forests.append(
                    self._item_group_boot_node_from_cache(row.item_group, by_name, children)
                )
        return forests

    @staticmethod
    def _item_group_link_rows(rows: list):
        """Build name → row and parent → ordered child names (in-memory tree edges)."""
        by_name: dict[str, dict] = {r["name"]: r for r in rows}

        children_by_parent: dict[str, list[str]] = defaultdict(list)
        for name, r in by_name.items():
            parent = r.get("parent_item_group")
            if not parent or parent not in by_name:
                continue
            children_by_parent[parent].append(name)

        for _parent, cnames in children_by_parent.items():
            cnames.sort(
                key=lambda n: (by_name[n].get("item_group_name") or "").lower()
            )

        return by_name, children_by_parent

    def _item_group_boot_node_from_cache(
        self,
        name: str,
        by_name: dict[str, dict],
        children_by_parent: dict[str, list[str]],
    ) -> dict | None:
        r = by_name.get(name)
        if not r:
            return None
        ig = bool(r.get("is_group"))
        node: dict = {
            "name": name,
            "label": r.get("item_group_name") or name,
            "is_group": ig,
            "is_directory": ig,
        }
        child_names = children_by_parent.get(name, [])
        if child_names:
            children_out = []
            for cname in child_names:
                child = self._item_group_boot_node_from_cache(cname, by_name, children_by_parent)
                if child:
                    children_out.append(child)
            if children_out:
                node["children"] = children_out
        return node


    
    