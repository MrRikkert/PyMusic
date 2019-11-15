from pony.orm import db_session
from starlette.requests import Request
from app.server import app

# wrap every request in a PonyORM 'db_session'
@app.middleware("http")
async def db_middleware(request: Request, call_next):
    with db_session:
        response = await call_next(request)
        return response
