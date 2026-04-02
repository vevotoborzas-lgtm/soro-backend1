from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import account, articles, auth, keywords, webhooks
from app.core.config import get_settings
from app.core.database import Base, engine
from app.services.ai_service import anthropic_key_debug_info


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Soro.hu API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(keywords.router)
app.include_router(account.router)
app.include_router(webhooks.router)


@app.get("/")
async def root():
    return {"service": "Soro.hu API", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/debug/env")
async def debug_env():
    """Temporary: verify Anthropic env without exposing secrets. Remove after fixing deploy."""
    return anthropic_key_debug_info()


@app.get("/v1/ping")
async def ping():
    return {"message": "ok"}
