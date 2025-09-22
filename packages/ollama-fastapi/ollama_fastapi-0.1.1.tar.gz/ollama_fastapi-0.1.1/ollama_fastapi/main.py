from fastapi import FastAPI
from pydantic import BaseModel
from .client import OllamaClient

app = FastAPI(title="Ollama FastAPI Wrapper", version="0.1.0")
ollama = OllamaClient(model="llama3")

class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate_text(req: PromptRequest):
    """Send a prompt to Ollama and return the generated text."""
    try:
        response = ollama.generate(req.prompt)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
