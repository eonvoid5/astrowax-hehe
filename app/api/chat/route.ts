import { SYSTEM_PROMPT } from '../../../lib/prompt';

function normalizeMessages(messages: any[]) {
  return (messages || []).slice(-30).map((m: any) => ({
    role: m.role === 'assistant' ? 'assistant' : 'user',
    content: String(m.content ?? ''),
  }));
}

function extractOpenAIText(data: any) {
  if (typeof data?.output_text === 'string' && data.output_text) return data.output_text;
  const parts = data?.output?.flatMap((item: any) => item?.content || []) || [];
  return parts
    .filter((part: any) => part?.type === 'output_text' && typeof part?.text === 'string')
    .map((part: any) => part.text)
    .join('\n')
    .trim();
}

async function askOpenAI(messages: any[]) {
  const key = process.env.OPENAI_API_KEY;
  if (!key) throw new Error('OPENAI_API_KEY is not configured.');

  const model = process.env.OPENAI_MODEL || 'gpt-5.6-luna';
  const baseUrl = (process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1').replace(/\/$/, '');

  const response = await fetch(`${baseUrl}/responses`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${key}`,
    },
    body: JSON.stringify({
      model,
      instructions: SYSTEM_PROMPT,
      input: messages,
      temperature: 0.2,
    }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data?.error?.message || `OpenAI returned HTTP ${response.status}`);

  return extractOpenAIText(data) || 'No response generated.';
}

async function askOllama(messages: any[]) {
  const baseUrl = (process.env.OLLAMA_URL || 'http://127.0.0.1:11434').replace(/\/$/, '');
  const model = process.env.OLLAMA_MODEL || 'qwen3:8b';

  const response = await fetch(`${baseUrl}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model,
      stream: false,
      messages: [{ role: 'system', content: SYSTEM_PROMPT }, ...messages],
      options: { temperature: 0.2 },
    }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data?.error || `Ollama returned HTTP ${response.status}`);
  return data?.message?.content || 'No response generated.';
}

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    const input = normalizeMessages(messages);
    const provider = (process.env.AI_PROVIDER || (process.env.OPENAI_API_KEY ? 'openai' : 'ollama')).toLowerCase();

    if (provider === 'openai') {
      return Response.json({ text: await askOpenAI(input), provider: 'openai' });
    }

    return Response.json({ text: await askOllama(input), provider: 'ollama' });
  } catch (error: any) {
    const message = String(error?.message || error || 'Unknown AI error');
    return Response.json(
      {
        error:
          message.includes('OPENAI_API_KEY')
            ? 'OpenAI is selected but OPENAI_API_KEY is missing. Add it to the VPS environment, or set AI_PROVIDER=ollama to use local AI.'
            : message.includes('fetch') || message.includes('Ollama')
              ? 'The AI backend is unreachable. On a VPS using Ollama, start Ollama and install the configured model. If you want ChatGPT-style answers, configure OPENAI_API_KEY and AI_PROVIDER=openai.'
              : message,
      },
      { status: 503 },
    );
  }
}
