# Checkout: контракт клиента (SPA → fadl_pos)

Цель: клиент передаёт **минимум полей**, как при сборке нативного SI/PI в Form; сервер собирает документ, SABB, налоги и totals. Ничего не захардкожено — все id из boot, каталога и ERPNext.

Превью налогов на кассе клиент считает сам из **boot** + **каталога**; в checkout налоги и итоги **не являются источником истины** (сервер пересчитает).

---

## 1. Что клиент использует локально (не в checkout)

### 1.1 `catalog.boot`

| Ключ | Для чего на кассе |
|------|-------------------|
| `pos_profile` | company, warehouse (default), selling_price_list, `allow_rate_change`, `allow_discount_change`, `taxes_and_charges`, currency, … |
| `precision` | округление как на сервере |
| `warehouses[]` | выбор склада по строке |
| `item_groups.tree` | узел `tax` = **Item Tax Template** (имя), наследуется по дереву групп |
| `taxes[]` | справочник **Sales Taxes and Charges Template** (`title`, `taxes[{ account_head, rate, charge_type, … }]`) — счета/ставки уровня компании |
| `opening_voucher` | смена открыта |

### 1.2 `catalog.items` / поиск

На каждый товар (минимум для UI и превью):

- `item_code`, `item_name`, `item_group`, `uom`, `stock_uom`, `uoms[]`
- `price_list_rate`, `has_serial_no`, `has_batch_no`
- `actual_qty` (остаток на складе профиля / выбранном)
- при скане: `serial_no`, `batch_no`, `barcode`

**Превью налога на строке (клиент):**

1. Взять **Item Tax Template** для товара: с Item (если API отдаёт), иначе подъём по `item_groups.tree` от `item_group` (поле `tax` на узле).
2. Загрузить состав шаблона (нужен API или расширение boot): строки `{ account_head, rate }` из DocType **Item Tax Template** — те же счета, что потом попадут в `item_tax_rate` на SI.
3. Сопоставить с `boot.taxes` / счетами документа: на строке активна **одна** VAT-ставка (остальные 0), как в lab `message (1).txt`.
4. `line_net = qty × rate` (минус скидка строки); налог строки = `line_net × active_rate / 100` по каждому счёту из шаблона, где rate > 0.
5. Итог чека: сумма `line_net` + сумма налогов по строкам; округление по `precision`.

Если состав **Item Tax Template** не в boot — добавить RPC `catalog.item_tax_templates` или поле в `items` (без хардкода имён шаблонов).

### 1.3 POS Profile (из boot)

Уважать на UI (сервер тоже проверит при save):

- `allow_rate_change` / `allow_discount_change`
- `allow_partial_payment`
- `disable_rounded_total`

---

## 2. Что клиент отправляет: `CheckoutIn`

Один JSON (POST), без полного SI/PI.

### 2.1 Корень документа

| Поле | Тип | Обяз. | Описание |
|------|-----|-------|----------|
| `pos_profile` | string | да* | *или из сессии/token, если сервер подставит сам |
| `customer` | string | да | Customer.name |
| `warehouse` | string | нет | склад по умолчанию для строк без своего `warehouse` |
| `posting_date` | string (date) | нет | default: today (server) |
| `coupon_code` | string | нет | |
| `additional_discount_percent` | number | нет | скидка на чек, если разрешено профилем |
| `additional_discount_amount` | number | нет | альтернатива % |
| `invoice_name` | string | нет | для обновления черновика |
| `is_return` | boolean | нет | default false |
| `return_against` | string | нет | при возврате |
| `submit` | boolean | нет | false = draft save, true = submit |
| `payments` | PaymentIn[] | нет** | **обязателен при `submit: true` (кроме возврата по правилам ERPNext) |
| `items` | CheckoutLineIn[] | да | min 1 |

**Не передавать:** `doctype`, `taxes[]`, `item_wise_tax_details`, `grand_total`, `net_total`, `debit_to`, `company`, `currency`, `taxes_and_charges`, GL-поля.

### 2.2 `PaymentIn`

| Поле | Тип | Обяз. |
|------|-----|-------|
| `mode_of_payment` | string | да |
| `amount` | number | да |

Опционально: `account`, `type` — только если у вас кастом MOP; иначе сервер из POS Profile.

### 2.3 `CheckoutLineIn` (одна строка корзины = одна строка SI/PI)

| Поле | Тип | Обяз. | Описание |
|------|-----|-------|----------|
| `item_code` | string | да | |
| `qty` | number | да | > 0 (для продажи) |
| `uom` | string | нет | если нет — stock_uom с сервера |
| `warehouse` | string | нет | **свой склад на строку**; иначе `warehouse` корня / профиль |
| `rate` | number | нет | только если кассир менял цену и `allow_rate_change` |
| `discount_percent` | number | нет | если `allow_discount_change` |
| `discount_amount` | number | нет | альтернатива % |
| `barcode` | string | нет | для `get_item_details` / scan |
| `serial_batch` | SerialBatchIn | нет | см. ниже |
| `item_tax_template` | string | нет | **только override**; иначе сервер из Item/Group/Customer |
| `line_id` | string | нет | id строки черновика при update |

**Не передавать на строке:** `amount`, `net_amount`, `item_tax_rate`, `income_account`, `serial_no`, `batch_no`, `use_serial_batch_fields`, `serial_and_batch_bundle`, `conversion_factor` (сервер), `stock_qty`.

**Правила строк:**

- Один `item_code` + разный `uom` → **две строки** в `items[]` (как Синупрет Nos + Kg в lab).
- Не склеивать строки на клиенте по `item_code`.
- `qty` строки после serial: либо клиент выставляет `qty = sum(|entry.qty|)` для batch-only, либо сервер синхронизирует с SABB после создания bundle (как Desk: `abs(total_qty)`).

### 2.4 `SerialBatchIn`

| Поле | Тип | Обяз. | Описание |
|------|-----|-------|----------|
| `warehouse` | string | нет | override склада для bundle; иначе warehouse строки |
| `type_of_transaction` | string | нет | default `Outward` (продажа); `Inward` для возврата-прихода по правилам ERPNext |
| `entries` | SerialBatchEntryIn[] | да* | *если товар serial/batch |

### 2.5 `SerialBatchEntryIn`

| Поле | Тип | Когда |
|------|-----|--------|
| `serial_no` | string | товар `has_serial_no` |
| `batch_no` | string | товар `has_batch_no` |
| `qty` | number | **обязателен** если **только batch** (без serial); положительное, **без минуса** |

| Режим | entries |
|-------|---------|
| Serial (+ optional batch на serial) | `{ "serial_no": "…", "batch_no": "…"? }` — **без qty** |
| Только batch | `{ "batch_no": "…", "qty": 3 }` |
| Несколько batch | несколько entries или несколько строк корзины |
| Без учёта serial/batch | поле `serial_batch` **опустить** |

Сервер: `add_serial_batch_ledgers` / тот же pipeline → `serial_and_batch_bundle`, `use_serial_batch_fields = 0`, без legacy `serial_no` на строке.

---

## 3. Пример полного запроса (как lab + разные склады)

```json
{
  "pos_profile": "h",
  "customer": "Grant Plastics Ltd.",
  "warehouse": "Finished Goods - FTD",
  "submit": true,
  "payments": [
    { "mode_of_payment": "Cash", "amount": 90322 }
  ],
  "items": [
    {
      "item_code": "Амоксацилин-0001",
      "qty": 4,
      "uom": "Nos",
      "warehouse": "Finished Goods - FTD",
      "barcode": "4603182017031",
      "serial_batch": {
        "entries": [
          { "serial_no": "SN-A", "batch_no": "bebebe" },
          { "serial_no": "SN-B", "batch_no": "bebebe" }
        ]
      }
    },
    {
      "item_code": "SKU007",
      "qty": 1,
      "uom": "Nos",
      "warehouse": "Stores - FTD",
      "rate": 900
    },
    {
      "item_code": "Синупрет-0001",
      "qty": 1,
      "uom": "Nos",
      "barcode": "4660011218786"
    },
    {
      "item_code": "Синупрет-0001",
      "qty": 2,
      "uom": "Kg",
      "warehouse": "Finished Goods - FTD"
    },
    {
      "item_code": "Лоратадин-0001",
      "qty": 1,
      "rate": 0,
      "serial_batch": {
        "entries": [{ "serial_no": "SN-L1" }]
      }
    }
  ]
}
```

---

## 4. Превью налогов на кассе (клиент) vs checkout

| Данные | Где | В checkout? |
|--------|-----|-------------|
| Состав Item Tax Template | boot extension / catalog | нет (только локально) |
| `boot.taxes` | boot | нет |
| `item_tax_template` override | строка | опционально |
| `grand_total`, tax rows | UI | **нет** — сервер пересчитает |

Опционально для аудита (не обязательно):

```json
"client_preview": {
  "net_total": 42900,
  "tax_total": 47422,
  "grand_total": 90322
}
```

Сервер может логировать расхождение с пересчётом; **не** использовать для проводок.

---

## 5. Ответ сервера `CheckoutOut` (кратко)

| Ключ | Смысл |
|------|--------|
| `name` | PI/SI |
| `status` | success / error |
| `items[]` | `line_id`, `item_code`, `qty`, `uom`, `warehouse`, `net_amount`, `item_tax_template`, `serial_and_batch_bundle`, `tax_lines[{description, rate, amount}]` |
| `taxes_summary[]` | агрегат как `taxes[]` после save |
| `net_total`, `grand_total`, `rounded_total` | авторитетные |
| `payments` | как в документе |

---

## 6. Сборка на сервере (нативный порядок, без хардкода)

1. `POS Settings.invoice_type` → PI или SI.
2. `frappe.new_doc` / `get_doc` + `set_pos_fields` из **POS Profile** (не из клиента).
3. Для каждой `CheckoutLineIn`:
   - `get_item_details` (item_code, uom, warehouse, customer, qty, rate, barcode, is_pos, …).
   - применить rate/discount если разрешено профилем.
   - если `serial_batch` → `add_serial_batch_ledgers` → `serial_and_batch_bundle`.
4. `set_missing_values` → `calculate_taxes_and_totals` → `save` / `submit`.
5. Submit → `submit_serial_batch_bundle` (не `make_bundle_using_old_serial_batch_fields` при пустых serial_no/batch_no на строке).

---

## 7. Чеклист «ничего не захардкодить»

- [ ] `pos_profile`, `customer`, склады — id из ERPNext/boot.
- [ ] `mode_of_payment` — из `opening_voucher.balance_details` / профиля.
- [ ] Item Tax Template — из Item / Item Group / Customer, не константа в коде.
- [ ] Счета налогов — из шаблонов, не зашитые строки `"VAT 18% - FTD"` в Python.
- [ ] Doctype инвойса — из `POS Settings`.
- [ ] UOM / conversion — из Item, не фиксированный список.

---

## 8. Связь с текущим API

Сейчас: `fadl_pos.api.invoice.save` + `data` (полный doc JSON).

Целевое: `fadl_pos.api.invoice.checkout` (или `save` с режимом) принимает **только** структуру раздела 2; старый fat JSON — deprecated для SPA.

См. также: `docs/SPA_FRONTEND_INTEGRATION.md`, lab `docs/message (1).txt`.
