from typing import Optional

from fastapi import HTTPException

from src.backend.repositories.transaction_repo import TransactionRepository
from src.backend.repositories.payment_repo import PaymentRepository
from src.backend.models.payment import PaymentOptions
from src.backend.models.payment_transaction import PaymentTransactionCreate
from src.backend.services.payment_service import PaymentService

class TransactionController:
    def __init__(self, payment_repo: Optional[PaymentRepository] = None, repo: Optional[TransactionRepository] = None) -> None:
        self.payment_repo = payment_repo or PaymentRepository()
        self.transaction_repo = repo or TransactionRepository()
        self.payment_service = PaymentService()

    def get_payment_by_id(self, payment_id: int):
        payment = self.payment_repo.get_payment_by_id(payment_id)
        if payment == None:
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        return payment
    
    def get_transaction(self, transaction_id: int):
        transaction = self.transaction_repo.get_transaction_by_id(transaction_id)
        if transaction == None:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
        return transaction
    
    def get_all_transactions_by_user_id(self, user_id: int):
        list_of_transactions = self.transaction_repo.get_all_transactions_by_user_id(user_id)
        if len(list_of_transactions) == 0:
            raise HTTPException(status_code=404, detail=f"No transaction was found for user id: {user_id}")
        return list_of_transactions
    
    '''
    The idea for creting a transaction is to create a transaction object holding an payment_method_id and call the function below
    FYI, it is needed that when adding a payment_method_id to call and retrieve the id from the active payment method (there is function on the payment controller that retrieves the active payment method using the user_id)
    '''
    def create_transaction(self, transaction: PaymentTransactionCreate):
        try:
            # Now serialize the payment transaction for storage
            transaction_info = transaction.model_dump(mode="json")
            payment = self.get_payment_by_id(transaction_info['payment_method_id'])

            # Checking payment method
            if(payment['method'] == PaymentOptions.CASH.value):
                transaction_info['is_successful'] = True
            else:
                # Validating payment
                if(self.payment_service.simulate_payment(payment)):
                    transaction_info['is_successful'] = True
                else:
                    transaction_info['is_successful'] = False
                    raise ValueError("Payment was declined.")
                
            transaction_info['user_id'] = payment['user_id']
                
            return self.transaction_repo.create_transaction(transaction_info)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def delete_transaction(self, transaction_id: int):
        return self.transaction_repo.delete_transaction(transaction_id)