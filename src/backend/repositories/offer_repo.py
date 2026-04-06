import json

class OfferRepository:
    def __init__(self, database: str = None) -> None:
        self.offer_database = database or "data/offers.json"