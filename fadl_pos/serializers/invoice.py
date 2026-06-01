from typing import Any, TypedDict


class InvoiceResponseSerializer(TypedDict, total=False):
	status: str
	name: str
	message: str | None
	invoice: dict[str, Any] | None
	valid: bool | None
	errors: list[str] | None
	warnings: list[str] | None
