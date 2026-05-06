from typing import TypedDict, List, Optional, Dict

class LoyaltyPointSerializer(TypedDict):
    customer: str
    loyalty_program: str
    loyalty_points: int
    redeem_loyalty_points: int

class CouponSerializer(TypedDict):
    coupon_code: str
    valid: bool
    message: Optional[str]

class PaymentUpdateResponse(TypedDict):
    status: str
    name: str
    paid_amount: float
    outstanding_amount: float
