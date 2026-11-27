from google import genai
from google.genai import types

client = genai.Client()


def get_weather(city: str) -> str:
    """Return a sample weather report for a city."""
    return f"The weather in {city} is 22 degrees C and sunny."


config = types.GenerateContentConfig(
    tools=[get_weather],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What's the weather in Tokyo?",
    config=config,
)

print(response.text)
