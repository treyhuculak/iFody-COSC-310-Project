import json
from fastapi import HTTPException
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
        return self.offer_repo.add_offer(offer)

    def del_offer(self, offer: Offer) -> dict | None:
        '''
        A wrapper function for the del_offer function of the OfferRepository class.
        Deletes an existing Offer instance from the database.
        '''
        return self.offer_repo.del_offer(offer)

    def get_active_offer(self) -> dict | None:
        '''
        Retrieves the currently activated Offer instance if available.
        '''
        if any([offer["is_active"] for offer in self.offer_suggestions]):
            return [offer for offer in self.offer_suggestions if offer["is_active"]][0]
        else:
            return None

    def get_offer_suggestions(self) -> list[Offer]:
        '''
        Retrieves the suggested Offer instances for the users.
        '''
        return self.offer_suggestions
    
    def activate_offer(self, offer_id: int) -> dict | None:
        '''
        Activates the corresponding Offer instance according to the provided offer_id.
        Only one offer can be active at a time.
        '''
        if offer_id in [offer["offer_id"] for offer in self.offer_suggestions]:
            if any([offer["is_active"] for offer in self.offer_suggestions]):
                raise HTTPException(status_code = 409, detail = "Only one offer may be active simultaneously.")
            else:
                for i in range(len(self.offer_suggestions)):
                    if self.offer_suggestions[i]["offer_id"] == offer_id:
                        self.offer_suggestions[i]["is_active"] = True
                        weekly_offers_file = self.offer_repo.get_weekly_offers_file()
                        with open(weekly_offers_file, "w") as file:
                            json.dump(self.offer_suggestions, file, indent = 4)
                        return self.offer_suggestions[i]
        else:
            return None
        
    def deactivate_offer(self, offer_id: int) -> dict | None:
        '''
        Deactivates the corresponding Offer instance according to the provided offer_id.
        '''
        if offer_id in [offer["offer_id"] for offer in self.offer_suggestions]:
            for i in range(len(self.offer_suggestions)):
                if self.offer_suggestions[i]["offer_id"] == offer_id:
                    if self.offer_suggestions[i]["is_active"]:
                        self.offer_suggestions[i]["is_active"] = False
                        weekly_offers_file = self.offer_repo.get_weekly_offers_file()
                        with open(weekly_offers_file, "w") as file:
                            json.dump(self.offer_suggestions, file, indent = 4)
                        return self.offer_suggestions[i]
        else:
            return None
    
    def refresh_offer_suggestions(self) -> None:
        '''
        Refreshes the offer suggestions by retrieving the assigned amount of new Offer instances from the database at random.
        '''
        weekly_offers_file = self.offer_repo.get_weekly_offers_file()
        with open(weekly_offers_file, "w") as file: file.write("[]")
        self.offer_suggestions = self.offer_repo.get_new_offers(self.offers_each_week)