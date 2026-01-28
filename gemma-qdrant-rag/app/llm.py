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
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        full_prompt = f"""
        You are a helpful AI assistant. 
        Current Time: {current_time}
        
        Context information (if any):
        ---------------------
        {context}
        ---------------------
        
        Task:
        1. Use the provided context to answer the query if the information is present there.
        2. If the context does not contain the answer, use your own internal knowledge to provide a helpful response.
        3. If the user asks for the time, use the "Current Time" provided above.
        
        Query: {prompt}
        Answer:
        """
        
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
