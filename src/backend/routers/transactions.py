from fastapi import APIRouter, Depends
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

@router.delete("/{transaction_id}", response_model=PaymentTransaction)
def delete_transaction(transaction_id: int, controller: TransactionController = Depends(get_controller)):
    deleted_transaction = controller.delete_transaction(transaction_id)
    return deleted_transaction

@router.get("/{transaction_id}", response_model=PaymentTransaction)
def get_transaction(transaction_id: int, controller: TransactionController = Depends(get_controller)):
    return controller.get_transaction(transaction_id)

@router.get("/user_transactions/{user_id}", response_model=list)
def get_all_transactions_by_user(user_id: int, controller: TransactionController = Depends(get_controller)):
    return controller.get_all_transactions_by_user_id(user_id)