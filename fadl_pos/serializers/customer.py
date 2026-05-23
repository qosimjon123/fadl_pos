from typing import TypedDict, List, Dict, Any, Optional

class CustomerResponseSerializer(TypedDict, total=False):
    customers: List[Dict[str, Any]]
    customer: Optional[Dict[str, Any]]
    status: str
    message: Optional[str]
