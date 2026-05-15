import frappe
from fadl_pos.api.login.rpc_params import strip_rpc_noise
from fadl_pos.services.customer_service import CustomerService


@frappe.whitelist()
def get(action: str, **kwargs):
	"""
	Read-only customer queries (list, full doc, recent POS transactions).

	**Route:** ``/api/method/fadl_pos.api.customer.get``

	**Input:**

	- ``action`` (str, required): ``list`` | ``details`` | ``recent_transactions``.
	- ``list``: optional ``search_term`` (str), ``limit`` (int, capped).
	- ``details``: ``customer`` (str) — Customer name.
	- ``recent_transactions``: ``customer`` (str) — native merged SI + POS Invoice list.

	**Output:**

	- ``list``: ``{"customers": [{name, customer_name, email_id, mobile_no, ...}]}``.
	- ``details``: ``{"customer": {<Customer doc dict>}}``.
	- ``recent_transactions``: ``{"transactions": [...]}`` from
	  ``erpnext...point_of_sale.get_customer_recent_transactions``.
	"""
	return CustomerService().get(action, **strip_rpc_noise(kwargs))


@frappe.whitelist(methods=["POST"])
def manage(action: str, data: str):
	"""
	Create/update customers or patch Desk POS-style fields via native helper.

	**Route:** ``/api/method/fadl_pos.api.customer.manage`` (POST)

	**Input:**

	- ``action`` (str, required): ``create`` | ``update`` | ``set_info``.
	- ``data`` (str, required): JSON object string.

	``data`` by ``action``:

	- ``create``: Customer fields; ``customer_group`` / ``territory`` default from standard defaults if omitted.
	  Required minimally: naming fields per ERPNext Customer validation (often ``customer_name``).
	- ``update``: must include ``name`` (Customer id); remaining keys applied via ``doc.update``.
	- ``set_info``: ``fieldname`` (e.g. ``email_id``, ``mobile_no``, ``loyalty_program``),
	  ``customer`` (str), ``value`` (str, optional default ``""``) — calls native ``set_customer_info``.

	**Output:**

	- ``create``: ``{"status": "success", "customer": {...}, "message": ...}``.
	- ``update``: ``{"status": "success", "customer": {...}}``.
	- ``set_info``: ``{"status": "success", "message": ...}``.
	"""
	service = CustomerService()
	parsed_data = service._parse_json(data)
	return service.manage(action, parsed_data)
