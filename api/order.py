# api/order.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import sys
import os

# add repo root to path để import core.py
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

import core

app = FastAPI()

@app.get("/")
def index():
    return {"status": "ok", "message": "Order endpoint"}

@app.get("/order")
def order(id: str = Query(...), key: str = Query(...)):
    if key != "dichvusale-io-vn":
        raise HTTPException(status_code=403, detail="Invalid key")

    tokens = core.load_tokens()
    if not tokens:
        raise HTTPException(status_code=500, detail="token.txt empty")

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
