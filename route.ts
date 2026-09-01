import { SYSTEM_PROMPT } from '@/lib/prompt';

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    const baseUrl = (process.env.OLLAMA_URL || 'http://127.0.0.1:11434').replace(/\/$/, '');
    const model = process.env.OLLAMA_MODEL || 'qwen3:8b';

    const input = (messages || []).slice(-20).map((m: any) => ({
      role: m.role === 'assistant' ? 'assistant' : 'user',
      content: String(m.content),
    }));

    const response = await fetch(`${baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        stream: false,
        messages: [{ role: 'system', content: SYSTEM_PROMPT }, ...input],
        options: { temperature: 0.2 },
      }),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      return Response.json(
        { error: data?.error || `Ollama returned HTTP ${response.status}` },
        { status: 502 },
      );
    }

    return Response.json({ text: data?.message?.content || 'No response generated.' });
  } catch (error) {
    return Response.json(
      { error: 'Could not reach Ollama. Make sure Ollama is running and the model is installed.' },
      { status: 503 },
    );
  }
}
