import frappe
from fadl_pos.services.stock_service import StockService

@frappe.whitelist()
def get(action: str, **kwargs):
    """
    Unified stock endpoint.
    Route: /api/method/fadl_pos.api.stock.get
    Params: action (single|batch|warehouses|bundle), item_code, warehouse, etc.
    """
    return StockService().get(action, **kwargs)
