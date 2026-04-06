from src.backend.models.offer import Offer
from src.backend.repositories.offer_repo import OfferRepository

class OfferService:
    def __init__(
            self,
            offer_repo: OfferRepository = None,
            offers_each_week: int = 4
        ) -> None:
        '''
        Initializes the OfferService instance.
        The system retrieves four Offer instances by default and stores them in the offer_suggestions attribute.
        '''
        self.offer_repo = offer_repo or OfferRepository()
        self.offers_each_week = offers_each_week
        self.offer_suggestions = self.offer_repo.get_new_offers(self.offers_each_week)

    def add_offer(self, offer: Offer) -> dict | None:
        '''
        A wrapper function for the add_offer function of the OfferRepository class.
        Adds a new Offer instance to the database.
        '''
        self.offer_repo.add_offer(offer)

    def del_offer(self, offer: Offer) -> dict | None:
        '''
        A wrapper function for the del_offer function of the OfferRepository class.
        Deletes an existing Offer instance from the database.
        '''
        self.offer_repo.del_offer(offer)

    def get_offer_suggestions(self) -> list[Offer]:
        '''
        Retrieves the suggested Offer instances for the users.
        '''
        return self.offer_suggestions
    
    def refresh_offer_suggestions(self) -> None:
        '''
        Refreshes the offer suggestions by retrieving the assigned amount of new Offer instances from the database at random.
        '''
        self.offer_suggestions = self.offer_repo.get_new_offers(self.offers_each_week)