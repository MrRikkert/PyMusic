from fastapi import FastAPI

from app.routers import user

app = FastAPI(
    title="PyMusic", docs_url="/api/docs/swagger", redoc_url="/api/docs/redoc"
)

app.include_router(user.router, prefix="/user", tags=["user"])
