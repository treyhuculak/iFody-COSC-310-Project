from pydantic import BaseModel, Field

class PaymentTransactionBase(BaseModel):
    payment_method_id: int
    order_id: int
    amount: float = Field(..., gt=0)

class PaymentTransactionCreate(PaymentTransactionBase):
    pass


class PaymentTransaction(PaymentTransactionBase):
    id: int
    is_successful: bool