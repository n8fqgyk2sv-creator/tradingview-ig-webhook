import json
import asyncio
from vercel_kv import Client
from api.ig import place_market_with_sl_tp

kv = Client()

async def handler(event, context):
    keys = await kv.keys("trade:*")
    for key in keys:
        data = await kv.get(key)
        trade = json.loads(data)

        trade_id = key.replace("trade:", "")
        print(f"Processing trade {trade_id}")

        result = await place_market_with_sl_tp(
            trade["side"], trade["epic"], trade["qty"],
            sl_level=trade.get("sl"), tp_level=trade.get("tp")
        )

        print(f"Result for {trade_id}: {result}")

        # Remove from KV after processing
        await kv.delete(key)

    return {"statusCode": 200, "body": "Queue processed"}
