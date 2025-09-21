from setuptools import setup, find_packages

setup(
    name="harsh-ai-assistant",
    version="0.1.2",
    author="Harish Reddy",
    author_email="iharish.reddy17@gmail.com",
    description="A custom AI assistant using LangGraph and LangChain",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/harishreddy17/Custom-AI-Assistant",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "langgraph",
        "langchain",
        "langchain-openai",
        "chromadb",
        "faiss-cpu",
        "tiktoken",
        "colorama",
        "pygit2",
        "pytest",
        "pyyaml"
    ],
    entry_points={
        "console_scripts": [
            "harsh_ai_assistant=harsh_ai_assistant.interface.cli:main"
        ]
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
