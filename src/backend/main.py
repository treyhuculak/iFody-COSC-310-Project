from fastapi import FastAPI

from src.backend.routers import restaurants
from src.backend.routers import orders
from src.backend.routers import payment
from src.backend.routers import notification
from src.backend.routers import transaction

app = FastAPI()

app.include_router(restaurants.router)
app.include_router(orders.router)
app.include_router(payment.router)
app.include_router(notification.router)
app.include_router(transaction.router)

@app.get("/")
def root():
    return {"message": "Hello World"}
    
