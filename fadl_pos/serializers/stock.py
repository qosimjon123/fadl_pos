from typing import TypedDict, List, Dict, Optional

class StockAvailabilitySerializer(TypedDict):
    item_code: str
    warehouse: str
    actual_qty: float

class WarehouseAvailabilitySerializer(TypedDict):
    warehouse: str
    actual_qty: float
    reserved_qty: float
    projected_qty: float

class BatchStockSerializer(TypedDict):
    item_code: str
    actual_qty: float

class StockResponseSerializer(TypedDict, total=False):
    item_code: Optional[str]
    warehouse: Optional[str]
    actual_qty: Optional[float]
    stocks: Optional[List[BatchStockSerializer]]
    warehouses: Optional[List[WarehouseAvailabilitySerializer]]
    bundle_availability: Optional[float]
