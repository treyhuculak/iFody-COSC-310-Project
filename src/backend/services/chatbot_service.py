import httpx
import os
from src.backend.repositories.restaurant_repo import RestaurantRepository

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def find_all_restaurants_and_menu_items() -> str:
    '''
    Find all restaurant and corresponding menu items from the database.
    Returns a string of all available restaurants and menu items.
    This is for the chatbot to search through to find recommendation for users.
    '''
    from src.backend.repositories.restaurant_repo import RestaurantRepository

    restaurant_repo = RestaurantRepository()
    restaurants = restaurant_repo._get_all_restaurants()  # use the internal helper directly

    all_options = "Available restaurants and menu items:\n"
    for r in restaurants:
        if not r.get('is_available', True):
            continue

        all_options += f"\nRestaurant: {r.get('name', 'Unknown')}, Cuisine: {r.get('cuisine', 'Unknown')}, City: {r.get('city', 'Unknown')}, Province: {r.get('province', 'Unknown')}, Delivery fee: ${r.get('delivery_fee', 0)}\n"
        for item in r.get('menu_items', []):
            all_options += f"  - {item['name']}: {item['description']}, ${item['price']}\n"

    return all_options

def chat(user_message: str) -> str:
    '''
    input user message and the list of all restaurants and menu items to the model as one prompt
    returns the model's response
    '''
    all_options = find_all_restaurants_and_menu_items()

    prompt = f"""You are a food assistant that helps people in an food delivery app.
                Help them choose food according to the menu listed below.
                Provide food suggestions and tell them why the foods fit their requirements.
                Keep responses short and friendly.

                {all_options}

                User: {user_message}
                Assistant:"""

    response = httpx.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        },
        timeout=200.0
    )
    return response.json()["response"] 
