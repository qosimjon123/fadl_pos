from typing import TypedDict, List, Dict, Optional

class InvoiceItemSerializer(TypedDict):
    item_code: str
    qty: float
    rate: float
    uom: str
    warehouse: Optional[str]

class InvoicePaymentSerializer(TypedDict):
    mode_of_payment: str
    amount: float
    account: Optional[str]

class InvoiceSerializer(TypedDict, total=False):
    name: Optional[str]
    customer: str
    pos_profile: str
    company: str
    items: List[InvoiceItemSerializer]
    payments: List[InvoicePaymentSerializer]
    is_pos: int
    docstatus: int

class InvoiceResponseSerializer(TypedDict, total=False):
    status: str
    name: str
    message: Optional[str]
    invoice: Optional[dict]
