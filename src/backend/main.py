from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.backend.models.user import InvalidEmailError, InvalidPasswordError

from src.backend.routers import restaurants
from src.backend.routers import orders
from src.backend.routers import payments
from src.backend.routers import notification
from src.backend.routers import auth
from src.backend.routers import transactions
from src.backend.routers import deliveries
from src.backend.routers import chatbot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(notification.router)
app.include_router(transactions.router)
app.include_router(deliveries.router)
app.include_router(chatbot.router)

@app.exception_handler(InvalidEmailError)
async def email_error_handler(request, exc: InvalidEmailError):
    '''
    The function converts the InvalidEmailError class to a JSONResponse class.
    '''
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(InvalidPasswordError)
async def password_error_handler(request, exc: InvalidPasswordError):
    '''
    The function converts the InvalidPasswordError class to a JSONResponse class.
    '''
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.get("/")
def root():
    return {"message": "Hello World"}