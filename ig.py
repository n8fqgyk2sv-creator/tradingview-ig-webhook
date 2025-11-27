# ig.py
import os, requests, time

API_KEY = os.environ.get("IG_API_KEY")
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
IG_API_URL = os.environ.get("IG_API_URL", "https://demo-api.ig.com/gateway/deal")  # demo by default
ACCOUNT_ID = os.environ.get("IG_ACCOUNT_ID")  # optional but handy

HEADERS_BASE = {
    "X-IG-API-KEY": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json",
    "VERSION": "2"
}

def ig_login():
    """
    Create a session and return headers containing CST and X-SECURITY-TOKEN for subsequent calls.
    """
    # The IG API requires a specific header for the login request
    login_headers = HEADERS_BASE.copy()
    login_headers["VERSION"] = "3" # Login endpoint version
    
    body = {"identifier": IG_USERNAME, "password": IG_PASSWORD}
    
    try:
        r = requests.post(f"{IG_API_URL}/session", json=body, headers=login_headers, timeout=10)
        
        # Check for successful login status codes
        if r.status_code not in [200, 201]:
            return {"error": "login_failed", "status": r.status_code, "text": r.text}
        
        return {
            "CST": r.headers.get("CST"),
            "XST": r.headers.get("X-SECURITY-TOKEN")
        }
    except requests.exceptions.RequestException as e:
        return {"error": "login_request_exception", "exception": str(e)}


def make_headers(tokens):
    h = HEADERS_BASE.copy()
    if tokens:
        h["CST"] = tokens.get("CST")
        h["X-SECURITY-TOKEN"] = tokens.get("XST")
    return h

def place_market_with_sl_tp(direction, epic, size, sl_level=None, tp_level=None):
    """
    Place a market OTC positions order and attach optional sl/tp levels in the same request.
    """
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
        "currencyCode": "GBP",
        "timeInForce": "FOK" # Fill or Kill is often preferred for market orders
    }
    
    # Optional Account ID for API call (if you have multiple accounts)
    if ACCOUNT_ID:
        order["accountId"] = ACCOUNT_ID 
    
    # attach stop/limit levels if provided
    if sl_level is not None:
        order["stopLevel"] = float(sl_level)
    if tp_level is not None:
        order["limitLevel"] = float(tp_level)

    try:
        r = requests.post(f"{IG_API_URL}/positions/otc", json=order, headers=headers, timeout=10)
    except Exception as e:
        return {"error":"request_failed","exception":str(e)}

    # Ensure to always log out of the session (though Vercel function will terminate, it's good practice)
    # logout(tokens) # A separate logout function could be implemented for a persistent server, but less critical here.
    
    try:
        res = r.json()
    except:
        return {"error":"invalid_response","status_code": r.status_code, "text": r.text}

    # If IG returns OK with a deal reference, return it; otherwise return the raw res for debugging
    return {"status_code": r.status_code, "response": res}
