from typing import TypedDict, List, Optional

class PosProfileUser(TypedDict, total=False):
    name: str
    default: int
    user: str

class PosPaymentMethodNative(TypedDict, total=False):
    name: str
    default: int
    mode_of_payment: str
    allow_in_returns: int

class PosItemGroup(TypedDict, total=False):
    name: str
    item_group: str

class PosCustomerGroup(TypedDict, total=False):
    name: str
    customer_group: str

class PosProfileNative(TypedDict, total=False):
    name: str
    disabled: int
    customer: str
    company: str
    country: str
    company_address: str
    applicable_for_users: List[PosProfileUser]
    payments: List[PosPaymentMethodNative]
    item_groups: List[PosItemGroup]
    customer_groups: List[PosCustomerGroup]
    letter_head: str
    tc_name: str
    select_print_heading: str
    selling_price_list: str
    currency: str
    write_off_account: str
    write_off_cost_center: str
    account_for_change_amount: str
    income_account: str
    expense_account: str
    cost_center: str
    taxes_and_charges: str
    apply_discount_on: str
    tax_category: str
    print_format: str
    warehouse: str
    ignore_pricing_rule: int
    update_stock: int
    hide_unavailable_items: int
    hide_images: int
    auto_add_item_to_cart: int
    allow_rate_change: int
    allow_discount_change: int
    validate_stock_on_save: int
    write_off_limit: float
    disable_rounded_total: int
    utm_campaign: str
    utm_source: str
    utm_medium: str
    print_receipt_on_order_complete: int
    project: str
    set_grand_total_to_default_mop: int
    action_on_new_invoice: str
    allow_partial_payment: int


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

class PosProfileResponseSerializer(TypedDict, total=False):
    name: str
    status: str
    opening_entry: Optional[str]
    company: str
    checklists: List[Checklists]
    payment_methods: List[PaymentMethodSerializer]

class SessionListResponseSerializer(TypedDict):
    pos_profiles: List[PosProfileResponseSerializer]
