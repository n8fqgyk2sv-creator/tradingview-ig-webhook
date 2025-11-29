from http.server import BaseHTTPRequestHandler
import json

def handler(request, response):
    """
    Minimal webhook handler
    """
    try:
        data = json.loads(request.body.decode())
    except:
        data = {}

    print("Received data:", data)

    response.status_code = 200
    response.set_header("Content-Type", "application/json")
    response.send(json.dumps({"status": "ok"}))
