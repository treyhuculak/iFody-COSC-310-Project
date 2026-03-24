from fastapi import APIRouter, Depends
from src.backend.controllers.payment_controller import PaymentController
from src.backend.models.payment import Payment, PaymentCreate
from src.backend.models.card_payment import CardPaymentResponse, CardPaymentCreate

router = APIRouter(
    prefix="/payment",
    tags=["payment"]
)

def get_controller():
    return PaymentController()

@router.post("/card", response_model=CardPaymentResponse)
def add_payment(payment: CardPaymentCreate, active: bool, controller: PaymentController = Depends(get_controller)):
    new_payment = controller.add_payment_method(payment, active)
    return new_payment

@router.post("/cash", response_model=Payment)
def add_payment(payment: PaymentCreate, active: bool, controller: PaymentController = Depends(get_controller)):
    new_payment = controller.add_payment_method(payment, active)
    return new_payment

@router.put("/active/{user_id}/{payment_id}")
def update_active_payment(user_id: int, payment_id: int, controller: PaymentController = Depends(get_controller)):
    controller.switch_active_payment_method(user_id, payment_id)
    return {"message": f"Payment method {payment_id} is now active for user {user_id}"}

@router.delete("/card/{payment_id}", response_model=CardPaymentResponse)
def delete_payment(payment_id: int, controller: PaymentController = Depends(get_controller)):
    deleted_payment = controller.delete_payment_method(payment_id)
    return deleted_payment

@router.delete("/cash/{payment_id}", response_model=Payment)
def delete_payment(payment_id: int, controller: PaymentController = Depends(get_controller)):
    deleted_payment = controller.delete_payment_method(payment_id)
    return deleted_payment

@router.get("/card/{payment_id}", response_model=CardPaymentResponse)
def get_payment(payment_id: int, controller: PaymentController = Depends(get_controller)):
    return controller.get_payment(payment_id)

@router.get("/cash/{payment_id}", response_model=Payment)
def get_payment(payment_id: int, controller: PaymentController = Depends(get_controller)):
    return controller.get_payment(payment_id)

@router.get("/{user_id}", response_model=list)
def get_payment_methods_by_user_id(user_id: int, controller: PaymentController = Depends(get_controller)):
    return controller.get_payment_methods_by_user_id(user_id)

@router.get("/active/{user_id}", response_model=Payment | CardPaymentResponse)
def get_active_payment_method(user_id: int, controller: PaymentController = Depends(get_controller)):
    return controller.get_active_payment_method_by_user_id(user_id)