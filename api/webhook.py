import json
import time
import os

# Simple in-memory queue (serverless-safe: stores short-term in RAM)
# For production, use Vercel KV or Redis for persistence
queue = []

def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception as e:
        print("JSON parse error:", str(e))
        return {"statusCode": 400, "body": json.dumps({"error": "invalid_json", "exception": str(e)})}

    side = body.get("side")
    epic = body.get("epic")
    sl = body.get("sl")
    tp = body.get("tp")
    qty = body.get("qty")
    trade_id = body.get("trade_id")

    if not side or not epic or not trade_id:
        return {"statusCode": 400, "body": json.dumps({"error": "missing_fields", "received": body})}

    try:
        qty = float(qty)
    except:
        qty = float(os.environ.get("TRADE_SIZE", 0.1))

    # Append to queue with timestamp
    queue.append({
        "side": side,
        "epic": epic,
        "sl": sl,
        "tp": tp,
        "qty": qty,
        "trade_id": trade_id,
        "ts": time.time()
    })

    print(f"Queued trade {trade_id}: {side} {epic} {qty}")

    # Return immediately to TradingView
    return {"statusCode": 200, "body": json.dumps({"status": "queued", "trade_id": trade_id})}
