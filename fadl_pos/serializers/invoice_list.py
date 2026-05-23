from typing import TypedDict, List, Dict, Any, Optional

class InvoiceListResponseSerializer(TypedDict):
    invoices: List[Dict[str, Any]]
