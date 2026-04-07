from fastapi import APIRouter, Depends, HTTPException
from src.backend.controllers.offer_controller import OfferController
from src.backend.models.offer import Offer

router = APIRouter(
    prefix="/offers",
    tags=["offers"]
)

def get_controller():
    '''
    Returns the OfferController instance.
    '''
    return OfferController()

@router.post("/offers")
def add_offer(offer: Offer, controller: OfferController = Depends(get_controller)):
    '''
    Receives an Offer instance and calls the offer_controller's add_offer method.
    Returns the added Offer instance as a dictionary if successful, or an error message if the instance already exists.
    '''
    result = controller.add_offer(offer)
    if result is None:
        raise HTTPException(status_code = 409, detail = "Offer with this title already exists.")
    return result

@router.delete("/offers")
def del_offer(offer: Offer, controller: OfferController = Depends(get_controller)):
    '''
    Receives an Offer instance and calls the offer_controller's del_offer method.
    Returns the deleted Offer instance as a dictionary if successful, or an error message if the instance does not exist.
    '''
    result = controller.del_offer(offer)
    if result is None:
        raise HTTPException(status_code = 404, detail = "The Offer to be deleted does not exist.")
    return result

@router.get("/active")
def get_active_offer(controller: OfferController = Depends(get_controller)):
    '''
    Calls the offer_controller's get_active_offer method.
    Returns the currently activated Offer instance as a dictionary if available, or an error message if no active Offer exists.
    '''
    result = controller.get_active_offer()
    if result is None:
        raise HTTPException(status_code = 404, detail = "There is no active offer at the moment.")
    return result

@router.get("/suggestions")
def get_offer_suggestions(controller: OfferController = Depends(get_controller)):
    '''
    Calls the offer_controller's get_offer_suggestions method.
    Returns the list of suggested Offer instances for the users.
    '''
    return controller.get_offer_suggestions()

@router.post("/refresh")
def refresh_offer_suggestions(controller: OfferController = Depends(get_controller)):
    '''
    Calls the offer_controller's refresh_offer_suggestions method.
    Returns the refreshed list of suggested Offer instances for the users if it is the correct time to refresh.
    '''
    result = controller.refresh_offer_suggestions()
    if result is None:
        raise HTTPException(status_code = 400, detail = "Offer suggestions can only be refreshed once every 7 days.")
    return result

@router.post("/activate/{offer_id}")
def activate_offer(offer_id: int, controller: OfferController = Depends(get_controller)):
    '''
    Calls the offer_controller's activate_offer method with the provided offer_id.
    Returns the activated Offer instance as a dictionary if successful, or an error message if the instance does not exist or if another instance is already active.
    '''
    result = controller.activate_offer(offer_id)
    if result is None:
        raise HTTPException(status_code = 409, detail = "The Offer to be activated does not exist, or an Offer instance is already active.")
    return result

@router.post("/deactivate/{offer_id}")
def deactivate_offer(offer_id: int, controller: OfferController = Depends(get_controller)):
    '''
    Calls the offer_controller's deactivate_offer method with the provided offer_id.
    Returns the deactivated Offer instance as a dictionary if successful, or an error message if the instance does not exist or is not currently active.
    '''
    result = controller.deactivate_offer(offer_id)
    if result is None:
        raise HTTPException(status_code = 404, detail = "The Offer to be deactivated does not exist or is not currently active.")
    return result