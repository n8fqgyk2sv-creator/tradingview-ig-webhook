import json

def handler(request):
    """
    Minimal Vercel Python 3.12 webhook handler
    """
    try:
        # request.json() parses incoming JSON payload
        payload = request.json()
    except Exception:
        payload = {}

    # Print payload to Vercel logs
    print("Received payload:", payload)

    # Must return this structure for Vercel serverless functions
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "ok"})
    }
