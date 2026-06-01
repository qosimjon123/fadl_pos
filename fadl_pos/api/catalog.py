import frappe

from fadl_pos.api.login.rpc_params import strip_rpc_noise
from fadl_pos.services.catalog_service import CatalogService


@frappe.whitelist()
def get(action: str, **kwargs):
	service = CatalogService()
	return service.get(action, **strip_rpc_noise(kwargs))
