# ai_interview_coach/test_llm.py
from ai_llm import chat_with_model, MODEL_NAME
import requests

def check_server():
    """Check if Ollama server is running."""
    try:
        r = requests.get("http://127.0.0.1:11434/v1/models", timeout=5)
        models = [m["id"] for m in r.json().get("data", [])]
        if MODEL_NAME in models:
            return True
        else:
            print(f"❌ {MODEL_NAME} model not found on the server.")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot reach Ollama server. Please start it with 'ollama serve'.")
        return False

def run_interview():
    if not check_server():
        return

    history = []
    field = "Data Science"
    difficulty = "Expert"
    tag = "Machine Learning"

    print("🤖 Welcome to AI Interview Coach!")
    print(f"Field: {field}, Difficulty: {difficulty}, Tag: {tag}")
    print(f"Using Model: {MODEL_NAME}")
    print("Type 'exit' anytime to stop.\n")

    user_msg = "Hello, let's start the interview."
    while True:
        ai_response = chat_with_model(history, user_msg, field, difficulty, tag)
        print(f"\nAI: {ai_response}\n")

        user_msg = input("You: ")
        if user_msg.lower() in ["exit", "quit", "stop"]:
            print("✅ Interview ended. Good job!")
            break

        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": ai_response})

if __name__ == "__main__":
    run_interview()
