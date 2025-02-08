from flask import Flask, request, jsonify
import virtualboard

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to VirtualBoard API!"

@app.route('/process', methods=['POST'])
def process_data():
    try:
        data = request.json
        result = virtualboard.main_function(data)
        return jsonify({"output": result})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
