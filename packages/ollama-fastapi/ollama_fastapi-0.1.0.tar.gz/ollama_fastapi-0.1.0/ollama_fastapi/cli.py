import uvicorn

def main():
    """Start the FastAPI server."""
    uvicorn.run("ollama_fastapi.main:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
