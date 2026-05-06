from typing import TypedDict, List, Optional, Dict

class ItemSerializer(TypedDict, total=False):
    item_code: str
    item_name: str
    description: Optional[str]
    stock_uom: str
    image: Optional[str]
    is_stock_item: int
    has_batch_no: int
    has_serial_no: int
    item_group: str
    brand: Optional[str]
    has_variants: int
    variant_of: Optional[str]
    rate: float
    actual_qty: float
    uom: str
    currency: str
    price_list_rate: float
    
class BatchDetailItem(TypedDict):
    batch_no: str
    batch_qty: float
    expiry_date: Optional[str]
    manufacturing_date: Optional[str]

class SerialNoDetailItem(TypedDict):
    serial_no: str
    warehouse: Optional[str]

class UomConversionItem(TypedDict):
    uom: str
    conversion_factor: float

class EnrichedItemSerializer(ItemSerializer, total=False):
    batch_no_data: List[BatchDetailItem]
    serial_no_data: List[SerialNoDetailItem]
    item_uoms: List[UomConversionItem]
    uom_prices: Dict[str, float]
    max_discount: Optional[float]
    warehouse: str

class BrandSerializer(TypedDict):
    name: str

class ItemGroupSerializer(TypedDict):
    name: str
    is_group: int
    parent_item_group: Optional[str]

class CatalogResponseSerializer(TypedDict):
    items: List[ItemSerializer]
    brands: Optional[List[BrandSerializer]]
    item_groups: Optional[List[ItemGroupSerializer]]
    total_count: Optional[int]
