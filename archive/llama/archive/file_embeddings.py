import os
import requests
import json
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

load_dotenv()

# Ollama API URL
OLLAMA_API_URL = os.getenv("NEO4J_GENURL")

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def create_embeddings(text, model_name='sentence-transformers/all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    sentences = text.split('.')
    embeddings = model.encode(sentences)
    return sentences, embeddings

def save_embeddings_to_faiss(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def find_most_similar(sentence_embedding, index, k=5):
    distances, indices = index.search(np.array([sentence_embedding]), k)
    return indices[0]

def get_response_from_ollama_llama2(prompt):
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
            
            result = []
            for line in response.iter_lines():
                if line:
                    json_res = json.loads(line.decode('utf-8'))
                    if 'response' in json_res:
                        result.append(json_res['response'])
                        print(json_res['response'], end='', flush=True)
            
            final_response = ''.join(result)
            return final_response
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except json.JSONDecodeError as e:
        return f"JSON decode error: {e}"

if __name__ == "__main__":
    # Step 1: Extract text from PDF
    pdf_path = 'doc.pdf'
    text = extract_text_from_pdf(pdf_path)
    
    # Step 2: Create embeddings
    sentences, embeddings = create_embeddings(text)
    
    # Step 3: Save embeddings to FAISS
    index = save_embeddings_to_faiss(embeddings)
    
    # Step 4: Ask a question and find relevant sentences
    question = "Explain the main idea of the document."
    question_embedding = create_embeddings(question)[1][0]
    similar_indices = find_most_similar(question_embedding, index)
    
    # Step 5: Generate response from the most similar sentences
    context = ' '.join([sentences[idx] for idx in similar_indices])
    prompt = f"{context}\n\n{question}"
    print(f"\nPrompt: {prompt}\n")
    response = get_response_from_ollama_llama2(prompt)
    print(f"\nFinal Response: {response}")
