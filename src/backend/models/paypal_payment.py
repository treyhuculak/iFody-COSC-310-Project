from src.backend.models.payment import Payment, PaymentCreate
from enum import Enum
from pydantic import BaseModel

class PayPalOrderStatus(str, Enum):
    CREATED = "CREATED"
    SAVED = "SAVED"
    APPROVED = "APPROVED"
    VOIDED = "VOIDED"
    COMPLETED = "COMPLETED"
    PAYER_ACTION_REQUIRED = "PAYER_ACTION_REQUIRED"

class PayPalLink(BaseModel):
    href: str
    rel: str
    method: str

class PayPalBase(PaymentCreate):
    provider_order_id: str
    provider_status: PayPalOrderStatus
    links: list[PayPalLink] = []

class PayPalCreate(PayPalBase):
    pass

class PayPal(Payment):
    pass