from typing import TypedDict, Optional

class LoginRequest(TypedDict, total=False):
    usr: Optional[str]
    pwd: Optional[str]

class QRLoginRequest(TypedDict, total=False):
    encrypted_qr: Optional[str]
    pin_code: Optional[str]

class QRGenerateRequest(TypedDict, total=False):
    pin_code: Optional[str]

class AuthTokenResponse(TypedDict):
    token: str

class QRGenerateResponse(TypedDict):
    encrypted_qr: str
