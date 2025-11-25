# ================================
# Importing necessary libraries
# ================================
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime, timezone
import os

# Import your existing ask_bot function
from bot import ask_bot  

# ======================================
# FASTAPI PART
# ======================================
app = FastAPI(
    title="Mini Health Chatbot API",
    description="API for chatting with your health-restricted bot",
    version="1.0.0"
)

# Configure CORS origins via environment variable `ALLOWED_ORIGINS` (comma-separated).
# Falls back to a sensible default for local testing and the deployed frontend.
allowed = os.getenv("ALLOWED_ORIGINS")
if allowed:
    allow_origins = [o.strip() for o in allowed.split(",") if o.strip()]
else:
    allow_origins = [
        "https://chatbot-plum-seven.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class ChatRequest(BaseModel):
    message: str = Field(examples=["How do I stay healthy?"])
    api_key: Optional[str] = None
    use_password_mode: bool = False
    password: Optional[str] = None
    
    
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        req_ts = datetime.now(timezone.utc).isoformat()

        if request.api_key:
            response = ask_bot(request.message, request.api_key)

        elif request.use_password_mode:
            admin_pwd = os.getenv("ADMIN_PASSWORD")
            if not admin_pwd or request.password is None:
                return {"error": "Invalid password"}

            if request.password.lower() != admin_pwd.lower():
                return {"error": "Invalid password"}

            response = ask_bot(request.message)

        else:
            return {"error": "Provide api_key or enable password mode"}

        res_ts = datetime.now(timezone.utc).isoformat()
        return {
            "response": response,
            "request_ts": req_ts,
            "response_ts": res_ts
        }

    except Exception as e:
        return {"error": str(e)}

# Optional API check route
@app.get("/api")
def check_api():
    return {"message": "API running"}

static_dir = Path(__file__).parent / "frontend"
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="frontend")
