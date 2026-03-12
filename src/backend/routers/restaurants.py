from email.policy import default

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from src.backend.controllers.restaurant_controller import RestaurantController
from src.backend.models.restaurant import Restaurant, RestaurantCreate
from src.backend.models.menu_item import MenuItem, MenuItemCreate
from src.backend.models.pagination import PaginatedResponse
from src.backend.utils.auth_dependencies import requires_role

router = APIRouter(
    prefix="/restaurants",
    tags=["restaurants"]
)

def get_controller():
    return RestaurantController()

def get_user_id_from_auth():
    # TODO: Implement authentication and extract user ID from the token/session
    return 1  # Placeholder for testing purposes


@router.get("/owner/{owner_id}", response_model=PaginatedResponse[Restaurant])
def get_restaurants_by_owner(
    owner_id: int, 
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    controller: RestaurantController = Depends(get_controller)):
    return controller.get_restaurants_by_owner(owner_id, skip=skip, limit=limit)

@router.get("/location/{location}", response_model=PaginatedResponse[Restaurant])
def get_restaurants_by_location(
    location: str, 
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    controller: RestaurantController = Depends(get_controller)):
    return controller.get_restaurants_by_location(location, skip=skip, limit=limit)

@router.get("/filter", response_model=PaginatedResponse[Restaurant])
def filter_restaurants(
    cuisine: str = Query(default=""),
    location: str = Query(default=""),
    max_fee: float = Query(default=0, ge=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    controller: RestaurantController = Depends(get_controller)
):
    return controller.filter_restaurants(cuisine=cuisine, location=location, max_fee=max_fee, skip=skip, limit=limit)

@router.get("/search", response_model=PaginatedResponse[Restaurant])
def search_restaurants(
    name: str = Query(default=""), 
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    controller: RestaurantController = Depends(get_controller)):
    return controller.get_restaurants_by_partial_name(name, skip=skip, limit=limit)

@router.get("", response_model=PaginatedResponse[Restaurant])
def get_all_restaurants(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    controller: RestaurantController = Depends(get_controller)
    ):
    return controller.get_all_restaurants(skip=skip, limit=limit)


@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: int, controller: RestaurantController = Depends(get_controller)):
    restaurant = controller.get_restaurant_by_id(restaurant_id)
    return restaurant


@router.get("/{restaurant_id}/menu", response_model=PaginatedResponse[MenuItem])
def get_all_menu_items_by_restaurant(
    restaurant_id: int, 
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    controller: RestaurantController = Depends(get_controller)):
    menu_items = controller.get_menu_items_by_restaurant_id(restaurant_id, skip=skip, limit=limit)
    return menu_items

@router.get("/{restaurant_id}/menu/search", response_model=PaginatedResponse[MenuItem])
def search_menu_items(
    restaurant_id: int, 
    name: str = Query(default=""), 
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    controller: RestaurantController = Depends(get_controller)):
    return controller.get_menu_items_by_partial_name(restaurant_id, name, skip=skip, limit=limit)

@router.get("/{restaurant_id}/menu/filter", response_model=PaginatedResponse[MenuItem])
def filter_menu_items(
    restaurant_id: int, 
    max_price: float = Query(default=0, gt=0), 
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    controller: RestaurantController = Depends(get_controller)
):
    return controller.filter_menu_items(restaurant_id, max_price, skip=skip, limit=limit)

@router.get("/{restaurant_id}/menu/{menu_item_id}", response_model=MenuItem)
def get_menu_item_by_id(restaurant_id: int, menu_item_id: int, controller: RestaurantController = Depends(get_controller)):
    menu_items = controller.get_menu_items_by_restaurant_id(restaurant_id)
    if isinstance(menu_items, list):
        for item in menu_items:
            if isinstance(item, dict) and item.get("id") == menu_item_id:
                return item
    raise HTTPException(status_code=404, detail="Menu item not found")

@router.post("", response_model=Restaurant)
def add_restaurant(
    restaurant: RestaurantCreate, 
    controller: RestaurantController = Depends(get_controller),
    current_user_id: int = Depends(get_user_id_from_auth),
    current_user: dict = Depends(requires_role("RestaurantOwner"))
):
    new_rest = controller.add_restaurant(restaurant, owner_id=current_user_id)
    return new_rest


@router.post("/{restaurant_id}/menu", response_model=MenuItem)
def add_menu_item(
    restaurant_id: int, 
    menu_item: MenuItemCreate, 
    controller: RestaurantController = Depends(get_controller),
    current_user: dict = Depends(requires_role("RestaurantOwner"))
):
    new_item = controller.add_menu_item_to_restaurant(menu_item, restaurant_id)
    return new_item


@router.put("/{restaurant_id}", response_model=Restaurant)
def update_restaurant(
    restaurant_id: int, 
    name: Optional[str] = None, 
    cuisine: Optional[str] = None,
    location: Optional[str] = None, 
    delivery_fee: Optional[float] = Query(default=None, ge=0),
    is_available: Optional[bool] = None,
    controller: RestaurantController = Depends(get_controller),
):
    updated_rest = controller.update_restaurant(restaurant_id=restaurant_id, name=name, cuisine=cuisine, delivery_fee=delivery_fee, location=location, is_available=is_available)
    return updated_rest


@router.delete("/{restaurant_id}", response_model=Restaurant)
def delete_restaurant(
    restaurant_id: int, 
    controller: RestaurantController = Depends(get_controller),
    current_user: dict = Depends(requires_role("RestaurantOwner"))
):
    deleted_rest = controller.delete_restaurant(restaurant_id)
    return deleted_rest


@router.delete("/{restaurant_id}/menu/{menu_item_id}", response_model=MenuItem)
def delete_menu_item(
    restaurant_id: int, 
    menu_item_id: int, 
    controller: RestaurantController = Depends(get_controller),
    current_user: dict = Depends(requires_role("RestaurantOwner"))
):
    deleted_item = controller.delete_menu_item_from_restaurant(restaurant_id, menu_item_id)
    return deleted_item

@router.put("/{restaurant_id}/menu/{menu_item_id}", response_model=MenuItem)
def update_menu_item(
    restaurant_id: int, 
    menu_item_id: int, 
    name: Optional[str] = None, 
    description: Optional[str] = None, 
    price: Optional[float] = Query(default=None, gt=0),
    controller: RestaurantController = Depends(get_controller),
    current_user: dict = Depends(requires_role("RestaurantOwner"))
):
    updated_item = controller.update_menu_item_from_restaurant(restaurant_id=restaurant_id, menu_item_id=menu_item_id, name=name, description=description, price=price)
    return updated_item
