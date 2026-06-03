# SPA RPC migration (action → dedicated methods)

Breaking change: fadl_pos no longer uses `action` query parameters on combined endpoints.

## Session (unchanged paths)

| Method | Path |
|--------|------|
| List profiles | `fadl_pos.api.session.get_list` |
| Open shift | `fadl_pos.api.session.open_shift` |
| Close shift | `fadl_pos.api.session.close_shift` |

## Customer

| Old | New |
|-----|-----|
| `customer.get` + `action=list` | `fadl_pos.api.customer.list_customers` |
| `customer.get` + `action=details` | `fadl_pos.api.customer.details` |
| `customer.get` + `action=recent_transactions` | `fadl_pos.api.customer.recent_transactions` |
| `customer.manage` + `action=create` | `fadl_pos.api.customer.create` |
| `customer.manage` + `action=update` | `fadl_pos.api.customer.update` |
| `customer.manage` + `action=set_info` | `fadl_pos.api.customer.set_info` |

## Payment

| Old | New |
|-----|-----|
| `payment.manage` + `action=update_invoice_payments` | `fadl_pos.api.payment.update_invoice_payments` |
| `payment.manage` + `action=validate_coupon` | `fadl_pos.api.payment.validate_coupon` |
| `payment.manage` + `action=get_loyalty_details` | `fadl_pos.api.payment.get_loyalty_details` |

## Invoice list

| Old | New |
|-----|-----|
| `invoice_list.get` + `action=history` | `fadl_pos.api.invoice_list.history` |

## Catalog

| Old | New |
|-----|-----|
| `catalog.get` + `action=items` | `fadl_pos.api.catalog.items` |
| `catalog.get` + `action=boot` | `fadl_pos.api.catalog.boot` |

## Stock

| Old | New |
|-----|-----|
| `stock.get` + `action=single` | `fadl_pos.api.stock.single` |
| `stock.get` + `action=batch` | `fadl_pos.api.stock.batch` |
| `stock.get` + `action=warehouses` | `fadl_pos.api.stock.warehouses` |
| `stock.get` + `action=bundle` | `fadl_pos.api.stock.bundle` |
| `stock.get` + `action=auto_serial` | `fadl_pos.api.stock.auto_serial` |
| `stock.get` + `action=reserved_serials` | `fadl_pos.api.stock.reserved_serials` |
| `stock.update_warehouse` | `fadl_pos.api.stock.update_warehouse` (unchanged) |

## Offers

| Old | New |
|-----|-----|
| `offers.get` + `action=active_offers` | `fadl_pos.api.offers.active` |
| `offers.get` + `action=coupons` | `fadl_pos.api.offers.coupons` |
| `offers.apply` | `fadl_pos.api.offers.apply` (unchanged) |

## Invoice

| Old | New |
|-----|-----|
| `invoice.sync` + `action=save` | `fadl_pos.api.invoice.save` |
| `invoice.sync` + `action=submit` | `fadl_pos.api.invoice.submit` |
| `invoice.sync` + `action=return` | `fadl_pos.api.invoice.return_invoice` |
| `invoice.sync` + `action=void` | `fadl_pos.api.invoice.void` |
| `invoice.sync` + `action=validate` | `fadl_pos.api.invoice.validate_cart` |

## Validation

Unknown fields in RPC bodies now return **417** (`ValidationError`) via Pydantic `extra=forbid` on Input models.
