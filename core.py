# core.py
import os
import random
import requests
from typing import Tuple

# Path tới token.txt (root của repo)
ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(ROOT, "token.txt")

# timeout cố định
REQUEST_TIMEOUT = 180

def load_tokens(path: str = TOKEN_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        tokens = [line.strip() for line in f if line.strip()]
    return tokens

def pick_token(tokens):
    return random.choice(tokens) if tokens else None

def prepare_request(tiktok_id: str, api_token: str) -> Tuple[dict, dict, dict]:
    """
    Trả về (headers, cookies, data) để dùng cho request tới like.vn
    """
    link = f"https://www.tiktok.com/@{tiktok_id}"

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'vi-VN,vi;q=0.9',
        'api-token': api_token,
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://like.vn',
        'referer': 'https://like.vn/mua-follow-tiktok',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'x-requested-with': 'XMLHttpRequest',
    }

    # cookies có thể để trống hoặc giữ nếu cần
    cookies = {}

    data = {
        'objectId': link,
        'server_order': '6',
        'free': '1',
        'giftcode': '',
        'amount': '10',
        'note': '',
    }

    return headers, cookies, data

def call_likevn(headers: dict, cookies: dict, data: dict, timeout: int = REQUEST_TIMEOUT):
    """
    Gọi API upstream; trả về tuple (status_code, content, is_json)
    content là dict nếu is_json True, else raw text
    """
    url = "https://like.vn/api/mua-follow-tiktok/order"
    resp = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=timeout)
    text = resp.text
    try:
        js = resp.json()
        return resp.status_code, js, True
    except ValueError:
        return resp.status_code, text, False
