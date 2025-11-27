import os
import requests

def get_env_var(key, default=None):
    value = os.environ.get(key, default)
    if value is None:
        print(f"Warning: {key} not set in environment variables")
    return value

API_KEY = get_env_var("IG_API_KEY")
IG_USERNAME = get_env_var("IG_USERNAME")
IG_PASSWORD = get_env_var("IG_PASSWORD")
IG_API_URL = get_env_var("IG_API_URL", "https://demo-api.ig.com/gateway/deal")

HEADERS_BASE = {
    "X-IG-API-KEY": API_KEY or "",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "VERSION": "2"
}

def ig_login():
    if not all([API_KEY, IG_USERNAME, IG_PASSWORD]):
        return {"error": "missing_credentials"}
    body = {"identifier": IG_USERNAME, "password": IG_PASSWORD}
    try:
        r = requests.post(f"{IG_API_URL}/session", json=body, headers=HEADERS_BASE, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return {"error": "login_failed", "exception": str(e)}

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
        res = r.json()
    except Exception as e:
        return {"error": "request_failed", "exception": str(e)}

    return {"status_code": r.status_code, "response": res}
