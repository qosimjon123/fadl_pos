import frappe

from fadl_pos.api.login.rpc_params import strip_rpc_noise
from fadl_pos.services.offers_service import OffersService


@frappe.whitelist()
def get(action: str, **kwargs):
	"""
	Pricing rules snapshot and coupon code listing.

	**Route:** ``/api/method/fadl_pos.api.offers.get``

	**Input:**

	- ``action`` (str, required): ``active_offers`` | ``coupons``.
	- ``active_offers``: optional ``pos_profile`` (currently informational; rules filtered by validity dates).
	- ``coupons``: optional ``customer`` (reserved for future narrowing).

	**Output:**

	- ``active_offers``: ``{"offers": [{name, title, apply_on, rate_or_discount, ...}]}``.
	- ``coupons``: ``{"coupons": [{name, coupon_code, pricing_rule, valid_from, valid_upto}, ...]}``.
	"""
	return OffersService().get(action, **strip_rpc_noise(kwargs))


@frappe.whitelist(methods=["POST"])
def apply(invoice_name: str, coupon_code: str | None = None):
	"""
	Re-run pricing rules on a draft invoice by saving the document (native engine).

	**Route:** ``/api/method/fadl_pos.api.offers.apply`` (POST)

	**Input:**

	- ``invoice_name`` (str, required): existing **POS Invoice** or **Sales Invoice** id.
	- ``coupon_code`` (str, optional): sets ``coupon_code`` before save.

	**Output:**

	- ``{"status": "success", "invoice": {<full doc dict after save>}``}.
	"""
	return OffersService().apply_offer(invoice_name, coupon_code)
