import ollama
from openai import OpenAI
from app.config import settings

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
            "You are a helpful AI assistant. Use the provided context to answer the question accurately.\n"
            "If the context contains the answer (even as a definition or a single sentence), answer it directly.\n"
            "Only say you don't know if the answer is truly not present in the context.\n\n"
            f"### Context:\n{context}\n\n"
            f"### Question:\n{prompt}\n\n"
            f"### Answer:"
        )
        
        try:
            if self.provider == "ollama":
                client = ollama.Client(host=settings.OLLAMA_HOST)
                response = client.generate(
                    model=self.model, 
                    prompt=full_prompt,
                    options={
                        "num_predict": settings.LLM_MAX_TOKENS,
                        "temperature": settings.LLM_TEMPERATURE,
                        "top_p": settings.LLM_TOP_P
                    }
                )
                return response['response']
            elif self.provider == "openai_compatible":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=settings.LLM_MAX_TOKENS,
                    temperature=settings.LLM_TEMPERATURE,
                    top_p=settings.LLM_TOP_P
                )
                return response.choices[0].message.content
            else:
                return f"Unsupported provider: {self.provider}"
        except Exception as e:
            return f"Error connecting to {self.provider}: {str(e)}"
