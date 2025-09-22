# Ollama FastAPI Wrapper

A simple FastAPI wrapper for [Ollama](https://ollama.ai) models.

## Installation
```bash
pip install ollama-fastapi
```

## Usage

### Run API server
```bash
ollama-fastapi
```

### Call API
```bash
curl -X POST http://127.0.0.1:8000/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Write a haiku about FastAPI"}'
```

### Use in Python
```python
from ollama_fastapi.client import OllamaClient

ollama = OllamaClient("llama3")
print(ollama.generate("Hello world"))
```
