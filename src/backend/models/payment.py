from pydantic import BaseModel, Field
from enum import Enum

class PaymentOptions(Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"

class PaymentBase(BaseModel):
    user_id: int
    method: PaymentOptions

class PaymentCreate(PaymentBase):
    pass


class Payment(PaymentBase):
    id: int
    is_active: bool
