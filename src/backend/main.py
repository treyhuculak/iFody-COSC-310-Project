from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.routers import restaurants
from src.backend.routers import orders
from src.backend.routers import payments
from src.backend.routers import notification
from src.backend.routers import auth
from src.backend.routers import transactions
from src.backend.routers import deliveries

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(notification.router)
app.include_router(transactions.router)
app.include_router(deliveries.router)

@app.get("/")
def root():
    return {"message": "Hello World"}