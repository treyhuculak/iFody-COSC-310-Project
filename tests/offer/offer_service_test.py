from fastapi import HTTPException
import json
import pytest
from src.backend.models.offer import Offer, OfferType
from src.backend.repositories.offer_repo import OfferRepository
from src.backend.services.offer_service import OfferService

offers = [
    Offer(
        offer_id = 0,
        restaurant_id = 1,
        title = "Test Offer 1",
        description = "This is the first test offer.",
        offer_type = OfferType.DISCOUNT,
        applied_items = [1, 2],
        discount_value = 10.0,
        price_ceiling = None,
        start_date = None,
        end_date = None,
        is_active = False
    ),
    Offer(
        offer_id = 0,
        restaurant_id = 2,
        title = "Test Offer 2",
        description = "This is the second test offer.",
        offer_type = OfferType.FREE_ITEM,
        applied_items = [3],
        discount_value = None,
        price_ceiling = None,
        start_date = None,
        end_date = None,
        is_active = False
    ),
    Offer(
        offer_id = 0,
        restaurant_id = 3,
        title = "Test Offer 3",
        description = "This is the third test offer.",
        offer_type = OfferType.PRICE_CEILING,
        applied_items = [4, 5],
        discount_value = None,
        price_ceiling = 20.0,
        start_date = None,
        end_date = None,
        is_active = False
    ),
    Offer(
        offer_id = 0,
        restaurant_id = 4,
        title = "Test Offer 4",
        description = "This is the fourth test offer.",
        offer_type = OfferType.DISCOUNT,
        applied_items = [6],
        discount_value = 15.0,
        price_ceiling = None,
        start_date = None,
        end_date = None,
        is_active = False
    )
]

@pytest.fixture
def offer_service_init():
    '''
    Creates a draft database for the OfferService instance for testing purposes.
    The draft database is deleted after the test is done.
    '''
    repo = OfferRepository("data/draft_offers.json", "data/temp_weekly_offers.json")
    for offer in offers:
        repo.add_offer(offer)
    service = OfferService(repo, offers_each_week = 3)
    yield service
    import os
    os.remove(os.getcwd() + "/data/draft_offers.json")
    os.remove(os.getcwd() + "/data/temp_weekly_offers.json")

def test_get_offer_suggestions(offer_service_init):
    '''
    Tests the get_offer_suggestions function of the OfferService class.
    '''
    offer_suggestions = offer_service_init.get_offer_suggestions()
    assert len(offer_suggestions) == 3
    for offer in offer_suggestions:
        assert offer["offer_id"] != 0
        assert "Test Offer" in offer["title"]
        assert offer["offer_type"] in [
            OfferType.DISCOUNT.value,
            OfferType.FREE_ITEM.value,
            OfferType.PRICE_CEILING.value
        ]

def test_refresh_offer_suggestions(offer_service_init):
    '''
    Tests the refresh_offer_suggestions function of the OfferService class.
    '''
    offer_suggestions_1 = offer_service_init.get_offer_suggestions()
    offer_service_init.refresh_offer_suggestions()
    offer_suggestions_2 = offer_service_init.get_offer_suggestions()
    assert len(offer_suggestions_2) == 3
    for offer in offer_suggestions_2:
        assert offer["offer_id"] != 0
        assert "Test Offer" in offer["title"]
        assert offer["offer_type"] in [
            OfferType.DISCOUNT.value,
            OfferType.FREE_ITEM.value,
            OfferType.PRICE_CEILING.value
        ]
    assert offer_suggestions_1 != offer_suggestions_2

def test_add_offer(offer_service_init):
    '''
    Tests the add_offer function of the OfferService class.
    '''
    offer = Offer(
        offer_id = 0,
        restaurant_id = 5,
        title = "Test Offer 5",
        description = "This is the fifth test offer.",
        offer_type = OfferType.DISCOUNT,
        applied_items = [7, 8],
        discount_value = 20.0,
        price_ceiling = None,
        start_date = None,
        end_date = None,
        is_active = False
    )
    offer_service_init.add_offer(offer)
    with open("data/draft_offers.json", "r") as file:
        offers = json.load(file)
        assert len(offers) == 5
        assert offers[4]["offer_id"] == 5
        assert offers[4]["title"] == "Test Offer 5"
        assert offers[4]["offer_type"] == OfferType.DISCOUNT.value

def test_del_offer(offer_service_init):
    '''
    Tests the del_offer function of the OfferService class.
    '''
    offer = Offer(
        offer_id = 0,
        restaurant_id = 5,
        title = "Test Offer 5",
        description = "This is the fifth test offer.",
        offer_type = OfferType.DISCOUNT,
        applied_items = [7, 8],
        discount_value = 20.0,
        price_ceiling = None,
        start_date = None,
        end_date = None,
        is_active = False
    )
    offer_service_init.add_offer(offer)
    with open("data/draft_offers.json", "r") as file:
        offers = json.load(file)
        assert len(offers) == 5
    offer_service_init.del_offer(offer)
    with open("data/draft_offers.json", "r") as file:
        offers = json.load(file)
        assert len(offers) == 4

def test_activate_offer(offer_service_init):
    '''
    Tests the activate_offer function of the OfferService class.
    '''
    # We activate one Offer instance first and check its is_active field.
    offer_suggestions = offer_service_init.get_offer_suggestions()
    offer_chosen = offer_suggestions[0]
    chosen_offer_id = offer_chosen["offer_id"]
    active_offer = offer_service_init.activate_offer(chosen_offer_id)
    assert any([offer["is_active"] for offer in offer_suggestions])
    assert active_offer == offer_chosen
    assert offer_suggestions[0]["is_active"]
    # Since one Offer instance is activated, we cannot activate another one.
    offer_chosen = offer_suggestions[1]
    chosen_offer_id = offer_chosen["offer_id"]
    with pytest.raises(HTTPException):
        active_offer = offer_service_init.activate_offer(chosen_offer_id)
    # Here it's the same situation, but we try to activate a different one.
    offer_chosen = offer_suggestions[2]
    chosen_offer_id = offer_chosen["offer_id"]
    with pytest.raises(HTTPException):
        active_offer = offer_service_init.activate_offer(chosen_offer_id)

def test_deactivate_offer(offer_service_init):
    '''
    Tests the activate_offer function of the OfferService class.
    '''
    # We activate one Offer instance first and check its is_active field.
    offer_suggestions = offer_service_init.get_offer_suggestions()
    offer_chosen_1 = offer_suggestions[0]
    chosen_offer_id_1 = offer_chosen_1["offer_id"]
    offer_service_init.activate_offer(chosen_offer_id_1)
    # Since one Offer instance is activated, we cannot activate another one.
    offer_chosen_2 = offer_suggestions[1]
    chosen_offer_id_2 = offer_chosen_2["offer_id"]
    with pytest.raises(HTTPException):
        offer_service_init.activate_offer(chosen_offer_id_2)
    # We deactivate the first Offer instance we selected, now the second Offer instance should be activatable.
    offer_service_init.deactivate_offer(chosen_offer_id_1)
    assert offer_chosen_2 == offer_service_init.activate_offer(chosen_offer_id_2)
    assert offer_chosen_2 == offer_service_init.get_active_offer()
    assert offer_chosen_2["is_active"]