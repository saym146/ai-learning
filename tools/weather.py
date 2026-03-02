from langchain.tools import tool


@tool
def get_weather(location: str) -> str:
    """Get the weather at a location. It can be a city, State, Province"""
    return f"It's sunny in {location}."
