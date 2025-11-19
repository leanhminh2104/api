from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import requests
import random
import os
import json
from typing import Optional

app = FastAPI()

# Path tới token.txt (đặt cùng thư mục project)
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token.txt")

# Độ timeout chờ API trả lời (không sửa) = 180s
REQUEST_TIMEOUT = 180

def load_tokens(path: str):
    """Đọc token.txt, mỗi dòng 1 token, bỏ dòng rỗng"""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        tokens = [line.strip() for line in f.readlines() if line.strip()]
    return tokens

def build_likevn_request(tiktok_id: str, chosen_token: str):
    """Chuẩn bị headers/cookies/data giống trước, nhưng thay api-token bằng chosen_token"""
    link = f"https://www.tiktok.com/@{tiktok_id}"
    cookies = {
        # giữ hoặc bỏ cookie; nguyên mẫu có cookie cứng, vẫn để đây nếu cần
        '_gcl_au': '1.1.1794597456.1762092614',
        '_ga': 'GA1.1.1400119809.1762092615',
        # ... (nếu muốn xóa cookie có thể set = {})
    }

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'vi-VN,vi;q=0.9',
        'api-token': chosen_token,
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://like.vn',
        'referer': 'https://like.vn/mua-follow-tiktok',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'objectId': link,
        'server_order': '6',
        'free': '1',
        'giftcode': '',
        'amount': '10',
        'note': '',
    }

    return headers, cookies, data

@app.get("/api/order")
def order_tiktok(id: str = Query(..., description="tiktok id (không kèm @)"),
                 key: str = Query(..., description="phải là 'dichvusale-io-vn' để được phép")):
    """
    Gọi API đặt follow cho profile tiktok: ?id=<id>&key=dichvusale-io-vn
    Trả nguyên response JSON API của like.vn (success hay fail đều trả y nguyên).
    """
    # kiểm tra key
    if key != "dichvusale-io-vn":
        raise HTTPException(status_code=403, detail="Invalid key")

    # load token list
    tokens = load_tokens(TOKEN_FILE)
    if not tokens:
        raise HTTPException(status_code=500, detail="No tokens available on server (token.txt missing or empty).")

    # chọn ngẫu nhiên token
    chosen_token = random.choice(tokens)

    # build request
    headers, cookies, data = build_likevn_request(id, chosen_token)

    # gọi API với timeout cố định 180s
    try:
        resp = requests.post("https://like.vn/api/mua-follow-tiktok/order",
                             headers=headers,
                             cookies=cookies,
                             data=data,
                             timeout=REQUEST_TIMEOUT)
    except requests.Timeout:
        return JSONResponse(status_code=504, content={"status": "error", "message": "Upstream API timeout (180s)"})
    except requests.RequestException as e:
        return JSONResponse(status_code=502, content={"status": "error", "message": f"Upstream request failed: {str(e)}"})

    # cố parse JSON nếu có, nếu không trả text
    text = resp.text
    try:
        parsed = resp.json()
        # nếu đúng chuẩn success cụ thể
        # Trả nguyên nội dung API trả về (nguyên vẹn)
        return JSONResponse(status_code=resp.status_code, content=parsed)
    except ValueError:
        # không phải JSON, trả nguyên text
        return JSONResponse(status_code=resp.status_code, content={"raw": text})
