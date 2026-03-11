import pytest, typing
from src.backend.repositories.manageable_restaurant_repo import \
    ManageableRestaurantRepository, NotARestaurantOwnerError, RestaurantLinkedException
from src.backend.repositories.restaurant_repo import RestaurantRepository

repo = ManageableRestaurantRepository(
        "data/temp_user_db.json",
        "data/temp_rest_db.json",
        "data/temp_link_db.json"
)
user_example = {
    "id": 1,
    "username": "TestRO",
    "email": "TestRO@123.com",
    "password": "Test@222",
    "role": "restaurant owner",
    "is_logged_in": True,
    "is_blocked": False
}
linked_restaurant_example = {
    "name": "The Gourmet Kitchen",
    "cuisine": "Italian",
    "location": "Kelowna, BC",
    "delivery_fee": 5.99,
    "owner_id": 1,
    "id": 1,
    "is_available": True,
    "menu_items": [
        {
            "name": "Spaghetti Carbonara",
            "description": "Classic Italian pasta with creamy sauce, pancetta, and Parmesan cheese.",
            "price": 12.99,
            "id": 1
        },
        {
            "name": "Margherita Pizza",
            "description": "Traditional pizza with fresh tomatoes, mozzarella, basil, and olive oil.",
            "price": 10.99,
            "id": 2
        }
    ],
    "is_linked": True
}
not_linked_restaurant_example = {
    "name": "The Sushi World",
    "cuisine": "Japanese",
    "location": "Vancouver, BC",
    "delivery_fee": 3.99,
    "owner_id": 2,
    "id": 2,
    "is_available": True,
    "menu_items": [
        {
            "name": "California Roll",
            "description": "Crab, avocado, cucumber, and sushi rice rolled in seaweed.",
            "price": 8.99,
            "id": 1
        },
        {
            "name": "Spicy Tuna Roll",
            "description": "Tuna mixed with spicy mayo, rolled with sushi rice and seaweed.",
            "price": 9.99,
            "id": 2
        }
    ],
    "is_linked": False
}

@pytest.fixture
def setup_user_db() -> typing.Generator:
    '''
    Make sure there are three empty draft databases before each test function runs.
    '''
    repo = ManageableRestaurantRepository(
        "data/temp_user_db.json",
        "data/temp_rest_db.json",
        "data/temp_link_db.json"
    )
    repo.user_repo.add_user(user_example)
    repo.rest_repo.add_restaurant(linked_restaurant_example)
    repo.rest_repo.add_restaurant(not_linked_restaurant_example)
    yield
    import os
    os.remove(os.getcwd() + "/data/temp_user_db.json")
    os.remove(os.getcwd() + "/data/temp_rest_db.json")
    os.remove(os.getcwd() + "/data/temp_link_db.json")

def test_valid_add_restaurant_to_restaurant_owner(setup_user_db) -> None:
    repo.add_restaurant_to_restaurant_owner(user_example["id"], not_linked_restaurant_example["id"])