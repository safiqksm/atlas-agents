"""Anthropic ReAct example with project .env loading and safe arithmetic.

Usage:
    python online/atlas_v01_anthropic_fixed.py "What is 42 * 17?"
"""

import ast
import math
import sys
from pathlib import Path

from anthropic import APIError, Anthropic
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)
sys.path.insert(0, str(PROJECT_ROOT))

from shared.config import require_key
from shared.skills import WebSkill

_web = WebSkill()
MODEL = "claude-sonnet-5-5"

TOOLS = [
    {
        "name": "search_web",
        "description": "Search the web using DuckDuckGo. Returns top results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic such as '2 + 3 * 4'",
                }
            },
            "required": ["expression"],
        },
    },
]


def _evaluate_arithmetic(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Only numeric values are allowed.")
        return value

    if isinstance(node, ast.UnaryOp):
        value = _evaluate_arithmetic(node.operand)
        if isinstance(node.op, ast.UAdd):
            return value
        if isinstance(node.op, ast.USub):
            return -value
        raise ValueError("Unsupported unary operator.")

    if isinstance(node, ast.BinOp):
        left = _evaluate_arithmetic(node.left)
        right = _evaluate_arithmetic(node.right)
        if isinstance(node.op, ast.Add):
            result = left + right
        elif isinstance(node.op, ast.Sub):
            result = left - right
        elif isinstance(node.op, ast.Mult):
            result = left * right
        elif isinstance(node.op, ast.Div):
            result = left / right
        elif isinstance(node.op, ast.FloorDiv):
            result = left // right
        elif isinstance(node.op, ast.Mod):
            result = left % right
        elif isinstance(node.op, ast.Pow):
            if abs(right) > 100:
                raise ValueError("Exponent magnitude must be at most 100.")
            result = left**right
        else:
            raise ValueError("Unsupported arithmetic operator.")

        if isinstance(result, int) and result.bit_length() > 4096:
            raise ValueError("Result is too large.")
        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("Result is not finite.")
        return result

    raise ValueError("Use numeric literals and basic arithmetic only.")


def calculate(expression: str) -> int | float:
    if len(expression) > 256:
        raise ValueError("Expression is too long.")

    parsed = ast.parse(expression, mode="eval")
    if sum(1 for _ in ast.walk(parsed)) > 100:
        raise ValueError("Expression is too complex.")
    return _evaluate_arithmetic(parsed.body)


def execute_tool(name: str, args: dict) -> str:
    if name == "search_web":
        query = args.get("query")
        if not isinstance(query, str):
            return "Error: query must be a string."
        return _web._search(query)

    if name == "calculator":
        expression = args.get("expression")
        if not isinstance(expression, str):
            return "Error: expression must be a string."
        try:
            return str(calculate(expression))
        except (ArithmeticError, SyntaxError, ValueError) as error:
            return f"Calculator error: {error}"

    return f"Unknown tool: {name}"


def run_anthropic_react(prompt: str, max_iterations: int = 5) -> str:
    """Run a ReAct loop using Anthropic's tool-calling API."""
    messages = [{"role": "user", "content": prompt}]
    client = Anthropic(api_key=require_key("anthropic"))

    try:
        for iteration in range(max_iterations):
            print(f"\n── Iteration {iteration + 1} ──")
            response = client.messages.create(
                model=MODEL,
                max_tokens=1000,
                system="You are Atlas, a research assistant. Use tools to find answers.",
                tools=TOOLS,
                messages=messages,
            )

            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})
            tool_use_blocks = [
                block for block in assistant_content if block.type == "tool_use"
            ]

            if not tool_use_blocks:
                text_blocks = [
                    block.text for block in assistant_content if block.type == "text"
                ]
                print("Final answer received.")
                return "\n".join(text_blocks)

            tool_results = []
            for block in tool_use_blocks:
                print(f"Calling: {block.name}({block.input})")
                result = execute_tool(block.name, block.input)
                print(f"Tool result: {result[:150]}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        return "Agent reached maximum iterations."
    finally:
        client.close()


def main() -> int:
    question = " ".join(sys.argv[1:]) or "What is 42 * 17?"
    print(f"Atlas v0.1 (Anthropic) — {question}\n")

    try:
        answer = run_anthropic_react(question)
    except APIError as error:
        print(f"Anthropic API request failed: {error}", file=sys.stderr)
        return 1

    print(f"\n{'=' * 50}\nFINAL ANSWER:\n{'=' * 50}\n{answer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
