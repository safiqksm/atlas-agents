"""
Atlas v0.1 — Streaming Variant (Online Extra)
================================================
Demonstrates real-time streaming with the Anthropic API.

Usage:
    python atlas_v01_streaming_fixed.py "What is the Model Context Protocol?"

Requires: pip install anthropic python-dotenv
"""

import sys
from pathlib import Path

from anthropic import APIError, Anthropic
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)
sys.path.insert(0, str(PROJECT_ROOT))

from shared.config import require_key

MODEL = "claude-sonnet-5-5"


def stream_agent_response(prompt: str) -> None:
    """Stream the model response in real time."""
    print("🔄 Streaming response...\n")
    client = Anthropic(api_key=require_key("anthropic"))

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=1000,
            system="You are Atlas, a research assistant. Think step by step before answering.",
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            current_type = None
            for event in stream:
                if event.type == "content_block_start":
                    block = event.content_block
                    if block.type == "text":
                        if current_type != "text":
                            current_type = "text"
                            print("💭 ", end="", flush=True)
                    elif block.type == "tool_use":
                        current_type = "tool"
                        print(f"\n🔧 [Tool Call: {block.name}]", flush=True)

                elif event.type == "content_block_delta":
                    delta = event.delta
                    if hasattr(delta, "text"):
                        print(delta.text, end="", flush=True)
                    elif hasattr(delta, "partial_json"):
                        print(f"  args: {delta.partial_json}", end="", flush=True)

        print("\n\n✅ Stream complete.")
    finally:
        client.close()


def main() -> int:
    prompt = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "Explain how AI agents use tools, step by step."
    )
    print(f"🔍 Atlas v0.1 (Streaming) — {prompt}\n")

    try:
        stream_agent_response(prompt)
    except APIError as error:
        print(f"Anthropic API request failed: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
