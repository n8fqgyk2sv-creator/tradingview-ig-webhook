from http.server import BaseHTTPRequestHandler
import json
import requests
import os

# IG API credentials — store these as environment variables in Vercel
IG_API_KEY = os.environ.get("IG_API_KEY")
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
IG_ACC_TYPE = os.environ.get("IG_ACC_TYPE", "DEMO")  # DEMO or LIVE
IG_BASE_URL = "https://demo-api.ig.com/gateway/deal" if IG_ACC_TYPE=="DEMO" else "https://api.ig.com/gateway/deal"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the incoming JSON payload
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        print("Received payload:", payload)

        # Example: Extract info from TradingView alert
        ticker = payload.get("ticker")
        price = payload.get("price")
        alert_name = payload.get("alert_name")

        # Only send order if we have required info
        if ticker and price and alert_name:
            self.send_ig_order(ticker, price, alert_name)

        # Respond OK
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = json.dumps({"status": "ok"})
        self.wfile.write(response.encode('utf-8'))

    def send_ig_order(self, epic, price, direction):
        """
        Sends a simple market order to IG.com via REST API
        """
        try:
            # Step 1: Authenticate and get X-SECURITY-TOKEN + C-SRF-TOKEN
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
                print("IG login failed:", r.text)
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
                "direction": "BUY" if direction.upper() == "BUY" else "SELL",
                "size": 1,  # adjust size
                "orderType": "MARKET",
                "currencyCode": "USD",
                "forceOpen": True
            }

            r2 = requests.post(order_url, headers=order_headers, json=order_payload)
            print("Order response:", r2.status_code, r2.text)

        except Exception as e:
            print("Error sending IG order:", e)
