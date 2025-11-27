import os
import json
from ig import place_market_with_sl_tp

# Simple in-memory duplicate protection
recent_trades = {}
RECENT_TTL = 60*60  # 1 hour

def handler(event, context):
    # Parse POST body
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        return {"statusCode": 400, "body": json.dumps({"error": "invalid_json"})}

    side = body.get("side")
    epic = body.get("epic")
    sl = body.get("sl")
    tp = body.get("tp")
    qty = body.get("qty")
    trade_id = body.get("trade_id")

    if not side or not epic or not trade_id:
        return {"statusCode": 400, "body": json.dumps({"error": "missing_fields", "received": body})}

    # duplicate prevention
    import time
    now = time.time()
    # clean up old trades
    for k in list(recent_trades.keys()):
        if now - recent_trades[k] > RECENT_TTL:
            del recent_trades[k]
    if trade_id in recent_trades:
        return {"statusCode": 200, "body": json.dumps({"status": "ignored", "reason": "duplicate", "trade_id": trade_id})}
    recent_trades[trade_id] = now

    try:
        qty = float(qty)
    except:
        qty = float(os.environ.get("TRADE_SIZE", 0.1))

    result = place_market_with_sl_tp(side, epic, qty, sl_level=sl, tp_level=tp)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "order_attempted",
            "payload": body,
            "result": result
        })
    }
