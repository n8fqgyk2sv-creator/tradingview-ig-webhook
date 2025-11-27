import os
import json
import time
from ig import place_market_with_sl_tp

# In-memory duplicate prevention
recent_trades = {}
RECENT_TTL = 60*60  # 1 hour

def handler(event, context):
    try:
        # Parse POST body safely
        body = json.loads(event.get("body") or "{}")
    except Exception as e:
        print("Error parsing JSON:", str(e))
        return {"statusCode": 400, "body": json.dumps({"error": "invalid_json", "exception": str(e)})}

    side = body.get("side")
    epic = body.get("epic")
    sl = body.get("sl")
    tp = body.get("tp")
    qty = body.get("qty")
    trade_id = body.get("trade_id")

    if not side or not epic or not trade_id:
        return {"statusCode": 400, "body": json.dumps({"error": "missing_fields", "received": body})}

    # Duplicate prevention
    now = time.time()
    for k in list(recent_trades.keys()):
        if now - recent_trades[k] > RECENT_TTL:
            del recent_trades[k]
    if trade_id in recent_trades:
        return {"statusCode": 200, "body": json.dumps({"status": "ignored", "reason": "duplicate", "trade_id": trade_id})}
    recent_trades[trade_id] = now

    # Determine quantity
    try:
        qty = float(qty)
    except:
        qty = float(os.environ.get("TRADE_SIZE", 0.1))

    # Wrap IG call in try/except to prevent crash
    try:
        result = place_market_with_sl_tp(side, epic, qty, sl_level=sl, tp_level=tp)
    except Exception as e:
        print("Error placing order:", str(e))
        result = {"error": "exception_in_place_market", "exception": str(e)}

    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "order_attempted",
            "payload": body,
            "result": result
        })
    }
