from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel
from app.core.config import get_settings
from app.core.security import verify_hmac_signature


router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])
settings = get_settings()


class PublishConfirmPayload(BaseModel):
    article_id: str
    wp_post_id: str | None = None
    wp_post_url: str | None = None
    status: str = "published"


@router.post("/publish-confirm")
async def publish_confirm(
    request: Request,
    payload: PublishConfirmPayload,
    x_soro_signature: str | None = Header(default=None),
    x_signature: str | None = Header(default=None),
):
    sig = x_soro_signature or x_signature
    if not sig:
        raise HTTPException(status_code=401, detail="Missing signature header")
    body = await request.body()
    if not verify_hmac_signature(body, sig, settings.webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    return {"ok": True, "article_id": payload.article_id, "status": payload.status}
