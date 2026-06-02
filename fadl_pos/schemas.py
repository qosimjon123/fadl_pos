from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InputSchema(BaseModel):
	model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class OutputSchema(BaseModel):
	model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class PaginatedQuery(InputSchema):
	limit: int = Field(ge=1, le=100)


class CatalogItemOut(OutputSchema):
	name: str
	item_name: str
	description: str
	item_group: str
	uom: str
	item_image: str | None = None
	is_stock_item: bool
	barcode: str | None = None
	has_serial_no: bool
	has_batch_no: bool
	serial_no: str | None = None
	batch_no: str | None = None
	actual_qty: float
	price_list_rate: float | None = None
	currency: str | None = None
	tax_code: str | None = None
	max_discount: float | None = None
	brand: str | None = None


class CatalogOut(OutputSchema):
	items: list[CatalogItemOut]
	brands: list[dict[str, Any]] | None = None
	item_groups: list[dict[str, Any]] | None = None
	total_count: int | None = None


CatalogResponseSerializer = CatalogOut


class CustomerOut(OutputSchema):
	name: str
	customer_name: str
	customer_pos_id: str | None = None
	email_id: str | None = None
	mobile_no: str | None = None
	outstanding_balance: float


class CustomerListQuery(PaginatedQuery):
	search_term: str = ""


class CustomerDetailsQuery(InputSchema):
	customer: str = Field(min_length=1)


class CustomerManageBody(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class BalanceDetailItem(InputSchema):
	mode_of_payment: str = Field(min_length=1)
	opening_amount: float


class ClosingReconciliationItem(InputSchema):
	mode_of_payment: str = Field(min_length=1)
	closing_amount: float


class OpenShiftQuery(InputSchema):
	pos_profile: str = Field(min_length=1)
	company: str = Field(min_length=1)
	comment: str | None = None


class CloseShiftQuery(InputSchema):
	opening_entry_name: str = Field(min_length=1)
	comment: str | None = None


class InternalPaymentMethod(OutputSchema):
	pos_profile: str
	mode_of_payment: str
	default: int
	mop_type: str


class ChecklistItem(OutputSchema):
	title: str


class Checklists(OutputSchema):
	opening: list[ChecklistItem]
	closing: list[ChecklistItem]


class PaymentMethodOut(OutputSchema):
	name: str
	default: int
	type: str
	required_ob: bool


class PosProfileOut(OutputSchema):
	name: str
	status: str
	company: str
	opening_entry: str | None = None
	opening_entry_date: datetime | date | None = None
	checklists: list[Checklists] | None = None
	payment_methods: list[PaymentMethodOut] | None = None


class SessionListOut(OutputSchema):
	pos_profiles: list[PosProfileOut]


class CloseShiftOut(OutputSchema):
	status: str
	closing_entry: str
	is_final: bool
	entry_status: str
	error_message: str | None = None
	message: str | None = None


BalanceDetailItemType = BalanceDetailItem
ClosingReconciliationItemType = ClosingReconciliationItem
SessionListResponseSerializer = SessionListOut
CloseShiftResponse = CloseShiftOut
PaymentMethodSerializer = PaymentMethodOut
PosProfileResponseSerializer = PosProfileOut


class LoginQuery(InputSchema):
	usr: str = Field(min_length=1)
	pwd: str = Field(min_length=1)


class QRLoginQuery(InputSchema):
	encrypted_qr: str = Field(min_length=1)
	pin_code: str = Field(min_length=1)


class QRGenerateQuery(InputSchema):
	pin_code: str = Field(min_length=1)


class AuthTokenOut(OutputSchema):
	token: str


class QRGenerateOut(OutputSchema):
	encrypted_qr: str


class QRPayloadPlain(OutputSchema):
	v: int
	api_key: str
	qr_token: str


AuthTokenResponse = AuthTokenOut
QRGenerateResponse = QRGenerateOut


class CartLineIn(InputSchema):
	item_code: str = Field(min_length=1)
	qty: float = Field(ge=0)


class CartValidateIn(InputSchema):
	items: list[CartLineIn]
	warehouse: str = Field(min_length=1)


class CartValidateOut(OutputSchema):
	valid: bool
	errors: list[str]
	warnings: list[str]


class InvoiceSyncBody(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class InvoiceOut(OutputSchema):
	status: str | None = None
	name: str | None = None
	message: str | None = None
	invoice: dict[str, Any] | None = None
	valid: bool | None = None
	errors: list[str] | None = None
	warnings: list[str] | None = None


InvoiceResponseSerializer = InvoiceOut


class StockOut(OutputSchema):
	item_code: str | None = None
	warehouse: str | None = None
	actual_qty: float | None = None
	stocks: list[dict[str, Any]] | None = None
	warehouses: list[dict[str, Any]] | None = None
	bundle_availability: float | None = None
	serial_nos: list[str] | None = None
	reserved_serial_nos: list[str] | None = None
	status: bool | None = None
	message: str | None = None


StockResponseSerializer = StockOut


class OffersOut(OutputSchema):
	offers: list[dict[str, Any]]
	coupons: list[dict[str, Any]]
	status: str | None = None
	message: str | None = None


OffersResponseSerializer = OffersOut


class CouponOut(OutputSchema):
	coupon_code: str
	valid: bool
	message: str | None = None


class PaymentUpdateOut(OutputSchema):
	status: str
	name: str
	paid_amount: float
	outstanding_amount: float


CouponSerializer = CouponOut
PaymentUpdateResponse = PaymentUpdateOut


class InvoiceListQuery(PaginatedQuery):
	search_term: str = ""
	status: str = "Paid"


class InvoiceListOut(OutputSchema):
	invoices: list[dict[str, Any]]


InvoiceListResponseSerializer = InvoiceListOut
