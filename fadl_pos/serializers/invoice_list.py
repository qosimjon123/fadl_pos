from typing import TypedDict, List, Optional

class InvoiceListItemSerializer(TypedDict):
    name: str
    customer: str
    customer_name: str
    grand_total: float
    currency: str
    posting_date: str
    posting_time: str
    status: str
    doctype: str

class InvoiceListResponseSerializer(TypedDict):
    invoices: List[InvoiceListItemSerializer]
