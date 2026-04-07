from fastapi import HTTPException
import json
import pytest
from src.backend.controllers.offer_controller import OfferController
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
def offer_controller_init():
    '''
    Creates an instance of the OfferController class, with draft databases.
    '''
    repo = OfferRepository(database = "data/test_offers.json")
    for offer in offers:
        repo.add_offer(offer)
    service = OfferService(repo, 3)
    controller = OfferController(service)
    yield controller
    import os
    os.remove(os.getcwd() + "/data/test_offers.json")

def test_add_offer(offer_controller_init):
    '''
    Tests the add_offer function of the OfferController class.
    '''
    offer = Offer(
        offer_id = 0,
        restaurant_id = 5,
        title = "Test Offer 5",
        description = "This is the fifth test offer.",
        offer_type = OfferType.FREE_ITEM,
        applied_items = [7],
        discount_value = None,
        price_ceiling = None,
        start_date = None,
        end_date = None,
        is_active = False
    )
    result = offer_controller_init.add_offer(offer)
    assert result != None
    assert result["title"] == "Test Offer 5"

def test_del_offer(offer_controller_init):
    '''
    Tests the del_offer function of the OfferController class.
    '''
    offer = Offer(
        offer_id = 1,
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
    )
    result = offer_controller_init.del_offer(offer)
    assert result != None
    assert result["title"] == "Test Offer 1"
    with open("data/test_offers.json", "r") as file:
        offers = json.load(file)
        assert "Test Offer 1" not in [offer["title"] for offer in offers]

def test_get_active_order(offer_controller_init):
    '''
    Tests the get_active_order function of the OfferController class.
    '''
    chosen_offer = offer_controller_init.get_offer_suggestions()[0]
    chosen_offer_id = chosen_offer["offer_id"]
    offer_controller_init.activate_offer(chosen_offer_id)
    assert offer_controller_init.get_active_offer() == chosen_offer

def test_get_offer_suggestions(offer_controller_init):
    '''
    Tests the get_offer_suggestions function of the OfferController class.
    '''
    assert offer_controller_init.get_offer_suggestions() != None
    assert len(offer_controller_init.get_offer_suggestions()) == 3

def test_refresh_offer_suggestions(offer_controller_init):
    '''
    Tests the refresh_offer_suggestions function of the OfferController class.
    We are actually testing that a manual refresh is forbidden because we need to wait 7 days.
    '''
    assert offer_controller_init.refresh_offer_suggestions() == None

def test_activate_offer(offer_controller_init):
    '''
    Tests the activate_offer function of the OfferController class.
    '''
    offers = offer_controller_init.get_offer_suggestions()
    chosen_offer = offers[0]
    chosen_offer_id = chosen_offer["offer_id"]
    assert chosen_offer == offer_controller_init.activate_offer(chosen_offer_id)
    another_offer = offers[1]
    another_offer_id = another_offer["offer_id"]
    with pytest.raises(HTTPException):
        offer_controller_init.activate_offer(another_offer_id)

def test_deactivate_offer(offer_controller_init):
    '''
    Tests the deactivate_offer function of the OfferController class.
    '''
    offers = offer_controller_init.get_offer_suggestions()
    chosen_offer = offers[0]
    chosen_offer_id = chosen_offer["offer_id"]
    offer_controller_init.activate_offer(chosen_offer_id)
    another_offer = offers[1]
    another_offer_id = another_offer["offer_id"]
    with pytest.raises(HTTPException):
        offer_controller_init.activate_offer(another_offer_id)
    offer_controller_init.deactivate_offer(chosen_offer_id)
    assert another_offer == offer_controller_init.activate_offer(another_offer_id)