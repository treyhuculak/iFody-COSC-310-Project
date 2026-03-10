from fastapi import FastAPI

from src.backend.routers import restaurants
from src.backend.routers import orders
from src.backend.routers import payment

app = FastAPI()

app.include_router(restaurants.router)
app.include_router(orders.router)
app.include_router(payment.router)

@app.get("/")
def root():
    return {"message": "Hello World"}
    
