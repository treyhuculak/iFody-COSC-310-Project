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
    repo = OfferRepository("data/draft_offers.json")
    for offer in offers:
        repo.add_offer(offer)
    service = OfferService(repo, offers_each_week = 3)
    yield service
    import os
    os.remove(os.getcwd() + "/data/draft_offers.json")

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