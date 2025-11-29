import json

def handler(request):
    """
    Minimal webhook handler for Vercel
    """
    try:
        payload = request.json()  # parses incoming JSON automatically
    except Exception:
        payload = {}

    # Logs the payload in Vercel dashboard
    print("Received payload:", payload)

    # Must return a dict with these keys
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "ok"})
    }
