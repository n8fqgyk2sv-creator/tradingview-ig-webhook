import os
import httpx

async def ig_login():
    API_KEY = os.environ.get("IG_API_KEY")
    IG_USERNAME = os.environ.get("IG_USERNAME")
    IG_PASSWORD = os.environ.get("IG_PASSWORD")
    IG_API_URL = os.environ.get("IG_API_URL", "https://demo-api.ig.com/gateway/deal")

    if not all([API_KEY, IG_USERNAME, IG_PASSWORD]):
        return {"error": "missing_credentials"}

    headers = {
        "X-IG-API-KEY": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "VERSION": "2"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(
                f"{IG_API_URL}/session",
                json={"identifier": IG_USERNAME, "password": IG_PASSWORD},
                headers=headers
            )
            r.raise_for_status()
        except httpx.RequestError as e:
            return {"error": "login_failed", "exception": str(e)}

    return {
        "CST": r.headers.get("CST"),
        "XST": r.headers.get("X-SECURITY-TOKEN")
    }

async def place_market_with_sl_tp(direction, epic, size, sl_level=None, tp_level=None):
    IG_API_URL = os.environ.get("IG_API_URL", "https://demo-api.ig.com/gateway/deal")
    tokens = await ig_login()
    if "error" in tokens:
        return tokens

    headers = {
        "X-IG-API-KEY": os.environ.get("IG_API_KEY") or "",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "VERSION": "2",
        "CST": tokens.get("CST"),
        "X-SECURITY-TOKEN": tokens.get("XST")
    }

    order = {
        "epic": epic,
        "expiry": "-",
        "direction": "BUY" if str(direction).lower() in ["buy","long"] else "SELL",
        "size": float(size),
        "orderType": "MARKET",
        "forceOpen": True,
        "guaranteedStop": False,
        "currencyCode": "GBP"
    }

    if sl_level is not None:
        order["stopLevel"] = float(sl_level)
    if tp_level is not None:
        order["limitLevel"] = float(tp_level)

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(f"{IG_API_URL}/positions/otc", json=order, headers=headers)
            try:
                res = r.json()
            except:
                res = {"text": r.text, "status_code": r.status_code}
        except httpx.RequestError as e:
            return {"error": "request_failed", "exception": str(e)}

    return {"status_code": r.status_code, "response": res}
