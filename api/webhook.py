# api/webhook.py
import os, time, json
from flask import Flask, request, jsonify
# Import the helper module from the root of the project
from ig import place_market_with_sl_tp 

# Vercel needs the Flask app instance to be named 'app'
app = Flask(__name__)

# NOTE: In-memory duplicate protection (recent_trades) is NOT reliable
# on serverless platforms like Vercel because each request can spin up a new instance.
# For production stability, you should use a simple database (e.g., Redis, Vercel KV) 
# or check against open positions on IG.
# We will keep the in-memory version for this *example* setup, but be aware of this limitation.
recent_trades = {}
RECENT_TTL = 60 * 60  # keep trade ids for 1 hour

def is_duplicate(trade_id):
    # This logic is non-persistent on Vercel and is for demonstration only.
    now = time.time()
    for k, v in list(recent_trades.items()):
        if now - v > RECENT_TTL:
            del recent_trades[k]
    return trade_id in recent_trades

def mark_done(trade_id):
    # This state will likely be lost after the function finishes execution.
    recent_trades[trade_id] = time.time()

# The path for this function will be /api/webhook
@app.route("/webhook", methods=["POST"])
def webhook_handler():
    # TradingView sends a raw POST request with a JSON body
    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"error": "no_json", "detail": "Request body is not valid JSON."}), 400
    except Exception as e:
        return jsonify({"error": "json_parse_failed", "exception": str(e)}), 400
        
    # Expected fields: side, epic, entry, sl, tp, qty, trade_id
    side = data.get("side")
    epic = data.get("epic")
    sl = data.get("sl", None)
    tp = data.get("tp", None)
    qty = data.get("qty", None)
    trade_id = data.get("trade_id", None)

    # Basic validation
    if not side or not epic or not trade_id:
        return jsonify({"error":"missing_fields","received":data}), 400

    # DUPLICATE PREVENTION (Unreliable on Serverless, see note above)
    if is_duplicate(trade_id):
        return jsonify({"status":"ignored","reason":"duplicate_in_memory","trade_id":trade_id}), 200

    # Defensive type conversion for quantity
    try:
        qty = float(qty)
    except:
        # Use an environment variable for a default quantity if conversion fails
        qty = float(os.environ.get("TRADE_SIZE", 0.1)) 
        
    # Place market order with SL/TP
    result = place_market_with_sl_tp(side, epic, qty, sl_level=sl, tp_level=tp)

    # Mark as executed (state will likely be lost)
    mark_done(trade_id)
    
    # IG API call was attempted, return the result from the trading function
    return jsonify({"status":"order_attempted","payload":data,"result":result}), 200


@app.route("/", methods=["GET"])
def home():
    # Simple check to see if the function is running
    return "IG Webhook Receiver is running. Send POST requests to /api/webhook"

# The Vercel runtime handles the `if __name__ == "__main__"` block,
# exposing the 'app' instance as the serverless function.
