# Login API — Input / Output (зеркало Pydantic → Valibot)

Источник правды в бэкенде:

- `fadl_pos/schemas/input.py` — `LoginQuery`, `QRLoginQuery`, `QRGenerateQuery`
- `fadl_pos/schemas/output.py` — `AuthTokenOut`, `QRGenerateOut`
- `fadl_pos/api/login/login_endpoints.py` — whitelist
- `fadl_pos/api/login/auth_service.py` — бизнес-правила (PIN, Basic token)

Общие правила Pydantic `InputSchema`: **`extra: "forbid"`**, **`str_strip_whitespace: true`**.

---

## Обёртка Frappe (все method)

HTTP **200** при успехе:

```ts
type FrappeRpcSuccess<T> = {
  message: T;
  // опционально на ошибках:
  exc?: string;
  _server_messages?: string;
};
```

Ошибки:

| HTTP | Когда |
|------|--------|
| **401** | `AuthenticationError` — неверный логин/пароль, PIN, QR |
| **417** | `ValidationError` — Pydantic In (лишние поля, пустые строки) |
| **429** | rate limit на `login` / `login_qr` (30 req / 60 s) |

Тело запроса: **`Content-Type: application/json`**, поля **на верхнем уровне** (не вложенный `args`, если не используешь Frappe SDK с `args`).

---

## 1. `login` — пароль

**Path:** `POST /api/method/fadl_pos.api.login.login_endpoints.login`  
**Guest:** да (`allow_guest`)  
**Auth header:** не нужен  

### Pydantic In → `LoginQuery`

| Поле | Тип | Обязательно | Правила |
|------|-----|-------------|---------|
| `usr` | `string` | да | `min_length=5`, `max_length=100`, trim |
| `pwd` | `string` | да | `min_length=8`, `max_length=100`, trim |

Лишние ключи в JSON → **417**.

Псевдонимы `email` / `password` **не** принимаются — только `usr` / `pwd`.

### Pydantic Out → `AuthTokenOut` (в `message`)

| Поле | Тип | Обязательно | Формат |
|------|-----|-------------|--------|
| `token` | `string` | да | `Basic <base64(api_key:api_secret)>` |

Пример `message`:

```json
{
  "token": "Basic YWJjMTIzOmRlZjQ1Ng=="
}
```

Использование: заголовок `Authorization: <message.token>` на всех защищённых RPC.

### Пример запроса

```json
{
  "usr": "cashier@example.com",
  "pwd": "secret"
}
```

---

## 2. `login_qr` — QR + PIN

**Path:** `POST /api/method/fadl_pos.api.login.login_endpoints.login_qr`  
**Guest:** да  
**Rate limit:** 30 / 60 s  

### Pydantic In → `QRLoginQuery`

| Поле | Тип | Обязательно | Правила |
|------|-----|-------------|---------|
| `encrypted_qr` | `string` | да | `min_length=10`, `max_length=512`, trim; blob из `generate_qr` (~170+ символов) |
| `pin_code` | `string` | да | ровно **6 цифр** `^\d{6}$`, trim |

### Pydantic Out → `AuthTokenOut`

Тот же объект, что у `login`: `{ token: string }`.

### Пример запроса

```json
{
  "encrypted_qr": "gAAAAA....",
  "pin_code": "424242"
}
```

---

## 3. `generate_qr` — выпуск QR

**Path:** `POST /api/method/fadl_pos.api.login.login_endpoints.generate_qr`  
**Guest:** нет — нужен **`Authorization`** (уже залогиненный пользователь Desk/POS)  

### Pydantic In → `QRGenerateQuery`

| Поле | Тип | Обязательно | Правила |
|------|-----|-------------|---------|
| `pin_code` | `string` | да | ровно **6 цифр** `^\d{6}$`, trim |

### Pydantic Out → `QRGenerateOut` (в `message`)

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `encrypted_qr` | `string` | да | ciphertext; сохраняется в `User.qr_encrypted_data`; повторный вызов **инвалидирует** старый blob |

### Пример запроса

```json
{
  "pin_code": "123456"
}
```

### Пример ответа

```json
{
  "message": {
    "encrypted_qr": "..."
  }
}
```

---

## 4. `clear_sessions` — сброс ключей и QR

**Path:** `POST /api/method/fadl_pos.api.login.login_endpoints.clear_sessions`  
**Guest:** нет  
**Body:** пустой объект `{}` или без тела  

### Pydantic In

Нет полей (пустой `InputSchema` не используется — параметров whitelist нет).

### Pydantic Out → `AuthTokenOut`

Новый `{ token }` после ротации `api_secret` и очистки QR blob.

---

## Внутренний payload QR (не по HTTP)

Внутри шифрования (`QRPayloadPlain`) — **не** парсить на фронте, только для справки:

| Поле | Тип | Значение |
|------|-----|----------|
| `v` | `int` | всегда `1` |
| `api_key` | `string` | ключ User |
| `qr_token` | `string` | длина **32** |

---

## Valibot (TypeScript) — копия контрактов

```typescript
import * as v from "valibot";

/** Pydantic InputSchema: extra forbid + trim on strings */
const usrField = v.pipe(v.string(), v.trim(), v.minLength(5), v.maxLength(100));
const pwdField = v.pipe(v.string(), v.trim(), v.minLength(8), v.maxLength(100));
const encryptedQrField = v.pipe(v.string(), v.trim(), v.minLength(10), v.maxLength(512));
const pinCode = v.pipe(
  v.string(),
  v.trim(),
  v.regex(/^\d{6}$/, "PIN must be a 6-digit code"),
);

// --- Request bodies (top-level JSON) ---

/** LoginQuery */
export const LoginInSchema = v.strictObject({
  usr: usrField,
  pwd: pwdField,
});
export type LoginIn = v.InferOutput<typeof LoginInSchema>;

/** QRLoginQuery */
export const QRLoginInSchema = v.strictObject({
  encrypted_qr: encryptedQrField,
  pin_code: pinCode,
});
export type QRLoginIn = v.InferOutput<typeof QRLoginInSchema>;

/** QRGenerateQuery */
export const QRGenerateInSchema = v.strictObject({
  pin_code: pinCode,
});
export type QRGenerateIn = v.InferOutput<typeof QRGenerateInSchema>;

// --- Response payloads (inside Frappe `message`) ---

/** AuthTokenOut */
export const AuthTokenOutSchema = v.strictObject({
  token: v.pipe(
    v.string(),
    v.regex(/^Basic [A-Za-z0-9+/]+=*$/, "Expected Basic base64 authorization value"),
  ),
});
export type AuthTokenOut = v.InferOutput<typeof AuthTokenOutSchema>;

/** QRGenerateOut */
export const QRGenerateOutSchema = v.strictObject({
  encrypted_qr: v.pipe(v.string(), v.minLength(1)),
});
export type QRGenerateOut = v.InferOutput<typeof QRGenerateOutSchema>;

// --- Frappe wrappers ---

export const FrappeAuthTokenResponseSchema = v.object({
  message: v.union([AuthTokenOutSchema, v.string()]),
});
export type FrappeAuthTokenResponse = v.InferOutput<typeof FrappeAuthTokenResponseSchema>;

export const FrappeQRGenerateResponseSchema = v.object({
  message: v.union([QRGenerateOutSchema, v.string()]),
});
export type FrappeQRGenerateResponse = v.InferOutput<typeof FrappeQRGenerateResponseSchema>;

// --- Endpoint map (для клиента) ---

export const LOGIN_METHODS = {
  login: "fadl_pos.api.login.login_endpoints.login",
  loginQr: "fadl_pos.api.login.login_endpoints.login_qr",
  generateQr: "fadl_pos.api.login.login_endpoints.generate_qr",
  clearSessions: "fadl_pos.api.login.login_endpoints.clear_sessions",
} as const;

// --- Parse helpers ---

export function parseLoginIn(data: unknown): LoginIn {
  return v.parse(LoginInSchema, data);
}

export function parseQRLoginIn(data: unknown): QRLoginIn {
  return v.parse(QRLoginInSchema, data);
}

export function parseQRGenerateIn(data: unknown): QRGenerateIn {
  return v.parse(QRGenerateInSchema, data);
}

export function parseAuthTokenMessage(data: unknown): AuthTokenOut {
  const wrapped = v.parse(FrappeAuthTokenResponseSchema, data);
  if (typeof wrapped.message === "string") {
    throw new Error(wrapped.message);
  }
  return wrapped.message;
}

export function parseQRGenerateMessage(data: unknown): QRGenerateOut {
  const wrapped = v.parse(FrappeQRGenerateResponseSchema, data);
  if (typeof wrapped.message === "string") {
    throw new Error(wrapped.message);
  }
  return wrapped.message;
}
```

### Замечания для Valibot

1. **`v.strictObject`** — аналог `extra=forbid` (неизвестные ключи → ошибка).
2. **PIN** — в Pydantic In только `min_length=1`; regex `^\d{6}$` проверяется в `auth_service._require_pin` → на фронте дублируем regex, чтобы не слать лишние запросы.
3. **`token`** — в Out нет отдельного поля `authorization`; только `token` (уже с префиксом `Basic `).
4. **`clear_sessions`** — не описывай In-схему; POST без полей.
5. После `parseAuthTokenMessage` сохраняй `token` и подставляй в `headers.Authorization` для `generate_qr` / `clear_sessions` и остальных RPC.

### Пример вызова (fetch)

```typescript
import { parseLoginIn, parseAuthTokenMessage, LOGIN_METHODS } from "./login-schemas";

async function login(site: string, usr: string, pwd: string) {
  const body = parseLoginIn({ usr, pwd });
  const res = await fetch(`${site}/api/method/${LOGIN_METHODS.login}`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.exc ?? res.statusText);
  return parseAuthTokenMessage(json);
}
```

---

## Соответствие Pydantic ↔ Valibot

| Pydantic (Python) | Valibot (TS) | HTTP method |
|-------------------|--------------|-------------|
| `LoginQuery` | `LoginInSchema` | `login` |
| `QRLoginQuery` | `QRLoginInSchema` | `login_qr` |
| `QRGenerateQuery` | `QRGenerateInSchema` | `generate_qr` |
| — | (нет body) | `clear_sessions` |
| `AuthTokenOut` | `AuthTokenOutSchema` | `login`, `login_qr`, `clear_sessions` |
| `QRGenerateOut` | `QRGenerateOutSchema` | `generate_qr` |

---

## Порядок QR-flow на фронте

1. `login` (usr/pwd) или существующий token → `Authorization`
2. `generate_qr` + PIN → сохранить `encrypted_qr` (показать QR)
3. Другой девайс: `login_qr` + тот же PIN → `token`
4. `clear_sessions` при logout — старый token и QR недействительны
