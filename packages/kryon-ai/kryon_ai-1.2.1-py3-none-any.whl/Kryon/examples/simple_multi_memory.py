"""
Simple usage example showing how to quickly configure multi-backend memory.

This example shows the most common configuration patterns for the
Kryon multi-backend memory system.
"""

from Kryon.llms.groq_llm import GroqLLM
from Kryon.core.predefined_tools import search_web, llm_summarize
from Kryon.core.agent import Agent
from Kryon.Database import LocalMemory

def quick_start_example():
    """Quick start with local memory only."""
    # Create LLM
    api_key = "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"  # Replace with your API key
    llm = GroqLLM(api_key=api_key, model="openai/gpt-oss-120b")
    
    # Simple local memory configuration
    agent = Agent(
        name="QuickAgent", 
        llm=llm,
        tools=[search_web, llm_summarize],
        tasks=["Search for Python best practices", "Summarize findings"],
        memory_backends={}  # This automatically creates a local memory backend
    )
    # Note: When memory_backends is provided (even empty), it enables multi-memory mode
    
    print("Running quick start example...")
    results = agent.run()
    return agent

def advanced_config_example():
    """Advanced configuration with multiple backends."""
    api_key = "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"  # Replace with your API key
    llm = GroqLLM(api_key=api_key, model="openai/gpt-oss-120b")
    
    # Configure multiple memory backends
    memory_backends = {
        # Local JSON storage
        "local": LocalMemory(
            file_path="agent_memory.json",
            max_entries=1000
        ),
        
        # MongoDB storage (uncomment if MongoDB available)
        # "mongo": MongoMemory(
        #     uri="mongodb://localhost:27017",
        #     database="my_agents",
        #     collection="agent_memory"
        # ),
        
        # Vector database storage (uncomment if dependencies available)
        # "vector": VectorMemory(
        #     provider="chroma",
        #     persist_directory="./vector_db",
        #     openai_api_key="your-api-key-here"
        # )
    }
    
    agent = Agent(
        name="AdvancedAgent",
        llm=llm,
        tools=[search_web, llm_summarize],
        tasks=["Research AI safety", "Summarize key points"],
        memory_backends=memory_backends
    )
    
    print("Running advanced configuration...")
    results = agent.run()
    
    # Show analytics
    analytics = agent.get_memory_analytics()
    print("\\nMemory Analytics:")
    for backend, stats in analytics.items():
        print(f"{backend}: {stats.get('total_entries', 0)} entries")
    
    return agent

if __name__ == "__main__":
    print("Kryon Multi-Backend Memory Examples")
    print("===================================")
    
    # Run quick start
    quick_agent = quick_start_example()
    
    print("\\n" + "="*40 + "\\n")
    
    # Run advanced config
    advanced_agent = advanced_config_example()
    
    print("\\nExamples completed successfully!")