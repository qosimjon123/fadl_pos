# _source_warehouse

This directory is reference-only. Runtime code must not import from here.

## Current Policy

`fadl_pos` is native ERPNext POS compatible by default:

- Use ERPNext native DocTypes and controllers for accounting, stock, invoices, payments, returns, opening entries, and closing entries.
- Keep the custom session/open/close API contract only as long as it creates standard `POS Opening Entry` and `POS Closing Entry` documents.
- Do not copy or depend on POS Next code.
- Do not add offline/idempotency/PWA cache logic.

## Allowed Sources

- `erpnext.selling.page.point_of_sale.point_of_sale`
- `erpnext.accounts.doctype.pos_invoice.pos_invoice`
- `erpnext.accounts.doctype.pos_opening_entry.pos_opening_entry`
- `erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry`
- `erpnext.accounts.doctype.pos_profile.pos_profile`
- Standard ERPNext/Frappe DocTypes through `frappe.get_doc`, `frappe.get_all`, native controller methods, and whitelisted native helpers.

## Explicitly Out Of Scope

- POS Next API helpers, DocTypes, hooks, overrides, wallet, offers, custom POS settings, and alternate shift documents.
- Offline invoice sync, `offline_id`, retry queues, IndexedDB, service workers, and bulk cache endpoints.
- Any custom flow that produces accounting/stock results different from native ERPNext.

If a feature cannot be implemented with native ERPNext behavior, keep it out of `fadl_pos` until it is explicitly approved as a separate custom contract.
