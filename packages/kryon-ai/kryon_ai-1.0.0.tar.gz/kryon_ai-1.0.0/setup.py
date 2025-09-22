from setuptools import setup, find_packages

setup(
    name="kryon-ai",  # Unique package name on PyPI
    version="0.1.0",
    author="Syed Farith C",
    author_email="syedfarith1351.com",
    description="Multi-backend Kryon Agent with optional MongoDB and Vector memory support",
    long_description=open("README.md", encoding="utf-8").read(),

    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kryon-agent",  # Optional
    packages=find_packages(),
    install_requires=[
        "requests",
        "pymongo",      # optional, keep if MongoDB support
        "chromadb",     # optional, if vector memory support
        "openai", 
              "groq"      # optional, for LLM embeddings
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
