import json
import pytest
from src.backend.repositories.offer_repo import OfferRepository
from src.backend.models.offer import Offer, OfferType

@pytest.fixture
def offer_repo_init():
    '''
    Creates a draft database for testing purposes.
    The draft database is deleted after the test is done.
    '''
    repo = OfferRepository("data/draft_offers.json")
    yield repo
    import os
    os.remove(os.getcwd() + "/data/draft_offers.json")

def test_add_offer(offer_repo_init):
    '''
    Tests the add_offer function of the OfferRepository class.
    '''
    offer = Offer(
        offer_id = 0,
        restaurant_id = 1,
        title = "Test Offer",
        description = "This is a test offer.",
        offer_type = OfferType.DISCOUNT,
        applied_items = [1, 2],
        discount_value = 10.0,
        price_ceiling = None,
        start_date = None,
        end_date = None,
        is_active = False
    )
    offer_repo_init.add_offer(offer)
    with open("data/draft_offers.json", "r") as file:
        offers = json.load(file)
        assert len(offers) == 1
        assert offers[0]["offer_id"] == 1
        assert offers[0]["title"] == "Test Offer"
        assert offers[0]["offer_type"] == OfferType.DISCOUNT.value

def test_del_offer(offer_repo_init):
    '''
    Tests the del_offer function of the OfferRepository class.
    '''
    offer = Offer(
        offer_id = 0,
        restaurant_id = 1,
        title = "Test Offer",
        description = "This is a test offer.",
        offer_type = OfferType.DISCOUNT.value,
        applied_items = [1, 2],
        discount_value = 10.0,
        price_ceiling = None,
        start_date = None,
        end_date = None,
        is_active = False
    )
    offer_repo_init.add_offer(offer)
    with open("data/draft_offers.json", "r") as file:
        offers = json.load(file)
        assert len(offers) == 1
    offer_repo_init.del_offer(offer)
    with open("data/draft_offers.json", "r") as file:
        offers = json.load(file)
        assert len(offers) == 0

def test_get_new_offers(offer_repo_init):
    '''
    Tests the get_new_offers function of the OfferRepository class.
    '''
    offer1 = Offer(
        offer_id = 0,
        restaurant_id = 1,
        title = "Test Offer 1",
        description = "This is a test offer.",
        offer_type = OfferType.DISCOUNT.value,
        applied_items = [1, 2],
        discount_value = 10.0,
        price_ceiling = None,
        start_date = None,
        end_date = None,
        is_active = False
    )
    offer2 = Offer(
        offer_id = 0,
        restaurant_id = 1,
        title = "Test Offer 2",
        description = "This is another test offer.",
        offer_type = OfferType.FREE_ITEM.value,
        applied_items = [3],
        discount_value = None,
        price_ceiling = None,
        start_date = None,
        end_date = None,
        is_active = False
    )
    offer_repo_init.add_offer(offer1)
    offer_repo_init.add_offer(offer2)
    new_offers = offer_repo_init.get_new_offers(1)
    assert len(new_offers) == 1
    new_offers = offer_repo_init.get_new_offers(2)
    assert len(new_offers) == 2
    new_offers = offer_repo_init.get_new_offers(10)
    assert len(new_offers) == 2