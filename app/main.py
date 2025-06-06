from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, plan


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="AppKnox Billing System",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def welcome():
    return "welcome to appknox billing system"


app.include_router(auth.auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(plan.router, prefix="/api/v1", tags=["Subscription"])