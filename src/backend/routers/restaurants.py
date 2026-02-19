from fastapi import APIRouter, Depends, HTTPException
from typing import List
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
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.get("/{restaurant_id}/menu", response_model=List[MenuItem])
def get_menu_items(restaurant_id: int, controller: RestaurantController = Depends(get_controller)):
    return controller.get_menu_items_by_restaurant_id(restaurant_id)


@router.post("/", response_model=Restaurant)
def create_restaurant(
    restaurant: RestaurantCreate, 
    controller: RestaurantController = Depends(get_controller)
):
    return controller.create_restaurant(restaurant)


@router.post("/{restaurant_id}/menu", response_model=MenuItem)
def add_menu_item(
    restaurant_id: int, 
    menu_item: MenuItemCreate, 
    controller: RestaurantController = Depends(get_controller)
):
    return controller.add_menu_item_to_restaurant(menu_item, restaurant_id)
