# _source_warehouse — Склад исходников POS

> **Цель**: Собрать ВСЕ файлы ERPNext native POS + POS Next, покрывающие 100% POS-функционала.
> По мере реализации в `fadl_pos/services/` и `fadl_pos/api/`, помечаем файлы как `DEPRECATED`.

## Ключевой принцип

> [!CAUTION]
> **Если функционал POS Next дублирует native ERPNext — мы НЕ рассматриваем POS Next версию.**
> Используем native ERPNext через `import`. POS Next копируем ТОЛЬКО для эксклюзивного функционала.

## Статусы

| Статус | Значение |
|---|---|
| `PENDING` | Ещё не обработан, будем реализовывать |
| `IN_PROGRESS` | Частично покрыт нашим кодом |
| `DEPRECATED` | Полностью покрыт `fadl_pos` |
| `IMPORT` | Используем через `from erpnext.* import` |
| `COPY` | Копируем логику из POS Next (нет аналога в native) |
| `SKIP` | Не берём — native ERPNext покрывает этот функционал |
| `REFERENCE_ONLY` | Только для справки, не копируем логику |
| `FUTURE` | Фаза 5+, не сейчас |

---

## ERPNext Native POS — ИСТОЧНИК ПРАВДЫ

### 01_pos_page/ — `point_of_sale.py` (546 строк)

Главный backend файл нативного POS. **ВСЕ функции отсюда — IMPORT.**

| Функция | Наш endpoint | Стратегия | Статус |
|---|---|---|---|
| `check_opening_entry(user)` | `session.init` | IMPORT | PENDING |
| `create_opening_voucher(pos_profile, company, balance_details)` | `session.open` | IMPORT | PENDING |
| `get_pos_profile_data(pos_profile)` | `session.init` | IMPORT | PENDING |
| `get_items(start, page_length, price_list, item_group, pos_profile)` | `catalog.get(action=items)` | IMPORT | PENDING |
| `search_by_term(search_term, warehouse, price_list)` | `catalog.get(action=search)` | IMPORT | PENDING |
| `search_for_serial_or_batch_or_barcode_number(search_value)` | `catalog.get(action=barcode)` | IMPORT | PENDING |
| `item_group_query(...)` | `catalog.get(action=groups)` | IMPORT | PENDING |
| `get_past_order_list(search_term, status, limit)` | `invoice_list.get(action=history)` | IMPORT | PENDING |
| `set_customer_info(fieldname, customer, value)` | `customer.manage(action=update)` | IMPORT | PENDING |
| `get_customer_recent_transactions(customer)` | `customer.manage(action=details)` | IMPORT | PENDING |

JS файлы — `REFERENCE_ONLY` (мы делаем PWA, не используем Desk UI).

---

### 02_pos_invoice/ — `pos_invoice.py` (1119 строк)

| Функция | Наш endpoint | Стратегия | Статус |
|---|---|---|---|
| `POSInvoice.validate/submit/cancel` | `invoice.sync` | IMPORT (doc methods) | PENDING |
| `POSInvoice.update_payments(payments)` | `payment.manage(action=add_partial)` | IMPORT | PENDING |
| `make_sales_return(source_name)` | `invoice.sync(action=return)` | IMPORT | PENDING |
| `get_stock_availability(item_code, warehouse)` | `stock.get(action=single)` | IMPORT | PENDING |
| `set_status()` | Автоматически | REFERENCE_ONLY | — |

---

### 03_pos_opening_entry/ — `pos_opening_entry.py` (123 строки)

| Функционал | Стратегия | Статус |
|---|---|---|
| Создание/валидация Opening Entry | IMPORT (через `create_opening_voucher`) | PENDING |

### 04_pos_closing_entry/ — `pos_closing_entry.py` (443 строки)

| Функция | Наш endpoint | Стратегия | Статус |
|---|---|---|---|
| `make_closing_entry_from_opening(opening_entry)` | `session.close` | IMPORT | PENDING |

### 05_pos_profile/ — `pos_profile.py` (346 строк)

| Функционал | Стратегия | Статус |
|---|---|---|
| POS Profile read/settings | IMPORT (через `get_pos_profile_data`) | PENDING |

### 06_pos_settings/ — `pos_settings.py` (57 строк)

| Функционал | Статус |
|---|---|
| invoice_type (POS Invoice vs Sales Invoice) | REFERENCE_ONLY |

### 07_pos_invoice_merge_log/ — (688 строк)

| Функционал | Статус |
|---|---|
| Merge при POS Closing | REFERENCE_ONLY |

### 08_pricing_rule/ — `utils.py` (779 строк)

| Функция | Наш endpoint | Стратегия | Статус |
|---|---|---|---|
| `validate_coupon_code(coupon_name)` | `offers.get(action=validate)` | IMPORT | PENDING |
| `update_coupon_code_count(coupon_name, type)` | Автоматически при submit | REFERENCE_ONLY | — |
| `apply_pricing_rule*` | Автоматически при `doc.save()` | REFERENCE_ONLY | — |

### 09_coupon_code/ — `coupon_code.py` (48 строк)

| Функционал | Наш endpoint | Стратегия | Статус |
|---|---|---|---|
| Coupon Code DocType | `offers.get(action=coupons)` | QUERY (read-only) | PENDING |

### 10_promotional_scheme/ — (400 строк)

| Функционал | Статус |
|---|---|
| Batch creation of Pricing Rules | REFERENCE_ONLY |

### 11_serial_no/ — `serial_no.py` (310 строк)

| Функция | Наш endpoint | Стратегия | Статус |
|---|---|---|---|
| `auto_fetch_serial_number` | `stock.get(action=serial_batch)` | IMPORT | PENDING |
| `get_pos_reserved_serial_nos` | `stock.get(action=serial_batch)` | IMPORT | PENDING |

---

## POS Next — Анализ: Native покрывает или нет?

### 20_posnext_api/ — API файлы POS Next

---

#### `shifts.py` (184 строки) → **99% SKIP — native покрывает**

| Функция POS Next | Аналог в Native ERPNext | Решение |
|---|---|---|
| `get_opening_dialog_data()` | `check_opening_entry(user)` + `get_pos_profile_data()` | **SKIP** — native |
| `check_opening_shift(user)` | `check_opening_entry(user)` из `point_of_sale.py` | **SKIP** — native |
| `create_opening_shift(...)` | `create_opening_voucher(...)` из `point_of_sale.py` | **SKIP** — native |
| `get_closing_shift_data(opening)` | `make_closing_entry_from_opening()` из `pos_closing_entry.py` | **SKIP** — native |
| `submit_closing_shift(closing)` | `make_closing_entry_from_opening()` + `doc.submit()` | **SKIP** — native |

> **Вердикт**: Полностью покрыт native. Не рассматриваем.

---

#### `partial_payments.py` (993 строки) → **SKIP — native v16 покрывает**

| Функция POS Next | Аналог в Native ERPNext | Решение |
|---|---|---|
| Весь файл | `POS Invoice.update_payments()` (native v16) | **SKIP** |

> **Вердикт**: ERPNext v16 имеет native `update_payments()`, `set_status("Partly Paid")`, `allow_partial_payment` в POS Profile. Полный анализ — см. `partial_payments_analysis.md`.

---

#### `offers.py` (596 строк) → **SKIP — native Pricing Rule + Coupon Code**

| Функция POS Next | Аналог в Native ERPNext | Решение |
|---|---|---|
| Кастомный `POS Offer` DocType | Native `Pricing Rule` | **SKIP** |
| Кастомный `POS Coupon` DocType | Native `Coupon Code` | **SKIP** |
| `get_offers(pos_profile)` | `frappe.get_list("Pricing Rule")` | **SKIP** — наша query |
| `validate_offer()` | Автоматически при `doc.save()` | **SKIP** |

> **Вердикт**: Полностью покрыт native Pricing Rule + Coupon Code. Не рассматриваем.

---

#### `promotions.py` (949 строк) → **SKIP — native Pricing Rule + Promotional Scheme**

| Функция POS Next | Аналог в Native ERPNext | Решение |
|---|---|---|
| Весь файл | `Pricing Rule` + `Promotional Scheme` + `apply_pricing_rule_on_transaction()` | **SKIP** |

> **Вердикт**: ERPNext Pricing Rule engine покрывает все виды промо-акций. Не рассматриваем.

---

#### `bootstrap.py` (266 строк) → **ЧАСТИЧНО SKIP**

| Функция POS Next | Аналог в Native ERPNext | Решение |
|---|---|---|
| `get_initial_data()` → POS profiles | `check_opening_entry()` + `get_pos_profile_data()` | **SKIP** — native |
| `_get_precision_settings()` | Наша utility | **COPY** — полезная утилита |
| `_get_open_shift()` | `check_opening_entry(user)` | **SKIP** — native |
| `_get_pos_settings()` | `get_pos_profile_data()` | **SKIP** — native |
| `_get_payment_methods()` | `get_pos_profile_data()` (includes payments) | **SKIP** — native |
| `_get_user_language()` | Наша utility | **COPY** — small helper |

> **Вердикт**: 90% покрыт native. Копируем только 2 утилиты.

---

#### `pos_profile.py` (663 строки) → **90% SKIP**

| Функция POS Next | Аналог в Native ERPNext | Решение |
|---|---|---|
| `get_pos_profiles()` | `pos_profile_query()` из `pos_profile.py` | **SKIP** — native |
| `get_pos_profile_data()` | `get_pos_profile_data()` из `point_of_sale.py` | **SKIP** — native |
| `get_pos_settings()` | Часть `get_pos_profile_data()` | **SKIP** — native |
| `get_payment_methods()` | Из POS Profile child table `payments` | **SKIP** — native |
| `get_taxes()` | Из POS Profile → Sales Taxes template | **SKIP** — native |
| `get_warehouses()` | `frappe.get_list("Warehouse")` | **COPY** — POS Next exclusive (multi-warehouse) |
| `get_default_customer()` | POS Profile.customer | **SKIP** — native |
| `update_warehouse()` | — | **COPY** — POS Next exclusive |
| `get_sales_persons()` | — | **COPY** — POS Next exclusive |
| `create_pos_profile()` | Desk only | **SKIP** — не для POS UI |
| `update_pos_profile()` | Desk only | **SKIP** — не для POS UI |
| `delete_pos_profile()` | Desk only | **SKIP** — не для POS UI |
| `get_wallet_payment_flags()` | — | **FUTURE** (wallet) |

> **Вердикт**: 3 функции полезны, остальное native.

---

#### `items.py` (2361 строк) → **~40% SKIP, ~60% COPY**

| Функция POS Next | Аналог в Native ERPNext | Решение |
|---|---|---|
| `get_stock_availability(item, wh)` | Native `get_stock_availability()` в `pos_invoice.py` | **SKIP** — native |
| `search_by_barcode(barcode, profile)` | Native `search_for_serial_or_batch_or_barcode_number()` | **SKIP** — native |
| `get_items(pos_profile, ...)` | Native `get_items()` в `point_of_sale.py` | **SKIP** — native |
| `get_item_stock(item_code, wh)` | Native `get_stock_availability()` | **SKIP** — native |
| `get_item_detail(item, doc, wh, price_list)` | — | **COPY** — обогащённый ответ |
| `get_items_bulk(pos_profile, ...)` | — | **COPY** — для offline кэша PWA |
| `get_items_count(pos_profile, ...)` | — | **COPY** — пагинация |
| `get_item_details(item_code, pos_profile)` | — | **COPY** — детали с ценой/скидкой |
| `get_item_groups(pos_profile)` | Native `item_group_query()` | **SKIP** — native |
| `get_brands(pos_profile)` | — | **COPY** — нет в native |
| `get_item_variants(template, profile)` | — | **COPY** — нет в native |
| `get_stock_quantities(item_codes, wh)` | — | **COPY** — batch запрос N товаров |
| `get_item_warehouse_availability(item_code)` | — | **COPY** — все склады |
| `get_product_bundle_availability(item, wh)` | — | **COPY** — Product Bundle |
| `get_batch_serial_details(item, wh)` | — | **COPY** — batch/serial details |
| `get_batch_serial_data_for_items(items, wh)` | — | **COPY** — bulk serial/batch |
| `_calculate_bundle_availability_bulk(...)` | — | **COPY** — helper |
| `_build_item_base_conditions(...)` | — | **COPY** — helper |

> **Вердикт**: Функции работы со списком/поиском — native. Bulk, variants, brands, multi-warehouse, bundle — COPY.

---

#### `invoices.py` (3038 строк) → **~30% SKIP, ~50% COPY, ~20% REFERENCE**

| Функция POS Next | Аналог в Native ERPNext | Решение |
|---|---|---|
| `update_invoice(data)` — save | `frappe.get_doc("POS Invoice").save()` | **SKIP** — native doc.save() |
| `submit_invoice(invoice)` | `doc.submit()` | **SKIP** — native |
| `get_invoice(invoice_name)` | `frappe.get_doc()` | **SKIP** — native |
| `delete_invoice(invoice)` | `frappe.delete_doc()` | **SKIP** — native |
| `get_invoices(pos_profile, limit)` | Native `get_past_order_list()` | **SKIP** — native |
| `validate_cart_items(items, pos_profile)` | — | **COPY** — pre-submit валидация |
| `validate_return_items(orig, return_items)` | — | **COPY** — return валидация |
| `get_draft_invoices(opening_shift)` | — | **COPY** — черновики текущей смены |
| `cleanup_old_drafts(pos_profile)` | — | **COPY** — очистка старых draft |
| `check_offline_invoice_synced(offline_id)` | — | **COPY** — offline sync PWA |
| `_ensure_offline_uniqueness(offline_id)` | — | **COPY** — offline идемпотентность |
| `validate_manual_rate_edit(item, profile)` | — | **COPY** — проверка ручной цены |
| `_validate_stock_on_invoice(invoice_doc)` | Native `validate_stock_availablility()` | **SKIP** — native |
| `_auto_set_return_batches(invoice_doc)` | — | **COPY** — авто-подбор batch для return |
| `_filter_fully_returned(invoices)` | — | **COPY** — фильтр полностью возвращённых |
| `calculate_price_list_rate(...)` | — | **COPY** — helper |
| `standardize_pricing_rules(items)` | — | **COPY** — helper |
| `get_payment_account(mode, company)` | Native `get_bank_cash_account()` | **SKIP** — native |

> **Вердикт**: CRUD и основная обработка — native. Offline sync, draft management, pre-validation — COPY.

---

#### `customers.py` (265 строк) → **~50% SKIP, ~50% COPY**

| Функция POS Next | Аналог в Native ERPNext | Решение |
|---|---|---|
| `get_customers(search, profile, limit)` | `frappe.get_list("Customer")` | **SKIP** — native query |
| `get_customer_details(customer)` | `frappe.get_doc("Customer")` + loyalty | **SKIP** — native |
| `create_customer(...)` | — | **COPY** — создание из POS UI |
| `auto_assign_loyalty_program(doc)` | — | **COPY** — авто-программа лояльности |
| `get_default_loyalty_program(company)` | — | **COPY** — helper |

> **Вердикт**: Чтение — native. Создание клиента из POS — COPY.

---

#### `credit_sales.py` (752 строки) → **FUTURE**

> Продажи в кредит — Phase 5. Не рассматриваем сейчас.

---

#### `wallet.py` (519 строк) → **FUTURE**

> Кошелёк — Phase 5. Не рассматриваем сейчас.

---

#### `branding.py` (221 строка) → **SKIP**

> Брендинг POS Next UI. У нас своя PWA — не нужно.

---

#### `qz.py` (186 строк) → **FUTURE**

> QZ Tray для печати чеков. Phase 5.

---

#### `localization.py` (140 строк) → **FUTURE**

> Локализация. Phase 5.

---

#### `constants.py` (73 строки) → **COPY** (частично)

> Полезные константы. Скопируем нужные.

---

#### `utilities.py` (112 строк) → **COPY** (частично)

> Утилиты (wallet modes etc). Скопируем нужные.

---

#### `sales_invoice_hooks.py` (143 строки) → **REFERENCE**

> Хуки на Sales Invoice. Посмотрим при реализации fiscal/.

---

#### `auth.py` (25 строк) → **SKIP**

> Уже есть наш `login/`.

---

### 21_posnext_services/ — POS Next Services

| Файл | Функционал | Решение | Статус |
|---|---|---|---|
| `barcode.py` (193) | Правила парсинга баркодов | **COPY** | PENDING |

---

### 22_posnext_overrides/ — POS Next Overrides

| Файл | Функционал | Решение | Статус |
|---|---|---|---|
| `pricing_rule.py` (87) | Override Pricing Rule | **REFERENCE** — используем native | — |
| `sales_invoice.py` (163) | Override Sales Invoice | **REFERENCE** — посмотрим при fiscal/ | — |

---

### 23_posnext_doctypes/ — POS Next Custom DocTypes

| DocType | Строки | Native аналог? | Решение |
|---|---|---|---|
| `pos_opening_shift` | 44 | ✅ Native `POS Opening Entry` | **SKIP** |
| `pos_closing_shift` | 634 | ✅ Native `POS Closing Entry` | **SKIP** |
| `pos_offer` | 12 | ✅ Native `Pricing Rule` | **SKIP** |
| `pos_offer_detail` | 12 | ✅ Native `Pricing Rule` child | **SKIP** |
| `pos_coupon` | 205 | ✅ Native `Coupon Code` | **SKIP** |
| `pos_coupon_detail` | 9 | ✅ Native `Coupon Code` | **SKIP** |
| `pos_settings` | 169 | ⚠️ Частично native `POS Profile` | **REFERENCE** |
| `pos_payment_entry_reference` | 9 | ✅ Native `Sales Invoice Payment` | **SKIP** |
| `offline_invoice_sync` | 101 | ❌ Нет в native | **COPY** |
| `pos_barcode_rules` | 9 | ❌ Нет в native | **COPY** |
| `pos_brands_detail` | 9 | ❌ Нет в native | **COPY** |
| `pos_opening_shift_detail` | 12 | ✅ Native child table | **SKIP** |
| `pos_closing_shift_detail` | 12 | ✅ Native child table | **SKIP** |
| `pos_closing_shift_taxes` | 12 | ✅ Native child table | **SKIP** |
| `sales_invoice_reference` | 12 | ✅ Native links | **SKIP** |
| `wallet` | 256 | ❌ Нет в native | **FUTURE** |
| `wallet_transaction` | 603 | ❌ Нет в native | **FUTURE** |
| `referral_code` | 233 | ❌ Нет в native | **FUTURE** |
| `brainwise_branding` | 415 | N/A | **SKIP** |

---

### 24_posnext_tasks/ — Scheduled Tasks

| Файл | Функционал | Решение |
|---|---|---|
| `branding_monitor.py` | Мониторинг брендинга | **SKIP** |
| `cleanup_expired_promotions.py` | Очистка акций | **SKIP** — native Pricing Rule имеет valid_upto |

---

### 25_posnext_misc/ — Hooks, Config

| Файл | Функционал | Решение |
|---|---|---|
| `hooks.py` | doc_events, overrides | **REFERENCE** (для нашего hooks.py) |
| `install.py` | after_install setup | **REFERENCE** (для нашего install.py) |
| `uninstall.py` | cleanup | **SKIP** |
| `utils.py` | Утилиты | **REFERENCE** |
| `validations.py` | Валидации | **REFERENCE** |
| `realtime_events.py` | WebSocket events | **FUTURE** |

---

## Итоговая сводка: что берём

### Из Native ERPNext — IMPORT (15 функций)

Всё из `point_of_sale.py`, `pos_closing_entry.py`, `pos_invoice.py`, `serial_no.py`, `pricing_rule/utils.py`.

### Из POS Next — COPY (только эксклюзив, ~30% от объёма)

| Область | Функции для копирования | Источник |
|---|---|---|
| **Каталог** | `get_items_bulk`, `get_items_count`, `get_item_details`, `get_brands`, `get_item_variants`, `get_stock_quantities`, `get_item_warehouse_availability`, `get_product_bundle_availability`, `get_batch_serial_*`, helpers | `items.py` |
| **Инвойсы** | `validate_cart_items`, `validate_return_items`, `get_draft_invoices`, `cleanup_old_drafts`, `check_offline_invoice_synced`, `_ensure_offline_uniqueness`, `validate_manual_rate_edit`, `_auto_set_return_batches`, `_filter_fully_returned`, helpers | `invoices.py` |
| **Клиенты** | `create_customer`, `auto_assign_loyalty_program` | `customers.py` |
| **Баркод** | `barcode.py` (service) | `barcode.py` |
| **DocTypes** | `offline_invoice_sync`, `pos_barcode_rules`, `pos_brands_detail` | doctypes/ |
| **Утилиты** | `_get_precision_settings`, `_get_user_language`, select constants | `bootstrap.py`, `constants.py` |

### НЕ берём из POS Next (native покрывает)

| Область | Что пропускаем | Почему |
|---|---|---|
| Смены | `shifts.py` (184 строки) | Native `check_opening_entry` + `create_opening_voucher` + `make_closing_entry_from_opening` |
| Partial Payments | `partial_payments.py` (993 строки) | Native `POS Invoice.update_payments()` |
| Offers/Promotions | `offers.py` (596) + `promotions.py` (949) = 1545 строк | Native `Pricing Rule` + `Coupon Code` + `Promotional Scheme` |
| POS Profile | 90% `pos_profile.py` (663 строки) | Native `get_pos_profile_data()` |
| Bootstrap | 90% `bootstrap.py` (266 строк) | Native `check_opening_entry` + `get_pos_profile_data` |
| DocTypes | 10 из 20 DocTypes | Дублируют native `POS Opening Entry`, `POS Closing Entry`, `Pricing Rule`, `Coupon Code` |
| Branding | `branding.py` (221 строка) | Наша PWA, не нужен POS Next UI |
| Auth | `auth.py` (25 строк) | Уже есть `login/` |

### Экономия

| | Строк кода | % от POS Next |
|---|---|---|
| Всего POS Next | ~15,000 | 100% |
| SKIP (native покрывает) | **~10,500** | **~70%** |
| COPY (эксклюзив) | ~4,500 | ~30% |
| FUTURE (Phase 5+) | ~2,000 | — |

**Мы экономим ~70% работы** за счёт использования native ERPNext.
