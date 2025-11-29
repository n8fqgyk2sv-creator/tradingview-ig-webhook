from http.server import BaseHTTPRequestHandler
import json
import requests
import os
import datetime

# --------------------------
# Environment Variables (set in Vercel)
# --------------------------
IG_API_KEY = os.environ.get("IG_API_KEY")
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
IG_ACC_TYPE = os.environ.get("IG_ACC_TYPE", "DEMO")  # DEMO or LIVE

IG_BASE_URL = "https://demo-api.ig.com/gateway/deal" if IG_ACC_TYPE.upper() == "DEMO" else "https://api.ig.com/gateway/deal"

# Known tickers allowed
ALLOWED_TICKERS = ["CS.D.EURUSD.CFD.IP", "CS.D.GBPUSD.CFD.IP"]  # Add the tickers you want

# Max order size
DEFAULT_ORDER_SIZE = 1

# --------------------------
# Handler Class
# --------------------------
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the incoming JSON payload
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # Log payload with timestamp
        timestamp = datetime.datetime.utcnow().isoformat()
        print(f"[{timestamp}] Received payload:", payload)

        # Validate payload
        ticker = payload.get("ticker")
        price = payload.get("price")
        alert_name = payload.get("alert_name")

        if not ticker or not price or not alert_name:
            print(f"[{timestamp}] Missing required fields. Ignoring alert.")
            return self.respond_ok()

        if ticker not in ALLOWED_TICKERS:
            print(f"[{timestamp}] Ticker {ticker} not allowed. Ignoring alert.")
            return self.respond_ok()

        direction = alert_name.upper()
        if direction not in ["BUY", "SELL"]:
            print(f"[{timestamp}] Invalid alert_name: {alert_name}. Must be BUY or SELL. Ignoring alert.")
            return self.respond_ok()

        # Send order to IG
        self.send_ig_order(ticker, price, direction)

        # Respond to TradingView
        return self.respond_ok()

    # --------------------------
    # Send order to IG.com
    # --------------------------
    def send_ig_order(self, epic, price, direction):
        timestamp = datetime.datetime.utcnow().isoformat()
        try:
            # Step 1: Authenticate
            session_url = f"{IG_BASE_URL}/session"
            headers = {
                "Content-Type": "application/json",
                "X-IG-API-KEY": IG_API_KEY,
            }
            data = {
                "identifier": IG_USERNAME,
                "password": IG_PASSWORD,
                "encryptedPassword": ""
            }
            r = requests.post(session_url, headers=headers, json=data)
            if r.status_code != 200:
                print(f"[{timestamp}] IG login failed:", r.text)
                return

            auth_data = r.json()
            security_token = auth_data.get("securityToken")
            c_srf_token = auth_data.get("cst")
            account_id = auth_data.get("currentAccountId")

            # Step 2: Place order
            order_url = f"{IG_BASE_URL}/positions/otc"
            order_headers = {
                "Content-Type": "application/json",
                "X-IG-API-KEY": IG_API_KEY,
                "CST": c_srf_token,
                "X-SECURITY-TOKEN": security_token
            }
            order_payload = {
                "epic": epic,
                "expiry": "-",
                "direction": direction,
                "size": DEFAULT_ORDER_SIZE,
                "orderType": "MARKET",
                "currencyCode": "USD",
                "forceOpen": True
            }

            r2 = requests.post(order_url, headers=order_headers, json=order_payload)
            print(f"[{timestamp}] Order response ({direction} {epic}):", r2.status_code, r2.text)

        except Exception as e:
            print(f"[{timestamp}] Error sending IG order:", e)

    # --------------------------
    # Standard OK response
    # --------------------------
    def respond_ok(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = json.dumps({"status": "ok"})
        self.wfile.write(response.encode('utf-8'))
