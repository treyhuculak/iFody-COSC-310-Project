from fastapi import FastAPI

from src.backend.routers import restaurants
from src.backend.routers import orders
from src.backend.routers import notification
from src.backend.routers import auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(orders.router)
app.include_router(notification.router)

@app.get("/")
def root():
    return {"message": "Hello World"}
    
