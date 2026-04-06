import datetime
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
                    self.offer_id = max(offer["offer_id"] for offer in offers) + 1
                else:
                    self.offer_id = 1
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.offer_database, "w") as file:
                json.dump([], file, indent = 4)
                self.offer_id = 1

    def add_offer(self, offer: Offer) -> dict | None:
        '''
        Adds a new Offer instance to the database.
        '''
        with open(self.offer_database, "r") as file:
            offers = json.load(file)
            offer.offer_id = self.offer_id
            self.offer_id += 1
            offer = offer.model_dump()
            if hasattr(offer["offer_type"], "value"):
                offer["offer_type"] = offer["offer_type"].value
            if offer["title"] in [o["title"] for o in offers]:
                return None
            offers.append(offer)
        with open(self.offer_database, "w") as file:
            json.dump(offers, file, indent = 4)
            return offer

    def del_offer(self, offer: Offer) -> dict | None:
        '''
        Deletes an existing Offer instance from the database.
        '''
        with open(self.offer_database, "r") as file:
            offers = json.load(file)
            offer = offer.model_dump()
            if hasattr(offer["offer_type"], "value"):
                offer["offer_type"] = offer["offer_type"].value
            try:
                offers.remove(offer)
            except ValueError:
                return None
        with open(self.offer_database, "w") as file:
            json.dump(offers, file, indent = 4)
            return offer

    def get_new_offers(self, amount: int) -> list[Offer]:
        '''
        Retrieves a specified number of Offer instances from the database.
        This is a helper function for getting weekly offers for the users.
        '''
        with open(self.offer_database, "r") as file:
            offers = json.load(file)[:]
            if len(offers) < amount:
                offer_suggestions = offers
            else:
                offer_suggestions = random.sample(offers, k = amount)
            '''
            Dates should not be stored directly on the Offer instances in the database.
            The relevant attributes must be computed and assigned at retrieval time.
            '''
            current_date = datetime.datetime.now()
            offer_deadline = current_date + datetime.timedelta(days = 7)
            for offer in offer_suggestions:
                offer["start_date"] = current_date.isoformat()
                offer["end_date"] = offer_deadline.isoformat()
        return offer_suggestions