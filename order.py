from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import requests
import random
import os
import json

app = FastAPI()

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "token.txt")
REQUEST_TIMEOUT = 180

def load_tokens(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [x.strip() for x in f.readlines() if x.strip()]

def build_likevn_request(tiktok_id: str, api_token: str):
    link = f"https://www.tiktok.com/@{tiktok_id}"

    headers = {
        "accept": "application/json",
        "api-token": api_token,
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "user-agent": "Mozilla/5.0",
    }

    data = {
        "objectId": link,
        "server_order": "6",
        "free": "1",
        "giftcode": "",
        "amount": "10",
        "note": "",
    }

    return headers, {}, data

@app.get("/")
def index():
    return {"status": "ok", "message": "Order API online"}

@app.get("/order")
def order(id: str = Query(...), key: str = Query(...)):
    if key != "dichvusale-io-vn":
        raise HTTPException(status_code=403, detail="Invalid key")

    tokens = load_tokens(TOKEN_FILE)
    if not tokens:
        raise HTTPException(status_code=500, detail="token.txt empty")

    chosen = random.choice(tokens)
    headers, cookies, data = build_likevn_request(id, chosen)

    try:
        r = requests.post(
            "https://like.vn/api/mua-follow-tiktok/order",
            headers=headers,
            cookies=cookies,
            data=data,
            timeout=REQUEST_TIMEOUT
        )
    except requests.Timeout:
        return {"status": "error", "message": "Upstream timeout"}

    try:
        return r.json()
    except:
        return {"raw": r.text}
