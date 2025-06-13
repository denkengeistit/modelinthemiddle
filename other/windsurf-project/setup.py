from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="model-in-the-middle",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A lightweight framework for LLM-MCP server integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/model-in-the-middle",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "pydantic>=1.8.0",
        "uvicorn>=0.15.0",
        "python-dotenv>=0.19.0",
        "httpx>=0.23.0",
        "loguru>=0.5.3",
        "typer>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "mitm=model_in_the_middle.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
