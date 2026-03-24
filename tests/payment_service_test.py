import json
import pytest
from src.backend.models.card_payment import CardPaymentCreate, CardPaymentBrand
from src.backend.models.payment import PaymentOptions
from src.backend.services.payment_service import PaymentService

card_payment = CardPaymentCreate(
    user_id = 2,
    method = PaymentOptions.CREDIT_CARD.value,
    card_digits = "4234567812345678",
    expiration_month = 12,
    expiration_year = 2028,
    CVV = "123",
    name_on_card = "Umberto De Luca"
)

card_payment_2 = CardPaymentCreate(
    user_id = 2,
    method = PaymentOptions.CREDIT_CARD.value,
    card_digits = "5234567812345678",
    expiration_month = 12,
    expiration_year = 2028,
    CVV = "123",
    name_on_card = "Umberto De Luca"
)

card_payment_3 = CardPaymentCreate(
    user_id = 2,
    method = PaymentOptions.CREDIT_CARD.value,
    card_digits = "1234567812345678",
    expiration_month = 12,
    expiration_year = 2028,
    CVV = "123",
    name_on_card = "Umberto De Luca"
)

payment_service = PaymentService()

# Unit tests for PaymentService
def test_validate_card_cvv():
    assert payment_service.validate_card_CVV(card_payment.CVV)

def test_validate_card_cvv_with_invalid_cvv():
    assert not payment_service.validate_card_CVV("12")

def test_validate_card_expiration_date():
    assert payment_service.validate_card_expiration_date(card_payment.expiration_month, card_payment.expiration_year)

def test_validate_invalid_card_expiration_year():
    assert not payment_service.validate_card_expiration_date(card_payment.expiration_month, 2012)

def test_validate_invalid_card_expiration_month():
    assert not payment_service.validate_card_expiration_date(1, 2026)

def test_validate_card_digits():
    assert payment_service.validate_card_digits(card_payment.card_digits)

def test_validate_invalid_card_digits():
    assert not payment_service.validate_card_digits("1234")

def test_validate_card_digits_as_non_digits():
    assert not payment_service.validate_card_digits("42345678ab345678")

def test_defining_card_brand_VISA():
    payment_service.define_card_brand(card_payment)

    assert CardPaymentBrand.VISA == card_payment.card_brand

def test_defining_card_brand_MASTER_CARD():
    payment_service.define_card_brand(card_payment_2)

    assert CardPaymentBrand.MASTER_CARD == card_payment_2.card_brand

def test_defining_card_brand_NO_BRAND():
    payment_service.define_card_brand(card_payment_3)

    assert CardPaymentBrand.NO_BRAND == card_payment_3.card_brand

def test_checking_successful_transaction():
    payment_service.define_card_brand(card_payment)
    dict_data = card_payment.model_dump(mode="json")

    assert payment_service.checking_payment_is_successful(dict_data)

def test_checking_unsuccessful_transaction():
    payment_service.define_card_brand(card_payment_3)
    dict_data = card_payment_3.model_dump(mode="json")
    
    assert not payment_service.checking_payment_is_successful(dict_data)

def test_simulating_payment():
    payment_service.define_card_brand(card_payment)
    dict_data = card_payment.model_dump(mode="json")

    assert payment_service.simulate_payment(dict_data)

def test_simulating_rejected_payment():
    payment_service.define_card_brand(card_payment_3)
    dict_data = card_payment_3.model_dump(mode="json")
    
    assert not payment_service.simulate_payment(dict_data)
