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

_RATE_TOLERANCE = 0.01


class ValidationService:
    """Backend validation prior to invoice save (stock and optional price list audit)."""

    @staticmethod
    def _price_list_for_audit(
        price_list: str | None, pos_profile: str | None
    ) -> str | None:
        if price_list:
            return price_list
        if pos_profile:
            return frappe.db.get_value("POS Profile", pos_profile, "selling_price_list")
        return None

    @staticmethod
    def _expected_item_rate(item_code: str, price_list: str) -> float | None:
        """Best-effort list rate from Item Price (validity window vs today)."""
        t = today()
        rows = frappe.get_all(
            "Item Price",
            filters={
                "item_code": item_code,
                "price_list": price_list,
                "selling": 1,
            },
            fields=["price_list_rate", "valid_from", "valid_upto"],
            order_by="valid_from desc",
            limit=20,
        )
        for row in rows:
            vf, vu = row.get("valid_from"), row.get("valid_upto")
            if vf and str(vf) > t:
                continue
            if vu and str(vu) < t:
                continue
            return flt(row.get("price_list_rate"))
        return None

    @staticmethod
    def validate_cart_items(
        items: list,
        warehouse: str,
        price_list: str | None = None,
        pos_profile: str | None = None,
    ) -> dict:
        """
        Stock check via ``get_stock_availability``; optional rate vs Item Price when ``price_list``
        (or profile default list) is known.
        """
        from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_stock_availability

        errors = []
        warnings = []

        if not warehouse:
            errors.append(_("warehouse is required."))
            return {"valid": False, "errors": errors, "warnings": warnings}

        pl = ValidationService._price_list_for_audit(price_list, pos_profile)

        for item in items:
            if not isinstance(item, dict):
                continue
            item_code = item.get("item_code")
            qty = flt(item.get("qty", 0))

            if not item_code:
                errors.append(_("Cart row missing item_code."))
                continue

            availability, is_stock_item, allow_negative = get_stock_availability(item_code, warehouse)
            if is_stock_item and not allow_negative and availability < qty:
                errors.append(
                    _(
                        "Item {0} has insufficient stock ({1} available, {2} requested)"
                    ).format(item_code, availability, qty)
                )

            if pl and "rate" in item and item.get("rate") is not None:
                expected = ValidationService._expected_item_rate(item_code, pl)
                if expected is not None:
                    sent = flt(item.get("rate"))
                    if abs(sent - expected) > _RATE_TOLERANCE:
                        warnings.append(
                            _(
                                "Item {0}: rate {1} does not match price list {2} (expected {3})."
                            ).format(item_code, sent, pl, expected)
                        )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
