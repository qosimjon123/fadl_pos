import frappe
from fadl_pos.services.catalog_service import CatalogService

@frappe.whitelist()
def get(action: str, **kwargs):
    """
    Unified catalog endpoint.
    Route: /api/method/fadl_pos.api.catalog.get
    Params: action (items|search|barcode|groups|brands|variants|bulk|details), and other filters.
    """
    service = CatalogService()
    # Map incoming strings to appropriate types if needed (BaseService helpers do this too)
    return service.get(action, **kwargs)
