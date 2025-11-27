# api/webhook.py
import os, time, json
from flask import Flask, request, jsonify
from ig import place_market_with_sl_tp

app = Flask(__name__)
recent_trades = {}
RECENT_TTL = 60*60

def is_duplicate(trade_id):
    now = time.time()
    for k, v in list(recent_trades.items()):
        if now - v > RECENT_TTL:
            del recent_trades[k]
    return trade_id in recent_trades

def mark_done(trade_id):
    recent_trades[trade_id] = time.time()

@app.route("/api/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "no_json"}), 400

    side = data.get("side")
    epic = data.get("epic")
    sl = data.get("sl", None)
    tp = data.get("tp", None)
    qty = data.get("qty", None)
    trade_id = data.get("trade_id", None)

    if not side or not epic or not trade_id:
        return jsonify({"error":"missing_fields","received":data}), 400

    if is_duplicate(trade_id):
        return jsonify({"status":"ignored","reason":"duplicate","trade_id":trade_id}), 200

    try:
        qty = float(qty)
    except:
        qty = float(os.environ.get("TRADE_SIZE", 0.1))

    result = place_market_with_sl_tp(side, epic, qty, sl_level=sl, tp_level=tp)
    mark_done(trade_id)
    return jsonify({"status":"order_attempted","payload":data,"result":result})
