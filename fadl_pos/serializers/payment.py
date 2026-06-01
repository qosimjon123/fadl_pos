from typing import TypedDict


class CouponSerializer(TypedDict):
	coupon_code: str
	valid: bool
	message: str | None


class PaymentUpdateResponse(TypedDict):
	status: str
	name: str
	paid_amount: float
	outstanding_amount: float
