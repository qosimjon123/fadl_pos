import frappe
from fadl_pos.api.login.rpc_params import strip_rpc_noise
from fadl_pos.services.catalog_service import CatalogService


@frappe.whitelist()
def get(action: str, **kwargs):
	"""
	Item catalog, search, barcode scan, groups, and SPA boot payload (ERPNext POS primitives).

	**Route:** ``/api/method/fadl_pos.api.catalog.get``

	**Input:**

	- ``action`` (str, required): ``items`` | ``search`` | ``barcode`` | ``groups`` | ``brands`` |
	  ``variants`` | ``details`` | ``boot``.
	- Additional kwargs depend on ``action``:

	  - ``items``: ``start`` (int), ``limit`` / ``page_length`` style via service defaults,
	    ``price_list``, ``item_group``, ``pos_profile``, ``search_term``.
	  - ``search``: ``search_term``, ``warehouse``, ``price_list`` — delegates to native ``search_by_term``.
	  - ``barcode``: ``search_value`` — native serial/batch/barcode resolver.
	  - ``groups``: ``pos_profile``, ``txt``, ``start``, ``limit`` — native item group query.
	  - ``brands``: ``pos_profile`` — simple Brand listing from DB.
	  - ``variants``: ``template_item``, ``pos_profile``.
	  - ``details``: ``item_code``, ``pos_profile``, optional ``warehouse``, ``price_list``.
	  - ``boot``: ``pos_profile`` (required) — opening voucher + profile + trees + warehouses.

	Numeric/string coercion follows ``CatalogService`` / Frappe conventions.

	**Output:** ``dict`` or native-return structures:

	- ``items``: native ``erpnext...point_of_sale.get_items`` payload.
	- ``search``: ``{"items": [...]}`` or ``None``.
	- ``barcode``: native scan result shape.
	- ``groups``: list of rows from native ``item_group_query``.
	- ``brands``: ``{"brands": [{"name": ...}, ...]}``.
	- ``variants``: ``{"items": [...]}`` enriched with stock/price from POS profile context.
	- ``details``: ``{"item": {...}}`` including ``item_uoms``, ``prices``.
	- ``boot``: large composite dict (``opening_voucher``, ``pos_profile``, ``item_groups``, ``warehouses``,
	  ``checklists``) — see ``CatalogService.boot_pos``.
	"""
	service = CatalogService()
	return service.get(action, **strip_rpc_noise(kwargs))
