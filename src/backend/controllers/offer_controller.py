import datetime
from fastapi import HTTPException
from src.backend.models.offer import Offer
from src.backend.services.offer_service import OfferService

class OfferController:
    def __init__(
            self,
            offer_service: OfferService = None
    ) -> None:
        '''
        Initializes the OfferController instance with the attributes.
        '''
        self.offer_service = offer_service or OfferService()
        self.offers = self.offer_service.get_offer_suggestions()
        if self.offers:
            self.next_refresh = self.offers[0]["end_date"]
        else:
            self.next_refresh = "N/A"

    def add_offer(self, offer: Offer) -> dict | None:
        '''
        A wrapper function for the add_offer function of the OfferRepository class.
        Adds a new Offer instance to the database.
        '''
        return self.offer_service.add_offer(offer)
    
    def del_offer(self, offer: Offer) -> dict | None:
        '''
        A wrapper function for the del_offer function of the OfferRepository class.
        Deletes an existing Offer instance from the database.
        '''
        return self.offer_service.del_offer(offer)
    
    def get_offer_suggestions(self) -> list[Offer]:
        '''
        Retrieves the suggested Offer instances for the users.
        '''
        return self.offers
    
    def refresh_offer_suggestions(self) -> list[Offer] | None:
        '''
        Refreshes the offer suggestions by retrieving the assigned amount of new Offer instances from the database at random.
        The function checks whether it is the correct time to retrieve new Offer instances.
        '''
        current_time = datetime.datetime.now()
        target_deadline = datetime.datetime.fromisoformat(self.next_refresh)
        if current_time >= target_deadline:
            self.offer_service.refresh_offer_suggestions()
            self.offers = self.offer_service.get_offer_suggestions()
            if self.offers:
                self.next_refresh = self.offers[0]["end_date"]
            else:
                self.next_refresh = "N/A"
            return self.offers
        else:
            return None
        
    def activate_offer(self, offer_id: int) -> dict | None:
        '''
        Activates the corresponding Offer instance according to the provided offer_id.
        Only one offer can be active at a time.
        '''
        if offer_id in [offer["offer_id"] for offer in self.offers]:
            if any([offer["is_active"] for offer in self.offers]):
                raise HTTPException(status_code = 409, detail = "Only one offer may be active simultaneously.")
            else:
                for i in len(self.offers):
                    if self.offers[i]["offer_id"] == offer_id:
                        self.offers[i]["is_active"] = True
                        return self.offers[i]
        else:
            return None
        
    def deactivate_offer(self, offer_id: int) -> dict | None:
        '''
        Deactivates the corresponding Offer instance according to the provided offer_id.
        '''
        if offer_id in [offer["offer_id"] for offer in self.offers]:
            for i in len(self.offers):
                if self.offers[i]["offer_id"] == offer_id:
                    if self.offers[i]["is_active"]:
                        self.offers[i]["is_active"] = False
                        return self.offers[i]
        else:
            return None