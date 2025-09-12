import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-coder"  # 或 deepseek-chat, 视本地模型而定

def get_deepseek_reply(prompt: str) -> str:
    """
    调用本地 Ollama 的 DeepSeek 模型，返回回复文本。
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Ollama 返回格式通常为 {'response': '...'}
    return data.get("response", "").strip()