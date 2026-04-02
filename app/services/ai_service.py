import json
import os
import anthropic

SYSTEM_PROMPT_ARTICLE = """Te egy profi magyar SEO szovegiro vagy.
Irj kb. 1200 szavas magyar cikket, strukturalt HTML tartalommal.
KIMENETKENT CSAK ervenyes JSON-t adj vissza, semmi mast.
Pontos formatum:
{
  "title": "...",
  "meta_title": "...",
  "meta_description": "...",
  "excerpt": "...",
  "focus_keyword": "...",
  "tags": ["tag1", "tag2"],
  "content": "<h1>...</h1><h2>...</h2><p>...</p>",
  "seo_score": 87,
  "word_count": 1180
}
"""

SYSTEM_PROMPT_KEYWORDS = """Te egy magyar SEO elemzo vagy.
Adj kulcsszo otleteket JSON tombben, minden elem tartalmazza:
keyword, volume, difficulty, cpc, trend.
Csak ervenyes JSON-t adj vissza.
"""


def _extract_text_from_response(resp) -> str:
    parts: list[str] = []
    for block in resp.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "".join(parts).strip()


def anthropic_key_debug_info() -> dict:
    """For GET /debug/env — no secret values. Only ANTHROPIC_API_KEY."""
    raw = os.environ.get("ANTHROPIC_API_KEY", "")
    key = raw.strip().strip('"').strip("'")
    if key:
        return {"anthropic_api_key_present": True, "env_name_found": "ANTHROPIC_API_KEY"}
    return {"anthropic_api_key_present": False, "env_name_found": None}


async def generate_article(topic: str, target_site: str | None = None) -> dict:
    import os

    all_env_keys = [k for k in os.environ.keys()]
    api_key = os.environ.get("ANTHROPIC_API_KEY", "NOT_FOUND")
    print(f"DEBUG ENV KEYS: {all_env_keys}")
    print(
        f"DEBUG ANTHROPIC KEY: {api_key[:10] if api_key != 'NOT_FOUND' else 'NOT_FOUND'}"
    )

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    user_prompt = f"Tema: {topic}\nCeloldal: {target_site or 'n/a'}"
    resp = await client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=4096,
        temperature=0.4,
        system=SYSTEM_PROMPT_ARTICLE,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = _extract_text_from_response(resp)
    return json.loads(raw)


async def generate_keywords(seed_keyword: str, industry: str | None = None) -> list[dict]:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    user_prompt = f"Magkulcsszo: {seed_keyword}\nIparag: {industry or 'altalanos'}"
    resp = await client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=2048,
        temperature=0.3,
        system=SYSTEM_PROMPT_KEYWORDS,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = _extract_text_from_response(resp)
    parsed = json.loads(raw)
    if isinstance(parsed, dict) and "keywords" in parsed:
        return parsed["keywords"]
    return parsed
