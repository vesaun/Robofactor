from fastapi import FastAPI, Request, Header
import hmac, hashlib, os

app = FastAPI()

WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "changeme").encode()

def verify_signature(payload: bytes, signature: str) -> bool:
    mac = hmac.new(WEBHOOK_SECRET, msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

@app.post("/github/webhooks")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    body = await request.body()
    if not verify_signature(body, x_hub_signature_256 or ""):
        return {"status": "invalid signature"}
    event = request.headers.get("X-GitHub-Event")
    print(f"✅ Received {event}")
    return {"status": "ok"}
