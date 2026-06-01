from typing import Any, TypedDict


class StockResponseSerializer(TypedDict, total=False):
	item_code: str | None
	warehouse: str | None
	actual_qty: float | None
	stocks: list[dict[str, Any]] | None
	warehouses: list[dict[str, Any]] | None
	bundle_availability: float | None
	serial_nos: list[str] | None
	reserved_serial_nos: list[str] | None
	status: bool | None
	message: str | None
