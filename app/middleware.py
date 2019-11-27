from pony.orm import db_session
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.server import app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_middleware(request: Request, call_next):
    """Wraps every API call in a PonyORM db_session"""
    with db_session:
        response = await call_next(request)
        return response
