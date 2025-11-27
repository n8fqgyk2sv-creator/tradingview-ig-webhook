import asyncio
from ig import place_market_with_sl_tp
import os

# For production, you’d pull from persistent KV / DB
from api.webhook import queue

async def process_queue():
    while queue:
        trade = queue.pop(0)
        print(f"Processing trade {trade['trade_id']}")
        result = await place_market_with_sl_tp(
            trade['side'], trade['epic'], trade['qty'],
            sl_level=trade['sl'], tp_level=trade['tp']
        )
        print(f"Result for {trade['trade_id']}: {result}")

async def handler(event, context):
    try:
        await process_queue()
    except Exception as e:
        print("Error processing queue:", str(e))
    return {"statusCode": 200, "body": "Queue processed"}

