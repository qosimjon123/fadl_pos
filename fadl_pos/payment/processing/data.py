import frappe
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import (
	get_outstanding_invoices as get_erpnext_outstanding_invoices,
)
from erpnext.controllers.accounts_controller import (
	get_advance_payment_entries_for_regional,
)
from frappe import _
from frappe.utils import cint, flt, getdate, nowdate

MAX_OUTSTANDING_PAGE_LENGTH = 500


def _coerce_text_filter(value: str, field_label: str) -> str | None:
	if value is None:
		return None
	if isinstance(value, (list, tuple, dict, set)):
		frappe.throw(_("Invalid {0} filter").format(field_label))

	coerced = str(value).strip()
	if not coerced:
		return None
	return coerced


def _coerce_non_negative_int(value, default=0) -> int:
	try:
		parsed = cint(value)
	except Exception:
		return default
	return max(parsed, 0)


def _coerce_bool(value: str | bool | int | float | None, default=False) -> bool:
	if value is None:
		return default

	if isinstance(value, bool):
		return value

	if isinstance(value, (int, float)):
		return bool(value)

	if isinstance(value, str):
		lowered = value.strip().lower()
		if not lowered:
			return default
		if lowered in {"1", "true", "yes", "y", "on", "t"}:
			return True
		if lowered in {"0", "false", "no", "n", "off", "f"}:
			return False
		try:
			return bool(int(lowered))
		except Exception:
			return default

	return default


def get_outstanding_invoices(
	customer: str | None = None,
	company: str | None = None,
	currency: str | None = None,
	pos_profile: str | None = None,
	include_all_currencies: bool = False,
	page_start: int = 0,
	page_length: int | None = None,
):
	"""
	Fetch outstanding invoices with optional multi-currency support.

	Args:
	    include_all_currencies (bool): If True, returns invoices in ALL currencies instead of filtering
	"""
	try:
		customer = _coerce_text_filter(customer, _("Customer"))
		company = _coerce_text_filter(company, _("Company"))
		currency = _coerce_text_filter(currency, _("Currency"))
		pos_profile = _coerce_text_filter(pos_profile, _("POS Profile"))
		include_all_currencies = _coerce_bool(include_all_currencies, default=False)

		if not customer or not company:
			return []

		page_start = _coerce_non_negative_int(page_start, default=0)
		page_length = _coerce_non_negative_int(page_length, default=0)
		if page_length:
			page_length = min(page_length, MAX_OUTSTANDING_PAGE_LENGTH)

		party_account = get_party_account("Customer", customer, company)
		customer_name = frappe.get_cached_value("Customer", customer, "customer_name")

		outstanding_invoices = get_erpnext_outstanding_invoices(
			"Customer",
			customer,
			[party_account],
		)

		sales_invoice_meta = {}
		sales_invoice_names = [
			row.get("voucher_no")
			for row in outstanding_invoices
			if row.get("voucher_type") == "Sales Invoice"
		]
		if sales_invoice_names:
			sales_invoice_meta = {
				row.get("name"): row
				for row in frappe.get_list(
					"Sales Invoice",
					filters={"name": ("in", sales_invoice_names)},
					fields=["name", "pos_profile", "currency", "customer_name"],
				)
			}

		normalized_rows = []
		for invoice in outstanding_invoices:
			outstanding_amount = flt(invoice.get("outstanding_amount"))
			if outstanding_amount <= 0:
				continue

			voucher_type = invoice.get("voucher_type")
			voucher_no = invoice.get("voucher_no")
			meta = sales_invoice_meta.get(voucher_no) if voucher_type == "Sales Invoice" else {}

			row_currency = invoice.get("currency") or (meta or {}).get("currency")
			if currency and not include_all_currencies and row_currency != currency:
				continue

			row_pos_profile = (meta or {}).get("pos_profile")
			if pos_profile and voucher_type == "Sales Invoice" and row_pos_profile != pos_profile:
				continue

			normalized_rows.append(
				frappe._dict(
					{
						"voucher_no": voucher_no,
						"voucher_type": voucher_type,
						"outstanding_amount": outstanding_amount,
						"invoice_amount": flt(invoice.get("invoice_amount")) or outstanding_amount,
						"due_date": invoice.get("due_date") or invoice.get("posting_date"),
						"posting_date": invoice.get("posting_date"),
						"currency": row_currency,
						"pos_profile": row_pos_profile,
						"customer": customer,
						"customer_name": (meta or {}).get("customer_name") or customer_name,
					}
				)
			)

		normalized_rows = sorted(
			normalized_rows,
			key=lambda inv: (
				(getdate(inv.get("posting_date")) if inv.get("posting_date") else getdate(nowdate())),
				inv.get("voucher_no"),
			),
			reverse=True,
		)

		if page_length:
			return normalized_rows[page_start : page_start + page_length]

		return normalized_rows
	except Exception as e:
		frappe.logger().error(f"Error in get_outstanding_invoices: {e!s}")
		return []


def get_unallocated_payments(
	customer: str | None = None,
	company: str | None = None,
	currency: str | None = None,
	mode_of_payment: str | None = None,
	include_all_currencies: bool = False,
):
	customer = _coerce_text_filter(customer, _("Customer"))
	company = _coerce_text_filter(company, _("Company"))
	currency = _coerce_text_filter(currency, _("Currency"))
	mode_of_payment = _coerce_text_filter(mode_of_payment, _("Mode of Payment"))
	include_all_currencies = _coerce_bool(include_all_currencies, default=False)

	if not customer or not company:
		return []

	customer_name = frappe.get_cached_value("Customer", customer, "customer_name")
	party_account = get_party_account("Customer", customer, company)

	filters = {
		"party": customer,
		"company": company,
		"docstatus": 1,
		"party_type": "Customer",
		"payment_type": "Receive",
		"unallocated_amount": [">", 0],
	}
	if currency and not include_all_currencies:
		filters["paid_from_account_currency"] = currency
	if mode_of_payment:
		filters.update({"mode_of_payment": mode_of_payment})
	unallocated_payment = frappe.get_list(
		"Payment Entry",
		filters=filters,
		fields=[
			"name",
			"paid_amount",
			"party_name as customer_name",
			"received_amount",
			"posting_date",
			"unallocated_amount",
			"mode_of_payment",
			"paid_from_account_currency as currency",
			"paid_from as account",
		],
		order_by="posting_date asc",
	)

	if not include_all_currencies and currency and not unallocated_payment:
		fallback_filters = dict(filters)
		fallback_filters.pop("paid_from_account_currency", None)
		unallocated_payment = frappe.get_list(
			"Payment Entry",
			filters=fallback_filters,
			fields=[
				"name",
				"paid_amount",
				"party_name as customer_name",
				"received_amount",
				"posting_date",
				"unallocated_amount",
				"mode_of_payment",
				"paid_from_account_currency as currency",
				"paid_from as account",
			],
			order_by="posting_date asc",
		)
	for payment in unallocated_payment:
		payment["voucher_type"] = "Payment Entry"
		payment["is_credit_note"] = 0

	condition = frappe._dict(
		{
			"company": company,
			"get_payments": True,
		}
	)
	regional_entries = get_advance_payment_entries_for_regional(
		"Customer",
		customer,
		[party_account],
		"Sales Order",
		against_all_orders=True,
		condition=condition,
	)

	existing_keys = {(row.get("voucher_type"), row.get("name")) for row in unallocated_payment}
	for row in regional_entries or []:
		reference_type = row.get("reference_type")
		reference_name = row.get("reference_name")
		amount = flt(row.get("amount"))

		if not reference_type or not reference_name or amount <= 0:
			continue

		key = (reference_type, reference_name)
		if key in existing_keys:
			continue

		mode_of_payment_label = row.get("mode_of_payment")
		if reference_type == "Sales Invoice":
			mode_of_payment_label = _("Credit Note")
		elif reference_type == "Journal Entry":
			mode_of_payment_label = _("Journal Entry")

		unallocated_payment.append(
			{
				"name": reference_name,
				"paid_amount": amount,
				"received_amount": amount,
				"customer_name": customer_name,
				"posting_date": row.get("posting_date"),
				"unallocated_amount": amount,
				"mode_of_payment": mode_of_payment_label,
				"currency": row.get("currency") or currency,
				"voucher_type": reference_type,
				"is_credit_note": 1 if reference_type == "Sales Invoice" else 0,
				"reference_row": row.get("reference_row"),
				"account": row.get("account") or party_account,
				"remarks": row.get("remarks"),
				"cost_center": row.get("cost_center"),
				"exchange_rate": flt(row.get("exchange_rate")) or 1,
				"is_advance": row.get("is_advance"),
			}
		)
		existing_keys.add(key)

	params = {
		"company": company,
		"customer": customer,
		"party_account": party_account,
	}

	query = """
            SELECT
                je.name AS name,
                je.posting_date AS posting_date,
                je.remark AS remarks,
                jea.name AS reference_row,
                jea.account AS account,
                jea.account_currency AS currency,
                (jea.credit_in_account_currency - jea.debit_in_account_currency) AS unallocated_amount,
                jea.cost_center AS cost_center,
                jea.exchange_rate AS exchange_rate,
                jea.is_advance AS is_advance
            FROM `tabJournal Entry` je
            INNER JOIN `tabJournal Entry Account` jea ON jea.parent = je.name
            WHERE je.docstatus = 1
            AND je.company = %(company)s
            AND jea.party_type = 'Customer'
            AND jea.party = %(customer)s
            AND jea.account = %(party_account)s
            AND (jea.reference_type IS NULL OR jea.reference_type = '' OR jea.reference_type = 'Sales Order')
            AND (jea.reference_name IS NULL OR jea.reference_name = '')
            AND (jea.credit_in_account_currency - jea.debit_in_account_currency) > 0
            ORDER BY je.posting_date ASC
        """

	if currency and not include_all_currencies:
		query += " AND jea.account_currency = %(currency)s"
		params["currency"] = currency

	journal_entries = frappe.db.sql(
		query,
		params,
		as_dict=True,
	)

	for journal in journal_entries:
		amount = flt(journal.get("unallocated_amount"))
		if amount <= 0:
			continue

		key = ("Journal Entry", journal.get("name"))
		if key in existing_keys:
			continue

		unallocated_payment.append(
			{
				"name": journal.get("name"),
				"paid_amount": amount,
				"received_amount": amount,
				"customer_name": customer_name,
				"posting_date": journal.get("posting_date"),
				"unallocated_amount": amount,
				"mode_of_payment": _("Journal Entry"),
				"currency": journal.get("currency") or currency,
				"voucher_type": "Journal Entry",
				"is_credit_note": 0,
				"reference_row": journal.get("reference_row"),
				"account": journal.get("account") or party_account,
				"remarks": journal.get("remarks"),
				"cost_center": journal.get("cost_center"),
				"exchange_rate": flt(journal.get("exchange_rate")) or 1,
				"is_advance": journal.get("is_advance"),
			}
		)
		existing_keys.add(key)

	credit_notes = frappe.get_list(
		"Sales Invoice",
		filters={
			"customer": customer,
			"company": company,
			"docstatus": 1,
			"is_return": 1,
			"outstanding_amount": ("<", 0),
		},
		fields=[
			"name",
			"posting_date",
			"customer_name",
			"return_against",
			"outstanding_amount",
			"currency",
			"conversion_rate",
			"remarks",
		],
		order_by="posting_date asc",
	)

	for note in credit_notes:
		outstanding_credit = abs(flt(note.outstanding_amount or 0))
		if not outstanding_credit:
			continue

		unallocated_payment.append(
			{
				"name": note.name,
				"paid_amount": outstanding_credit,
				"received_amount": outstanding_credit,
				"customer_name": note.customer_name,
				"posting_date": note.posting_date,
				"unallocated_amount": outstanding_credit,
				"mode_of_payment": _("Credit Note"),
				"currency": note.currency or currency,
				"voucher_type": "Sales Invoice",
				"is_credit_note": 1,
				"return_against": note.return_against,
				"reference_invoice": note.return_against,
				"conversion_rate": note.conversion_rate,
				"remarks": note.remarks,
			}
		)

	unallocated_payment = sorted(
		unallocated_payment,
		key=lambda pay: (
			(getdate(pay.get("posting_date")) if pay.get("posting_date") else getdate(nowdate())),
			pay.get("name"),
		),
	)

	return unallocated_payment


def get_available_pos_profiles(company: str, currency: str):
	pos_profiles_list = frappe.get_list(
		"POS Profile",
		filters={"disabled": 0, "company": company, "currency": currency},
		page_length=1000,
		pluck="name",
	)
	return pos_profiles_list


def get_unreconciled_entries(
	customer: str,
	company: str,
	currency: str | None = None,
	pos_profile: str | None = None,
	mode_of_payment: str | None = None,
	include_all_currencies: bool = False,
):
	return {
		"invoices": get_outstanding_invoices(
			customer=customer,
			company=company,
			currency=currency,
			pos_profile=pos_profile,
			include_all_currencies=include_all_currencies,
		),
		"payments": get_unallocated_payments(
			customer=customer,
			company=company,
			currency=currency,
			mode_of_payment=mode_of_payment,
			include_all_currencies=include_all_currencies,
		),
	}
