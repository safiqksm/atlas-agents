"""Send a small test prompt to each configured LLM provider.

Usage:
    python ch01_react_from_scratch/check_provider_apis.py
    python ch01_react_from_scratch/check_provider_apis.py "Say hello briefly."

Set OPENAI_API_KEY, GOOGLE_API_KEY, and ANTHROPIC_API_KEY in the project-root
.env file. Values from this file take precedence over shell environment values.
Missing keys are reported as skipped, and the script exits nonzero unless all
three providers respond successfully.
"""

import sys
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

from anthropic import APIError as AnthropicAPIError
from anthropic import Anthropic
from google.genai.errors import APIError as GeminiAPIError
from google import genai
from openai import APIError as OpenAIAPIError
from openai import OpenAI

sys.path.insert(0, str(PROJECT_ROOT))
from shared.config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

PROVIDER_ERRORS = (
    OpenAIAPIError,
    GeminiAPIError,
    AnthropicAPIError,
    RuntimeError,
)
DEFAULT_PROMPT = "Reply with a short greeting to confirm the API is working."


def ask_openai(prompt: str, api_key: str, model: str) -> str:
    response = OpenAI(api_key=api_key).chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or "(empty response)"


def ask_gemini(prompt: str, api_key: str, model: str) -> str:
    with genai.Client(api_key=api_key) as client:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
    return response.text or "(empty response)"


def ask_anthropic(prompt: str, api_key: str, model: str) -> str:
    response = Anthropic(api_key=api_key).messages.create(
        model=model,
        max_tokens=128,
        messages=[{"role": "user", "content": prompt}],
    )
    return "\n".join(
        block.text for block in response.content if block.type == "text"
    ) or "(empty response)"


def check_provider(
    name: str,
    model: str,
    api_key: str,
    ask: Callable[[str, str, str], str],
    prompt: str,
) -> bool:
    if not api_key:
        print(f"[SKIP] {name}: API key is missing from the project-root .env.")
        return False

    try:
        answer = ask(prompt, api_key, model)
    except PROVIDER_ERRORS as error:
        message = str(error).replace(api_key, "[REDACTED]")
        print(f"[FAIL] {name}: {type(error).__name__}: {message}")
        return False

    print(f"[OK] {name} ({model})")
    print(f"     {answer}\n")
    return True


def main() -> int:
    prompt = " ".join(sys.argv[1:]) or DEFAULT_PROMPT
    print(f"Prompt: {prompt}\n")

    providers = [
        ("OpenAI", OPENAI_MODEL, OPENAI_API_KEY, ask_openai),
        ("Gemini", GEMINI_MODEL, GOOGLE_API_KEY, ask_gemini),
        ("Anthropic", ANTHROPIC_MODEL, ANTHROPIC_API_KEY, ask_anthropic),
    ]
    results = [
        check_provider(name, model, api_key, ask, prompt)
        for name, model, api_key, ask in providers
    ]

    passed = sum(results)
    print(f"Result: {passed}/{len(providers)} providers responded successfully.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
