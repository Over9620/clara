from flask import Flask, request, jsonify
from clara_web import handle_clara_request

app = Flask(__name__)


@app.post("/clara")
def clara_endpoint():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    reply = handle_clara_request(message)
    return jsonify({"response": reply})


@app.get("/")
def health():
    return jsonify({"status": "ok", "service": "clara-web"})
