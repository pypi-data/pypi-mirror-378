"""
Hello Agent Example - Kryon AI Agent Framework

This example demonstrates how to create an AI agent with memory backends
that can search the web, summarize information, and explain concepts.
"""

from Kryon.core.agent import Agent
from Kryon.llms.groq_llm import GroqLLM
from Kryon.core.predefined_tools import chat_agent, llm_summarize, explain
from Kryon.core.tool import tool
import requests
from Kryon.Database import LocalMemory
import requests

# Configuration
SERP_API_KEY = "your-serpapi-key-here"  # Replace with your actual API key
GROQ_API_KEY = "your-groq-api-key-here"  # Replace with your actual API key

# Custom tool for web search
@tool
def search_web(query: str):
    """Search the web using SerpAPI."""
    url = f"https://serpapi.com/search.json?q={query}&api_key={SERP_API_KEY}"
    try:
        response = requests.get(url).json()
        results = [f"{r['title']}: {r['link']}" for r in response.get("organic_results", [])[:5]]
        return results
    except Exception:
        return ["Search service temporarily unavailable"]

# LLM setup
llm = GroqLLM(api_key=GROQ_API_KEY, model="openai/gpt-oss-120b")

# Memory configuration
memory_backends = {
    "local": LocalMemory(file_path="agent_memory.json", max_entries=1000)
}

# Tasks to execute
tasks = [
    "Search about LLM models",
    "Summarize findings"
]

# Agent setup
agent = Agent(
    name="Researcher",
    llm=llm,
    tools=[chat_agent, llm_summarize, explain, search_web],
    tasks=tasks,
    memory_backends=memory_backends
)

if __name__ == "__main__":
    # Execute all tasks
    results = agent.run()
    
    # Display memory analytics
    analytics = agent.get_memory_analytics()
    print(f"\nMemory Analytics: {analytics['local']['total_entries']} entries stored")