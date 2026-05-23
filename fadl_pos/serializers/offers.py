from typing import TypedDict, List, Dict, Any, Optional

class OffersResponseSerializer(TypedDict, total=False):
    offers: List[Dict[str, Any]]
    coupons: List[Dict[str, Any]]
    status: str
    message: Optional[str]
