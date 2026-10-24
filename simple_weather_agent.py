"""
Simple Anthropic Weather Agent - Beginner Level

This is a basic example showing how to build an AI agent that can use tools.
The agent has ONE tool: get_weather

Key Concepts:
- stop_reason = "tool_use" → Agent wants to use a tool
- stop_reason = "end_turn" → Agent has the final answer

Usage:
    python simple_weather_agent.py

Note: This example uses Anthropic's Claude API. If you don't have an Anthropic API key,
      you can get one from https://console.anthropic.com
"""

import os
from dotenv import load_dotenv
import anthropic

# Load API key from .env file
load_dotenv()

# Try to get Anthropic API key, provide helpful message if missing
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key or api_key.startswith("ask-ant-usr-"):
    print("\n⚠️  Error: Valid ANTHROPIC_API_KEY not found!")
    print("   Get your API key from: https://console.anthropic.com")
    print("   Then add it to your .env file: ANTHROPIC_API_KEY=sk-ant-xxx...\n")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)

# ============================================================================
# STEP 1: Define the tool (what the agent can do)
# ============================================================================
tools = [{
    "name": "get_weather",
    "description": "Get weather for a city",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string"}
        },
        "required": ["city"]
    }
}]

# ============================================================================
# STEP 2: Create the tool function (what happens when tool is called)
# ============================================================================
def get_weather(city):
    """Returns weather for a city"""
    # In real life, you'd call an actual weather API
    # For learning, we'll use fake data
    return f"{city}: Sunny, 72°F"

# ============================================================================
# STEP 3: The Agent Loop
# ============================================================================
def run_agent(user_question):
    """
    This is the main agent loop. It keeps running until we get a final answer.
    """
    # Start with the user's question
    messages = [{"role": "user", "content": user_question}]

    print(f"\n🧑 User: {user_question}\n")

    # Loop until we get the final answer
    while True:
        # Ask Claude
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=256,
            tools=tools,
            messages=messages
        )

        print(f"🤖 Claude's stop_reason: {response.stop_reason}")
        print(f"🤖 Claude's content: {response.content}")
        # Check what Claude wants to do
        if response.stop_reason == "tool_use":
            # Claude wants to use a tool!

            # Find the tool call (simple for loop - beginner friendly)
            tool = None
            for block in response.content:
                if block.type == "tool_use":
                    tool = block
                    break

            print(f"   ↳ Claude wants to call: {tool.name}({tool.input})")

            # Execute the tool
            result = get_weather(tool.input["city"])

            print(f"   ↳ Tool returned: {result}\n")

            # Send the result back to Claude
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool.id,
                    "content": result
                }]
            })

        elif response.stop_reason == "end_turn":
            # Claude has the final answer!

            print(f"🤖 Claude's content: {response.content}")
            final_answer = response.content[0].text
            print(f"✅ Final Answer: {final_answer}\n")

            return final_answer

        else:
            print(f"Unexpected stop_reason: {response.stop_reason}")
            break

# ============================================================================
# STEP 4: Run the agent
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("Simple Weather Agent - Learning Example")
    print("="*60)

    # Example 1: Simple question
    run_agent("What's the weather in Austin?")

    print("\n" + "="*60 + "\n")

    
