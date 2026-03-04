from fastapi import FastAPI

from src.backend.routers import restaurants
from src.backend.routers import order

app = FastAPI()

app.include_router(restaurants.router)
app.include_router(order.router)

@app.get("/")
def root():
    return {"message": "Hello World"}
    
