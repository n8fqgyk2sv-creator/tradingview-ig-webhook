import json
import os
from vercel_kv import Client

kv = Client()

async def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": "invalid_json", "exception": str(e)})}

    side = body.get("side")
    epic = body.get("epic")
    qty = float(body.get("qty", os.environ.get("TRADE_SIZE", 0.1)))
    trade_id = body.get("trade_id")
    sl = body.get("sl")
    tp = body.get("tp")

    if not side or not epic or not trade_id:
        return {"statusCode": 400, "body": json.dumps({"error": "missing_fields"})}

    # Save to Vercel KV
    await kv.set(f"trade:{trade_id}", json.dumps({
        "side": side,
        "epic": epic,
        "qty": qty,
        "sl": sl,
        "tp": tp
    }))

    print(f"Queued trade {trade_id}: {side} {epic} {qty}")

    return {"statusCode": 200, "body": json.dumps({"status": "queued", "trade_id": trade_id})}
