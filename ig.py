import os
import requests

def get_env_var(key, default=None):
    value = os.environ.get(key, default)
    if value is None:
        print(f"Warning: {key} not set in environment variables")
    return value

def ig_login():
    API_KEY = get_env_var("IG_API_KEY")
    IG_USERNAME = get_env_var("IG_USERNAME")
    IG_PASSWORD = get_env_var("IG_PASSWORD")
    IG_API_URL = get_env_var("IG_API_URL", "https://demo-api.ig.com/gateway/deal")

    if not all([API_KEY, IG_USERNAME, IG_PASSWORD]):
        return {"error": "missing_credentials"}

    headers = {
        "X-IG-API-KEY": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "VERSION": "2"
    }

    try:
        r = requests.post(f"{IG_API_URL}/session",
                          json={"identifier": IG_USERNAME, "password": IG_PASSWORD},
                          headers=headers,
                          timeout=10)
        r.raise_for_status()
    except Exception as e:
        return {"error": "login_failed", "exception": str(e)}

    return {
        "CST": r.headers.get("CST"),
        "XST": r.headers.get("X-SECURITY-TOKEN")
    }

def make_headers(tokens):
    API_KEY = get_env_var("IG_API_KEY")
    headers = {
        "X-IG-API-KEY": API_KEY or "",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "VERSION": "2"
    }
    if tokens:
        headers["CST"] = tokens.get("CST")
        headers["X-SECURITY-TOKEN"] = tokens.get("XST")
    return headers

def place_market_with_sl_tp(direction, epic, size, sl_level=None, tp_level=None):
    IG_API_URL = get_env_var("IG_API_URL", "https://demo-api.ig.com/gateway/deal")

    tokens = ig_login()
    if "error" in tokens:
        return tokens

    headers = make_headers(tokens)
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

    try:
        r = requests.post(f"{IG_API_URL}/positions/otc", json=order, headers=headers, timeout=10)
        try:
            res = r.json()
        except:
            res = {"text": r.text, "status_code": r.status_code}
    except Exception as e:
        return {"error": "request_failed", "exception": str(e)}

    return {"status_code": r.status_code, "response": res}
