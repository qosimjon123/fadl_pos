from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, model_validator

OptionalStr = Annotated[
	str | None,
	BeforeValidator(lambda v: None if v in (None, "") else str(v)),
]
OptionalFloat = Annotated[
	float | None,
	BeforeValidator(lambda v: None if v in (None, "") else float(v)),
]


class CatalogItemSerializer(BaseModel):
	"""POS catalog line — normalized from ERPNext item / get_items row."""

	model_config = ConfigDict(extra="ignore")

	item_code: str = ""
	item_name: str = ""
	description: str = ""
	item_group: str = ""
	uom: str = ""
	item_image: OptionalStr = None
	is_stock_item: bool = False
	barcode: OptionalStr = None
	has_serial_no: bool = False
	has_batch_no: bool = False
	serial_no: OptionalStr = None
	batch_no: OptionalStr = None
	actual_qty: float = 0
	price_list_rate: OptionalFloat = None
	currency: OptionalStr = None
	tax_code: OptionalStr = None
	max_discount: OptionalFloat = None
	brand: OptionalStr = None

	@model_validator(mode="before")
	@classmethod
	def map_erp_fields(cls, raw: Any) -> Any:
		if not isinstance(raw, dict):
			return raw
		return {
			**raw,
			"item_code": raw.get("item_code") or raw.get("name") or "",
			"uom": raw.get("uom") or raw.get("stock_uom") or "",
		}


class CatalogResponseSerializer(BaseModel):
	model_config = ConfigDict(extra="ignore")

	items: list[CatalogItemSerializer] = []
	brands: list[dict[str, Any]] | None = None
	item_groups: list[dict[str, Any]] | None = None
	total_count: int | None = None


def serialize_catalog_item(raw: dict[str, Any]) -> dict[str, Any]:
	return CatalogItemSerializer.model_validate(raw).model_dump()
