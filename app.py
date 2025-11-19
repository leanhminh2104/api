# app.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import core

app = FastAPI(title="LikeVN Order API")

@app.get("/")
def home():
    return {"status": "ok", "message": "Service running"}

@app.get("/api/order")
def order(id: str = Query(..., description="TikTok id (không kèm @)"),
          key: str = Query(..., description="phải là 'dichvusale-io-vn'")):
    # kiểm tra key
    if key != "dichvusale-io-vn":
        raise HTTPException(status_code=403, detail="Invalid key")

    tokens = core.load_tokens()
    if not tokens:
        raise HTTPException(status_code=500, detail="token.txt missing or empty")

    chosen = core.pick_token(tokens)
    headers, cookies, data = core.build_payload_and_headers(id, chosen)

    try:
        status_code, content, is_json = core.call_upstream(headers, cookies, data)
    except Exception as e:
        return JSONResponse(status_code=502, content={"status": "error", "message": f"Upstream request failed: {str(e)}"})

    if is_json:
        return JSONResponse(status_code=status_code, content=content)
    else:
        return JSONResponse(status_code=status_code, content={"raw": content})
