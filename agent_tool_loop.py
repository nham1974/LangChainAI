import anthropic

client = anthropic.Anthropic()

# 1. Tool definition
tools = [{
    "name": "get_weather",
    "description": "Get weather for a city",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
    }
}]

# 2. Tool function
def get_weather(city):
    return f"{city}: Sunny, 72°F"

# 3. Start conversation
messages = [{"role": "user", "content": "What's the weather in Austin?"}]

# 4. Agent loop
while True:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=256,
        tools=tools,
        messages=messages
    )

    print(f"stop_reason: {response.stop_reason}")

    if response.stop_reason == "tool_use":
        tool = next(b for b in response.content if b.type == "tool_use")
        result = get_weather(tool.input["city"])

        print(f"  ↳ Called {tool.name}({tool.input['city']}) → {result}")

        # feed result back and loop
        messages += [
            {"role": "assistant", "content": response.content},
            {"role": "user",      "content": [{"type": "tool_result", "tool_use_id": tool.id, "content": result}]}
        ]

    else:  # end_turn
        print(f"\nFinal answer: {response.content[0].text}")
        break
