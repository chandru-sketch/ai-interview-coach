import requests

try:
    r = requests.get("http://127.0.0.1:11434/v1/models", timeout=10)
    print("Server reachable!")
    print(r.json())
except Exception as e:
    print("Error:", e)
