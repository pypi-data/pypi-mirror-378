"""
Basic Agent Example - Kryon AI Agent Framework

This example shows the simplest way to use Kryon agents without memory backends.
Perfect for getting started quickly.
"""

from Kryon.core.agent import Agent
from Kryon.llms.groq_llm import GroqLLM
from Kryon.core.predefined_tools import explain, llm_summarize

def main():
    """Simple agent example without memory backends."""
    # Replace with your actual API key
    API_KEY = "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"
    
    # Create LLM
    llm = GroqLLM(api_key=API_KEY, model="openai/gpt-oss-120b")
    
    # Create simple agent (legacy mode - no memory backends)
    agent = Agent(
        name="SimpleAgent",
        llm=llm,
        tools=[explain, llm_summarize],
        tasks=[
            "Explain machine learning in simple terms",
            "Summarize the explanation"
        ]
    )
    
    # Execute tasks
    results = agent.run()
    
    print(f"Agent completed {len(results)} tasks successfully")
    return results

if __name__ == "__main__":
    main()