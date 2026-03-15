import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.orders import get_controller
from src.backend.repositories.order_repo import OrderRepository
from src.backend.controllers.order_controller import OrderController
from src.backend.models.order import OrderCreate, OrderStatus, OrderLocation


def test_add_review_to_order(test_client):
    # First, create an order to review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Now add a review for that order
    review_data = {
        "rating": 4,
        "title": "Good food, slow delivery",
        "comment": "Great food, but delivery was slow."
    }
    review_response = test_client.post(f"/orders/{order_id}/review", json=review_data)
    assert review_response.status_code == 200
    created_review = review_response.json()
    assert created_review["rating"] == review_data["rating"]
    assert created_review["comment"] == review_data["comment"]
    assert created_review["title"] == review_data["title"]

    
def test_add_review_to_nonexistent_order(test_client):
    review_data = {
        "rating": 5,
        "title": "Excellent!",
        "comment": "Best meal ever!"
    }
    response = test_client.post("/orders/999/review", json=review_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Order with id 999 not found."

    
def test_add_review_with_invalid_rating(test_client):
    # First, create an order to review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Now try to add a review with an invalid rating
    review_data = {
        "rating": 6,  # Invalid rating (should be between 1 and 5)
        "title": "Invalid rating",
        "comment": "This review has an invalid rating."
    }
    review_response = test_client.post(f"/orders/{order_id}/review", json=review_data)
    assert review_response.status_code == 422


def test_add_review_with_missing_fields(test_client):
    # First, create an order to review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Now try to add a review with missing fields
    review_data = {
        "rating": 4,
        # Missing title and comment
    }
    review_response = test_client.post(f"/orders/{order_id}/review", json=review_data)
    assert review_response.status_code == 422


def test_add_review_to_order_with_existing_review(test_client):
    # First, create an order to review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Add the first review
    review_data_1 = {
        "rating": 4,
        "title": "Good food",
        "comment": "The food was good."
    }
    review_response_1 = test_client.post(f"/orders/{order_id}/review", json=review_data_1)
    assert review_response_1.status_code == 200

    # Now try to add a second review for the same order
    review_data_2 = {
        "rating": 2,
        "title": "Changed my mind",
        "comment": "Actually, the food was not that good."
    }
    review_response_2 = test_client.post(f"/orders/{order_id}/review", json=review_data_2)
    assert review_response_2.status_code == 400
    assert review_response_2.json()["detail"] == f"Order with id {order_id} already has a review."


def test_delete_review_from_order(test_client):
    # First, create an order to review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Add a review for that order
    review_data = {
        "rating": 4,
        "title": "Good food",
        "comment": "The food was good."
    }
    review_response = test_client.post(f"/orders/{order_id}/review", json=review_data)
    assert review_response.status_code == 200

    # Now delete the review
    delete_response = test_client.delete(f"/orders/{order_id}/review")
    assert delete_response.status_code == 200


def test_delete_nonexistent_review(test_client):
    # First, create an order without a review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Now try to delete a review that doesn't exist
    delete_response = test_client.delete(f"/orders/{order_id}/review")
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == f"Review for order with id {order_id} not found."


def test_update_review_from_order(test_client):
    # First, create an order to review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Add a review for that order
    review_data = {
        "rating": 4,
        "title": "Good food",
        "comment": "The food was good."
    }
    review_response = test_client.post(f"/orders/{order_id}/review", json=review_data)
    assert review_response.status_code == 200

    # Now update the review
    updated_review_data = {
        "rating": 5,
        "title": "Actually it was great",
        "comment": "I changed my mind the food was great"
    }
    update_response = test_client.put(f"/orders/{order_id}/review", json=updated_review_data)
    assert update_response.status_code == 200
    updated_review = update_response.json()
    assert updated_review["rating"] == updated_review_data["rating"]
    assert updated_review["comment"] == updated_review_data["comment"]
    assert updated_review["title"] == updated_review_data["title"]


def test_update_nonexistent_review(test_client):
    # First, create an order without a review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Now try to update a review that doesn't exist
    updated_review_data = {
        "rating": 5,
        "title": "Nonexistent review",
        "comment": "Trying to update a review that doesn't exist."
    }
    update_response = test_client.put(f"/orders/{order_id}/review", json=updated_review_data)
    # should create the review if it doesn't exist, so we expect a 200 response with the new review data
    assert update_response.status_code == 200


def test_get_review_from_order(test_client):
    # First, create an order to review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Add a review for that order
    review_data = {
        "rating": 4,
        "title": "Good food",
        "comment": "The food was good."
    }
    review_response = test_client.post(f"/orders/{order_id}/review", json=review_data)
    assert review_response.status_code == 200

    # Now get the review
    get_response = test_client.get(f"/orders/{order_id}/review")
    assert get_response.status_code == 200
    retrieved_review = get_response.json()
    assert retrieved_review["rating"] == review_data["rating"]
    assert retrieved_review["comment"] == review_data["comment"]
    assert retrieved_review["title"] == review_data["title"]


def test_get_nonexistent_review(test_client):
    # First, create an order without a review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Now try to get a review that doesn't exist
    get_response = test_client.get(f"/orders/{order_id}/review")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == f"Review for order with id {order_id} not found."