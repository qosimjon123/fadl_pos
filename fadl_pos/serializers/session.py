from typing import TypedDict, List, Optional

class BalanceDetailItem(TypedDict):
    mode_of_payment: str
    opening_amount: float

class OpenShiftRequest(TypedDict):
    pos_profile: str
    company: str
    balance_details: List[BalanceDetailItem]

class ClosingReconciliationItem(TypedDict):
    mode_of_payment: str
    closing_amount: float

class CloseShiftResponse(TypedDict, total=False):
    status: str
    closing_entry: str
    is_final: bool
    message: str

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
