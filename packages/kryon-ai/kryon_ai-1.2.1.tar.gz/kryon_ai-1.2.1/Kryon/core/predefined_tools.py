# Kryon/core/predefined_tools.py
from Kryon.core.tool import tool

# Generic Chat Agent
@tool
def chat_agent(task: str, llm):
    """
    Generic chat tool: responds to user input using any provided LLM.
    """
    prompt = f"User asked: {task}"
    return llm.generate(prompt)

# Generic Summarization Tool  
@tool
def llm_summarize(task: str, llm):
    """
    Summarizes the input text using any LLM.
    """
    prompt = f"Summarize this text: {task}"
    return llm.generate(prompt)

# Generic Explanation Tool
@tool
def explain(task: str, llm):
    """
    Explains a concept or task in simple terms using the provided LLM.
    """
    prompt = f"Explain the following in simple words: {task}"
    return llm.generate(prompt)

# Web Search Tool (mock implementation)
@tool
def search_web(query: str):
    """
    Mock web search tool that returns sample search results.
    Replace with actual web search implementation.
    """
    # Mock search results for demonstration
    mock_results = [
        f'What is LLM (Large Language Model)?: https://aws.amazon.com/what-is/large-language-model/',
        f'Large language model: https://en.wikipedia.org/wiki/Large_language_model', 
        f'What Are Large Language Models (LLMs)?: https://www.ibm.com/think/topics/large-language-models',
        f'Large Language Models (LLMs) with Google AI: https://cloud.google.com/ai/llms',
        f'What is an LLM (large language model)?: https://www.cloudflare.com/learning/ai/what-is-large-language-model/'
    ]
    return mock_results
