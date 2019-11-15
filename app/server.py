from fastapi import FastAPI

from app.routers import user_controller

app = FastAPI()

app.include_router(user_controller.router, prefix="/user", tags=["user"])
