import requests

class EasyAPI:
    def __init__(self):
        self.supported_models = ["openai", "anthropic", "gemini", "mistral", "cohere"]

    def run(self, module, apikey, prompt):
        module = module.lower()
        if module not in self.supported_models:
            raise ValueError(f"Unsupported module: {module}")

        if module == "openai":
            return self._openai(apikey, prompt)
        elif module == "anthropic":
            return self._anthropic(apikey, prompt)
        elif module == "gemini":
            return self._gemini(apikey, prompt)
        elif module == "mistral":
            return self._mistral(apikey, prompt)
        elif module == "cohere":
            return self._cohere(apikey, prompt)

    def _openai(self, key, prompt):
        headers = {"Authorization": f"Bearer {key}"}
        json = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}]
        }
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json)
        return r.json()["choices"][0]["message"]["content"]

    def _anthropic(self, key, prompt):
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
        json = {
            "model": "claude-2.1",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=json)
        return r.json()["content"][0]["text"]

    def _gemini(self, key, prompt):
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text

    def _mistral(self, key, prompt):
        headers = {"Authorization": f"Bearer {key}"}
        json = {
            "model": "mistral-small",
            "messages": [{"role": "user", "content": prompt}]
        }
        r = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=json)
        return r.json()["choices"][0]["message"]["content"]

    def _cohere(self, key, prompt):
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        json = {"model": "command-r", "prompt": prompt, "max_tokens": 300}
        r = requests.post("https://api.cohere.ai/v1/generate", headers=headers, json=json)
        return r.json()["generations"][0]["text"]
