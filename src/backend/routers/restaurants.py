from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from src.backend.controllers.restaurant_controller import RestaurantController
from src.backend.models.restaurant import Restaurant, RestaurantCreate
from src.backend.models.menu_item import MenuItem, MenuItemCreate

router = APIRouter(
    prefix="/restaurants",
    tags=["restaurants"]
)

def get_controller():
    return RestaurantController()


@router.get("/", response_model=List[Restaurant])
def get_all_restaurants(controller: RestaurantController = Depends(get_controller)):
    return controller.get_all_restaurants()


@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: int, controller: RestaurantController = Depends(get_controller)):
    restaurant = controller.get_restaurant_by_id(restaurant_id)
    if isinstance(restaurant, dict) and "error" in restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.get("/{restaurant_id}/menu", response_model=List[MenuItem])
def get_all_menu_items_by_restaurant(restaurant_id: int, controller: RestaurantController = Depends(get_controller)):
    menu_items = controller.get_menu_items_by_restaurant_id(restaurant_id)
    if isinstance(menu_items, dict) and "error" in menu_items:
        raise HTTPException(status_code=404, detail="Menu items not found for restaurant")
    return menu_items


@router.post("/", response_model=Restaurant)
def add_restaurant(
    restaurant: RestaurantCreate, 
    controller: RestaurantController = Depends(get_controller)
):
    new_rest = controller.create_restaurant(restaurant)
    if isinstance(new_rest, dict) and "error" in new_rest:
        raise HTTPException(status_code=400, detail=new_rest["error"])
    return new_rest


@router.post("/{restaurant_id}/menu", response_model=MenuItem)
def add_menu_item(
    restaurant_id: int, 
    menu_item: MenuItemCreate, 
    controller: RestaurantController = Depends(get_controller)
):
    new_item = controller.add_menu_item_to_restaurant(menu_item, restaurant_id)
    if isinstance(new_item, dict) and "error" in new_item:
        raise HTTPException(status_code=400, detail=new_item["error"])
    return new_item


@router.put("/{restaurant_id}", response_model=Restaurant)
def update_restaurant(
    restaurant_id: int, 
    name: Optional[str] = None, 
    cuisine: Optional[str] = None,
    location: Optional[str] = None, 
    delivery_fee: Optional[float] = None,
    controller: RestaurantController = Depends(get_controller)
):
    updated_rest = controller.update_restaurant(restaurant_id=restaurant_id, name=name, cuisine=cuisine, delivery_fee=delivery_fee, location=location)
    if isinstance(updated_rest, dict) and "error" in updated_rest:
        raise HTTPException(status_code=400, detail=updated_rest["error"])
    return updated_rest


@router.delete("/{restaurant_id}", response_model=Restaurant)
def delete_restaurant(
    restaurant_id: int, 
    controller: RestaurantController = Depends(get_controller)
):
    deleted_rest = controller.delete_restaurant(restaurant_id)
    if isinstance(deleted_rest, dict) and "error" in deleted_rest:
        raise HTTPException(status_code=404, detail=deleted_rest["error"])
    return deleted_rest


@router.delete("/{restaurant_id}/menu/{menu_item_id}", response_model=MenuItem)
def delete_menu_item(
    restaurant_id: int, 
    menu_item_id: int, 
    controller: RestaurantController = Depends(get_controller)
):
    deleted_item = controller.delete_menu_item_from_restaurant(restaurant_id, menu_item_id)
    if isinstance(deleted_item, dict) and "error" in deleted_item:
        raise HTTPException(status_code=404, detail=deleted_item["error"])
    return deleted_item

@router.put("/{restaurant_id}/menu/{menu_item_id}", response_model=MenuItem)
def update_menu_item(
    restaurant_id: int, 
    menu_item_id: int, 
    name: Optional[str] = None, 
    description: Optional[str] = None, 
    price: Optional[float] = None,
    controller: RestaurantController = Depends(get_controller)
):
    updated_item = controller.update_menu_item_from_restaurant(restaurant_id=restaurant_id, menu_item_id=menu_item_id, name=name, description=description, price=price)
    if isinstance(updated_item, dict) and "error" in updated_item:
        raise HTTPException(status_code=404, detail=updated_item["error"])
    return updated_item
