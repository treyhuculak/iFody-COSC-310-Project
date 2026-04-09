import datetime
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
        A wrapper function for the add_offer function of the OfferService class.
        Adds a new Offer instance to the database.
        '''
        return self.offer_service.add_offer(offer)
    
    def del_offer(self, offer: Offer) -> dict | None:
        '''
        A wrapper function for the del_offer function of the OfferService class.
        Deletes an existing Offer instance from the database.
        '''
        return self.offer_service.del_offer(offer)

    def get_active_offer(self) -> dict | None:
        '''
        A wrapper function for the get_active_offer function of the OfferService class.
        Retrieves the currently activated Offer instance if available.
        '''
        return self.offer_service.get_active_offer()
    
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
        if self.next_refresh == "N/A":
            return None
        try:
            target_deadline = datetime.datetime.fromisoformat(self.next_refresh)
        except ValueError:
            return None
        if current_time >= target_deadline:
            self.offer_service.refresh_offer_suggestions()
            self.offers = self.offer_service.get_offer_suggestions()
            if self.offers:
                self.next_refresh = self.offers[0]["end_date"]
            else:
                self.next_refresh = "N/A"
            return self.offers
        return None
        
    def activate_offer(self, offer_id: int) -> dict | None:
        '''
        A wrapper function for the activate_offer function of the OfferService class.
        Activates the corresponding Offer instance according to the provided offer_id.
        '''
        active_offer = self.offer_service.activate_offer(offer_id)
        self.offers = self.offer_service.get_offer_suggestions()
        return active_offer
        
    def deactivate_offer(self, offer_id: int) -> dict | None:
        '''
        A wrapper function for the deactivate_offer function of the OfferService class.
        Deactivates the corresponding Offer instance according to the provided offer_id.
        '''
        adjusted_offer = self.offer_service.deactivate_offer(offer_id)
        self.offers = self.offer_service.get_offer_suggestions()
        return adjusted_offer