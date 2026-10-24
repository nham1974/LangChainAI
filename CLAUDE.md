# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LangChainAI is a learning/exploration project for LangChain and LangGraph frameworks. The repository contains experimental code and Jupyter notebooks demonstrating various LangChain patterns.

## Development Setup

### Environment Setup
```bash
# Python 3.13+ required
uv venv
source .venv/bin/activate  # macOS/Linux
uv pip install -e .
```

### Environment Variables
Create a `.env` file with:
```
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here  # if using Google GenAI
```

Load environment variables in code:
```python
from dotenv import load_dotenv
import os
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
```

## Running Code

### Python Scripts
```bash
# Run the basic hello world
python main.py

# Run the Anthropic agent loop example
python agent_tool_loop.py
```

### Jupyter Notebooks
The `updatedlangchain/` directory contains learning notebooks:
- `intro.ipynb` - LangChain basics, agent creation with `create_agent()`
- `tools.ipynb` - Tool integration patterns with `@tool` decorator
- `messages.ipynb` - Message handling
- `middleware.ipynb` - Middleware patterns
- `modelintegration.ipynb` - Multi-provider model integration
- `StreamingandBatch.ipynb` - Streaming and batch processing
- `structuredoutput.ipynb` - Structured output handling

Start Jupyter:
```bash
jupyter lab
# or
jupyter notebook
```

## Architecture Patterns

### LangChain V1 Agent Pattern
The project uses LangChain V1 patterns with `langchain.agents.create_agent()`:
```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-5",
    tools=[your_tools],
    system_prompt="your system prompt"
)

response = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
```

### Tool Definition Pattern
Two approaches are demonstrated:

1. **Decorator-based** (preferred in notebooks):
```python
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get weather at a location"""
    return f"its sunny in {location}"
```

2. **Schema-based** (Anthropic API):
```python
tools = [{
    "name": "get_weather",
    "description": "Get weather for a city",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
    }
}]
```

### Tool Execution Loop
Standard 3-step pattern used throughout:
1. Model generates tool calls
2. Execute tools and collect results
3. Pass results back to model for final response

See `agent_tool_loop.py` for Anthropic implementation or `updatedlangchain/tools.ipynb` for LangChain implementation.

### Multi-Provider Model Integration
The project integrates multiple LLM providers:
- OpenAI via `langchain-openai`
- Groq via `langchain-groq` or `langchain.chat_models.init_chat_model("groq:qwen/qwen3-32b")`
- Google GenAI via `langchain-google-genai`
- Anthropic directly via `anthropic.Anthropic()` (in agent_tool_loop.py)

## Key Implementation Details

### Model Binding
Models are bound to tools using:
```python
model_with_tools = model.bind_tools([tool1, tool2])
```

### Message Format
LangChain uses a message list format:
```python
messages = [
    {"role": "user", "content": "..."},
    AIMessage(...),
    ToolMessage(...)
]
```

### Response Structure
Agent responses contain:
```python
response = agent.invoke(...)
response["messages"]  # Full message history
response["messages"][-1].content  # Final answer
```

## Dependencies

Core frameworks:
- `langchain>=1.3.4` - Main framework
- `langgraph>=1.2.4` - Graph-based agent orchestration
- `langchain-community>=0.4.2` - Community integrations

LLM providers:
- `langchain-openai>=1.2.2`
- `langchain-groq>=1.1.2`
- `langchain-google-genai>=4.2.4`
- `anthropic` - Direct API usage in agent_tool_loop.py

Utilities:
- `python-dotenv>=1.2.2` - Environment variable management
- `ipykernel>=7.2.0` - Jupyter notebook support
