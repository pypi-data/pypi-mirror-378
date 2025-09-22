import subprocess

class OllamaClient:
    def __init__(self, model="llama3"):
        self.model = model

    def generate(self, prompt: str) -> str:
        """Run Ollama locally with the given prompt."""
        cmd = ["ollama", "run", self.model]
        process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        out, err = process.communicate(input=prompt)
        if process.returncode != 0:
            raise RuntimeError(f"Ollama error: {err.strip()}")
        return out.strip()
