import json

def handler(request, context):
    try:
        body = request.json()
    except:
        body = {}

    return {
        "status": 200,
        "body": json.dumps({
            "message": "Webhook received successfully",
            "received": body
        })
    }
