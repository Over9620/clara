from flask import Flask, request, jsonify
from clara_ai import aria_brain

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Clara AI!"

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_input = request.json.get('message')
    response = aria_brain(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=5000)