from typing import Any, Optional, TypedDict

import frappe
from frappe.utils import flt, nowdate
from fadl_pos.meta import CUSTOMER_FIELDS


class CustomerSerializer(TypedDict, total=False):
    name: str
    customer_name: str
    customer_pos_id: Optional[str]
    email_id: Optional[str]
    mobile_no: Optional[str]
    outstanding_balance: float


def _fetch_outstanding_balances(parties: list[str], company: str | None = None) -> dict[str, float]:
    company = company or frappe.defaults.get_user_default("Company")
    if not parties or not company:
        return {}
    from erpnext.accounts.utils import get_currency_precision

    precision = get_currency_precision()
    rows = frappe.db.sql(
        """
        SELECT party,
            sum(round(debit_in_account_currency, %(p)s))
                - sum(round(credit_in_account_currency, %(p)s)) AS balance
        FROM `tabGL Entry`
        WHERE is_cancelled = 0
            AND company = %(company)s
            AND party_type = 'Customer'
            AND party IN %(parties)s
            AND posting_date <= %(date)s
        GROUP BY party
        """,
        {"company": company, "parties": parties, "date": nowdate(), "p": precision},
        as_dict=True,
    )
    return {r.party: flt(r.balance) for r in rows}


def serialize_customer(raw: dict[str, Any], **extra: Any) -> CustomerSerializer:
    return {**{f: raw.get(f) for f in CUSTOMER_FIELDS}, **extra}


def serialize_customers(rows: list[dict[str, Any]]) -> list[CustomerSerializer]:
    parties = [r["name"] for r in rows if r.get("name")]
    balances = _fetch_outstanding_balances(parties)
    return [
        serialize_customer(r, outstanding_balance=balances.get(r["name"], 0.0))
        for r in rows
    ]
