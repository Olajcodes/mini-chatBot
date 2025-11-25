# Importing necessary libraries
from openai import OpenAI
from dotenv import load_dotenv
try:
    from yaspin import yaspin
except Exception:
    class _Dummy:
        def __init__(self, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            return False
    def yaspin(**kwargs):
        return _Dummy()
import os
from typing import Optional

# Loading the .env file (optional for local dev)
load_dotenv()

# Fetch the key form the dotenv to a variable name
default_api_key = os.getenv("OPENAI_API_KEY")

# ======================================
# CHATBOT CONFIGURATION & PERSONA
# ======================================
SYSTEM_PROMPT = (
    "You are a strictly health-focused AI assistant. "
    "You must only answer questions related to health, fitness, nutrition,"
    "diseases, medications, medical advice, anatomy, physiology, or wellbeing. "
    "If the user asks anything outside health, politely decline. "
    "Never provide instructions that could cause harm. "
    "If a question requires urgent medical attention, instruct the user to see a doctor immediately. "
    "Format all responses as clean plain text with no markdown or special characters."
)
# ================================
        # Model configuration
# ================================
MODEL_NAME = "gpt-5-chat-latest"
TEMPERATURE = 0.2
TOP_P = 0.9
MAX_OUTPUT_TOKENS = 400

# Limit chat history size
MAX_HISTORY = 10  # last 10 messages only


# Maintain a list for chat history (simple global demo)
chat_history = []

def get_currentTime() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

def get_client(provided_key: Optional[str]) -> OpenAI:
    """Create an OpenAI client using the provided key or environment.
    Raises if no key can be found.
    """
    key = provided_key or default_api_key
    if not key:
        raise ValueError("No OpenAI API key available. Provide OpenAI-Key or set OPENAI_API_KEY.")
    return OpenAI(api_key=key)


# ======================================
        # Function to Ask the Bot
# ======================================
def ask_bot(user_message: str, api_key: Optional[str] = None) -> str:
    """
    Sends a question to the health bot and returns the response.
    Keeps context history so the bot can remember previous messages.
    """
    client = get_client(api_key)
    
    # Add user message to history with timestamp
    chat_history.append({"role": "user", "content": user_message, "ts": get_currentTime()})
    
    # Build input with system prompt & history
    # Map internal history to API-compatible messages (ignore extra fields like ts)
    input_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m.get("role", "user"), "content": m.get("content", "")} for m in chat_history
    ]
    
    # Nice loading state (terminal mode)
    with yaspin(text="Bot thinking...", color="cyan"):
        try:
            response = client.responses.create(
                model=MODEL_NAME,
                input=input_messages,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )
        except Exception as e:
            # Surface useful debugging info in logs and raise so the API can return the error
            # The exception message from the SDK usually contains status and details (e.g., model not found)
            err_msg = f"OpenAI API call failed: {e}"
            print(err_msg)
            raise RuntimeError(err_msg)
        
    answer = response.output_text.strip()
        
    # Update bot's answer to history
    chat_history.append({"role": "assistant", "content": answer, "ts": get_currentTime()})
    
    # Validate chat history
    if len(chat_history) > MAX_HISTORY:
        chat_history[:] = chat_history[-MAX_HISTORY:]

    return answer


# Optional code for running continuous on Terminal
if __name__ == "__main__":
    print("Mini-Health ChatBot (type 'exit' to quit)")
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        answer = ask_bot(user_input)
        print(f"\nBot: {answer}")
