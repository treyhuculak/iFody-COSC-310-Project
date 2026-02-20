from fastapi import FastAPI

from src.backend.routers import restaurants

app = FastAPI()

app.include_router(restaurants.router)

@app.get("/")
def root():
    return {"message": "Hello World"}
    
