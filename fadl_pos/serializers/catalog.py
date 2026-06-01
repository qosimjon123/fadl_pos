from __future__ import annotations

from typing import Any, TypedDict


class CatalogItemSerializer(TypedDict, total=False):
	item_code: str
	item_name: str
	description: str
	item_group: str
	uom: str
	item_image: str | None
	is_stock_item: bool
	barcode: str | None

	has_serial_no: bool
	has_batch_no: bool
	serial_no: str | None
	batch_no: str | None
	actual_qty: float
	price_list_rate: float | None
	currency: str | None

	tax_code: str | None
	max_discount: float | None
	brand: str | None


class CatalogResponseSerializer(TypedDict, total=False):
	items: list[CatalogItemSerializer]
	brands: list[dict[str, Any]] | None
	item_groups: list[dict[str, Any]] | None
	total_count: int | None


def _optional_str(value: Any) -> str | None:
	if value is None or value == "":
		return None
	return str(value)


def _optional_float(value: Any) -> float | None:
	if value is None or value == "":
		return None
	return float(value)


def serialize_catalog_item(raw: dict[str, Any]) -> CatalogItemSerializer:
	return CatalogItemSerializer(
		item_code=raw.get("item_code") or raw.get("name") or "",
		item_name=raw.get("item_name") or "",
		description=raw.get("description") or "",
		item_group=raw.get("item_group") or "",
		uom=raw.get("uom") or raw.get("stock_uom") or "",
		item_image=_optional_str(raw.get("item_image")),
		is_stock_item=bool(raw.get("is_stock_item")),
		barcode=_optional_str(raw.get("barcode")),
		has_serial_no=bool(raw.get("has_serial_no")),
		has_batch_no=bool(raw.get("has_batch_no")),
		serial_no=_optional_str(raw.get("serial_no")),
		batch_no=_optional_str(raw.get("batch_no")),
		actual_qty=float(raw.get("actual_qty") or 0),
		price_list_rate=_optional_float(raw.get("price_list_rate")),
		currency=_optional_str(raw.get("currency")),
		tax_code=_optional_str(raw.get("tax_code")),
		max_discount=_optional_float(raw.get("max_discount")),
		brand=_optional_str(raw.get("brand")),
	)
