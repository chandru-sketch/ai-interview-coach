import requests

try:
    # Check the Ollama server models endpoint
    r = requests.get("http://127.0.0.1:11434/v1/models", timeout=5)
    print("✅ Connected! Models:", r.json())
except Exception as e:
    print("❌ Cannot reach Ollama server:", e)
