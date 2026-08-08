import json
from collections import defaultdict
from datetime import timedelta

import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from frappe import _, cstr
from frappe.utils import (
	cint,
	flt,
	getdate,
	money_in_words,
	now_datetime,
	nowdate,
)
from frappe.utils.background_jobs import enqueue

from fadl_pos.utilities import get_invoice_type, is_pos_cashier
from fadl_pos.stock.processing.guards import (
	_apply_item_name_overrides,
	_auto_set_return_batches,
	_collect_stock_errors,
	_deduplicate_free_items,
	_merge_duplicate_taxes,
	_should_block,
	_strip_client_freebies_from_payload,
	validate_stock_on_invoice,
)
from fadl_pos.invoice.processing.utils import (
	_build_invoice_remarks,
	_get_return_validity_settings,
	_resolve_effective_price_list,
	_set_return_valid_upto,
	_validate_return_window,
	get_latest_rate,
)
from fadl_pos.payment.processing.credit import redeeming_customer_credit
from fadl_pos.utilities.processing.helpers import ensure_child_doctype, set_batch_nos_for_bundles

_coupon_row_fields = ("coupon", "coupon_code", "type", "pos_offer", "applied", "customer")
_offer_row_fields = ("offer_name", "offer", "apply_on", "offer_applied", "coupon_based")


def _set_child_table_from_detail(
	doc,
	child_field: str,
	detail_rows: list[dict],
	allowed_keys: tuple[str, ...],
) -> None:
	"""Replace a child table on *doc* with rows built from *detail_rows*.

	Safely ignores unknown keys so the frontend dict doesn't need to match
	exactly.
	"""
	if not detail_rows:
		return

	if not hasattr(doc, child_field):
		return

	doc.set(child_field, [])
	for row_data in detail_rows:
		if not isinstance(row_data, dict):
			continue
		cleaned = {k: row_data[k] for k in allowed_keys if k in row_data}
		if cleaned:
			doc.append(child_field, cleaned)


def _resolve_write_off_limit(pos_profile_doc: dict) -> float | None:
	if not pos_profile_doc:
		return None

	candidate_fields = (
		"write_off_limit",
		"max_write_off_amount",
		"max_write_off_amount",
		"write_off_amount",
		"write_off_limit",
	)

	for fieldname in candidate_fields:
		raw_value = pos_profile_doc.get(fieldname)
		if raw_value in (None, ""):
			continue
		limit = flt(raw_value)
		if limit > 0:
			return limit

	return None


def _apply_write_off_settings(invoice_doc: dict, data: dict):
	enable_write_off = cint(data.get("is_write_off_change"))

	if invoice_doc.is_return or not enable_write_off:
		invoice_doc.write_off_amount = 0
		invoice_doc.base_write_off_amount = 0
		return

	requested_write_off = flt(data.get("write_off_amount") or invoice_doc.get("write_off_amount"))
	if requested_write_off <= 0:
		invoice_doc.write_off_amount = 0
		invoice_doc.base_write_off_amount = 0
		return

	invoice_total = abs(flt(invoice_doc.rounded_total or invoice_doc.grand_total))
	effective_write_off = min(requested_write_off, invoice_total)

	profile_doc = None
	if invoice_doc.pos_profile and frappe.db.exists("POS Profile", invoice_doc.pos_profile):
		profile_doc = frappe.get_cached_doc("POS Profile", invoice_doc.pos_profile)

	write_off_limit = _resolve_write_off_limit(profile_doc)
	if write_off_limit is not None:
		effective_write_off = min(effective_write_off, write_off_limit)

	allow_partial_payment = cint(profile_doc.get("allow_partial_payment")) if profile_doc else 0
	is_credit_sale = cint(data.get("is_credit_sale"))

	settled_by_payments = 0
	for payment in invoice_doc.get("payments") or []:
		settled_by_payments += max(flt(payment.get("amount")), 0)

	settled_by_loyalty = max(flt(invoice_doc.get("loyalty_amount")), 0)
	settled_by_customer_credit = max(flt(data.get("redeemed_customer_credit")), 0)
	remaining_after_write_off = invoice_total - (
		settled_by_payments + settled_by_loyalty + settled_by_customer_credit + effective_write_off
	)

	if (
		write_off_limit is not None
		and requested_write_off > write_off_limit
		and remaining_after_write_off > 0.001
		and not allow_partial_payment
		and not is_credit_sale
	):
		frappe.throw(
			_(
				"Write off amount exceeds the allowed limit ({0}). Please add payment for the remaining amount."
			).format(write_off_limit)
		)

	precision_write_off = invoice_doc.precision("write_off_amount") or 2
	precision_base_write_off = invoice_doc.precision("base_write_off_amount") or 2
	conversion_rate = flt(invoice_doc.get("conversion_rate") or 1)

	invoice_doc.write_off_amount = flt(effective_write_off, precision_write_off)
	invoice_doc.base_write_off_amount = flt(effective_write_off * conversion_rate, precision_base_write_off)


def _safe_date_string(value: str) -> str | None:
	if value in (None, ""):
		return None

	if isinstance(value, str):
		normalized = value.strip()
		if not normalized:
			return None
		if normalized.lower() in {"invalid date", "nan", "none", "null", "undefined"}:
			return None
		value = normalized

	try:
		return str(getdate(value))
	except Exception:
		return None


def _sanitize_delivery_dates(payload: dict):
	if not isinstance(payload, dict):
		return

	if "pos_delivery_date" in payload:
		payload["pos_delivery_date"] = _safe_date_string(payload.get("pos_delivery_date"))

	items = payload.get("items")
	if not isinstance(items, list):
		return

	for item in items:
		if isinstance(item, dict) and "delivery_date" in item:
			item["delivery_date"] = _safe_date_string(item.get("delivery_date"))


def update_invoice(data: str) -> dict:
	currency_cache = {}
	data = json.loads(data)
	_sanitize_delivery_dates(data)
	_strip_client_freebies_from_payload(data)

	# Extract coupon/offer detail rows before doc creation – the frontend
	# sends ``coupons`` and ``offers`` as JSON-encoded name lists (strings)
	# which Frappe cannot process as child-table data.  The actual row data
	# arrives in ``coupons_detail`` / ``offers_detail`` instead.
	coupons_detail = data.pop("coupons_detail", None) or []
	data.pop("coupons", None)
	offers_detail = data.pop("offers_detail", None) or []
	data.pop("offers", None)

	pos_profile = data.get("pos_profile")
	doctype = get_invoice_type()

	data.setdefault("doctype", doctype)

	return_validity_enabled, default_validity_days = _get_return_validity_settings(pos_profile)

	if data.get("name"):
		invoice_doc = frappe.get_doc(doctype, data.get("name"))
		invoice_doc.update(data)
	else:
		invoice_doc = frappe.get_doc(data)

	# Populate coupons child table from frontend detail rows
	_set_child_table_from_detail(invoice_doc, "coupons", coupons_detail, _coupon_row_fields)
	_set_child_table_from_detail(invoice_doc, "offers", offers_detail, _offer_row_fields)

	if (data.get("is_return") or invoice_doc.is_return) and invoice_doc.get("return_against"):
		from fadl_pos.invoice.processing.returns import validate_return_items

		validation = validate_return_items(
			invoice_doc.return_against,
			[d.as_dict() for d in invoice_doc.items],
			doctype=invoice_doc.doctype,
		)
		if not validation.get("valid"):
			frappe.throw(validation.get("message"))

	_validate_return_window(invoice_doc, doctype, return_validity_enabled)

	customer_name = invoice_doc.get("customer")
	if customer_name and not frappe.db.exists("Customer", customer_name):
		try:
			cust = frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": customer_name,
					"customer_group": "All Customer Groups",
					"territory": "All Territories",
					"customer_type": "Individual",
				}
			)
			cust.flags.ignore_permissions = True
			cust.insert()
			invoice_doc.customer = cust.name
			invoice_doc.customer_name = cust.customer_name
		except Exception as e:
			frappe.log_error(f"Failed to create customer {customer_name}: {e}")

	effective_price_list = _resolve_effective_price_list(
		invoice_doc.get("customer"),
		invoice_doc.get("pos_profile") or pos_profile,
		invoice_doc.get("selling_price_list") or data.get("selling_price_list"),
	)
	if effective_price_list:
		invoice_doc.selling_price_list = effective_price_list

	selected_currency = data.get("currency")
	price_list_currency = data.get("price_list_currency")
	if not price_list_currency and invoice_doc.get("selling_price_list"):
		price_list_currency = frappe.db.get_value("Price List", invoice_doc.selling_price_list, "currency")

	overrides = {d.idx: {"item_name": d.item_name} for d in invoice_doc.items}
	locked_items = {}
	if invoice_doc.is_return:
		for d in invoice_doc.items:
			if d.get("locked_price"):
				locked_items[d.idx] = {
					"rate": d.rate,
					"price_list_rate": d.price_list_rate,
					"discount_percentage": d.discount_percentage,
					"discount_amount": d.discount_amount,
					"is_free_item": d.get("is_free_item"),
				}

	invoice_doc.ignore_pricing_rule = 1
	invoice_doc.flags.ignore_pricing_rule = True

	_deduplicate_free_items(invoice_doc)

	invoice_doc.set_missing_values()
	if effective_price_list:
		invoice_doc.selling_price_list = effective_price_list

	_set_return_valid_upto(invoice_doc, return_validity_enabled, default_validity_days)

	_apply_item_name_overrides(invoice_doc, overrides)

	_merge_duplicate_taxes(invoice_doc)

	if locked_items:
		for item in invoice_doc.items:
			locked = locked_items.get(item.idx)
			if locked:
				item.update(locked)
		invoice_doc.calculate_taxes_and_totals()

	company_currency = (
		frappe.get_cached_value("Company", invoice_doc.company, "default_currency") or invoice_doc.currency
	)

	if selected_currency:
		invoice_doc.currency = selected_currency
	price_list_currency = price_list_currency or company_currency

	conversion_rate = 1
	exchange_rate_date = invoice_doc.posting_date
	if invoice_doc.currency != company_currency:
		conversion_rate, exchange_rate_date = get_latest_rate(
			invoice_doc.currency,
			company_currency,
			cache=currency_cache,
		)
		if not conversion_rate or flt(conversion_rate) <= 0:
			frappe.throw(
				_(
					"Unable to find exchange rate for {0} to {1}. Please create a Currency Exchange record manually"
				).format(invoice_doc.currency, company_currency)
			)

		plc_conversion_rate = 1
		if price_list_currency != invoice_doc.currency:
			plc_conversion_rate, _ignored = get_latest_rate(
				price_list_currency,
				invoice_doc.currency,
				cache=currency_cache,
			)
			if not plc_conversion_rate or flt(plc_conversion_rate) <= 0:
				frappe.throw(
					_(
						"Unable to find exchange rate for {0} to {1}. Please create a Currency Exchange record manually"
					).format(price_list_currency, invoice_doc.currency)
				)

		invoice_doc.conversion_rate = conversion_rate
		invoice_doc.plc_conversion_rate = plc_conversion_rate
		invoice_doc.price_list_currency = price_list_currency

		for item in invoice_doc.items:
			if item.price_list_rate:
				item.base_price_list_rate = flt(
					item.price_list_rate * (conversion_rate / plc_conversion_rate),
					item.precision("base_price_list_rate"),
				)
			if item.rate:
				item.base_rate = flt(item.rate * conversion_rate, item.precision("base_rate"))
			if item.amount:
				item.base_amount = flt(item.amount * conversion_rate, item.precision("base_amount"))

		for payment in invoice_doc.payments:
			payment.base_amount = flt(payment.amount * conversion_rate, payment.precision("base_amount"))

		invoice_doc.base_total = flt(invoice_doc.total * conversion_rate, invoice_doc.precision("base_total"))
		invoice_doc.base_net_total = flt(
			invoice_doc.net_total * conversion_rate,
			invoice_doc.precision("base_net_total"),
		)
		invoice_doc.base_grand_total = flt(
			invoice_doc.grand_total * conversion_rate,
			invoice_doc.precision("base_grand_total"),
		)
		invoice_doc.base_rounded_total = flt(
			invoice_doc.rounded_total * conversion_rate,
			invoice_doc.precision("base_rounded_total"),
		)
		invoice_doc.base_in_words = money_in_words(invoice_doc.base_rounded_total, company_currency)

		data["conversion_rate"] = conversion_rate
		data["plc_conversion_rate"] = plc_conversion_rate
		data["exchange_rate_date"] = exchange_rate_date

	inclusive = frappe.get_cached_value("POS Profile", invoice_doc.pos_profile, "tax_inclusive")
	if invoice_doc.get("taxes"):
		for tax in invoice_doc.taxes:
			if tax.charge_type == "Actual":
				tax.included_in_print_rate = 0
			else:
				tax.included_in_print_rate = 1 if inclusive else 0

	if invoice_doc.is_return:
		for payment in invoice_doc.payments:
			payment.amount = -abs(payment.amount)
			payment.base_amount = -abs(payment.base_amount)

		invoice_doc.paid_amount = flt(sum(p.amount for p in invoice_doc.payments))
		invoice_doc.base_paid_amount = flt(sum(p.base_amount for p in invoice_doc.payments))

	invoice_doc.flags.ignore_permissions = True
	frappe.flags.ignore_account_permission = True
	invoice_doc.docstatus = 0
	invoice_doc.save()

	response = invoice_doc.as_dict()
	response["conversion_rate"] = invoice_doc.conversion_rate
	response["plc_conversion_rate"] = invoice_doc.plc_conversion_rate
	response["exchange_rate_date"] = exchange_rate_date
	return response


def submit_invoice(invoice: str, data: str | dict, submit_in_background: bool = False) -> dict:
	from fadl_pos.invoice.processing.payment import _create_change_payment_entries

	if isinstance(data, str):
		data = json.loads(data)
	if isinstance(invoice, str):
		invoice = json.loads(invoice)

	_sanitize_delivery_dates(invoice)
	submit_in_background = cint(submit_in_background)
	_strip_client_freebies_from_payload(invoice)

	# Extract coupon/offer detail rows – same as update_invoice.
	coupons_detail = invoice.pop("coupons_detail", None) or []
	invoice.pop("coupons", None)
	offers_detail = invoice.pop("offers_detail", None) or []
	invoice.pop("offers", None)

	pos_profile = invoice.get("pos_profile")
	doctype = get_invoice_type()
	invoice_name = invoice.get("name")
	if not invoice_name or not frappe.db.exists(doctype, invoice_name):
		# Re-inject detail rows so update_invoice can process them.
		if coupons_detail:
			invoice["coupons_detail"] = coupons_detail
		if offers_detail:
			invoice["offers_detail"] = offers_detail
		created = update_invoice(json.dumps(invoice))
		invoice_name = created.get("name")
		invoice_doc = frappe.get_doc(doctype, invoice_name)
	else:
		if "modified" in invoice:
			del invoice["modified"]
		invoice_doc = frappe.get_doc(doctype, invoice_name)

		if invoice_doc.docstatus == 1:
			return {"name": invoice_doc.name, "status": invoice_doc.docstatus}
		if invoice_doc.docstatus == 2:
			frappe.throw(_("Invoice {0} has been cancelled and cannot be submitted.").format(invoice_name))

		invoice_doc.update(invoice)

		# Populate coupons/offers child tables
		_set_child_table_from_detail(invoice_doc, "coupons", coupons_detail, _coupon_row_fields)
		_set_child_table_from_detail(invoice_doc, "offers", offers_detail, _offer_row_fields)

	_deduplicate_free_items(invoice_doc)

	if invoice_doc.redeem_loyalty_points and not invoice_doc.loyalty_program:
		invoice_doc.loyalty_program = frappe.db.get_value("Customer", invoice_doc.customer, "loyalty_program")

	if invoice_doc.redeem_loyalty_points and invoice_doc.loyalty_program:
		if not invoice_doc.loyalty_redemption_account:
			invoice_doc.loyalty_redemption_account = frappe.db.get_value(
				"Loyalty Program", invoice_doc.loyalty_program, "expense_account"
			)

		if not invoice_doc.loyalty_redemption_cost_center:
			invoice_doc.loyalty_redemption_cost_center = invoice_doc.cost_center or frappe.db.get_value(
				"POS Profile", pos_profile, "cost_center"
			)

	_apply_item_name_overrides(invoice_doc)
	if invoice.get("pos_delivery_date"):
		invoice_doc.update_stock = 0
	mop_cash_list = [
		i.mode_of_payment
		for i in invoice_doc.payments
		if "cash" in i.mode_of_payment.lower() and i.type == "Cash"
	]
	if len(mop_cash_list) > 0:
		cash_account = get_bank_cash_account(mop_cash_list[0], invoice_doc.company)
	else:
		cash_account = {"account": frappe.get_value("Company", invoice_doc.company, "default_cash_account")}

	invoice_doc.remarks = _build_invoice_remarks(invoice_doc)

	total_cash = 0
	if data.get("redeemed_customer_credit"):
		total_cash = invoice_doc.total - float(data.get("redeemed_customer_credit"))

	is_payment_entry = 0
	if data.get("redeemed_customer_credit"):
		for row in data.get("customer_credit_dict"):
			if row["type"] == "Advance" and row["credit_to_redeem"]:
				advance = frappe.db.get_value(
					"Payment Entry",
					row["credit_origin"],
					["name", "remarks", "unallocated_amount"],
					as_dict=True,
				)

				advance_payment = {
					"reference_type": "Payment Entry",
					"reference_name": advance.get("name"),
					"remarks": advance.get("remarks"),
					"advance_amount": advance.get("unallocated_amount"),
					"allocated_amount": row["credit_to_redeem"],
				}

				advance_row = invoice_doc.append("advances", {})
				advance_row.update(advance_payment)
				child_dt = (
					"POS Invoice Advance" if invoice_doc.doctype == "POS Invoice" else "Sales Invoice Advance"
				)
				ensure_child_doctype(invoice_doc, "advances", child_dt)
				invoice_doc.is_pos = 0
				is_payment_entry = 1

	payments = invoice_doc.payments

	_auto_set_return_batches(invoice_doc)

	set_batch_nos_for_bundles(invoice_doc, "warehouse", throw=True)

	validate_stock_on_invoice(invoice_doc)

	_apply_write_off_settings(invoice_doc, data)

	invoice_doc.flags.ignore_permissions = True
	frappe.flags.ignore_account_permission = True
	invoice_doc.printed = 1
	invoice_doc.save()

	if data.get("due_date"):
		frappe.db.set_value(
			invoice_doc.doctype,
			invoice_doc.name,
			"due_date",
			data.get("due_date"),
			update_modified=False,
		)

	allow_background_submit = frappe.get_value(
		"POS Profile",
		invoice_doc.pos_profile,
		"allow_submissions_in_background_job",
	)

	if submit_in_background and allow_background_submit:
		enqueue(
			method=submit_in_background_job,
			queue="default",
			timeout=3000,
			is_async=True,
			kwargs={
				"invoice": invoice_doc.name,
				"doctype": invoice_doc.doctype,
				"data": data,
				"is_payment_entry": is_payment_entry,
				"total_cash": total_cash,
				"cash_account": cash_account,
				"payments": payments,
			},
		)
	else:
		invoice_doc.submit()

		_create_change_payment_entries(invoice_doc, data, pos_profile, cash_account)
		redeeming_customer_credit(invoice_doc, data, is_payment_entry, total_cash, cash_account, payments)

	return {"name": invoice_doc.name, "status": invoice_doc.docstatus}


def submit_in_background_job(*args, **kwargs):
	from fadl_pos.invoice.processing.payment import _create_change_payment_entries

	invoice = kwargs.get("invoice")
	try:
		doctype = kwargs.get("doctype") or "Sales Invoice"
		data = kwargs.get("data") or {}
		is_payment_entry = kwargs.get("is_payment_entry")
		total_cash = kwargs.get("total_cash")
		cash_account = kwargs.get("cash_account")
		payments = kwargs.get("payments") or []

		invoice_doc = frappe.get_doc(doctype, invoice)

		if invoice_doc.docstatus == 1:
			return

		invoice_doc.flags.ignore_permissions = True
		frappe.flags.ignore_account_permission = True

		validate_stock_on_invoice(invoice_doc)
		if hasattr(invoice_doc, "validate_credit_limit"):
			invoice_doc.validate_credit_limit()

		invoice_doc.remarks = _build_invoice_remarks(invoice_doc)

		_apply_write_off_settings(invoice_doc, data)

		if invoice_doc.redeem_loyalty_points and not invoice_doc.loyalty_program:
			invoice_doc.loyalty_program = frappe.db.get_value(
				"Customer", invoice_doc.customer, "loyalty_program"
			)

		if invoice_doc.redeem_loyalty_points and invoice_doc.loyalty_program:
			if not invoice_doc.loyalty_redemption_account:
				invoice_doc.loyalty_redemption_account = frappe.db.get_value(
					"Loyalty Program", invoice_doc.loyalty_program, "expense_account"
				)

			if not invoice_doc.loyalty_redemption_cost_center:
				invoice_doc.loyalty_redemption_cost_center = invoice_doc.cost_center

		invoice_doc.save()

		invoice_doc.submit()

		_create_change_payment_entries(invoice_doc, data, invoice_doc.pos_profile, cash_account)
		redeeming_customer_credit(invoice_doc, data, is_payment_entry, total_cash, cash_account, payments)

	except Exception as e:
		frappe.db.rollback()
		error_msg = str(e)
		frappe.log_error(f"POS Background Submission Failed for {invoice}: {error_msg}")
		frappe.publish_realtime(
			"pos_invoice_submit_error",
			{"invoice": invoice, "error": error_msg},
			user=frappe.session.user,
		)


def validate_cart_items(items: list, pos_profile: str | None = None):
	"""Validate cart items for available stock.

	Returns a list of item dicts where requested quantity exceeds availability.
	This can be used on the front-end for pre-submission checks.
	"""

	if isinstance(items, str):
		items = json.loads(items)

	if pos_profile and not frappe.db.exists("POS Profile", pos_profile):
		pos_profile = None

	if not _should_block(pos_profile):
		return []

	errors = _collect_stock_errors(items, pos_profile=pos_profile)
	if not errors:
		return []

	return errors


def enforce_stock_availability(invoice_doc):
	"""
	Block the sale when it would take stock below zero.
	"""

	from fadl_pos.stock.processing.availability import lock_bins_for_update
	from fadl_pos.stock.processing.guards import validate_stock_on_invoice

	if invoice_doc.get("is_return"):
		return

	lock_bins_for_update(
		[
			{"item_code": row.item_code, "warehouse": row.warehouse}
			for row in (invoice_doc.get("items") or []) + (invoice_doc.get("packed_items") or [])
		]
	)
	validate_stock_on_invoice(invoice_doc)


def _get_item_rate_precision():
	"""Return item rate precision from System Settings float_precision, default 3."""
	val = frappe.db.get_default("float_precision")
	try:
		p = cint(val)
		return p if p >= 0 else 3
	except Exception:
		return 3


def _resolve_invoice_posting_date(pos, requested_posting_date=None, current_posting_date=None):
	"""Respect the POS Profile posting-date setting while validating client input."""
	if not cint(pos.get("allow_change_posting_date")):
		return nowdate()

	candidate = requested_posting_date or current_posting_date
	if not candidate:
		return nowdate()

	try:
		return str(getdate(candidate))
	except Exception:
		frappe.throw(_("Posting Date must be a valid date"))


def _mark_xpos_delivery_charges_managed(invoice_doc):
	"""Keep delivery-charge selection under fadl_pos API control for this request."""
	if getattr(invoice_doc, "flags", None) is None:
		invoice_doc.flags = frappe._dict()
	invoice_doc.flags.xpos_skip_auto_delivery_charges = True


def _apply_invoice_delivery_charge_fields(invoice_doc, data: dict):
	"""Apply the delivery-charge selection supplied by the fadl_pos client."""
	_mark_xpos_delivery_charges_managed(invoice_doc)
	selected_charge = data.get("pos_delivery_charges") or None
	invoice_doc.pos_delivery_charges = selected_charge
	invoice_doc.pos_delivery_charges_rate = (
		flt(data.get("pos_delivery_charges_rate", 0)) if selected_charge else 0
	)


def _apply_invoice_loyalty_fields(invoice_doc, data: dict):
	"""Apply loyalty redemption fields without trusting the client amount."""
	redeem_points = cint(data.get("loyalty_points", 0))
	redeem_loyalty = cint(data.get("redeem_loyalty_points", 0)) and redeem_points > 0
	invoice_doc.redeem_loyalty_points = 1 if redeem_loyalty else 0
	invoice_doc.loyalty_points = redeem_points if redeem_loyalty else 0
	invoice_doc.loyalty_amount = 0


def _prepare_invoice_totals_for_loyalty_validation(invoice_doc):
	"""Pre-calculate invoice totals before ERPNext validates loyalty redemption."""
	from fadl_pos.invoice.events import apply_tax_inclusive, calc_delivery_charges

	calc_delivery_charges(invoice_doc)
	apply_tax_inclusive(invoice_doc)
	invoice_doc.calculate_taxes_and_totals()


def _resolve_loyalty_paid_amount(invoice_doc) -> float:
	"""Let ERPNext derive the redeemable loyalty amount from the selected points."""
	if not (getattr(invoice_doc, "redeem_loyalty_points", 0) and getattr(invoice_doc, "loyalty_points", 0)):
		invoice_doc.loyalty_amount = 0
		return 0

	from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
		validate_loyalty_points,
	)

	invoice_doc.loyalty_amount = 0
	validate_loyalty_points(invoice_doc, cint(invoice_doc.loyalty_points))
	return round(flt(invoice_doc.loyalty_amount or 0), 2)


def _coerce_amount(value) -> float:
	"""Coerce invoice amounts without depending on request-local Frappe state."""
	try:
		return round(float(value or 0), 2)
	except (TypeError, ValueError):
		return 0.0


def _get_unpaid_balance(invoice_doc) -> float:
	"""Return the unpaid balance remaining on an invoice after applied settlements."""
	outstanding_amount = _coerce_amount(getattr(invoice_doc, "outstanding_amount", 0))
	if outstanding_amount > 0:
		return outstanding_amount

	grand_total = abs(
		_coerce_amount(getattr(invoice_doc, "rounded_total", 0) or getattr(invoice_doc, "grand_total", 0))
	)
	settled_amount = abs(_coerce_amount(getattr(invoice_doc, "paid_amount", 0))) + abs(
		_coerce_amount(getattr(invoice_doc, "write_off_amount", 0))
	)
	return max(0.0, round(grand_total - settled_amount, 2))


def _validate_unpaid_balance_permissions(invoice_doc, pos_profile_doc, data: dict):
	"""Enforce POS Profile permissions before submitting an invoice with a balance due."""
	if cint(getattr(invoice_doc, "is_return", 0)):
		return

	outstanding_amount = _get_unpaid_balance(invoice_doc)
	if outstanding_amount <= 0.009:
		return

	allow_credit_sale = cint(pos_profile_doc.get("allow_credit_sale"))
	allow_partial_payment = cint(pos_profile_doc.get("allow_partial_payment"))
	requested_credit_sale = cint(data.get("is_credit_sale"))
	settled_amount = abs(_coerce_amount(getattr(invoice_doc, "paid_amount", 0))) + abs(
		_coerce_amount(getattr(invoice_doc, "write_off_amount", 0))
	)

	if requested_credit_sale or settled_amount <= 0.009:
		if not allow_credit_sale:
			frappe.throw(_("Credit sale is not allowed for POS Profile {0}.").format(pos_profile_doc.name))
		return

	if not (allow_partial_payment or allow_credit_sale):
		frappe.throw(_("Partial payment is not allowed for POS Profile {0}.").format(pos_profile_doc.name))


def _get_default_pos_payment_mode(pos_profile_doc) -> str:
	"""Return the default mode of payment configured on the POS Profile."""
	payments = getattr(pos_profile_doc, "payments", None) or []
	if payments:
		mode_of_payment = getattr(payments[0], "mode_of_payment", None)
		if mode_of_payment:
			return mode_of_payment
	return "Cash"


def _ensure_pos_invoice_payment_row(invoice_doc, pos_profile_doc, require_payment_row: bool):
	"""Seed a zero-amount payment row so ERPNext accepts POS sale submissions."""
	if not require_payment_row:
		return

	existing_payments = None
	if hasattr(invoice_doc, "get"):
		try:
			existing_payments = invoice_doc.get("payments")
		except Exception:
			existing_payments = None

	if existing_payments is None:
		existing_payments = getattr(invoice_doc, "payments", None)

	if existing_payments:
		return

	invoice_doc.append(
		"payments",
		{
			"mode_of_payment": _get_default_pos_payment_mode(pos_profile_doc),
			"amount": 0,
		},
	)


def find_invoice_by_local_id(local_id: str | None, warehouse: str | None = None) -> tuple[str, str] | None:
	"""Return (doctype, name) of an invoice already created for this client local_id.

	The desktop/offline client assigns every cart a stable ``local_id`` and may
	re-push it after a dropped response. Looking it up here makes invoice creation
	idempotent so a retry returns the original invoice instead of creating a second
	real Sales Invoice (double stock depletion + double revenue).
	"""
	if not local_id:
		return None
	for dt in ("Sales Invoice", "POS Invoice"):
		name = frappe.db.get_value(
			dt, {"xpos_local_id": local_id, "set_warehouse": warehouse, "docstatus": 1}, "name"
		)
		if name:
			return dt, name
	return None


def create_invoice(data: str | dict, local_id: str | None = None):
	"""Create a POS Sales Invoice from cart data.

	Args:
	    data: JSON string (or dict) containing the cart payload.
	    local_id: Stable client-side id used to deduplicate sync retries so the
	        same cart is never committed twice (exactly-once invoice creation).
	"""
	data = json.loads(data) if isinstance(data, str) else data

	local_id = local_id or data.get("local_id")

	warehouse = data.get("warehouse")
	existing = find_invoice_by_local_id(local_id, warehouse)
	if existing:
		dt, name = existing
		return {**_build_invoice_response(frappe.get_doc(dt, name)), "duplicate": True}

	pos_profile = data.get("pos_profile")
	customer = data.get("customer")
	items = data.get("items", [])
	payments = data.get("payments", [])
	pos_opening_entry = data.get("pos_opening_entry")
	is_return = data.get("is_return", 0)
	return_against = data.get("return_against")
	additional_discount_percentage = flt(data.get("additional_discount_percentage", 0))
	discount_amount = flt(data.get("discount_amount", 0))
	submit_in_background = cint(data.get("submit_in_background", 0))

	if not pos_profile:
		frappe.throw(_("POS Profile is required"))
	if not customer:
		frappe.throw(_("Customer is required"))
	if not items:
		frappe.throw(_("At least one item is required"))

	pos = frappe.get_cached_doc("POS Profile", pos_profile)

	doctype = get_invoice_type()

	debit_to = None
	if hasattr(pos, "debit_to") and pos.get("debit_to"):
		debit_to = pos.debit_to
	if not debit_to:
		debit_to = frappe.db.get_value("Company", pos.company, "default_receivable_account")

	invoice_name = data.get("name")
	is_existing_draft = False

	if invoice_name and frappe.db.exists(doctype, invoice_name):
		invoice_doc = frappe.get_doc(doctype, invoice_name)
		if invoice_doc.docstatus != 0:
			frappe.throw(_("Only draft invoices can be updated and submitted"))

		if invoice_doc.get("pos_awaiting_settlement") and not is_pos_cashier(
			frappe.session.user, pos_profile
		):
			frappe.throw(_("Only a cashier can settle this invoice."), frappe.PermissionError)

		is_existing_draft = True
		invoice_doc.set("items", [])
		invoice_doc.set("payments", [])
		invoice_doc.set("taxes", [])
		if hasattr(invoice_doc, "sales_team"):
			invoice_doc.set("sales_team", [])
		if hasattr(invoice_doc, "coupons"):
			invoice_doc.set("coupons", [])
		if hasattr(invoice_doc, "offers"):
			invoice_doc.set("offers", [])
	else:
		invoice_doc = frappe.new_doc(doctype)

	invoice_doc.is_pos = 1
	if local_id:
		invoice_doc.xpos_local_id = local_id
	invoice_doc.pos_profile = pos_profile
	invoice_doc.customer = customer
	invoice_doc.company = pos.company
	invoice_doc.debit_to = debit_to
	if pos.allow_change_posting_date:
		invoice_doc.set_posting_time = 1
		invoice_doc.posting_date = _resolve_invoice_posting_date(
			pos,
			data.get("posting_date"),
			getattr(invoice_doc, "posting_date", None) if is_existing_draft else None,
		)
		invoice_doc.posting_time = now_datetime().strftime("%H:%M:%S")
	else:
		invoice_doc.set_posting_time = 0
		invoice_doc.posting_date = nowdate()
		invoice_doc.posting_time = now_datetime().strftime("%H:%M:%S")

	invoice_doc.set_warehouse = pos.warehouse
	invoice_doc.update_stock = cint(pos.get("update_stock")) or 1
	invoice_doc.currency = (
		data.get("currency")
		or pos.currency
		or frappe.db.get_value("Company", pos.company, "default_currency")
	)
	invoice_doc.selling_price_list = data.get("selling_price_list") or pos.get("selling_price_list")

	if data.get("conversion_rate"):
		invoice_doc.conversion_rate = flt(data["conversion_rate"])
	if data.get("price_list_currency"):
		invoice_doc.price_list_currency = data["price_list_currency"]
	if data.get("plc_conversion_rate"):
		invoice_doc.plc_conversion_rate = flt(data["plc_conversion_rate"])

	invoice_doc.is_return = 1 if is_return else 0
	if is_return:
		invoice_doc.is_return = 1
		if return_against:
			invoice_doc.return_against = return_against
			items = _validate_return_invoice(return_against, customer, items)
		else:
			frappe.throw(_("Return Against invoice is required for returns"))
	else:
		invoice_doc.return_against = None

	if additional_discount_percentage:
		invoice_doc.additional_discount_percentage = additional_discount_percentage
		invoice_doc.apply_discount_on = data.get("apply_discount_on") or "Grand Total"
	elif discount_amount:
		invoice_doc.discount_amount = discount_amount
		invoice_doc.apply_discount_on = data.get("apply_discount_on") or "Grand Total"

	invoice_doc.pos_notes = data.get("pos_notes", "")
	invoice_doc.pos_delivery_date = data.get("pos_delivery_date", None) or None
	if data.get("sales_person", None):
		invoice_doc.append(
			"sales_team",
			{
				"sales_person": data["sales_person"],
				"allocated_percentage": 100,
			},
		)

	_apply_invoice_loyalty_fields(invoice_doc, data)

	if data.get("write_off_amount"):
		invoice_doc.write_off_amount = flt(data["write_off_amount"])
		invoice_doc.write_off_account = data.get("write_off_account") or pos.get("write_off_account")
		invoice_doc.write_off_cost_center = data.get("write_off_cost_center") or pos.get(
			"write_off_cost_center"
		)

	rate_precision = _get_item_rate_precision()

	from fadl_pos.permissions.permission import user_has_pos_permission

	allow_rate_change = user_has_pos_permission("allow_change_price", pos_profile=pos.name)

	for item_data in items:
		item_rate = flt(item_data.get("rate", 0), rate_precision)
		item_qty = flt(item_data.get("qty", 1), 3)

		if not allow_rate_change:
			price_list = pos.get("selling_price_list")
			if price_list:
				price_list_rate = frappe.db.get_value(
					"Item Price",
					{
						"item_code": item_data.get("item_code"),
						"price_list": price_list,
						"selling": 1,
						"uom": item_data.get("uom") or item_data.get("stock_uom"),
					},
					"price_list_rate",
				)
				if price_list_rate is not None and flt(price_list_rate, rate_precision) != item_rate:
					item_rate = flt(price_list_rate, rate_precision)

		item = invoice_doc.append("items", {})
		item.item_code = item_data.get("item_code")
		item.item_name = item_data.get("item_name")
		item.local_item_name = frappe.db.get_value(
			"Item", item_data.get("item_code"), "local_item_name"
		) or item_data.get("item_name")
		item.qty = item_qty
		item.uom = item_data.get("uom") or item_data.get("stock_uom")
		item.warehouse = item_data.get("warehouse") or pos.warehouse

		if is_return:
			item.warehouse = item_data.get("warehouse") or item_data.get("source_warehouse") or item.warehouse
			for fieldname in (
				"sales_invoice_item",
				"pos_invoice_item",
				"sales_order",
				"delivery_note",
				"so_detail",
				"dn_detail",
				"expense_account",
				"pos_invoice",
			):
				if item_data.get(fieldname) is not None:
					try:
						setattr(item, fieldname, item_data.get(fieldname))
					except Exception:
						# Optional return-link metadata; skip fields the doctype does not accept.
						frappe.log_error(
							title="X POS Optional Return Item Field",
							message=f"Could not set {fieldname} on return item {item_data.get('item_code')}",
						)

		disc_pct = flt(item_data.get("discount_percentage", 0), 2)
		disc_amt = flt(item_data.get("discount_amount", 0), 2)

		max_discount = flt(pos.get("max_discount_percentage_allowed", 0))
		if max_discount > 0 and disc_pct > max_discount:
			frappe.throw(
				_("Item {0}: Discount {1}% exceeds maximum allowed {2}%").format(
					item_data.get("item_code"), disc_pct, max_discount
				)
			)

		item.price_list_rate = item_rate
		if disc_pct:
			item.discount_percentage = disc_pct
			item.rate = flt(item_rate * (1.0 - disc_pct / 100.0), rate_precision)
		elif disc_amt:
			item.discount_amount = disc_amt
			item.rate = flt(item_rate - disc_amt, rate_precision)
		else:
			item.rate = item_rate
		if item_data.get("serial_no"):
			item.serial_no = item_data.get("serial_no")
		if item_data.get("batch_no"):
			item.batch_no = item_data.get("batch_no")
		if item_data.get("item_tax_template"):
			item.item_tax_template = item_data.get("item_tax_template")

		if item_data.get("additional_notes"):
			try:
				item.additional_notes = item_data["additional_notes"]
			except Exception:
				# Optional client metadata — continue without blocking the sale.
				frappe.log_error(
					title="X POS Optional Item Notes",
					message=f"Could not set additional_notes on item {item_data.get('item_code')}",
				)
		if item_data.get("delivery_date"):
			try:
				item.delivery_date = item_data["delivery_date"]
			except Exception:
				# Optional client metadata — continue without blocking the sale.
				frappe.log_error(
					title="X POS Optional Item Delivery Date",
					message=f"Could not set delivery_date on item {item_data.get('item_code')}",
				)

	existing_account_heads = set()
	if pos.taxes_and_charges:
		invoice_doc.taxes_and_charges = pos.taxes_and_charges
		tax_template = frappe.get_doc("Sales Taxes and Charges Template", pos.taxes_and_charges)
		for tax in tax_template.taxes:
			invoice_doc.append(
				"taxes",
				{
					"charge_type": tax.charge_type,
					"account_head": tax.account_head,
					"description": tax.description,
					"rate": tax.rate,
					"cost_center": tax.cost_center,
					"included_in_print_rate": tax.included_in_print_rate,
				},
			)
			existing_account_heads.add(tax.account_head)

	from fadl_pos.utilities.processing.helpers import add_taxes_from_tax_template

	for item_row in invoice_doc.items:
		if getattr(item_row, "item_tax_template", None):
			add_taxes_from_tax_template(
				{"item_tax_template": item_row.item_tax_template},
				invoice_doc,
			)

	_apply_invoice_delivery_charge_fields(invoice_doc, data)

	loyalty_paid = 0
	if invoice_doc.redeem_loyalty_points and invoice_doc.loyalty_points:
		_prepare_invoice_totals_for_loyalty_validation(invoice_doc)
		loyalty_paid = _resolve_loyalty_paid_amount(invoice_doc)

	total_payment = 0
	for payment in payments:
		pay_amount = flt(payment.get("amount", 0), 2)
		if pay_amount != 0:
			invoice_doc.append(
				"payments",
				{
					"mode_of_payment": payment.get("mode_of_payment"),
					"amount": pay_amount,
					"account": payment.get("account"),
					"type": payment.get("type"),
				},
			)
			total_payment += pay_amount

	_ensure_pos_invoice_payment_row(invoice_doc, pos, bool(invoice_doc.is_pos and not invoice_doc.is_return))

	if loyalty_paid and hasattr(invoice_doc, "set_paid_amount"):
		_original_set_paid_amount = invoice_doc.set_paid_amount

		def _set_paid_amount_with_loyalty():
			_original_set_paid_amount()
			invoice_doc.paid_amount = flt(invoice_doc.paid_amount + loyalty_paid, 2)
			invoice_doc.base_paid_amount = flt(
				invoice_doc.base_paid_amount + (loyalty_paid * flt(invoice_doc.conversion_rate or 1)),
				2,
			)

		invoice_doc.set_paid_amount = _set_paid_amount_with_loyalty

	if is_return and doctype == "POS Invoice":
		invoice_doc.validate_change_amount = lambda: None
	else:
		invoice_doc.paid_amount = flt(total_payment + loyalty_paid, 2)
		invoice_doc.base_paid_amount = flt(invoice_doc.paid_amount * flt(invoice_doc.conversion_rate or 1), 2)

	change_amount = flt(data.get("change_amount", 0))
	if change_amount > 0:
		invoice_doc.change_amount = change_amount

	if pos_opening_entry:
		invoice_doc.pos_opening_entry = pos_opening_entry

	pos_coupons_data = data.get("coupons_detail") or []
	for coupon_row in pos_coupons_data:
		try:
			invoice_doc.append(
				"coupons",
				{
					"coupon": coupon_row.get("coupon"),
					"coupon_code": coupon_row.get("coupon_code"),
					"type": coupon_row.get("type"),
					"pos_offer": coupon_row.get("pos_offer"),
					"applied": cint(coupon_row.get("applied", 1)),
					"customer": coupon_row.get("customer") or customer,
				},
			)
		except Exception:
			frappe.log_error(
				title="X POS Coupon Apply Failed",
				message=frappe.get_traceback(),
			)
			raise

	pos_offers_data = data.get("offers_detail") or []
	for offer_row in pos_offers_data:
		try:
			invoice_doc.append(
				"offers",
				{
					"offer_name": offer_row.get("offer_name"),
					"offer": offer_row.get("offer"),
					"apply_on": offer_row.get("apply_on"),
					"offer_applied": cint(offer_row.get("offer_applied", 1)),
					"coupon_based": cint(offer_row.get("coupon_based", 0)),
					"coupon": offer_row.get("coupon"),
				},
			)
		except Exception:
			frappe.log_error(
				title="X POS Offer Apply Failed",
				message=frappe.get_traceback(),
			)
			raise

	try:
		enforce_return_validity = cint(pos.get("enable_return_validity"))
		if enforce_return_validity and not is_return:
			return_days = cint(pos.get("return_validity_days")) or 0
			if return_days > 0:
				invoice_doc.return_valid_upto = getdate(nowdate()) + timedelta(days=return_days)
	except Exception:
		# Optional profile metadata — continue without blocking the sale.
		frappe.log_error(
			title="X POS Return Validity",
			message=frappe.get_traceback(),
		)

	try:
		if is_existing_draft:
			invoice_doc.save(ignore_permissions=True)
		else:
			invoice_doc.insert(ignore_permissions=True)
	except frappe.exceptions.UniqueValidationError:
		frappe.db.rollback()
		existing = find_invoice_by_local_id(local_id, warehouse)
		if existing:
			dt, name = existing
			return {**_build_invoice_response(frappe.get_doc(dt, name)), "duplicate": True}
		raise

	enforce_stock_availability(invoice_doc)

	_validate_unpaid_balance_permissions(invoice_doc, pos, data)

	from fadl_pos.integrations.processing import fbr

	client_fbr_number = cstr(data.get("fbr_invoice_number") or "").strip()
	if client_fbr_number:
		fbr.apply_fiscal_number(invoice_doc, client_fbr_number)
		invoice_doc.save(ignore_permissions=True)
	else:
		outcome = fbr.prepare_fiscalization(invoice_doc)
		if outcome.status == "local_required":
			return {
				"status": "fbr_local_required",
				"name": invoice_doc.name,
				"doctype": doctype,
				"fbr_payload": outcome.payload,
				"fbr_local_service_url": outcome.local_service_url,
				"grand_total": invoice_doc.grand_total,
				"customer": invoice_doc.customer,
				"customer_name": invoice_doc.customer_name,
			}
		if outcome.status == "cloud":
			fbr.apply_fiscal_number(invoice_doc, outcome.fbr_invoice_number, outcome.posted_on)
			invoice_doc.save(ignore_permissions=True)

	if submit_in_background:
		enqueue(
			_submit_invoice_job,
			queue="short",
			timeout=300,
			invoice_name=invoice_doc.name,
			doctype=doctype,
		)
		return {
			"name": invoice_doc.name,
			"status": "Queued",
			"grand_total": invoice_doc.grand_total,
			"customer": invoice_doc.customer,
			"customer_name": invoice_doc.customer_name,
		}

	invoice_doc.submit()

	return _build_invoice_response(invoice_doc)


def _submit_invoice_job(invoice_name: str, doctype: str = "Sales Invoice"):
	"""Background job to submit an invoice."""
	user = frappe.session.user
	try:
		doc = frappe.get_doc(doctype, invoice_name)
		enforce_stock_availability(doc)
		doc.submit()
		frappe.db.commit()
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Failed to submit {doctype} {invoice_name}: {e}", "X POS Invoice Submission")
		frappe.publish_realtime(
			"pos_invoice_submit_error",
			{"invoice": invoice_name, "error": str(e)},
			user=user,
		)


def finalize_fiscal_invoice(name: str, fbr_invoice_number: str, doctype: str | None = None):
	"""Stamp a locally-obtained FBR number on a pending draft and submit it.

	Completes the offline-fiscalization handshake started by ``create_invoice`` when
	it returned ``fbr_local_required``: the client fetched the number from the local
	fiscalization service and passes it here to finalize the sale.
	"""
	from fadl_pos.integrations.processing import fbr

	doctype = doctype or get_invoice_type()
	fbr_invoice_number = cstr(fbr_invoice_number or "").strip()
	if not fbr_invoice_number:
		frappe.throw(_("FBR invoice number is required to finalize this invoice."))

	invoice_doc = frappe.get_doc(doctype, name)
	if invoice_doc.docstatus != 0:
		return _build_invoice_response(invoice_doc)

	if invoice_doc.get("pos_profile") and not is_pos_cashier(frappe.session.user, invoice_doc.pos_profile):
		frappe.throw(_("Only a cashier can finalize this invoice."), frappe.PermissionError)

	fbr.apply_fiscal_number(invoice_doc, fbr_invoice_number)
	invoice_doc.save(ignore_permissions=True)
	enforce_stock_availability(invoice_doc)
	invoice_doc.submit()
	return _build_invoice_response(invoice_doc)


def discard_draft_invoice(name: str, doctype: str | None = None) -> dict:
	"""Delete a draft invoice left pending when fiscalization could not complete.

	Used when both the FBR cloud and the local service are unreachable, so the sale
	could not be finalized and the draft should not linger.
	"""
	doctype = doctype or get_invoice_type()
	if not frappe.db.exists(doctype, name):
		return {"deleted": False}

	invoice_doc = frappe.get_doc(doctype, name)
	if invoice_doc.docstatus != 0:
		frappe.throw(_("Only a draft invoice can be discarded."))
	if invoice_doc.get("pos_profile") and not is_pos_cashier(frappe.session.user, invoice_doc.pos_profile):
		frappe.throw(_("Only a cashier can discard this invoice."), frappe.PermissionError)

	frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)
	return {"deleted": True}


def save_draft_invoice(data: str | dict):
	"""Save invoice as draft without submitting.

	If data contains a ``name`` field that matches an existing draft invoice,
	that draft is updated in place rather than creating a new document.
	"""
	data = json.loads(data) if isinstance(data, str) else data

	pos_profile = data.get("pos_profile")
	customer = data.get("customer")
	items = data.get("items", [])
	pos_opening_entry = data.get("pos_opening_entry")
	invoice_name = data.get("name")

	if not pos_profile or not customer or not items:
		frappe.throw(_("POS Profile, Customer, and Items are required"))

	pos = frappe.get_cached_doc("POS Profile", pos_profile)

	doctype = get_invoice_type()

	debit_to = None
	if hasattr(pos, "debit_to") and pos.get("debit_to"):
		debit_to = pos.debit_to
	if not debit_to:
		debit_to = frappe.db.get_value("Company", pos.company, "default_receivable_account")

	is_update = False
	if invoice_name and frappe.db.exists(doctype, invoice_name):
		invoice_doc = frappe.get_doc(doctype, invoice_name)
		if invoice_doc.docstatus != 0:
			frappe.throw(_("Invoice {0} is not a draft and cannot be updated").format(invoice_name))
		is_update = True
		invoice_doc.set("items", [])
		invoice_doc.set("taxes", [])
	else:
		invoice_doc = frappe.new_doc(doctype)

	invoice_doc.is_pos = 1
	invoice_doc.pos_profile = pos_profile
	invoice_doc.customer = customer
	invoice_doc.company = pos.company
	invoice_doc.debit_to = debit_to
	if pos.allow_change_posting_date:
		invoice_doc.set_posting_time = 1
		invoice_doc.posting_date = _resolve_invoice_posting_date(
			pos,
			data.get("posting_date"),
			getattr(invoice_doc, "posting_date", None) if is_update else None,
		)
		invoice_doc.posting_time = now_datetime().strftime("%H:%M:%S")
	else:
		invoice_doc.set_posting_time = 0
		invoice_doc.posting_date = nowdate()
		invoice_doc.posting_time = now_datetime().strftime("%H:%M:%S")
	invoice_doc.set_warehouse = pos.warehouse
	invoice_doc.update_stock = cint(pos.get("update_stock")) or 1
	invoice_doc.currency = (
		data.get("currency")
		or pos.currency
		or frappe.db.get_value("Company", pos.company, "default_currency")
	)
	invoice_doc.selling_price_list = data.get("selling_price_list") or pos.get("selling_price_list")

	if data.get("additional_discount_percentage"):
		invoice_doc.additional_discount_percentage = flt(data["additional_discount_percentage"])
		invoice_doc.apply_discount_on = data.get("apply_discount_on") or "Grand Total"
	elif data.get("discount_amount"):
		invoice_doc.discount_amount = flt(data["discount_amount"])
		invoice_doc.apply_discount_on = data.get("apply_discount_on") or "Grand Total"

	try:
		invoice_doc.pos_notes = data.get("pos_notes") or ""
	except Exception:
		# Optional client metadata — continue without blocking the draft save.
		frappe.log_error(
			title="X POS Optional Draft Notes",
			message=frappe.get_traceback(),
		)

	for item_data in items:
		item = invoice_doc.append("items", {})
		item.item_code = item_data.get("item_code")
		item.item_name = item_data.get("item_name")
		item.qty = flt(item_data.get("qty", 1))
		item.rate = flt(item_data.get("rate", 0))
		item.uom = item_data.get("uom") or item_data.get("stock_uom")
		item.warehouse = item_data.get("warehouse") or pos.warehouse
		if item_data.get("discount_percentage"):
			item.discount_percentage = flt(item_data["discount_percentage"])
		if item_data.get("discount_amount"):
			item.discount_amount = flt(item_data["discount_amount"])
		if item_data.get("serial_no"):
			item.serial_no = item_data["serial_no"]
		if item_data.get("batch_no"):
			item.batch_no = item_data["batch_no"]

	if pos.taxes_and_charges:
		invoice_doc.taxes_and_charges = pos.taxes_and_charges

	payments = data.get("payments", [])
	if payments:
		invoice_doc.set("payments", [])
		for payment in payments:
			pay_amount = flt(payment.get("amount", 0), 2)
			invoice_doc.append(
				"payments",
				{
					"mode_of_payment": payment.get("mode_of_payment"),
					"amount": pay_amount,
					"account": payment.get("account"),
					"type": payment.get("type"),
				},
			)

	_ensure_pos_invoice_payment_row(invoice_doc, pos, doctype == "POS Invoice")

	if pos_opening_entry:
		invoice_doc.pos_opening_entry = pos_opening_entry

	if data.get("pos_awaiting_settlement") and frappe.db.has_column(doctype, "pos_awaiting_settlement"):
		invoice_doc.pos_awaiting_settlement = 1

	_apply_invoice_delivery_charge_fields(invoice_doc, data)

	if is_update:
		invoice_doc.save(ignore_permissions=True)
	else:
		invoice_doc.insert(ignore_permissions=True)

	return {
		"name": invoice_doc.name,
		"grand_total": invoice_doc.grand_total,
		"customer": invoice_doc.customer,
		"customer_name": invoice_doc.customer_name,
	}


def _build_invoice_response(invoice_doc: dict) -> dict:
	"""Build a standard invoice response dict."""
	return {
		"name": invoice_doc.name,
		"grand_total": invoice_doc.grand_total,
		"net_total": invoice_doc.net_total,
		"total_taxes_and_charges": invoice_doc.total_taxes_and_charges,
		"paid_amount": invoice_doc.paid_amount,
		"change_amount": invoice_doc.change_amount,
		"outstanding_amount": getattr(invoice_doc, "outstanding_amount", 0),
		"customer": invoice_doc.customer,
		"customer_name": invoice_doc.customer_name,
		"posting_date": str(invoice_doc.posting_date),
		"status": invoice_doc.status if invoice_doc.docstatus == 1 else "Draft",
		"is_return": invoice_doc.is_return,
		"items": [
			{
				"item_code": i.item_code,
				"item_name": i.item_name,
				"qty": i.qty,
				"rate": i.rate,
				"amount": i.amount,
			}
			for i in invoice_doc.items
		],
	}


def _validate_return_invoice(return_against: str, customer: str, items: str | list) -> list:
	"""Validate return invoice data against the original invoice and attach source row references."""
	doctype = "Sales Invoice"
	if not frappe.db.exists(doctype, return_against):
		doctype = "POS Invoice"
		if not frappe.db.exists(doctype, return_against):
			frappe.throw(_("Original invoice {0} not found").format(return_against))

	original = frappe.get_doc(doctype, return_against)

	if original.customer != customer:
		frappe.throw(
			_("Customer mismatch: Return must be for the same customer ({0}) as the original invoice").format(
				original.customer_name or original.customer
			)
		)

	original_items_by_code = defaultdict(list)
	for original_item in original.items:
		original_items_by_code[original_item.item_code].append(original_item)

	link_field = "sales_invoice_item" if doctype == "Sales Invoice" else "pos_invoice_item"
	child_doctype = "Sales Invoice Item" if doctype == "Sales Invoice" else "POS Invoice Item"
	# nosemgrep: frappe-sql-format-injection — doctype/child_doctype/link_field from hardcoded allowlist, values parameterized
	query = f"""
        SELECT {link_field} AS row_name, COALESCE(SUM(ABS(qty)), 0) AS returned_qty
        FROM `tab{child_doctype}`
        WHERE parent IN (
            SELECT name FROM `tab{doctype}` WHERE return_against = %(return_against)s AND docstatus = 1
        )
            AND IFNULL({link_field}, '') != ''
        GROUP BY {link_field}
        """

	returned_rows = frappe.db.sql(
		query,
		{"return_against": return_against},
		as_dict=True,
	)
	returned_qty_by_row = {row.row_name: flt(row.returned_qty) for row in returned_rows if row.row_name}
	allocated_qty_by_row = defaultdict(float)
	prepared_items = []

	for item in items:
		item_code = item.get("item_code")
		return_qty = abs(flt(item.get("qty", 0)))

		if item_code not in original_items_by_code:
			frappe.throw(_("Item {0} was not in the original invoice {1}").format(item_code, return_against))

		remaining_to_allocate = return_qty
		total_original_qty = sum(flt(source_item.qty) for source_item in original_items_by_code[item_code])
		total_returned = sum(
			returned_qty_by_row.get(source_item.name, 0) for source_item in original_items_by_code[item_code]
		)

		for source_item in original_items_by_code[item_code]:
			already_returned = returned_qty_by_row.get(source_item.name, 0)
			already_allocated = allocated_qty_by_row.get(source_item.name, 0)
			remaining_on_row = flt(source_item.qty) - already_returned - already_allocated

			if remaining_on_row <= 0:
				continue

			allocated_qty = min(remaining_to_allocate, remaining_on_row)
			prepared_item = dict(item)
			prepared_item["qty"] = -allocated_qty
			prepared_item[link_field] = source_item.name
			prepared_item["sales_order"] = source_item.get("sales_order")
			prepared_item["delivery_note"] = source_item.get("delivery_note")
			prepared_item["so_detail"] = source_item.get("so_detail")
			prepared_item["dn_detail"] = source_item.get("dn_detail")
			prepared_item["expense_account"] = source_item.get("expense_account")
			prepared_item["source_warehouse"] = source_item.get("warehouse")
			if doctype == "Sales Invoice":
				prepared_item["pos_invoice"] = source_item.get("pos_invoice")
				prepared_item["pos_invoice_item"] = source_item.get("pos_invoice_item")

			prepared_items.append(prepared_item)
			allocated_qty_by_row[source_item.name] += allocated_qty
			remaining_to_allocate -= allocated_qty

			if remaining_to_allocate <= 0:
				break

		remaining_returnable = total_original_qty - total_returned
		if remaining_to_allocate > 0:
			frappe.throw(
				_(
					"Item {0}: Cannot return {1} units. Only {2} units remaining for return "
					"(Original: {3}, Already returned: {4})"
				).format(
					item_code,
					return_qty,
					remaining_returnable,
					total_original_qty,
					total_returned,
				)
			)

	return prepared_items

