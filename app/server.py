from fastapi import FastAPI

from app.routers import me, user

app = FastAPI(
    title="PyMusic", docs_url="/api/docs/swagger", redoc_url="/api/docs/redoc"
)

app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(me.router, prefix="/me", tags=["me"])
