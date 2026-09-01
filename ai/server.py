import os
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from model import TinyGPT

BASE = os.path.dirname(__file__)
CHECKPOINT = os.path.join(BASE, "checkpoints", "mcdevai.pt")
DATA = os.path.join(BASE, "data", "minecraft.txt")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
app = FastAPI(title="MC Dev AI Local Model")
model = None

class ChatRequest(BaseModel):
    messages: list[dict]
    max_new_tokens: int = 220
    temperature: float = 0.72


def load_model():
    global model
    if not os.path.exists(CHECKPOINT):
        return False
    model = TinyGPT().to(DEVICE)
    state = torch.load(CHECKPOINT, map_location=DEVICE)
    model.load_state_dict(state["model"])
    model.eval()
    return True


def clean(text: str) -> str:
    for marker in ("\nUser:", "\nUSER:", "\n### User:"):
        if marker in text:
            text = text.split(marker, 1)[0]
    return text.strip()

@app.on_event("startup")
def startup():
    load_model()

@app.get("/health")
def health():
    return {"ok": True, "model_loaded": model is not None, "device": DEVICE, "model": "MC-Dev-TinyGPT"}

@app.post("/generate")
def generate(req: ChatRequest):
    if model is None:
        return {"error": "MC Dev AI has not been trained yet. Run: python ai/train.py --steps 3000"}
    lines = ["MC Dev AI is a Minecraft engineering assistant. Be helpful, practical and concise."]
    for m in req.messages[-12:]:
        role = "User" if m.get("role") == "user" else "MC Dev AI"
        lines.append(f"{role}: {str(m.get('content',''))}")
    lines.append("MC Dev AI:")
    prompt = "\n".join(lines)
    ids = torch.tensor([list(prompt.encode("utf-8"))], dtype=torch.long, device=DEVICE)
    ids = ids.clamp(0, 255)
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=min(req.max_new_tokens, 400), temperature=req.temperature)
    generated = bytes(out[0].tolist()).decode("utf-8", errors="ignore")
    answer = clean(generated[len(prompt):])
    return {"text": answer or "I need a little more training data before I can answer that well.", "provider": "mc-dev-tinygpt"}
