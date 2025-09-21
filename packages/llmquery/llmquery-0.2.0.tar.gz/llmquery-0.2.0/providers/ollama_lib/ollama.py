import requests

"""
 curl http://localhost:11434/api/generate -d '{
  "model": "gemma:2b",
  "system": "X",
  "prompt": "What is the sky blue?",
  "stream": false
}'
"""

OLLAMA_API_ENDPOINT = "http://localhost:11434/api/generate"

ACCEPTED_MODELS = [
    # Meta Llama
    "llama4",
    "llama4:16x17b",
    "llama4:128x17b",
    "llama3.3",
    "llama3.2",
    "llama3.2-vision",
    "llama3.1:8b",
    "llama3.1:70b",
    "llama3.1:405b",
    # Alibaba Qwen
    "qwen3",
    "qwen2.5:7b",
    "qwen2.5:14b",
    "qwen2.5:32b",
    "qwen2.5:72b",
    # Google Gemma
    "gemma3n",
    "gemma2:2b",
    "gemma2:9b",
    "gemma2:27b",
    # DeepSeek
    "deepseek-r1",
    # Other models
    "phi4",
    "mistral-nemo",
]

DEFAULT_MODEL = "llama3.3"
DEFAULT_SYSTEM_PROMPT = "You are a highly intelligent assistant. Respond to user queries with precise, well-informed answers on the first attempt. Tailor responses to the user's context and intent, using clear and concise language. Always prioritize relevance, accuracy, and value."


def ollama_generate_content(
    url_endpoint: str = None,
    model: str = None,
    system_prompt: str = None,
    user_prompt: str = None,
):

    if not url_endpoint:
        url_endpoint = OLLAMA_API_ENDPOINT
    if not model:
        # There are not default set of accepted models for Ollama
        model = DEFAULT_MODEL
    if not system_prompt:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    if not user_prompt:
        raise ValueError("User prompt is required.")

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
    }

    response = requests.post(url_endpoint, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(
            f"Failed to connect to OLLAMA API. Status code: {response.status_code}. Response: {response.text}"
        )

    output = {
        "raw_response": response,
        "status_code": response.status_code,
        "data": data,
        "response": "",
    }

    if "response" not in response.json():
        raise Exception(
            f"Invalid response from OLLAMA API. Response: {response.json()}"
        )

    output["response"] = response.json()["response"]

    return output
