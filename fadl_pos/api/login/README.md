# Fadl POS Login API

These endpoints are Frappe RPC methods exposed through `/api/v2/method/...`.

Frappe v2 wraps successful return values in `data` and errors in `errors`.

## Response Shape

Successful response:

```json
{
  "data": "<endpoint return value>"
}
```

Error response:

```json
{
  "errors": [
    {
      "type": "AuthenticationError",
      "message": "Invalid PIN or encrypted QR payload",
      "title": "Message",
      "indicator": "red"
    }
  ]
}
```

Use the HTTP status code first, then `errors[0].type`, then `errors[0].message`.

Common statuses:

- `200`: success.
- `401`: authentication failed or token is invalid.
- `403`: authenticated user is not allowed to call the endpoint.
- `417`: validation error.
- `500`: unexpected server error.

## Authentication Header

Authenticated endpoints use the Basic token returned by `login`, `login_qr`, or `clear_sessions`:

```http
Authorization: Basic base64(api_key:api_secret)
Accept: application/json
Content-Type: application/json
```

Frappe also supports `Authorization: token api_key:api_secret`, but this API returns `Basic ...` because Frappe validates Basic API keys natively.

## POST login

Endpoint:

```text
/api/v2/method/fadl_pos.api.login.login_endpoints.login
```

Guest endpoint. Accepts either `login/password` or legacy `usr/pwd`.

Request:

```json
{
  "login": "user@example.com",
  "password": "secret"
}
```

Success:

```json
{
  "data": "Basic YXBpX2tleTphcGlfc2VjcmV0"
}
```

Errors:

- `401 AuthenticationError`: missing login/password, wrong credentials, disabled user, or standard user.

## POST generate_qr

Endpoint:

```text
/api/v2/method/fadl_pos.api.login.login_endpoints.generate_qr
```

Authenticated endpoint. Generates a fresh encrypted QR payload for the current user and stores it in `User.qr_encrypted_data`.

Every call replaces the previous QR payload. Old QR payloads stop working.

Request:

```json
{
  "pin_code": "123456"
}
```

Success:

```json
{
  "data": {
    "encrypted_qr": "FP1..."
  }
}
```

Errors:

- `401 AuthenticationError`: missing/invalid auth, guest user, or invalid PIN.
- `417 ValidationError`: `User.qr_encrypted_data` field is missing; run `bench migrate`.

## POST login_qr

Endpoint:

```text
/api/v2/method/fadl_pos.api.login.login_endpoints.login_qr
```

Guest endpoint. Decrypts `encrypted_qr` with the 6-digit PIN, validates the stored QR payload, and returns a Basic token.

Request:

```json
{
  "encrypted_qr": "FP1...",
  "pin_code": "123456"
}
```

Success:

```json
{
  "data": "Basic YXBpX2tleTphcGlfc2VjcmV0"
}
```

Errors:

- `401 AuthenticationError`: missing QR, invalid PIN, corrupted QR, old QR, disabled user, or standard user.

## POST clear_sessions

Endpoint:

```text
/api/v2/method/fadl_pos.api.login.login_endpoints.clear_sessions
```

Authenticated endpoint. Rotates the current user's API secret and clears `User.qr_encrypted_data`.

After this call, all devices using the previous token lose access. The response contains the new Basic token for the current user.

Request:

```json
{}
```

Success:

```json
{
  "data": "Basic bmV3X2FwaV9rZXk6bmV3X2FwaV9zZWNyZXQ"
}
```

Errors:

- `401 AuthenticationError`: missing/invalid auth, guest user, or standard user.

## TypeScript Client

```ts
export interface FrappeV2ErrorItem {
  type: string;
  message?: string;
  title?: string;
  indicator?: string;
  exception?: string;
}

export type FrappeV2Success<T> = { data: T };
export type FrappeV2Error = { errors: FrappeV2ErrorItem[]; messages?: unknown[] };

export class FrappeApiError extends Error {
  constructor(
    public status: number,
    public type: string,
    message: string,
    public errors: FrappeV2ErrorItem[],
  ) {
    super(message);
    this.name = "FrappeApiError";
  }
}

export async function frappeV2Post<T>(
  method: string,
  body: Record<string, unknown> = {},
  authorization?: string,
): Promise<T> {
  const response = await fetch(`/api/v2/method/${method}`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(authorization ? { Authorization: authorization } : {}),
    },
    body: JSON.stringify(body),
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errors = (payload as FrappeV2Error).errors ?? [];
    const first = errors[0];
    throw new FrappeApiError(
      response.status,
      first?.type ?? "UnknownError",
      first?.message ?? `Request failed with status ${response.status}`,
      errors,
    );
  }

  return (payload as FrappeV2Success<T>).data;
}
```

Example:

```ts
const method = "fadl_pos.api.login.login_endpoints.login";
const authorization = await frappeV2Post<string>(method, {
  login: "user@example.com",
  password: "secret",
});
```

## Suggested Frontend Flow

1. Call `login` with login/password.
2. Store returned `Basic ...` token in secure app storage.
3. Use this token as `Authorization` for `generate_qr`, `clear_sessions`, and other protected Fadl POS endpoints.
4. For QR login, scan/read `encrypted_qr`, ask for PIN, call `login_qr`, and replace the locally stored token with the returned token.
5. On `401 AuthenticationError`, remove local token and send user back to login/QR login.
