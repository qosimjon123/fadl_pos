from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OutputSchema(BaseModel):
	model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

	@classmethod
	def dump(cls, data: Any) -> dict[str, Any]:
		return cls.model_validate(data).model_dump()


class CatalogItemUomOut(OutputSchema):
	uom: str
	conversion_factor: float
	price: float | None = None


class CatalogItemOut(OutputSchema):
	name: str
	item_name: str
	description: str
	item_group: str
	stock_uom: str
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
	uoms: list[CatalogItemUomOut] = Field(default_factory=list)


class CatalogOut(OutputSchema):
	items: list[CatalogItemOut]

CatalogResponseSerializer = CatalogOut


class CustomerOut(OutputSchema):
	name: str
	customer_name: str
	customer_pos_id: str | None = None
	email_id: str | None = None
	mobile_no: str | None = None
	outstanding_balance: float


class CustomerListOut(OutputSchema):
	customers: list[CustomerOut]


class CustomerDetailsOut(OutputSchema):
	customer: CustomerOut


class CustomerManageOut(OutputSchema):
	status: str
	customer: dict[str, Any] | None = None
	message: str | None = None


class CustomerTransactionsOut(OutputSchema):
	transactions: list[dict[str, Any]]


class InternalPaymentMethod(OutputSchema):
	"""Row from SQL; not exposed in session RPC."""

	pos_profile: str
	mode_of_payment: str
	default: int
	custom_required_opening_balance: int = 0
	idx: int = 0


class ChecklistItem(OutputSchema):
	title: str


class Checklists(OutputSchema):
	opening: list[ChecklistItem]
	closing: list[ChecklistItem]


class PaymentMethodOut(OutputSchema):
	"""Opening/closing form: one row per MOP with Required Opening Balance (server-filtered)."""

	name: str


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


SessionListResponseSerializer = SessionListOut
CloseShiftResponse = CloseShiftOut
PaymentMethodSerializer = PaymentMethodOut
PosProfileResponseSerializer = PosProfileOut


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


class CartValidateOut(OutputSchema):
	valid: bool
	errors: list[str]
	warnings: list[str]


class InvoiceOut(OutputSchema):
	status: str | None = None
	name: str | None = None
	message: str | None = None
	invoice: dict[str, Any] | None = None
	valid: bool | None = None
	errors: list[str] | None = None
	warnings: list[str] | None = None


InvoiceResponseSerializer = InvoiceOut


class StockBatchRowOut(OutputSchema):
	item_code: str
	actual_qty: float


class WarehouseRowOut(OutputSchema):
	name: str
	warehouse_name: str | None = None
	actual_qty: float | None = None
	reserved_qty: float | None = None
	projected_qty: float | None = None


class StockOut(OutputSchema):
	item_code: str | None = None
	warehouse: str | None = None
	actual_qty: float | None = None
	stocks: list[StockBatchRowOut] | list[dict[str, Any]] | None = None
	warehouses: list[WarehouseRowOut] | list[dict[str, Any]] | None = None
	bundle_availability: float | None = None
	serial_nos: list[str] | None = None
	reserved_serial_nos: list[str] | None = None
	status: bool | None = None
	message: str | None = None


StockResponseSerializer = StockOut


class OffersOut(OutputSchema):
	offers: list[dict[str, Any]] = Field(default_factory=list)
	coupons: list[dict[str, Any]] = Field(default_factory=list)
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


class LoyaltyDetailsOut(OutputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class InvoiceListOut(OutputSchema):
	invoices: list[dict[str, Any]]


InvoiceListResponseSerializer = InvoiceListOut


class TaxRowOut(OutputSchema):
	account_head: str
	charge_type: str
	rate: float
	included_in_print_rate: int = 0
	idx: int | None = None


class TaxTemplateOut(OutputSchema):
	title: str
	taxes: list[TaxRowOut]


class OpeningBalanceOut(OutputSchema):
	mode_of_payment: str
	opening_amount: float
	default: bool = False
	allow_in_returns: bool = False


class OpeningVoucherOut(OutputSchema):
	name: str
	period_start_date: datetime | date | None = None
	user_full_name: str | None = None
	balance_details: list[OpeningBalanceOut]


class ItemGroupsTreeOut(OutputSchema):
	tree: list[dict[str, Any]]


class PrecisionOut(OutputSchema):
	model_config = ConfigDict(extra="ignore", str_strip_whitespace=True, populate_by_name=True)

	currency: int = 2
	float_precision: int = Field(default=3, alias="float", serialization_alias="float")
	rounding_method: str | None = None
	number_format: str | None = None


class BootPosOut(OutputSchema):
	opening_voucher: OpeningVoucherOut
	pos_profile: dict[str, Any]
	precision: PrecisionOut
	item_groups: ItemGroupsTreeOut
	warehouses: list[dict[str, Any]]
	checklists: Checklists
	taxes: list[TaxTemplateOut]


# --- Session envelope (get_list / open_shift return shape) ---
SessionListEnvelopeOut = SessionListOut


# --- Stock (per-endpoint) ---
class StockSingleOut(OutputSchema):
	item_code: str
	warehouse: str
	actual_qty: float


class StockBatchOut(OutputSchema):
	stocks: list[StockBatchRowOut]


class StockWarehousesListOut(OutputSchema):
	warehouses: list[WarehouseRowOut] | list[dict[str, Any]]


class StockBundleOut(OutputSchema):
	bundle_availability: float


class StockAutoSerialOut(OutputSchema):
	serial_nos: list[str]


class StockReservedSerialsOut(OutputSchema):
	reserved_serial_nos: list[str]


class StockUpdateWarehouseOut(OutputSchema):
	status: bool
	message: str
	warehouse: str | None = None


# --- Offers (per-endpoint) ---
class OffersActiveOut(OutputSchema):
	offers: list[dict[str, Any]] = Field(default_factory=list)


class OffersCouponsOut(OutputSchema):
	coupons: list[dict[str, Any]] = Field(default_factory=list)


class ApplyOfferOut(OutputSchema):
	status: str
	invoice: dict[str, Any] | None = None


# --- Invoice (per-endpoint) ---
class InvoiceSaveOut(OutputSchema):
	status: str
	name: str
	invoice: dict[str, Any] | None = None


class InvoiceSubmitOut(OutputSchema):
	status: str
	name: str
	message: str | None = None


class InvoiceReturnOut(OutputSchema):
	status: str
	name: str
	invoice: dict[str, Any] | None = None


class InvoiceVoidOut(OutputSchema):
	status: str
	name: str
	message: str | None = None
