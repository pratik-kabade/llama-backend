from flask import Flask, request, jsonify
from llm_settings import LLM

app = Flask(__name__)

# cors
from flask_cors import CORS
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Server is running"}), 200

@app.route('/api/get-response', methods=['POST'])
def get_response():
    """Returns the entire response at once, either as plain text or JSON."""
    data = request.json
    prompt = data.get('prompt')

    llm1=LLM(llm_model='llama2')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    result = llm1.fetch_entire_response(prompt)

    return jsonify({"response": result}), 200

@app.route('/api/get-rag-response', methods=['POST'])
def get_rag_response():
    data = request.json
    file_name = data.get('file_name')
    prompt = data.get('prompt')

    llm1=LLM(llm_model='llama2')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    result = llm1.rag_model(file_name, prompt)

    return jsonify({"response": result}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)

# curl -X POST http://127.0.0.1:5000/api/get-response -H "Content-Type: application/json" -d '{"prompt": "hi"}'
# curl -X POST http://127.0.0.1:5000/api/get-rag-response -H "Content-Type: application/json" -d '{"prompt": "what is this document about", "file_name": "Resume.pdf"}'
