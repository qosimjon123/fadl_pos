from typing import TypedDict, List, Dict, Any, Optional

class InvoiceResponseSerializer(TypedDict, total=False):
    status: str
    name: str
    message: Optional[str]
    invoice: Optional[Dict[str, Any]]
    valid: Optional[bool]
    errors: Optional[List[str]]
    warnings: Optional[List[str]]
