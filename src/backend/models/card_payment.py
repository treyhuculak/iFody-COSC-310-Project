from typing import List, Optional
from src.backend.models.payment import Payment, PaymentCreate

from enum import Enum

class CardPaymentBrand(Enum):
    MASTER_CARD = "MasterCard"
    VISA = "Visa"
    NO_BRAND = "brand_not_found"

class CardPaymentBase(PaymentCreate):
    card_digits: str
    expiration_month: int
    expiration_year: int
    CVV: str
    name_on_card: str
    card_brand: Optional[CardPaymentBrand] = None

class CardPaymentCreate(CardPaymentBase):
    pass

class CardPaymentResponse(Payment):
    expiration_month: int
    expiration_year: int
    name_on_card: str
    last4: str
    card_brand: CardPaymentBrand