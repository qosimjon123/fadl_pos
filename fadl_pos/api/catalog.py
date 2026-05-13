import frappe
from fadl_pos.services.catalog_service import CatalogService

@frappe.whitelist()
def get(action: str, **kwargs):
    """
    Unified catalog endpoint.
    Route: /api/method/fadl_pos.api.catalog.get
    Params: action (items|search|barcode|groups|brands|variants|details|boot), and other filters.
    For action=boot, pass pos_profile (required): opening voucher, profile settings, item group tree.
    """
    service = CatalogService()
    # Map incoming strings to appropriate types if needed (BaseService helpers do this too)
    return service.get(action, **kwargs)


