from typing import Any, TypedDict


class InvoiceListResponseSerializer(TypedDict):
	invoices: list[dict[str, Any]]
