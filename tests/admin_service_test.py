from src.backend.services.admin_service import AdminService
import pytest, typing

admin_service = AdminService()

def test_empty_get_all_orders() -> None:
    assert admin_service.get_all_orders() == []

def test_empty_get_most_popular_restaurant() -> None:
    assert admin_service.get_most_popular_restaurant() == None