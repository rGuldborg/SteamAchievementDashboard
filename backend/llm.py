import os
import json
import httpx
from models import Achievement, LLMEstimate

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-small-latest"


def build_prompt(achievements: list[Achievement]) -> str:
    lines = []
    for a in achievements[:30]:
        lines.append(f"- {a.display_name}: {a.global_percent}% completion globally")

    achievement_text = "\n".join(lines)

    return (
        "Du er en Steam-gaming ekspert. Baseret på følgende achievements og deres "
        "globale completion-procenter, estimer hvor mange timer det typisk tager at "
        "gennemføre spillet 100%. Husk at lav completion-procent betyder at achievementet "
        "er svært eller tidskrævende.\n\n"
        f"Achievements:\n{achievement_text}\n\n"
        "Svar med et JSON-objekt i præcis dette format (svar på dansk):\n"
        '{"estimated_hours": "X-Y timer", "reasoning": "kort forklaring på dansk"}'
    )


def estimate_completion_time(achievements: list[Achievement]) -> LLMEstimate:
    prompt = build_prompt(achievements)

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": MISTRAL_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
    }

    resp = httpx.post(MISTRAL_URL, headers=headers, json=body, timeout=30)
    resp.raise_for_status()

    content = resp.json()["choices"][0]["message"]["content"]
    parsed = json.loads(content)

    return LLMEstimate(
        estimated_hours=parsed.get("estimated_hours", "Ukendt"),
        reasoning=parsed.get("reasoning", ""),
    )
