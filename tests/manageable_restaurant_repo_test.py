import pytest, typing
from src.backend.repositories.manageable_restaurant_repo import \
    ManageableRestaurantRepository, NotARestaurantOwnerError, RestaurantLinkedException

repo = None
restaurant_owner_example = {
    "id": 1,
    "username": "TestRO",
    "email": "TestRO@123.com",
    "password": "Test@222",
    "role": "restaurant owner",
    "is_logged_in": True,
    "is_blocked": False
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
    Make sure there are three draft databases before each test function runs.
    '''
    global repo
    repo = ManageableRestaurantRepository(
        "data/temp_user_db.json",
        "data/temp_rest_db.json",
        "data/temp_link_db.json"
    )
    repo.user_repo._reinit_database()
    repo.user_repo.add_user(restaurant_owner_example)
    repo.rest_repo.add_restaurant(not_linked_restaurant_example)
    yield
    import os
    os.remove(os.getcwd() + "/data/temp_user_db.json")
    os.remove(os.getcwd() + "/data/temp_rest_db.json")
    os.remove(os.getcwd() + "/data/temp_link_db.json")

def test_valid_add_restaurant_to_restaurant_owner(setup_user_db) -> None:
    '''
    Tests linking an unlinked restaurant with a valid restaurant owner.
    '''
    repo.add_restaurant_to_restaurant_owner(restaurant_owner_example["id"], not_linked_restaurant_example["id"])

def test_add_linked_restaurant_to_restaurant_owner(setup_user_db) -> None:
    '''
    Tests linking a linked restaurant with a valid restaurant owner.
    '''
    # We first mark not_linked_restaurant_example as linked.
    repo.add_restaurant_to_restaurant_owner(restaurant_owner_example["id"], not_linked_restaurant_example["id"])
    with pytest.raises(RestaurantLinkedException):
        # The variable not_linked_restaurant_example is linked, so a RestaurantLinkedException should be raised now.
        repo.add_restaurant_to_restaurant_owner(restaurant_owner_example["id"], not_linked_restaurant_example["id"])

def test_add_restaurant_to_customer(setup_user_db) -> None:
    '''
    Tests attempting to link an unlinked restaurant to a customer, which should be treated as an invalid restaurant owner.
    '''
    customer = {
        "id": 2,
        "username": "NotARestaurantOwner",
        "email": "NotARestaurantOwner@123.com",
        "password": "Test@480",
        "role": "customer",
        "is_logged_in": True,
        "is_blocked": False
    }
    repo.user_repo.add_user(customer)
    with pytest.raises(NotARestaurantOwnerError):
        repo.add_restaurant_to_restaurant_owner(customer["id"], not_linked_restaurant_example["id"])