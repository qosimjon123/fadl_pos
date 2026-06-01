from __future__ import annotations

from typing import Any, List, Optional, TypedDict


class CatalogItemSerializer(TypedDict, total=False):
    item_code: str
    item_name: str
    description: str
    item_group: str
    uom: str
    item_image: Optional[str]
    is_stock_item: bool
    barcode: Optional[str]

    has_serial_no: bool
    has_batch_no: bool
    serial_no: Optional[str]
    batch_no: Optional[str]
    actual_qty: float
    price_list_rate: Optional[float]
    currency: Optional[str]

    tax_code: Optional[str]
    max_discount: Optional[float]
    brand: Optional[str]


class CatalogResponseSerializer(TypedDict, total=False):
    items: List[CatalogItemSerializer]
    brands: Optional[List[dict[str, Any]]]
    item_groups: Optional[List[dict[str, Any]]]
    total_count: Optional[int]
