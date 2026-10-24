---
name: agent-scaffold
description: Create a new LangGraph agent with tools following project patterns
arguments: [agent_name, tool_description]
---

## Task
Create a new LangGraph agent called **$agent_name** following the established patterns in this project.

## Current Project Structure
!`ls -la *.py 2>/dev/null | grep -v __pycache__`

## Existing Agent Pattern Reference
The project uses three main patterns:

1. **Simple Anthropic Pattern** (from `simple_weather_agent.py`) - **RECOMMENDED FOR BEGINNERS**:
   - Direct Anthropic API usage with simple for loops
   - Clear `stop_reason` logic (tool_use vs end_turn)
   - Beginner-friendly code with detailed comments
   - Best for learning how agents work

2. **LangChain V1 Pattern** (from `updatedlangchain/intro.ipynb`):
   - Uses `langchain.agents.create_agent()`
   - Model binding with `.bind_tools()`
   - Message-based invocation
   - Good for production LangChain apps

3. **Anthropic Advanced Pattern** (from `agent_tool_loop.py`):
   - Direct Anthropic API usage
   - More compact code with comprehensions
   - Manual message handling
   - Good for understanding internals

## Instructions

Create a new agent file named `$agent_name.py` using the **Simple Anthropic Pattern** (best for learning):

### Pattern: Simple Anthropic (Beginner-Friendly)

### 1. Imports and Environment Setup
```python
import os
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

# Get API key and validate
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key or api_key.startswith("ask-ant-usr-"):
    print("\n⚠️  Error: Valid ANTHROPIC_API_KEY not found!")
    print("   Get your API key from: https://console.anthropic.com")
    print("   Then add it to your .env file: ANTHROPIC_API_KEY=sk-ant-xxx...\n")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)
```

### 2. Tool Definitions
Create tool schemas and functions based on: **$tool_description**

```python
# Step 1: Define tool schema (tells Claude what the tool does)
tools = [{
    "name": "tool_name",
    "description": "Description of what this tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param_name": {
                "type": "string",
                "description": "What this parameter is for"
            }
        },
        "required": ["param_name"]
    }
}]

# Step 2: Create the actual tool function
def tool_name(param_name):
    """Implementation of the tool"""
    # Your logic here
    return f"Result for {param_name}"
```

### 3. Agent Loop with stop_reason Logic
This is the core agent loop - use simple for loops (beginner-friendly):

```python
def run_agent(user_question):
    """Run the agent with stop_reason logic"""
    # Start conversation
    messages = [{"role": "user", "content": user_question}]

    print(f"\n🧑 User: {user_question}\n")

    # Loop until we get final answer
    while True:
        # Call Claude
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=256,
            tools=tools,
            messages=messages
        )

        print(f"🤖 Claude's stop_reason: {response.stop_reason}")

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

            # Execute the tool (call your function)
            result = tool_name(tool.input["param_name"])

            print(f"   ↳ Tool returned: {result}\n")

            # Send result back to Claude
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
            final_answer = response.content[0].text
            print(f"✅ Final Answer: {final_answer}\n")
            return final_answer
        else:
            print(f"Unexpected stop_reason: {response.stop_reason}")
            break
```

### 4. Main Execution Block
```python
def main():
    print("="*60)
    print("$agent_name Agent")
    print("="*60)

    # Example usage
    run_agent("example query here")

if __name__ == "__main__":
    main()
```

### 5. Documentation
Add a clear docstring at the top:
```python
"""
$agent_name Agent

This agent uses the Anthropic API to $tool_description.

Key Concepts:
- stop_reason = "tool_use" → Agent wants to use a tool
- stop_reason = "end_turn" → Agent has the final answer

Tools:
- tool_name: description

Usage:
    python $agent_name.py

Environment Variables Required:
- ANTHROPIC_API_KEY (get from https://console.anthropic.com)
"""
```

## Additional Requirements

1. **Simple Code**: Use simple for loops, no complex comprehensions
2. **Clear Comments**: Add comments explaining what each part does
3. **Visual Feedback**: Use emoji and print statements to show execution flow:
   - 🧑 for user input
   - 🤖 for Claude's actions
   - ↳ for tool calls/results
   - ✅ for final answers
4. **Error Messages**: Add helpful error messages for missing API keys
5. **Model**: Use `claude-sonnet-4-5` for tool use capabilities

## After Creation

1. Test the agent with a sample query
2. Show the user how to run it: `python $agent_name.py`
3. Explain the output showing the stop_reason logic in action
4. Consider adding an interactive mode for user experimentation

## Code Style Guide (Beginner-Friendly)

**DO:**
- Use simple for loops: `for block in response.content:`
- Use descriptive variable names: `tool`, `result`, `final_answer`
- Add print statements to show what's happening
- Break complex logic into small steps with comments

**DON'T:**
- Use list comprehensions or `next()` for finding tools
- Use complex one-liners
- Skip error handling for API keys
- Assume the user knows what stop_reason means

## Example Tool Ideas (if not specified)

If $tool_description is not provided, create simple tools for:
- Weather information (get_weather, get_forecast)
- Math operations (calculate, convert_units)
- Text processing (count_words, reverse_text)
- Date/time (get_current_time, days_until)
