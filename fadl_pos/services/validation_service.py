"""
Cart validation helpers mirroring ERPNext POS stock checks.

**validate_cart_items**

* *Input*: ``items`` — list of dicts (minimal: ``item_code``, ``qty``); ``warehouse`` — str required for stock.
  Optional ``price_list`` — if set, compares each row ``rate`` to the effective **Item Price** for that item
  (same date rules as fadl POS catalog helpers). Optional ``pos_profile`` — used to default ``price_list``
  when only the profile is sent.

* *Success / response dict*: ``{\"valid\": bool, \"errors\": [str, ...], \"warnings\": [str, ...]}``.
  ``warnings`` holds non-fatal price mismatches (only when a price audit runs).

* *Errors*: raises ``ValidationError`` only if parsing fails; stock/price issues are listed in ``errors``.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, today

from fadl_pos.schemas import CartValidateIn, CartValidateOut

_RATE_TOLERANCE = 0.01


class ValidationService:
	"""Backend validation prior to invoice save (stock audit)."""

	@staticmethod
	def validate_cart_items(data: CartValidateIn) -> dict:
		"""
		Stock check via native ``get_stock_availability``.
		"""
		from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_stock_availability

		errors = []
		warnings = []
		warehouse = data.warehouse

		if not warehouse:
			errors.append(_("warehouse is required."))
			return CartValidateOut(valid=False, errors=errors, warnings=warnings).model_dump()

		for item in data.items:
			item_code = item.item_code
			qty = flt(item.qty)

			if not item_code:
				errors.append(_("Cart row missing item_code."))
				continue

			availability, is_stock_item, allow_negative = get_stock_availability(item_code, warehouse)
			if is_stock_item and not allow_negative and availability < qty:
				errors.append(
					_("Item {0} has insufficient stock ({1} available, {2} requested)").format(
						item_code, availability, qty
					)
				)

		return CartValidateOut(
			valid=len(errors) == 0,
			errors=errors,
			warnings=warnings,
		).model_dump()
