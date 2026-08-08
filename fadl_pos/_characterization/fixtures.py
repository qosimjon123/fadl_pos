# Copyright (c) 2026, FadlTech team and contributors

"""Deterministic fixture *spec* for xpos → fadl_pos characterization sites.

Pure Python constants / builders — no DB access. Integration tests (or a bench
setup script) should materialize these names on a clean site before running
parity cases.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Stable names used across characterization / parity tests
# ---------------------------------------------------------------------------

COMPANY = "Fadl Char Co"
COMPANY_ABBR = "FCC"
CURRENCY = "USD"
WAREHOUSE = "Stores - FCC"
POS_PROFILE = "Fadl Char POS"
CUSTOMER = "Fadl Char Customer"
PRICE_LIST = "Standard Selling"
COST_CENTER = "Main - FCC"
CASH_MOP = "Cash"
CARD_MOP = "Card"

ITEM_STOCK = "CHAR-ITEM-STOCK"
ITEM_BATCH = "CHAR-ITEM-BATCH"
ITEM_UOM_PARENT = "CHAR-ITEM-CARTON"
ITEM_FREE = "CHAR-ITEM-FREE"
OFFER_PCT = "CHAR-OFFER-10PCT"
COUPON_PROMO = "CHARCOUPON10"
BATCH_NO = "CHAR-BATCH-001"

STOCK_UOM = "Nos"
SALES_UOM = "Carton"
CARTON_CONVERSION = 24.0


# POS Profile flags expected by stock / invoice / offers / payment parity.
# Mix of ERPNext core fields and xpos/fadl_pos custom fields from the migration
# plan (stock_offers_invoice_payment + catalog + session fixtures already in
# fadl_pos).
POS_PROFILE_FLAGS: dict[str, Any] = {
	# Core ERPNext POS Profile
	"warehouse": WAREHOUSE,
	"company": COMPANY,
	"currency": CURRENCY,
	"selling_price_list": PRICE_LIST,
	"update_stock": 1,
	"hide_unavailable_items": 0,
	"allow_partial_payment": 0,
	# Stock guard (planned fadl_pos fixture; present in xpos custom)
	"block_sale_beyond_available_qty": 1,
	# Invoice credit / partial gates (xpos custom; used by invoice tests)
	"allow_credit_sale": 0,
	# Catalog (planned fadl_pos fixture)
	"hide_variants_items": 0,
	"show_template_items": 0,
	# Offers (planned fadl_pos fixture)
	"apply_customer_discount": 1,
	"auto_fetch_coupons_gifts": 1,
	"max_discount_percentage_allowed": 100,
	"print_discount_amount": 0,
	# Delivery (parity matrix still lists delivery RPC; optional on site)
	"use_delivery_charges": 0,
}

# Already shipped fadl_pos custom fields (session / checklist) — document only.
POS_PROFILE_FADL_SESSION_FLAGS: dict[str, str] = {
	"POS Profile User.custom_can_open": "Cashier may open a shift",
	"POS Profile User.custom_can_close": "Cashier may close a shift",
	"POS Payment Method.custom_required_opening_balance": "MOP needs opening amount",
	"POS Profile.custom_checklists": "Checklist section break",
	"POS Profile.custom_opening_checklist": "Opening checklist table",
	"POS Profile.custom_closing_checklists": "Closing checklist table",
}


def company_spec() -> dict[str, Any]:
	return {
		"doctype": "Company",
		"company_name": COMPANY,
		"abbr": COMPANY_ABBR,
		"default_currency": CURRENCY,
		"country": "United States",
	}


def warehouse_spec() -> dict[str, Any]:
	return {
		"doctype": "Warehouse",
		"warehouse_name": "Stores",
		"company": COMPANY,
		# ERPNext names warehouses as "<name> - <abbr>"
		"name": WAREHOUSE,
	}


def pos_profile_spec(*, flags: dict[str, Any] | None = None) -> dict[str, Any]:
	"""Return a POS Profile dict with characterization flags merged in."""
	payload = {
		"doctype": "POS Profile",
		"name": POS_PROFILE,
		"company": COMPANY,
		"warehouse": WAREHOUSE,
		"currency": CURRENCY,
		"selling_price_list": PRICE_LIST,
		"payments": [
			{"mode_of_payment": CASH_MOP, "default": 1},
			{"mode_of_payment": CARD_MOP, "default": 0},
		],
	}
	payload.update(POS_PROFILE_FLAGS)
	if flags:
		payload.update(flags)
	return payload


def stock_item_spec(
	item_code: str = ITEM_STOCK,
	*,
	stock_qty: float = 100.0,
	rate: float = 10.0,
) -> dict[str, Any]:
	return {
		"doctype": "Item",
		"item_code": item_code,
		"item_name": item_code,
		"item_group": "Products",
		"stock_uom": STOCK_UOM,
		"is_stock_item": 1,
		"is_sales_item": 1,
		"valuation_rate": rate,
		"standard_rate": rate,
		"_seed_bin_qty": stock_qty,
		"_seed_warehouse": WAREHOUSE,
	}


def batch_item_spec(*, stock_qty: float = 50.0) -> dict[str, Any]:
	spec = stock_item_spec(ITEM_BATCH, stock_qty=stock_qty, rate=15.0)
	spec["has_batch_no"] = 1
	spec["create_new_batch"] = 1
	spec["_seed_batch_no"] = BATCH_NO
	return spec


def uom_item_spec(*, pieces_on_hand: float = 48.0) -> dict[str, Any]:
	"""Stock item sold in Carton (24 Nos) — exercises UOM conversion guards."""
	spec = stock_item_spec(ITEM_UOM_PARENT, stock_qty=pieces_on_hand, rate=5.0)
	spec["uoms"] = [
		{"uom": STOCK_UOM, "conversion_factor": 1.0},
		{"uom": SALES_UOM, "conversion_factor": CARTON_CONVERSION},
	]
	spec["sales_uom"] = SALES_UOM
	return spec


def offer_spec() -> dict[str, Any]:
	return {
		"doctype": "POS Offer",
		"name": OFFER_PCT,
		"title": "10% Off Characterization",
		"company": COMPANY,
		"pos_profile": POS_PROFILE,
		"warehouse": WAREHOUSE,
		"disabled": 0,
		"auto": 1,
		"apply_on": "Item Code",
		"item": ITEM_STOCK,
		"discount_type": "Discount Percentage",
		"discount_percentage": 10,
		"min_qty": 1,
		"coupon_based": 0,
	}


def coupon_spec() -> dict[str, Any]:
	return {
		"doctype": "POS Coupon",
		"coupon_name": "Char Promo 10",
		"coupon_code": COUPON_PROMO,
		"coupon_type": "Promotional",
		"company": COMPANY,
		"pos_offer": OFFER_PCT,
		"maximum_use": 100,
		"used": 0,
	}


def characterization_manifest() -> dict[str, Any]:
	"""Full checklist of masters a characterization site should provide."""
	return {
		"company": company_spec(),
		"warehouse": warehouse_spec(),
		"pos_profile": pos_profile_spec(),
		"pos_profile_flags": dict(POS_PROFILE_FLAGS),
		"pos_profile_fadl_session_flags": dict(POS_PROFILE_FADL_SESSION_FLAGS),
		"customer": {"doctype": "Customer", "customer_name": CUSTOMER, "customer_type": "Individual"},
		"items": [
			stock_item_spec(),
			batch_item_spec(),
			uom_item_spec(),
			stock_item_spec(ITEM_FREE, stock_qty=20.0, rate=0.0),
		],
		"offers": [offer_spec()],
		"coupons": [coupon_spec()],
		"modes_of_payment": [CASH_MOP, CARD_MOP],
		"notes": (
			"Materialize via IntegrationTestCase / bench console; do not import "
			"frappe here. Stock Settings.allow_negative_stock should stay 0 for "
			"guard baselines."
		),
	}
