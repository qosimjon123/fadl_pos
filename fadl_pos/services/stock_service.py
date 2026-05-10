import frappe
from frappe import _
from frappe.utils import flt, cint
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
        elif action == "auto_serial":
            return self.auto_fetch_serial(**kwargs)
        elif action == "reserved_serials":
            return self.get_reserved_serials(**kwargs)
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

    def auto_fetch_serial(self, qty, item_code, warehouse, batch_nos=None):
        """
        Native wrapper: Auto-fetch available serial numbers for an item.
        """
        from erpnext.stock.doctype.serial_no.serial_no import auto_fetch_serial_number
        
        serials = auto_fetch_serial_number(
            qty=cint(qty),
            item_code=item_code,
            warehouse=warehouse,
            batch_nos=batch_nos,
            for_doctype="POS Invoice"
        )
        return {"serial_nos": serials}

    def get_reserved_serials(self, item_code, warehouse):
        """
        Native wrapper: Get serial numbers reserved in other open POS Invoices.
        """
        from erpnext.stock.doctype.serial_no.serial_no import get_pos_reserved_serial_nos
        
        filters = {"item_code": item_code, "warehouse": warehouse}
        serials = get_pos_reserved_serial_nos(filters)
        return {"reserved_serial_nos": serials}


    def update_warehouse(self, pos_profile: str, warehouse: str):
        """
        Update the warehouse for the POS Profile.
        """

        # Check if user has access to this POS Profile
        has_access = frappe.db.exists(
            "POS Profile User",
            {"parent": pos_profile, "user": frappe.session.user}
        )

        if not has_access and not frappe.has_permission("POS Profile", "write"):
            return {
                "status": False,
                "message": _("You don't have permission to update this POS Profile")
            }

        # Get POS Profile to check company
        profile_doc = frappe.get_doc("POS Profile", pos_profile)
        # Validate warehouse exists and is active
        warehouse_doc = frappe.get_doc("Warehouse", warehouse)
        if warehouse_doc.disabled and not warehouse_doc.is_group_warehouse:
            frappe.throw(_("Warehouse {0} is disabled").format(warehouse))

        # Validate warehouse belongs to same company
        if warehouse_doc.company != profile_doc.company:
            return {
                "status": False,
                "message": _(
                    "Warehouse {0} belongs to {1}, but POS Profile belongs to {2}"
                ).format(warehouse, warehouse_doc.company, profile_doc.company)
            }

        # Update the POS Profile
        profile_doc.warehouse = warehouse
        profile_doc.save()

        return {
            "status": True,
            "message": _("Warehouse updated successfully"),
            "warehouse": warehouse
        }


    def get_warehouses(self, pos_profile: str) -> list:
        """
        Get the warehouses for the POS Profile.
        """
        if not pos_profile:
            frappe.throw(_("POS Profile is required to get warehouses."))

        # Get the company from POS Profile
        company = frappe.db.get_value("POS Profile", pos_profile, "company")
        if not company:
            return []
        # Get all active warehouses for the company
        warehouses = frappe.get_list(
            "Warehouse",
            filters={
                "company": company,
                "disabled": 0,
                "is_group": 0
            },
            fields=["name", "warehouse_name"],
            order_by="warehouse_name",
            limit_page_length=0
        )
        # Return warehouses with human-readable names
        return warehouses
