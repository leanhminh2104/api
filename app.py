# app.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, Response
import core

app = FastAPI(title="LikeVN Order API")

@app.get("/")
def root():
    return {"status": "ok", "message": "Service running"}

@app.get("/api/order")
def order(id: str = Query(..., description="TikTok id (không kèm @)"),
          key: str = Query(..., description="key phải là 'dichvusale-io-vn'")):
    # kiểm tra key
    if key != "dichvusale-io-vn":
        raise HTTPException(status_code=403, detail="Invalid key")

    tokens = core.load_tokens()
    if not tokens:
        raise HTTPException(status_code=500, detail="token.txt missing or empty")

    chosen = core.pick_token(tokens)
    headers, cookies, data = core.build_payload_and_headers(id, chosen)

    try:
        status_code, content, is_json, resp_headers = core.call_upstream(headers, cookies, data)
    except core.requests.Timeout:
        return JSONResponse(status_code=504, content={"status": "error", "message": "Upstream timeout (180s)"})
    except Exception as e:
        return JSONResponse(status_code=502, content={"status": "error", "message": str(e)})

    # Nếu upstream trả JSON -> trả nguyên JSON
    if is_json:
        return JSONResponse(status_code=status_code, content=content)

    # Non-JSON -> trả nguyên bytes/text + đúng content-type từ upstream (nếu có)
    content_type = resp_headers.get("content-type", "text/html; charset=utf-8")
    # content is bytes (resp.content) from core.call_upstream
    # trả nguyên bytes để client thấy đúng HTML challenge nếu có
    return Response(content=content, status_code=status_code, media_type=content_type)
