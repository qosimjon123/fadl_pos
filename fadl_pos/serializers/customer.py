from typing import Any, Optional, TypedDict

from fadl_pos.meta import CUSTOMER_FIELDS


class CustomerSerializer(TypedDict, total=False):
    name: str
    customer_name: str
    customer_pos_id: Optional[str]
    email_id: Optional[str]
    mobile_no: Optional[str]
    outstanding_balance: float


def serialize_customer(raw: dict[str, Any], **extra: Any) -> CustomerSerializer:
    return {**{f: raw.get(f) for f in CUSTOMER_FIELDS}, **extra}
