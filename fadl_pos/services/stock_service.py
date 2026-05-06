import frappe
from frappe import _
from frappe.utils import flt

from fadl_pos.services._base import BaseService
from fadl_pos.serializers.stock import StockResponseSerializer

# Native Imports
from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_stock_availability as native_get_stock

class StockService(BaseService):
    
    def get(self, action: str, **kwargs) -> StockResponseSerializer:
        """
        Unified entry point for stock actions.
        """
        if action == "single":
            return self.get_single(**kwargs)
        elif action == "batch":
            return self.get_batch(**kwargs)
        elif action == "warehouses":
            return self.get_warehouses(**kwargs)
        elif action == "bundle":
            return self.get_bundle(**kwargs)
        else:
            frappe.throw(_("Invalid action: {0}").format(action))

    def get_single(self, item_code, warehouse):
        """
        Native: Get stock availability for a single item in a warehouse.
        """
        actual_qty, is_stock_item, is_negative_stock_allowed = native_get_stock(item_code, warehouse)
        return {
            "item_code": item_code,
            "warehouse": warehouse,
            "actual_qty": actual_qty
        }

    def get_batch(self, item_codes, warehouse):
        """
        POS Next Exclusive: Get stock quantities for multiple items at once.
        """
        if isinstance(item_codes, str):
            item_codes = frappe.parse_json(item_codes)
            
        # Implementation similar to POS Next get_stock_quantities
        Bin = frappe.qb.DocType("Bin")
        results = (
            frappe.qb.from_(Bin)
            .select(Bin.item_code, Bin.actual_qty)
            .where(Bin.item_code.isin(item_codes))
            .where(Bin.warehouse == warehouse)
            .run(as_dict=True)
        )
        
        # Ensure all requested items are in the response, default to 0
        res_map = {r["item_code"]: r["actual_qty"] for r in results}
        final_results = [{"item_code": code, "actual_qty": res_map.get(code, 0)} for code in item_codes]
        
        return {"stocks": final_results}

    def get_warehouses(self, item_code, company=None):
        """
        POS Next Exclusive: Get availability across all warehouses for a company.
        """
        # Implementation similar to POS Next get_item_warehouse_availability
        filters = {"item_code": item_code}
        if company:
            filters["company"] = company
            
        warehouses = frappe.get_all(
            "Bin",
            filters=filters,
            fields=["warehouse", "actual_qty", "reserved_qty", "projected_qty"]
        )
        return {"warehouses": warehouses}

    def get_bundle(self, item_code, warehouse):
        """
        POS Next Exclusive: Get availability for a Product Bundle.
        """
        # This calls get_product_bundle_availability pattern
        # Simplified: bundle qty is the minimum available sets based on components
        
        components = frappe.get_all(
            "Product Bundle Item",
            filters={"parent": item_code},
            fields=["item_code", "qty"]
        )
        
        if not components:
            return {"bundle_availability": 0}
            
        availabilities = []
        for comp in components:
            actual_qty, _, _ = native_get_stock(comp.item_code, warehouse)
            availabilities.append(actual_qty / comp.qty)
            
        return {"bundle_availability": min(availabilities) if availabilities else 0}
