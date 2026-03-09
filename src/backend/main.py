from fastapi import FastAPI

from src.backend.routers import restaurants
from src.backend.routers import order
from src.backend.routers import notif

app = FastAPI()

app.include_router(restaurants.router)
app.include_router(order.router)
app.include_router(notif.router)

@app.get("/")
def root():
    return {"message": "Hello World"}
    
