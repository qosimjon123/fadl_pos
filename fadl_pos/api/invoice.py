import frappe
from fadl_pos.services.invoice_service import InvoiceService


@frappe.whitelist(methods=["POST"])
def sync(action: str, data: str):
	"""
	Draft/submit/cancel POS or Sales invoices and validate cart stock (Desk POS parity where noted).

	**Route:** ``/api/method/fadl_pos.api.invoice.sync`` (POST)

	**Input (form / JSON body):**

	- ``action`` (str, required): one of ``save``, ``submit``, ``return``, ``void``, ``validate``.
	- ``data`` (str, required): JSON object (stringified for Frappe RPC) with action-specific fields.

	``data`` shapes by ``action``:

	- ``save`` / ``submit``: invoice fields for :class:`frappe.model.document.Document` construction
	  or ``name`` + partial fields for update. Doctype is taken from **POS Settings → invoice_type**
	  (``POS Invoice`` or ``Sales Invoice``) when ``name`` is omitted. Typical keys: ``customer``,
	  ``company``, ``items`` (child rows), ``payments``, ``taxes``, ``pos_profile``, etc.
	- ``return``: ``return_against`` (str, required) — submitted **POS Invoice** or **Sales Invoice**;
	  same flow as Desk (blank ``target_doc`` + whitelisted ``make_sales_return``). Optional:
	  ``company``, ``pos_profile``, ``set_warehouse`` to mirror session POS profile / warehouse after
	  mapping. Partial quantities: adjust lines on the returned draft (e.g. ``save``) before ``submit``.
	- ``void``: ``name`` (str, required) — draft deleted; submitted cancelled via ``doc.cancel()``.
	- ``validate``: ``items`` (list, required) — cart rows with at least ``item_code``, ``qty``;
	  ``warehouse`` (str, required). Optional ``price_list`` or ``pos_profile`` (uses profile's selling
	  price list) to add rate warnings vs **Item Price**.

	**Output:** ``dict`` — one of:

	- ``save``: ``{"status": "success", "name": "<invoice>", "invoice": {<full doc dict>}}``
	- ``submit``: ``{"status": "success", "name": "<invoice>", "message": "<translated string>"}``
	- ``return``: ``{"status": "success", "name": "<new invoice>", "invoice": {<full doc dict>}}``
	  (Desk-style ``target_doc`` shell + ``pos_invoice.make_sales_return`` or ``sales_invoice.make_sales_return``).
	- ``void``: ``{"status": "success", "name": "<invoice>", "message": ...}``
	- ``validate``: ``{"valid": bool, "errors": [str, ...], "warnings": [str, ...]}``
	"""
	service = InvoiceService()
	parsed_data = service._parse_json(data)
	return service.sync(action, parsed_data)
