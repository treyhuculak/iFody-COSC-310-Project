from fastapi import APIRouter, Depends
from src.backend.controllers.transaction_controller import TransactionController
from src.backend.controllers.paypal_controller import PayPalController
from src.backend.models.payment_transaction import PaymentTransaction, PaymentTransactionCreate
from src.backend.models.paypal_payment import PayPal

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"]
)

def get_controller():
    return TransactionController()

def get_paypal_controller():
    return PayPalController()

# Paypal return (after transaction confirmation) view 
@router.get("/paypal/return")
def paypal_return():
    return {"message": "PayPal approval completed"}

# Paypal cancel transaction view
@router.get("/paypal/cancel")
def paypal_cancel():
    return {"message": "PayPal payment was cancelled."}


@router.post("/", response_model=PaymentTransaction)
def add_transaction(transaction: PaymentTransactionCreate, controller: TransactionController = Depends(get_controller)):
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

'''
PayPal Stuff
'''

@router.post("/paypal/start", response_model=PayPal)
def start_paypal_transaction(transaction: PaymentTransactionCreate, controller: PayPalController = Depends(get_paypal_controller)):
    new_transaction = controller.start_paypal_transaction(transaction)
    return new_transaction

@router.delete("/paypal/{transaction_id}", response_model=PayPal)
def delete_paypal_transaction(transaction_id: int, controller: TransactionController = Depends(get_controller)):
    deleted_transaction = controller.delete_transaction(transaction_id)
    return deleted_transaction

@router.get("/paypal/{transaction_id}", response_model=PayPal)
def get_paypal_transaction(transaction_id: int, controller: TransactionController = Depends(get_controller)):
    return controller.get_transaction(transaction_id)

@router.post("/paypal/capture/{transaction_id}", response_model=PayPal)
def capture_paypal_transaction(transaction_id: int, controller: PayPalController = Depends(get_paypal_controller)):
    return controller.capture_paypal_transaction(transaction_id)