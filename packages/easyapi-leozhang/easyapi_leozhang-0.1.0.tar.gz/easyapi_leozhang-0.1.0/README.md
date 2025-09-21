# easyapi

A simple unified Python API wrapper for 5 major AI models:

- OpenAI
- Anthropic
- Google Gemini
- Mistral
- Cohere

## Installation

```bash
pip install easyapi
```

## Usage

```python
from easyapi import run

response = run("openai", "your_openai_api_key", "Hello, who are you?")
print(response)
```
