import os
import pickle
import secrets
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from help_man import ChatPipeline  # lets pickle find the class

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("Set API_KEY in your .env file")

with open("chat_pipeline.pkl", "rb") as f:
    pipe = pickle.load(f)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(key: str = Security(api_key_header)):
    if not key or not secrets.compare_digest(key, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

app = FastAPI()

class Req(BaseModel):
    message: str
    history: list[dict] = []

@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}

@app.post("/chat", dependencies=[Depends(verify_api_key)])
def chat(req: Req):
    try:
        reply, history = pipe.run(req.message, req.history)
        return {"reply": reply, "history": history}
    except Exception as e:
        print("Error:", repr(e))
        raise HTTPException(status_code=500, detail="Internal server error")