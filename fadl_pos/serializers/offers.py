from typing import Any, TypedDict


class OffersResponseSerializer(TypedDict, total=False):
	offers: list[dict[str, Any]]
	coupons: list[dict[str, Any]]
	status: str
	message: str | None
