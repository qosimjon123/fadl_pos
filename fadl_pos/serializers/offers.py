from typing import TypedDict, List, Optional, Dict

class PricingRuleSerializer(TypedDict):
    name: str
    title: str
    apply_on: str
    rate_or_discount: str
    discount_percentage: float
    discount_amount: float
    item_code: Optional[str]
    item_group: Optional[str]
    brand: Optional[str]
    priority: int

class CouponCodeSerializer(TypedDict):
    name: str
    coupon_code: str
    pricing_rule: str
    valid_from: Optional[str]
    valid_upto: Optional[str]

class OffersResponseSerializer(TypedDict, total=False):
    offers: List[PricingRuleSerializer]
    coupons: List[CouponCodeSerializer]
    status: str
    message: Optional[str]
