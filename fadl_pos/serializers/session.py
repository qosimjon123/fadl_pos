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
    entry_status: str
    error_message: Optional[str]
    message: str

# --- Internal Types (used within services) ---

class InternalPaymentMethod(TypedDict):
    pos_profile: str
    mode_of_payment: str
    default: int
    mop_type: str

# --- API Response Serializers ---

class ChecklistItem(TypedDict):
    title: str

class Checklists(TypedDict):
    opening: List[ChecklistItem]
    closing: List[ChecklistItem]

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
    checklists: Optional[List[Checklists]]
    payment_methods: Optional[List[PaymentMethodSerializer]]

class SessionListResponseSerializer(TypedDict):
    pos_profiles: List[PosProfileResponseSerializer]
