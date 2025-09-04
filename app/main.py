import os, hmac, hashlib
from fastapi import FastAPI, Request, Header
from dotenv import load_dotenv

load_dotenv()  # loads .env in local dev

app = FastAPI()
WEBHOOK_SECRET = (os.getenv("GITHUB_WEBHOOK_SECRET") or "").encode()

def verify_signature(payload: bytes, signature: str | None) -> bool:
    if not WEBHOOK_SECRET or not signature:
        return False
    mac = hmac.new(WEBHOOK_SECRET, msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)
    
@app.post("/github/webhooks")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None),
):
    body = await request.body()
    if not verify_signature(body, x_hub_signature_256):
        return {"status": "invalid signature"}
    # For now, just log the event type and return OK
    print(f"✅ Webhook received: {x_github_event}")
    return {"status": "ok"}
