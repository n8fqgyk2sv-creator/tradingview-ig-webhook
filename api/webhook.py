import os
import json
from ig import place_market_with_sl_tp

def handler(request, response):
    if request.method != "POST":
        return response.status(405).send("Method Not Allowed")

    try:
        data = request.json()
    except Exception:
        return response.status(400).json({"error": "invalid_json"})

    if not data:
        return response.status(400).json({"error": "no_json"})

    side = data.get("side")
    epic = data.get("epic")
    sl = data.get("sl")
    tp = data.get("tp")
    qty = data.get("qty")
    trade_id = data.get("trade_id")

    if not side or not epic or not trade_id:
        return response.status(400).json({"error": "missing_fields", "received": data})

    try:
        qty = float(qty)
    except:
        qty = float(os.environ.get("TRADE_SIZE", 0.1))

    result = place_market_with_sl_tp(side, epic, qty, sl_level=sl, tp_level=tp)

    return response.status(200).json({
        "status": "order_attempted",
        "payload": data,
        "result": result
    })
