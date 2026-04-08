from fastapi.testclient import TestClient
import json, pytest
from src.backend.controllers.offer_controller import OfferController
from src.backend.main import app
from src.backend.repositories.offer_repo import OfferRepository
from src.backend.routers.offer import get_controller
from src.backend.services.offer_service import OfferService

@pytest.fixture
def test_client(tmp_path):
    '''
    Provides a TestClient backed by a temporary JSON file instead of the real database.
    The temporary file is automatically deleted after each test so the production database is never touched.
    '''
    draft_offer_database = tmp_path / "draft_offer_database.json"
    draft_offer_database.write_text(
        json.dumps(
            [
                {
                    "offer_id": 1,
                    "restaurant_id": 1,
                    "title": "Lunch Special - 10% off",
                    "description": "Get 10% off your entire order between 11:00 and 14:00.",
                    "offer_type": 1,
                    "applied_items": [],
                    "discount_value": 10.0,
                    "price_ceiling": None,
                    "start_date": None,
                    "end_date": None,
                    "is_active": False
                },
                {
                    "offer_id": 2,
                    "restaurant_id": 1,
                    "title": "Free Miso Soup",
                    "description": "Receive a free Miso Soup with purchase.",
                    "offer_type": 2,
                    "applied_items": [
                        4
                    ],
                    "discount_value": None,
                    "price_ceiling": None,
                    "start_date": None,
                    "end_date": None,
                    "is_active": False
                },
                {
                    "offer_id": 3,
                    "restaurant_id": 2,
                    "title": "Brisket Plate Deal - $15",
                    "description": "Get the Smoked Brisket Plate for a fixed total of $15.",
                    "offer_type": 3,
                    "applied_items": [
                        1
                    ],
                    "discount_value": None,
                    "price_ceiling": 15.0,
                    "start_date": None,
                    "end_date": None,
                    "is_active": False
                },
                {
                    "offer_id": 4,
                    "restaurant_id": 2,
                    "title": "Wing Night - 15% off",
                    "description": "Save 15% on BBQ Chicken Wings every Tuesday.",
                    "offer_type": 1,
                    "applied_items": [
                        3
                    ],
                    "discount_value": 15.0,
                    "price_ceiling": None,
                    "start_date": None,
                    "end_date": None,
                    "is_active": False
                }
            ]
        )
    )

    draft_offer_repo = OfferRepository(str(draft_offer_database))
    draft_offer_service = OfferService(draft_offer_repo, 3)
    draft_controller = OfferController(draft_offer_service)

    app.dependency_overrides[get_controller] = lambda: draft_controller
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_add_unique_offer(test_client):
    '''
    Tests the add_offer function using a unique Offer instance.
    '''
    response = test_client.post(
        "/offers/offers",
        json = {
            "offer_id": 5,
            "restaurant_id": 3,
            "title": "Tiramisu On Us",
            "description": "Free Tiramisu with purchase.",
            "offer_type": 2,
            "applied_items": [
                5
            ],
            "discount_value": None,
            "price_ceiling": None,
            "start_date": None,
            "end_date": None,
            "is_active": False
        }
    )
    assert response.status_code == 200

def test_add_duplicated_offer(test_client):
    '''
    Tests the add_offer function using a duplicated Offer instance.
    '''
    response = test_client.post(
        "/offers/offers",
        json = {
            "offer_id": 1,
            "restaurant_id": 1,
            "title": "Lunch Special - 10% off",
            "description": "Get 10% off your entire order between 11:00 and 14:00.",
            "offer_type": 1,
            "applied_items": [],
            "discount_value": 10.0,
            "price_ceiling": None,
            "start_date": None,
            "end_date": None,
            "is_active": False
        }
    )
    assert response.status_code == 409

def test_del_existing_offer(test_client):
    '''
    Tests the del_offer function using an existing Offer instance.
    '''
    response = test_client.request(
        "DELETE",
        "/offers/offers",
        json={
            "offer_id": 1,
            "restaurant_id": 1,
            "title": "Lunch Special - 10% off",
            "description": "Get 10% off your entire order between 11:00 and 14:00.",
            "offer_type": 1,
            "applied_items": [],
            "discount_value": 10.0,
            "price_ceiling": None,
            "start_date": None,
            "end_date": None,
            "is_active": False
        }
    )
    assert response.status_code == 200

def test_del_nonexistent_offer(test_client):
    '''
    Tests the del_offer function using a nonexistent Offer instance.
    '''
    response = test_client.request(
        "DELETE",
        "/offers/offers",
        json = {
            "offer_id": 6,
            "restaurant_id": 3,
            "title": "Pizza Promo - 20% off",
            "description": "Enjoy 20% off Margherita Pizza for a limited time.",
            "offer_type": 1,
            "applied_items": [
                1
            ],
            "discount_value": 20.0,
            "price_ceiling": None,
            "start_date": None,
            "end_date": None,
            "is_active": False
        }
    )
    assert response.status_code == 404

def test_get_offer_suggestions(test_client):
    '''
    Tests the get_offer_suggestions function.
    '''
    response = test_client.get("/offers/suggestions")
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_refresh_offer_suggestions(test_client):
    '''
    Tests the refresh_offer_suggestions function.
    The function should not allow manual refreshing.
    '''
    response = test_client.post("/offers/refresh")
    assert response.status_code == 400

def test_activate_offer_with_no_existing_active_offers(test_client):
    '''
    Tests the activate_offer function when no active Offer instance currently exists.
    '''
    offers = test_client.get("/offers/suggestions").json()
    chosen_offer = offers[0]
    chosen_offer_id = chosen_offer["offer_id"]
    response = test_client.post(f"/offers/activate/{chosen_offer_id}")
    assert response.status_code == 200

def test_activate_offer_with_an_existing_active_offer(test_client):
    '''
    Tests the activate_offer function when an active Offer instance currently exists.
    '''
    offers = test_client.get("/offers/suggestions").json()
    chosen_offer = offers[0]
    chosen_offer_id = chosen_offer["offer_id"]
    test_client.post(f"/offers/activate/{chosen_offer_id}")
    response = test_client.post(f"/offers/activate/{chosen_offer_id}")
    assert response.status_code == 409
    another_offer = offers[1]
    another_offer_id = another_offer["offer_id"]
    response = test_client.post(f"/offers/activate/{another_offer_id}")
    assert response.status_code == 409

def test_deactivate_offer_with_valid_offer_instance(test_client):
    '''
    Tests the deactivate_offer function when an active Offer instance currently exists.
    '''
    offers = test_client.get("/offers/suggestions").json()
    chosen_offer = offers[0]
    chosen_offer_id = chosen_offer["offer_id"]
    test_client.post(f"/offers/activate/{chosen_offer_id}")
    response = test_client.post(f"/offers/deactivate/{chosen_offer_id}")
    assert response.status_code == 200

def test_deactivate_offer_with_invalid_offer_instance(test_client):
    '''
    Tests the deactivate_offer function when no active Offer instance currently exists.
    '''
    offers = test_client.get("/offers/suggestions").json()
    chosen_offer = offers[0]
    chosen_offer_id = chosen_offer["offer_id"]
    response = test_client.post(f"/offers/deactivate/{chosen_offer_id}")
    assert response.status_code == 404
    invalid_id = 100
    response = test_client.post(f"/offers/deactivate/{invalid_id}")
    assert response.status_code == 404

def test_get_active_offer(test_client):
    '''
    Tests get_active_offer with and without an active Offer instance.
    '''
    offers = test_client.get("/offers/suggestions").json()
    chosen_offer = offers[0]
    chosen_offer_id = chosen_offer["offer_id"]
    test_client.post(f"/offers/activate/{chosen_offer_id}")
    response = test_client.get("/offers/active")
    assert response.status_code == 200
    test_client.post(f"/offers/deactivate/{chosen_offer_id}")
    response = test_client.get("/offers/active")
    assert response.status_code == 404