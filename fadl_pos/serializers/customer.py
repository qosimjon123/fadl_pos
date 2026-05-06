from typing import TypedDict, List, Optional

class CustomerSerializer(TypedDict):
    name: str
    customer_name: str
    email_id: Optional[str]
    mobile_no: Optional[str]
    customer_group: str
    territory: str

class CustomerResponseSerializer(TypedDict, total=False):
    customers: List[CustomerSerializer]
    customer: Optional[CustomerSerializer]
    status: str
    message: Optional[str]
