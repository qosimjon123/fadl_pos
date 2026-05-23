"""
Item catalog: native ``point_of_sale`` search/list/scan plus SPA ``boot`` payload.

See :meth:`CatalogService.boot_pos` for the large composite response (opening voucher, profile, item group
trees, warehouses, checklists).
"""
import frappe
from frappe import _

from fadl_pos.services._base import BaseService
from fadl_pos.services.customer_service import CustomerService
from fadl_pos.services.session_service import SessionService
from fadl_pos.services.stock_service import StockService
from fadl_pos.serializers.catalog import CatalogResponseSerializer

from erpnext.selling.page.point_of_sale.point_of_sale import get_items as native_get_items

# Parent fields only — child tables (payments, applicable_for_users, checklists, …) are excluded at ORM level.
_BOOT_POS_PROFILE_FIELDS = (
    "name",
    "company",
    "warehouse",
    "currency",
    "selling_price_list",
    "customer",
    "hide_images",
    "auto_add_item_to_cart",
    "print_receipt_on_order_complete",
    "action_on_new_invoice",
    "allow_rate_change",
    "allow_discount_change",
    "allow_partial_payment",
    "set_grand_total_to_default_mop",
    "ignore_pricing_rule",
    "apply_discount_on",
    "taxes_and_charges",
    "tax_category",
    "letter_head",
    "write_off_account",
    "write_off_cost_center",
    "write_off_limit",
    "account_for_change_amount",
    "disable_rounded_total",
    "print_format",
)

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

    def get_items(self, start=0, limit=15, price_list=None, item_group=None, pos_profile=None, search_term=""):
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







    def boot_pos(self, pos_profile: str):
        """
        Собирает все необходимые данные для инициализации POS-приложения (SPA) за один запрос.
        """
        if not pos_profile:
            frappe.throw(_("Invalid POS Profile"))

        profile_row = frappe.db.get_value(
            "POS Profile",
            {"name": pos_profile, "disabled": 0},
            _BOOT_POS_PROFILE_FIELDS,
            as_dict=True,
        )
        if not profile_row:
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

        pay_rows = frappe.get_all(
            "POS Payment Method",
            filters={"parent": pos_profile, "parenttype": "POS Profile"},
            fields=["mode_of_payment", "default", "allow_in_returns"],
        )
        pay_by_mop = {row["mode_of_payment"]: row for row in pay_rows}
        mop_keys = [r.mode_of_payment for r in (opening.balance_details or []) if r.mode_of_payment]
        mop_types: dict[str, str | None] = {}
        if mop_keys:
            for mop in frappe.get_all(
                "Mode of Payment",
                filters={"name": ["in", list(dict.fromkeys(mop_keys))]},
                fields=["name", "type"],
            ):
                mop_types[mop.name] = mop.get("type")

        balance_details_out = []
        for row in opening.balance_details or []:
            pr = pay_by_mop.get(row.mode_of_payment) or {}
            balance_details_out.append(
                {
                    "mode_of_payment": row.mode_of_payment,
                    "opening_amount": row.opening_amount,
                    "default": bool(pr.get("default", 0)),
                    "allow_in_returns": bool(pr.get("allow_in_returns", 0)),
                    "mop_type": mop_types.get(row.mode_of_payment) or "Cash",
                }
            )

        stock = StockService()
        warehouses = stock.get_warehouses(profile_row.get("company"))

        checklists_map = SessionService()._fetch_checklists([pos_profile])
        checklists_payload = checklists_map.get(pos_profile) or {"opening": [], "closing": []}

        default_customer_doc = None
        if profile_row.get("customer"):
            try:
                default_customer_doc = CustomerService().get_details(profile_row["customer"])["customer"]
            except frappe.DoesNotExistError:
                pass

        pos_out = {
            "name": profile_row["name"],
            "company": profile_row["company"],
            "warehouse": profile_row["warehouse"],
            "currency": profile_row["currency"],
            "selling_price_list": profile_row["selling_price_list"],
            "customer": default_customer_doc,
            "hide_images": bool(profile_row.get("hide_images")),
            "auto_add_item_to_cart": bool(profile_row.get("auto_add_item_to_cart")),
            "print_receipt_on_order_complete": bool(profile_row.get("print_receipt_on_order_complete")),
            "action_on_new_invoice": profile_row.get("action_on_new_invoice"),
            "allow_rate_change": bool(profile_row.get("allow_rate_change")),
            "allow_discount_change": bool(profile_row.get("allow_discount_change")),
            "allow_partial_payment": bool(profile_row.get("allow_partial_payment")),
            "set_grand_total_to_default_mop": bool(profile_row.get("set_grand_total_to_default_mop")),
            "ignore_pricing_rule": bool(profile_row.get("ignore_pricing_rule")),
            "apply_discount_on": profile_row.get("apply_discount_on"),
            "taxes_and_charges": profile_row.get("taxes_and_charges") or None,
            "tax_category": profile_row.get("tax_category") or None,
            "letter_head": profile_row.get("letter_head") or None,
            "write_off_account": profile_row.get("write_off_account") or None,
            "write_off_cost_center": profile_row.get("write_off_cost_center") or None,
            "write_off_limit": profile_row.get("write_off_limit"),
            "account_for_change_amount": profile_row.get("account_for_change_amount") or None,
            "disable_rounded_total": bool(profile_row.get("disable_rounded_total")),
            "print_format": profile_row.get("print_format") or None,
        }

        invoice_type = frappe.db.get_single_value("POS Settings", "invoice_type") or "POS Invoice"
        if invoice_type not in ("POS Invoice", "Sales Invoice"):
            invoice_type = "POS Invoice"

        empty_invoice = frappe.new_doc(invoice_type).as_dict()
        item_groups_tree = self._build_item_group_tree(pos_profile)

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
                "tree": item_groups_tree,
            },
            "warehouses": warehouses,
            "checklists": checklists_payload,
            "invoice_type": invoice_type,
            "empty_invoice": empty_invoice,
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
            order_by="lft asc"
        )

        # Строим словарь узлов
        by_name = {
            g.name: {
                "name": g.name,
                "label": g.item_group_name,
                "is_group": bool(g.is_group),
                "is_directory": bool(g.is_group),
                "children": []
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


    
    