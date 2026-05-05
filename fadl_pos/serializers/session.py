from typing import TypedDict, List, Optional

# --- API Response Serializers ---

class ChecklistSection(TypedDict):
    opening: List[dict]

class Checklists(TypedDict, total=False):
    opening: List[dict]
    closing: List[dict]

class PaymentMethodSerializer(TypedDict):
    name: str
    default: int
    type: str
    required_ob: bool

class PosProfileResponseSerializer(TypedDict):
    name: str
    status: str
    opening_entry: Optional[str]
    company: str
    checklists: List[Checklists]
    payment_methods: List[PaymentMethodSerializer]

class SessionListResponseSerializer(TypedDict):
    pos_profiles: List[PosProfileResponseSerializer]
