import os
import json
import requests
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Fetch Ollama API URL from environment variables
OLLAMA_API_URL = os.getenv("NEO4J_GENURL")

def stream_response(prompt):
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'llama2',
        'prompt': prompt
    }
    try:
        with requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data), stream=True) as response:
            response.raise_for_status()
            
            # # Process the streaming response
            # for line in response.iter_lines():
            #     if line:
            #         json_res = json.loads(line.decode('utf-8'))
            #         if 'response' in json_res:
            #             yield json_res['response'] + '\n'

            # Get the response
            result = []
            for line in response.iter_lines():
                if line:
                    json_res = json.loads(line.decode('utf-8'))
                    if 'response' in json_res:
                        result.append(json_res['response'])
                        print(json_res['response'], end='', flush=True)
            
            # Join all response parts into a single string
            final_response = ''.join(result)
            return final_response

    except requests.exceptions.RequestException as e:
        yield f"Error: {e}\n"
    except json.JSONDecodeError as e:
        yield f"JSON decode error: {e}\n"

@app.route('/')
def home():
    return jsonify({"message": "Server is running"}), 200

@app.route('/get-response', methods=['POST'])
def get_response():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    return Response(stream_response(prompt), content_type='text/plain')

if __name__ == "__main__":
    app.run(debug=True, port=5000)


# curl -X POST http://127.0.0.1:5000/get-response -H "Content-Type: application/json" -d '{"prompt": "hi"}'
