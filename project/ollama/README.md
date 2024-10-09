# Ollama 

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama2
```

## Routes

- **GET**: `/` : Checks API status.
- **POST**: `/api/get-entire-response` : Gets reponse from LLM.
- **POST**: `/api/get-rag-response` : Gets reponse from RAG.

## Examples

```bash
curl -X POST http://127.0.0.1:5000/get-entire-response -H "Content-Type: application/json" -d '{"prompt": "hi"}'
```

```bash
curl -X POST http://127.0.0.1:5000/get-rag-response -H "Content-Type: application/json" -d '{"prompt": "what is this document about", "file_name": "Resume.pdf"}'
```
