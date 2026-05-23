from typing import TypedDict, List, Dict, Any, Optional

class StockResponseSerializer(TypedDict, total=False):
    item_code: Optional[str]
    warehouse: Optional[str]
    actual_qty: Optional[float]
    stocks: Optional[List[Dict[str, Any]]]
    warehouses: Optional[List[Dict[str, Any]]]
    bundle_availability: Optional[float]
    serial_nos: Optional[List[str]]
    reserved_serial_nos: Optional[List[str]]
    status: Optional[bool]
    message: Optional[str]
