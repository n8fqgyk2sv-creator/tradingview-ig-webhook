# ig.py
import os, requests, time

API_KEY = os.environ.get("IG_API_KEY")
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
IG_API_URL = os.environ.get("IG_API_URL", "https://demo-api.ig.com/gateway/deal")

if not all([API_KEY, IG_USERNAME, IG_PASSWORD]):
    # Prevent import-time crash
    print("Missing IG credentials in environment variables")

HEADERS_BASE = {
    "X-IG-API-KEY": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json",
    "VERSION": "2"
}

def ig_login():
    body = {"identifier": IG_USERNAME, "password": IG_PASSWORD}
    r = requests.post(f"{IG_API_URL}/session", json=body, headers=HEADERS_BASE, timeout=10)
    if r.status_code != 200:
        return {"error": "login_failed", "status": r.status_code, "text": r.text}
    return {
        "CST": r.headers.get("CST"),
        "XST": r.headers.get("X-SECURITY-TOKEN")
    }

def make_headers(tokens):
    h = HEADERS_BASE.copy()
    if tokens:
        h["CST"] = tokens.get("CST")
        h["X-SECURITY-TOKEN"] = tokens.get("XST")
    return h

def place_market_with_sl_tp(direction, epic, size, sl_level=None, tp_level=None):
    tokens = ig_login()
    if "error" in tokens:
        return tokens

    headers = make_headers(tokens)
    order = {
        "epic": epic,
        "expiry": "-",
        "direction": "BUY" if direction.lower() in ["buy","long"] else "SELL",
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

    try:
        r = requests.post(f"{IG_API_URL}/positions/otc", json=order, headers=headers, timeout=10)
    except Exception as e:
        return {"error":"request_failed","exception":str(e)}

    try:
        res = r.json()
    except:
        return {"error":"invalid_response","status_code": r.status_code, "text": r.text}

    return {"status_code": r.status_code, "response": res}
