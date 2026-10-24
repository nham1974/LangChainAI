"""
test_weather Agent

This agent uses the Anthropic API to get weather info for a city.
Weather data comes from Open-Meteo (https://open-meteo.com), which is free
and needs no API key.

Key Concepts:
- stop_reason = "tool_use" → Agent wants to use a tool
- stop_reason = "end_turn" → Agent has the final answer

Tools:
- get_weather: current weather conditions for a city
- get_forecast: a multi-day forecast for a city

Usage:
    python test_weather.py

Environment Variables Required:
- ANTHROPIC_API_KEY (get from https://console.anthropic.com)
"""

import os
from dotenv import load_dotenv
import anthropic
import requests

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
# STEP 1: Define the tools (tells Claude what each tool does)
# ============================================================================
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather conditions for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name, e.g. 'Austin'"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_forecast",
        "description": "Get a multi-day weather forecast for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name, e.g. 'Austin'"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to forecast (1-7)"
                }
            },
            "required": ["city"]
        }
    }
]

# ============================================================================
# STEP 2: Create the tool functions (what happens when a tool is called)
# ============================================================================
# We use Open-Meteo (https://open-meteo.com) - it's free and needs no API key.
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Open-Meteo returns a number (WMO weather code) instead of words,
# so this table turns the number into something readable
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Freezing fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Light freezing drizzle",
    57: "Freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Rain showers",
    82: "Heavy rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with light hail",
    99: "Thunderstorm with heavy hail",
}


def describe_weather_code(code):
    """Turn a WMO weather code into words"""
    return WEATHER_CODES.get(code, f"Unknown conditions (code {code})")


def find_city(city):
    """
    Look up a city's latitude and longitude.
    Returns a dict with the location, or None if the city wasn't found.
    """
    response = requests.get(GEOCODING_URL, params={"name": city, "count": 1}, timeout=10)
    response.raise_for_status()
    data = response.json()

    # No "results" key means the city wasn't found
    if "results" not in data:
        return None

    place = data["results"][0]

    # Build a nice display name like "Austin, Texas, United States"
    name_parts = [place["name"]]
    if place.get("admin1"):
        name_parts.append(place["admin1"])
    if place.get("country"):
        name_parts.append(place["country"])

    return {
        "name": ", ".join(name_parts),
        "latitude": place["latitude"],
        "longitude": place["longitude"],
    }


def get_weather(city):
    """Returns current weather for a city"""
    try:
        # Step A: turn the city name into coordinates
        location = find_city(city)
        if location is None:
            return f"Error: could not find a city called '{city}'"

        # Step B: ask for the current weather at those coordinates
        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": "auto",
        }
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        current = response.json()["current"]

    except requests.RequestException as error:
        # Return the error as text so Claude can explain it to the user
        return f"Error: weather service request failed ({error})"

    # Step C: format the result as plain text for Claude
    condition = describe_weather_code(current["weather_code"])
    return (
        f"{location['name']}: {condition}, {current['temperature_2m']}°F, "
        f"humidity {current['relative_humidity_2m']}%, "
        f"wind {current['wind_speed_10m']} mph"
    )


def get_forecast(city, days=3):
    """Returns a multi-day forecast for a city"""
    # Keep days between 1 and 7
    if days < 1:
        days = 1
    if days > 7:
        days = 7

    try:
        # Step A: turn the city name into coordinates
        location = find_city(city)
        if location is None:
            return f"Error: could not find a city called '{city}'"

        # Step B: ask for the daily forecast at those coordinates
        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "temperature_unit": "fahrenheit",
            "timezone": "auto",
            "forecast_days": days,
        }
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        daily = response.json()["daily"]

    except requests.RequestException as error:
        # Return the error as text so Claude can explain it to the user
        return f"Error: weather service request failed ({error})"

    # Step C: build the forecast one day at a time
    lines = []
    for i in range(len(daily["time"])):
        date = daily["time"][i]
        condition = describe_weather_code(daily["weather_code"][i])
        high = daily["temperature_2m_max"][i]
        low = daily["temperature_2m_min"][i]
        rain_chance = daily["precipitation_probability_max"][i]
        lines.append(f"{date}: {condition}, high {high}°F, low {low}°F, {rain_chance}% chance of rain")

    return f"{days}-day forecast for {location['name']}:\n" + "\n".join(lines)


def run_tool(name, tool_input):
    """Look up the tool Claude asked for and run it"""
    if name == "get_weather":
        return get_weather(tool_input["city"])
    elif name == "get_forecast":
        days = tool_input.get("days", 3)
        return get_forecast(tool_input["city"], days)
    else:
        return f"Error: unknown tool '{name}'"

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
            # Real forecasts are longer than fake ones, so give Claude room to answer
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        print(f"🤖 Claude's stop_reason: {response.stop_reason}")

        # Check what Claude wants to do
        if response.stop_reason == "tool_use":
            # Claude wants to use one or more tools!

            # Claude may ask for several tools at once (e.g. weather AND forecast),
            # so run every tool_use block and collect all the results
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"   ↳ Claude wants to call: {block.name}({block.input})")

                    # Execute the tool
                    result = run_tool(block.name, block.input)

                    print(f"   ↳ Tool returned: {result}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Send the results back to Claude
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            # Claude has the final answer!

            # Find the text block (simple for loop - beginner friendly)
            final_answer = ""
            for block in response.content:
                if block.type == "text":
                    final_answer = block.text
                    break

            print(f"✅ Final Answer: {final_answer}\n")
            return final_answer

        else:
            print(f"Unexpected stop_reason: {response.stop_reason}")
            break

# ============================================================================
# STEP 4: Run the agent
# ============================================================================
def main():
    print("=" * 60)
    print("test_weather Agent")
    print("=" * 60)

    # Example 1: Current weather (one tool call)
    run_agent("What's the weather in Austin?")

    print("\n" + "=" * 60 + "\n")

    # Example 2: Forecast (Claude picks the other tool)
    run_agent("Give me a 3-day forecast for Seattle.")

    print("\n" + "=" * 60 + "\n")

    # Interactive mode: try your own questions
    print("💬 Interactive mode - type a question, or 'quit' to exit")
    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ("quit", "exit", "q") or question == "":
            print("👋 Bye!")
            break
        run_agent(question)


if __name__ == "__main__":
    main()
