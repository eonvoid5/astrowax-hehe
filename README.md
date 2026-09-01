# MC Dev AI — VPS Edition

Minecraft development + hosting AI copilot designed to run directly on your VPS.

## Recommended: local Ollama AI

This version does **not** require an OpenAI API key. It connects to Ollama running on the same VPS. Ollama's official Qwen3 8B package is about 5.2 GB and can be run with `ollama run qwen3:8b`.

### 1. Install Ollama on the VPS

Install Ollama using its official installer, then run:

```bash
ollama pull qwen3:8b
```

### 2. Install Node.js dependencies

```bash
npm install
```

### 3. Configure

```bash
cp .env.example .env.local
```

Default values:

```env
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:8b
```

### 4. Build and start

```bash
npm run build
npm run start -- -H 0.0.0.0 -p 3000
```

Then open:

`http://YOUR_VPS_IP:3000`

For production, put Nginx/Caddy/Cloudflare in front of port 3000 and use HTTPS.

## Docker option

If Docker is installed:

```bash
docker compose up -d --build
```

The app is exposed on port 3000 and reaches Ollama on the VPS host.

## What it knows about

Paper, Spigot, Bukkit, Purpur, Fabric, Forge, NeoForge, Velocity, BungeeCord, plugins, mods, datapacks, commands, permissions, Java, Gradle/Maven, server.properties, configs, performance, JVM flags, Linux, Docker, Pterodactyl/Wings, reverse proxies, Cloudflare tunnels, networking, DNS, backups, security, logs and debugging.
