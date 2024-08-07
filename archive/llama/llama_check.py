import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
OLLAMA_API_URL = os.getenv("LLM_GENERATE_URL")

def get_response(prompt):
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
            
            # Process the streaming response
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
        return f"Error: {e}"
    except json.JSONDecodeError as e:
        return f"JSON decode error: {e}"

if __name__ == "__main__":
    prompt = "Hi"
    print(f"Prompt: {prompt}\n")
    response = get_response(prompt)
