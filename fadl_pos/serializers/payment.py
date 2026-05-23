from typing import TypedDict, Dict, Any, Optional

class CouponSerializer(TypedDict):
    coupon_code: str
    valid: bool
    message: Optional[str]

class PaymentUpdateResponse(TypedDict):
    status: str
    name: str
    paid_amount: float
    outstanding_amount: float
