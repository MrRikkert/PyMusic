import uvicorn
from fastapi import FastAPI
from pony.orm import db_session
from starlette.requests import Request

from app import settings
from app.db.base import db
from app.routers import user_controller

db.bind(**settings.DB_PARAMS)
db.generate_mapping(create_tables=True)

app = FastAPI()

app.include_router(user_controller.router, prefix="/user", tags=["user"])


# wrap every request in a PonyORM 'db_session'
@app.middleware("http")
async def db_middleware(request: Request, call_next):
    with db_session:
        response = await call_next(request)
        return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
