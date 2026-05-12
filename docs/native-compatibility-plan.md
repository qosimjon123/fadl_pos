# Fadl POS Native Compatibility Plan

## Source Of Truth

`fadl_pos` must use native ERPNext POS behavior for every accounting, stock, invoice, payment, return, opening, and closing result that is visible in Desk.

Use native ERPNext controllers and helpers first:

- `erpnext.selling.page.point_of_sale.point_of_sale`
- `erpnext.accounts.doctype.pos_invoice.pos_invoice`
- `erpnext.accounts.doctype.pos_opening_entry.pos_opening_entry`
- `erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry`
- `erpnext.accounts.doctype.pos_profile.pos_profile`

## Custom Session Contract

The session API is intentionally custom. It may keep its own profile visibility, Cash-only opening balance rules, QR approval, and close-shift request shape.

The compatibility boundary is the final document result:

- Opening must create standard `POS Opening Entry`.
- Closing must create standard `POS Closing Entry`.
- Closing should use native `make_closing_entry_from_opening`.
- Desk must be able to view and report on the resulting documents normally.

## Excluded Scope

Do not add or copy:

- POS Next APIs, DocTypes, hooks, overrides, wallet, offers, or custom POS settings.
- Offline sync, `offline_id`, retry queues, IndexedDB, service workers, or bulk cache endpoints.
- Any alternate POS shift documents such as `POS Opening Shift` or `POS Closing Shift`.

## Endpoint Classification

- `session.*`: custom contract that must end in native POS Opening/Closing Entry documents.
- `catalog.get(items|search|barcode|groups)`: native wrappers.
- `catalog.get(brands|variants|details)`: online read-only ERPNext DocType queries; no POS Next tables.
- `stock.get(single|batch|bundle|auto_serial|reserved_serials)`: native ERPNext stock/POS helpers.
- `invoice.sync(save|submit|return|void|validate)`: native `POS Invoice` document flow.
- `payment.manage(update_invoice_payments|validate_coupon|get_loyalty_details)`: native ERPNext helpers.
- `offers.*`: native Pricing Rule / Coupon Code only.

If a future endpoint needs behavior outside this list, classify it before implementation and reject it if it depends on POS Next or offline sync.
