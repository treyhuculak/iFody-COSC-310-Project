from pydantic import BaseModel, Field
from src.backend.models.payment import Payment, PaymentCreate

class CardPaymentBase(PaymentCreate):
    card_digits: str
    expiration_month: int
    expiration_year: int
    CVV: str
    name_on_card: str

class CardPaymentCreate(CardPaymentBase):
    pass

class CardPaymentResponse(Payment):
    expiration_month: int
    expiration_year: int
    name_on_card: str
    last4: str