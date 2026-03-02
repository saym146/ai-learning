# AI Learning Repository Overview

This repository is designed to help you learn AI concepts from the basics, progressing from non-agentic approaches to agentic solutions. The codebase is organized to reflect this learning path, making it easy to follow and extend.

## Structure & Intent

- **Non-Agentic Approach:** Start with simple, direct AI interactions.
- **Agentic Approach:** Progress to agent-based solutions that can use tools and solve more complex problems.
- **Tools:** Shared utilities and integrations for use by agents.
- **Tests:** Unit tests for all major components.

## Repository Diagram

```
ai-learning/
│
├── langchain/
│   ├── non-agentic/
│   │   ├── chat_loop_with_tools.py
│   │   └── chat_loop_with_tools.md
│   └── agentic/
│       └── chat_loop_with_tools_agent.py
│
├── tools/
│   ├── __init__.py
│   └── weather.py
│
├── tests/
│   └── test_langchain_first_handson.py
│
└── readme.md
```

## File & Folder Index

### langchain/non-agentic/
- [chat_loop_with_tools.py](langchain/non-agentic/chat_loop_with_tools.py)  
	Implements a basic chat loop using AI models, without agentic features. Demonstrates how to interact with models and use tools directly.
- [chat_loop_with_tools.md](langchain/non-agentic/chat_loop_with_tools.md)  
	Documentation and notes for the non-agentic chat loop.

### langchain/agentic/
- [chat_loop_with_tools_agent.py](langchain/agentic/chat_loop_with_tools_agent.py)  
	Shows how to build an agent that can use tools to solve problems, demonstrating agentic capabilities.

### tools/
- [__init__.py](tools/__init__.py)  
	Initializes the tools module.
- [weather.py](tools/weather.py)  
	Example tool for fetching weather information, usable by both non-agentic and agentic approaches.

### tests/
- [test_langchain_first_handson.py](tests/test_langchain_first_handson.py)  
	Contains unit tests for the initial LangChain hands-on exercises and code.

### [readme.md](readme.md)
- This file (you are reading it!) provides an overview, structure, and guidance for the repository.

---

## Summary

This repository is a step-by-step guide for learning AI, starting from basic model interactions and advancing to agentic problem-solving. The code is modular, with clear separation between approaches, shared tools, and comprehensive tests.

---

If you need a diagram in image format, you can use the above ASCII diagram or generate a flowchart using tools like draw.io or mermaid.
