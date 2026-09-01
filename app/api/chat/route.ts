import { SYSTEM_PROMPT } from '../../../lib/prompt';

function normalizeMessages(messages: any[]) {
  return (messages || []).slice(-30).map((m: any) => ({
    role: m.role === 'assistant' ? 'assistant' : 'user',
    content: String(m.content ?? ''),
  }));
}

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    const input = normalizeMessages(messages);
    const baseUrl = (process.env.MC_DEV_AI_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
    const response = await fetch(`${baseUrl}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          ...input,
        ],
        max_new_tokens: 240,
        temperature: 0.72,
      }),
      cache: 'no-store',
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok || data?.error) {
      throw new Error(data?.error || `MC Dev AI backend returned HTTP ${response.status}`);
    }

    return Response.json({ text: data.text || 'No response generated.', provider: 'mc-dev-tinygpt' });
  } catch (error: any) {
    return Response.json(
      { error: String(error?.message || 'MC Dev AI backend is unreachable. Start the local AI service on port 8000.') },
      { status: 503 },
    );
  }
}
