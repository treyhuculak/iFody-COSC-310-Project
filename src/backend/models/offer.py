from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class OfferType(Enum):
    '''
    There are 3 types of offers.

    DISCOUNT: A percentage discount on the total price of the order.
    FREE_ITEM: A free item gets added to the order when the condition is met.
    PRICE_CEILING: The total price of the order is fixed once the condition is met.
    '''
    DISCOUNT = 1
    FREE_ITEM = 2
    PRICE_CEILING = 3

class Offer(BaseModel):
    '''
    The foundation of the offer model.
    '''
    offer_id: int
    restaurant_id: int
    title: str
    description: str
    offer_type: OfferType
    applied_items: list[int]
    discount_value: float | None = None
    price_ceiling: float | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_active: bool