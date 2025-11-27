import os
import json
from ig import place_market_with_sl_tp

def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "invalid_json"})
        }

    side = body.get("side")
    epic = body.get("epic")
    sl = body.get("sl")
    tp = body.get("tp")
    qty = body.get("qty")
    trade_id = body.get("trade_id")

    if not side or not epic or not trade_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "missing_fields", "received": body})
        }

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
