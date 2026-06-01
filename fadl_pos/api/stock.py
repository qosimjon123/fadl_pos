import frappe

from fadl_pos.api.login.rpc_params import strip_rpc_noise
from fadl_pos.services.stock_service import StockService


@frappe.whitelist()
def get(action: str, **kwargs):
	"""
	Stock availability, warehouses, bundles, serial helpers (ERPNext POS stock helpers).

	**Route:** ``/api/method/fadl_pos.api.stock.get``

	**Input:**

	- ``action`` (str, required): ``single`` | ``batch`` | ``warehouses`` | ``bundle`` |
	  ``auto_serial`` | ``reserved_serials``.
	- ``single``: ``item_code`` (str), ``warehouse`` (str).
	- ``batch``: ``item_codes`` (list or JSON string of codes), ``warehouse`` (str).
	- ``warehouses``: ``pos_profile`` (str).
	- ``bundle``: ``item_code``, ``warehouse``.
	- ``auto_serial``: ``qty``, ``item_code``, ``warehouse``, optional ``batch_nos``
	  — forwards to ``erpnext...serial_no.auto_fetch_serial_number`` (for_doctype POS Invoice).
	- ``reserved_serials``: ``item_code``, ``warehouse`` — ``get_pos_reserved_serial_nos``.

	**Output:**

	- ``single``: ``{"item_code", "warehouse", "actual_qty"}`` (native ``get_stock_availability``).
	- ``batch``: ``{"stocks": [{"item_code", "actual_qty"}, ...]}``.
	- ``warehouses``: ``[{"name", "warehouse_name"}, ...]`` for profile company.
	- ``bundle``: ``{"bundle_availability": float}``.
	- ``auto_serial``: ``{"serial_nos": [...]}``.
	- ``reserved_serials``: ``{"reserved_serial_nos": [...]}``.
	"""
	return StockService().get(action, **strip_rpc_noise(kwargs))


@frappe.whitelist()
def update_warehouse(pos_profile: str, warehouse: str):
	"""
	Update ``POS Profile.warehouse`` after permission and company checks.

	**Route:** ``/api/method/fadl_pos.api.stock.update_warehouse``

	**Input:**

	- ``pos_profile`` (str, required): POS Profile name.
	- ``warehouse`` (str, required): leaf/active warehouse under same company.

	**Output:**

	- Success: ``{"status": True, "message": "<translated>", "warehouse": "<name>"}``.
	- Failure: ``{"status": False, "message": "<reason>"}`` (permissions / company mismatch).
	"""
	return StockService().update_warehouse(pos_profile, warehouse)
