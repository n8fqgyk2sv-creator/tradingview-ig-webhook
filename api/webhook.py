def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": "Method not allowed"
        }

    try:
        data = request.json()
    except Exception:
        data = None

    print("Received webhook:", data)

    return {
        "statusCode": 200,
        "body": "Webhook received"
    }
