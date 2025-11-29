import json

# This is the function signature Vercel expects
def handler(request):
    """
    Minimal webhook handler for Vercel
    """
    try:
        payload = request.json()  # parse JSON body
    except Exception:
        payload = {}

    print("Received payload:", payload)  # shows in Vercel logs

    # Return a valid response object
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "ok"})
    }
