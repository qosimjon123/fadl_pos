import frappe
from erpnext.accounts.doctype.journal_entry.journal_entry import get_default_bank_cash_account


def get_party_account(party_type: str, party: str, company: str) -> str | None:
	try:
		# First try to get from Party Account
		account = frappe.get_cached_value(
			"Party Account",
			{"parenttype": party_type, "parent": party, "company": company},
			"account",
		)

		if not account:
			account = frappe.get_cached_value(
				"Company",
				company,
				("default_receivable_account" if party_type == "Customer" else "default_payable_account"),
			)

		if not account:
			frappe.log_error(
				f"No account found for {party_type} {party} in company {company}",
				"POS Account Error",
			)

		return account
	except Exception as e:
		frappe.log_error(f"Error getting party account: {e!s}")
		return None


def get_bank_cash_account(company: str, mode_of_payment: str, bank_account: str | None = None) -> dict | None:
	bank = get_default_bank_cash_account(
		company, "Bank", mode_of_payment=mode_of_payment, account=bank_account
	)

	if not bank:
		bank = get_default_bank_cash_account(
			company, "Cash", mode_of_payment=mode_of_payment, account=bank_account
		)

	return bank


def set_paid_amount_and_received_amount(
	party_account_currency: str,
	bank: dict,
	outstanding_amount: float,
	payment_type: str,
	bank_amount: float | None,
	conversion_rate: float | None,
):
	paid_amount = received_amount = 0
	if party_account_currency == bank.account_currency:
		paid_amount = received_amount = abs(outstanding_amount)
	elif payment_type == "Receive":
		paid_amount = abs(outstanding_amount)
		if bank_amount:
			received_amount = bank_amount
		else:
			received_amount = paid_amount * conversion_rate

	else:
		received_amount = abs(outstanding_amount)
		if bank_amount:
			paid_amount = bank_amount
		else:
			paid_amount = received_amount * conversion_rate

	return paid_amount, received_amount


def get_mode_of_payment_accounts(company: str, mode_of_payments: str | list) -> dict:
	import json

	if isinstance(mode_of_payments, str):
		mode_of_payments = json.loads(mode_of_payments)

	currency_map = {}
	for mode in mode_of_payments:
		account = get_bank_cash_account(company, mode)
		if account:
			currency_map[mode] = account.get("account_currency")
	return currency_map
