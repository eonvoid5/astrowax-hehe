import argparse, os, random
import torch
from model import TinyGPT

DATA = os.path.join(os.path.dirname(__file__), "data", "minecraft.txt")
OUT = os.path.join(os.path.dirname(__file__), "checkpoints", "mcdevai.pt")


def load_bytes():
    with open(DATA, "rb") as f:
        raw = f.read()
    if len(raw) < 4096:
        raise RuntimeError("Training corpus is too small. Add more Minecraft/hosting text to ai/data/minecraft.txt")
    return torch.tensor(list(raw), dtype=torch.long)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=3000)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--block-size", type=int, default=256)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--resume", action="store_true")
    args = p.parse_args()

    torch.manual_seed(7)
    data = load_bytes()
    split = int(len(data) * 0.95)
    train, valid = data[:split], data[split:]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = TinyGPT(block_size=args.block_size).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.1)

    if args.resume and os.path.exists(OUT):
        state = torch.load(OUT, map_location=device)
        model.load_state_dict(state["model"])
        optimizer.load_state_dict(state["optimizer"])
        print("resumed", OUT)

    def batch(source):
        starts = torch.randint(0, len(source) - args.block_size - 1, (args.batch_size,))
        x = torch.stack([source[i:i+args.block_size] for i in starts]).to(device)
        y = torch.stack([source[i+1:i+args.block_size+1] for i in starts]).to(device)
        return x, y

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    model.train()
    for step in range(1, args.steps + 1):
        x, y = batch(train)
        _, loss = model(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step == 1 or step % 100 == 0:
            with torch.no_grad():
                vx, vy = batch(valid)
                _, vloss = model(vx, vy)
            print(f"step={step} train={loss.item():.4f} valid={vloss.item():.4f} device={device}")
            torch.save({"model": model.state_dict(), "optimizer": optimizer.state_dict(), "config": vars(args)}, OUT)

    print("saved", OUT)

if __name__ == "__main__":
    main()
