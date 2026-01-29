import ollama
from openai import OpenAI
from .config import settings

class GemmaLLM:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        
        if self.provider == "openai_compatible":
            self.client = OpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL
            )

    def generate(self, prompt: str, context: str = "") -> str:
        full_prompt = (
            f"### Context:\n{context}\n\n"
            f"### Question:\n{prompt}\n\n"
            f"### Answer:"
        )
        
        try:
            if self.provider == "ollama":
                client = ollama.Client(host=settings.OLLAMA_HOST)
                response = client.generate(model=self.model, prompt=full_prompt)
                return response['response']
            elif self.provider == "openai_compatible":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                return response.choices[0].message.content
            else:
                return f"Unsupported provider: {self.provider}"
        except Exception as e:
            return f"Error connecting to {self.provider}: {str(e)}"
