from pony.orm import db_session
from starlette.requests import Request
from app.server import app


@app.middleware("http")
async def db_middleware(request: Request, call_next):
    """Wraps every API call in a PonyORM db_session"""
    with db_session:
        response = await call_next(request)
        return response
