from setuptools import setup, find_packages

setup(
    name="kryon-ai",  # Unique package name on PyPI
    version="1.2.1",
    author="Syed Farith C",
    author_email="syedfarith1351.com",
    description="Multi-backend Kryon Agent with optional MongoDB and Vector memory support",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/syedfarith/kryon-ai",  # Optional
    packages=find_packages(),
    include_package_data=True,  # ✅ include __init__.py and data files
    install_requires=[
# Core dependencies
    "requests>=2.32.0",
    "numpy>=1.24.0",
    "pydantic>=1.10.2",
    "python-dotenv>=1.0.0",

    # LLM backends
    "openai>=1.0.0",              # OpenAI LLM
    "anthropic>=0.6.0",           # Claude LLM
    "google-generativeai>=0.1.0", # Gemini LLM
    "groq>=0.0.2",                # Groq LLM SDK

    # Database dependencies
    "pymongo>=4.4.0",             # MongoDB support
    "tinydb>=4.7.0",              # Local DB support
    "sqlalchemy>=2.0.0",          # Optional, if you want SQL support
    "faiss-cpu>=1.7.4",           # Vector DB (local embedding search)
    "python-dotenv>=1.0.0"        # for storing DB/API configs
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
