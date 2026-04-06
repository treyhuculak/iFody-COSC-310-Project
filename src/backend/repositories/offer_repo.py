import json
import random
from src.backend.models.offer import Offer

class OfferRepository:
    def __init__(self, database: str = None) -> None:
        '''
        Initializes the OfferRepository instance.
        '''
        self.offer_database = database or "data/offers.json"

        try:
            with open(self.offer_database, "r") as file:
                offers = json.load(file)
                if offers:
                    self.offer_id = max(offer["offer_id"] for offer in offers["Offers"]) + 1
                else:
                    self.offer_id = 1
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.offer_database, "w") as file:
                json.dump([], file, indent = 4)
                self.offer_id = 1

    def add_offer(self, offer: Offer) -> None:
        '''
        Adds a new Offer instance to the database.
        '''
        with open(self.offer_database, "r") as file:
            offers = json.load(file)
            offer.offer_id = self.offer_id
            self.offer_id += 1
            offer = offer.model_dump()
            offers.append(offer)
        with open(self.offer_database, "w") as file:
            json.dump(offers, file, indent = 4)

    def del_offer(self, offer: Offer) -> None:
        '''
        Deletes an existing Offer instance from the database.
        '''
        with open(self.offer_database, "r") as file:
            offers = json.load(file)
            offer = offer.model_dump()
            offers.remove(offer)
        with open(self.offer_database, "w") as file:
            json.dump(offers, file, indent = 4)

    def get_new_offers(self, amount: int) -> list[Offer]:
        '''
        Retrieves a specified number of Offer instances from the database.
        This is a helper function for getting weekly offers for the users.
        '''
        with open(self.offer_database, "r") as file:
            offers = json.load(file)
            if len(offers) < amount:
                offer_suggestions = offers
            else:
                offer_suggestions = random.choice(offers, k = amount)
        return offer_suggestions