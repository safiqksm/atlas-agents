import json

from openai import OpenAI

client = OpenAI()

# 1. Define a tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"],
            },
        },
    }
]


# 2. Implement the tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is 22 degrees C and sunny."


# 3. Call the LLM, execute tool calls, and send results back
messages = [{"role": "user", "content": "What's the weather in Tokyo?"}]

while True:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )
    message = response.choices[0].message
    messages.append(message)

    if not message.tool_calls:
        print(message.content)
        break

    for tool_call in message.tool_calls:
        if tool_call.function.name != "get_weather":
            raise ValueError(f"Unknown tool: {tool_call.function.name}")

        arguments = json.loads(tool_call.function.arguments)
        result = get_weather(**arguments)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
        )
