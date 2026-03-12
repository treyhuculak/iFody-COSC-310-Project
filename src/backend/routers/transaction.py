from fastapi import APIRouter, Depends, HTTPException, Query
from src.backend.controllers.transaction_controller import TransactionController
from src.backend.models.payment_transaction import PaymentTransaction, PaymentTransactionCreate

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"]
)

def get_controller():
    return TransactionController()

@router.post("/", response_model=PaymentTransaction)
def add_payment(transaction: PaymentTransactionCreate, controller: TransactionController = Depends(get_controller)):
    new_transaction = controller.create_transaction(transaction)
    return new_transaction