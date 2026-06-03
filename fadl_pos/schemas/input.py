from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class InputSchema(BaseModel):
	model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PaginatedQuery(InputSchema):
	limit: int = Field(ge=1, le=100)


class CustomerListQuery(PaginatedQuery):
	search_term: str = ""


class CustomerDetailsQuery(InputSchema):
	customer: str = Field(min_length=1)


class CustomerManageBody(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class BalanceDetailItem(InputSchema):
	name: str = Field(min_length=1)
	opening_amount: float


class ClosingReconciliationItem(InputSchema):
	name: str = Field(min_length=1)
	closing_amount: float


class OpenShiftQuery(InputSchema):
	pos_profile: str = Field(min_length=1)
	company: str = Field(min_length=1)
	comment: str | None = None


class CloseShiftQuery(InputSchema):
	opening_entry_name: str = Field(min_length=1)
	comment: str | None = None


class LoginQuery(InputSchema):
	usr: str = Field(min_length=1)
	pwd: str = Field(min_length=1)


class QRLoginQuery(InputSchema):
	encrypted_qr: str = Field(min_length=1)
	pin_code: str = Field(min_length=1)


class QRGenerateQuery(InputSchema):
	pin_code: str = Field(min_length=1)


class CartLineIn(InputSchema):
	item_code: str = Field(min_length=1)
	qty: float = Field(ge=0)


class CartValidateIn(InputSchema):
	items: list[CartLineIn]
	warehouse: str = Field(min_length=1)


class InvoiceSyncBody(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class InvoiceListQuery(PaginatedQuery):
	search_term: str = ""
	status: str = "Paid"


BalanceDetailItemType = BalanceDetailItem
ClosingReconciliationItemType = ClosingReconciliationItem

# --- Aliases (RPC boundary names) ---
CustomerListIn = CustomerListQuery
CustomerDetailsIn = CustomerDetailsQuery
CustomerRecentTransactionsIn = CustomerDetailsQuery
InvoiceListHistoryIn = InvoiceListQuery


# --- Session ---
class SessionListIn(InputSchema):
	pass


class OpenShiftIn(InputSchema):
	pos_profile: str = Field(min_length=1)
	company: str = Field(min_length=1)
	comment: str | None = None


class CloseShiftIn(InputSchema):
	opening_entry_name: str = Field(min_length=1)
	comment: str | None = None


# --- Customer manage ---
class CustomerCreateIn(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class CustomerUpdateIn(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)
	name: str = Field(min_length=1)


class CustomerSetInfoIn(InputSchema):
	fieldname: str = Field(min_length=1)
	customer: str = Field(min_length=1)
	value: str = ""


# --- Payment ---
class PaymentRowIn(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class PaymentUpdateIn(InputSchema):
	invoice_name: str = Field(min_length=1)
	payments: list[PaymentRowIn]


class CouponValidateIn(InputSchema):
	coupon_code: str = Field(min_length=1)


class LoyaltyDetailsIn(InputSchema):
	customer: str = Field(min_length=1)
	posting_date: str | None = None


# --- Catalog ---
class CatalogItemsIn(InputSchema):
	start: int = 0
	page_length: int = Field(default=15, ge=1, le=100)
	price_list: str | None = None
	item_group: str | None = None
	pos_profile: str = Field(min_length=1)
	search_term: str = ""


class CatalogBootIn(InputSchema):
	pos_profile: str = Field(min_length=1)


# --- Stock ---
class StockSingleIn(InputSchema):
	item_code: str = Field(min_length=1)
	warehouse: str = Field(min_length=1)


class StockBatchIn(InputSchema):
	item_codes: list[str]
	warehouse: str = Field(min_length=1)


class StockWarehousesIn(InputSchema):
	company: str | None = None
	pos_profile: str | None = None


class StockBundleIn(InputSchema):
	item_code: str = Field(min_length=1)
	warehouse: str = Field(min_length=1)


class StockAutoSerialIn(InputSchema):
	qty: int | float
	item_code: str = Field(min_length=1)
	warehouse: str = Field(min_length=1)
	batch_nos: str | list[str] | None = None


class StockReservedSerialsIn(InputSchema):
	item_code: str = Field(min_length=1)
	warehouse: str = Field(min_length=1)


class StockUpdateWarehouseIn(InputSchema):
	pos_profile: str = Field(min_length=1)
	warehouse: str = Field(min_length=1)


# --- Offers ---
class OffersActiveIn(InputSchema):
	pos_profile: str | None = None


class OffersCouponsIn(InputSchema):
	customer: str | None = None


class ApplyOfferIn(InputSchema):
	invoice_name: str = Field(min_length=1)
	coupon_code: str | None = None


# --- Invoice RPC ---
class InvoiceSaveIn(InputSchema):
	data: str = Field(min_length=1)


class InvoiceSubmitIn(InputSchema):
	data: str = Field(min_length=1)


class InvoiceReturnIn(InputSchema):
	data: str = Field(min_length=1)


class InvoiceVoidIn(InputSchema):
	data: str = Field(min_length=1)


class InvoiceValidateCartIn(InputSchema):
	data: str = Field(min_length=1)
