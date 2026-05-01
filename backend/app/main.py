from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from .config import settings
from .database import init_db
from .models import User, Scenario, History, ActionType, RefreshToken
from .rate_limit import limiter
from .routes import users_router, scenarios_router, history_router, graph_router, auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

Instrumentator().instrument(app).expose(app, endpoint="/api/metrics", include_in_schema=False)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(scenarios_router)
app.include_router(history_router)
app.include_router(graph_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Network Resilience API",
        "docs": "/api/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}