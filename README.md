# MC Dev AI — Own Local AI

MC Dev AI is being built as its own Minecraft-focused AI stack. It no longer depends on Ollama or an OpenAI API to answer chats.

## Architecture

```text
Browser
  ↓
Next.js MC Dev AI UI
  ↓
/api/chat
  ↓
Python AI service :8000
  ↓
MC-Dev-TinyGPT (Transformer trained from random weights)
  ↓
Minecraft + hosting training corpus
```

The first model is intentionally small so we can train and test it on a normal VPS. It is a foundation, not a ChatGPT-scale model yet. A useful human-like model requires much more training data and compute. Training a language model from scratch generally needs considerably more compute than fine-tuning an existing model.

## Start locally

Install Python dependencies:

```bash
pip install -r ai/requirements.txt
```

Train the first model:

```bash
python ai/train.py --steps 3000
```

The checkpoint is saved to `ai/checkpoints/mcdevai.pt` and is intentionally ignored by Git.

Start the AI service:

```bash
uvicorn ai.server:app --host 0.0.0.0 --port 8000
```

In another terminal, start the web app:

```bash
npm install
npm run build
npm run start -- -H 0.0.0.0 -p 3000
```

## Docker

```bash
docker compose up -d --build
```

The web app is on port 3000. The model service stays internal on port 8000.

## Growing the AI

Put additional clean Minecraft/hosting material into `ai/data/minecraft.txt` or extend the data pipeline. The long-term plan is:

1. Larger tokenizer and dataset.
2. Much larger Transformer.
3. Minecraft-specific instruction/chat data.
4. Retrieval from official Minecraft/Paper/Pterodactyl/Linux documentation.
5. Tool calling for logs, configs and server diagnostics.
6. Conversation memory.
7. Evaluation tests so the model learns useful answers instead of memorizing nonsense.
8. GPU training and quantized VPS inference.

Do not commit API keys or model checkpoints to Git.
