import os
import requests
from django.conf import settings

API_URL = "https://api.anthropic.com/v1/complete"


def generate(prompt: str, model: str = "claude-haiku-4.5", temperature: float = 0.0, max_tokens: int = 300):
    """Simple HTTP client for Anthropic Claude-compatible endpoint.

    This function uses a very small HTTP wrapper. If `ANTHROPIC_API_KEY` is not set
    it returns a helpful placeholder string so local development continues.
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY') or getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        return "[Anthropic API key not configured — set ANTHROPIC_API_KEY to enable AI responses]"

    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
    }

    payload = {
        'model': model,
        'prompt': prompt,
        'max_tokens_to_sample': max_tokens,
        'temperature': temperature,
    }

    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=20)
        r.raise_for_status()
    except Exception as e:
        return f"[Anthropic request failed: {e}]"

    data = r.json()
    # best-effort: try common response shapes
    if 'completion' in data:
        return data['completion']
    if 'output' in data and isinstance(data['output'], dict):
        return data['output'].get('text', str(data))
    # fallback to raw json
    return str(data)
