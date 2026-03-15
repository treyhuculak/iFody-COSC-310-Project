from typing import Optional

from fastapi import HTTPException

from src.backend.repositories.transaction_repo import TransactionRepository
from src.backend.repositories.payment_repo import PaymentRepository
from src.backend.models.payment import PaymentOptions
from src.backend.models.payment_transaction import PaymentTransactionCreate
from src.backend.services.payment_service import PaymentService
from src.backend.models.notification import NotificationType, NotificationCreate
from src.backend.controllers.notification_controller import NotificationController
from src.backend.repositories.notification_repo import NotificationRepository

class TransactionController:
    def __init__(self, payment_repo: Optional[PaymentRepository] = None, repo: Optional[TransactionRepository] = None, notif_controller: Optional[NotificationController] = None) -> None:
        self.payment_repo = payment_repo or PaymentRepository()
        self.transaction_repo = repo or TransactionRepository()
        self.notif_controller = notif_controller or NotificationController()
        self.payment_service = PaymentService()

    def get_payment_by_id(self, payment_id: int):
        payment = self.payment_repo.get_payment_by_id(payment_id)
        if payment == None:
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        return payment
    
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
                successful_cash_pay_notif = NotificationCreate(
                    user_id = payment["user_id"],
                    type = NotificationType.ORDER_IN_PROGRESS,
                    title = "Successful Cash Payment",
                    message = f"Your cash payment for order {transaction_info['order_id']} was successful",
                    is_read = False,
                    order_id = transaction_info['order_id']
                )
                self.notif_controller.create_notif(successful_cash_pay_notif)
            else:
                # Validating payment
                if(self.payment_service.simulate_payment(payment)):
                    transaction_info['is_successful'] = True
                    successful_card_pay_notif = NotificationCreate(
                        user_id = payment["user_id"],
                        type = NotificationType.ORDER_IN_PROGRESS,
                        title = "Successful Card Payment",
                        message = f"Your card payment for order {transaction_info['order_id']} was successful",
                        is_read = False,
                        order_id = transaction_info['order_id']
                    )
                    self.notif_controller.create_notif(successful_card_pay_notif)
                else:
                    transaction_info['is_successful'] = False
                    unsuccessful_payment_notif = NotificationCreate(
                        user_id = payment["user_id"],
                        type = NotificationType.PAYMENT_FAILED,
                        title = "Payment Failed",
                        message = f"Your payment for order {transaction_info['order_id']} has been declined",
                        is_read = False,
                        order_id = transaction_info['order_id']
                    )
                    self.notif_controller.create_notif(unsuccessful_payment_notif)
                    raise ValueError("Payment was declined.")
                
            return self.transaction_repo.create_transaction(transaction_info)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))