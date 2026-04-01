from flask import Flask, request, jsonify, send_from_directory
from clara_web import handle_clara_request
import os

app = Flask(__name__, static_folder="static")

@app.get("/")
def serve_ui():
    return send_from_directory("static", "index.html")

@app.post("/clara")
def clara_endpoint():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    reply = handle_clara_request(message)
    return jsonify({"response": reply})
