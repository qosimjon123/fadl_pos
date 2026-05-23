from typing import TypedDict, List, Dict, Any, Optional

class CatalogResponseSerializer(TypedDict, total=False):
    items: List[Dict[str, Any]]
    brands: Optional[List[Dict[str, Any]]]
    item_groups: Optional[List[Dict[str, Any]]]
    total_count: Optional[int]
