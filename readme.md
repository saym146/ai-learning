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
│       ├── chat_loop_with_tools_agent.py
│       └── chat_loop_with_tools_agent.md
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
- [chat_loop_with_tools_agent.md](langchain/agentic/chat_loop_with_tools_agent.md)  
	Documentation and notes for the agentic chat loop.

### tools/
- [__init__.py](tools/__init__.py)  
	Initializes the tools module.
- [weather.py](tools/weather.py)  
	Example tool for fetching weather information, usable by both non-agentic and agentic approaches.

### tests/
- [test_langchain_first_handson.py](tests/test_langchain_first_handson.py)  
	Contains unit tests for the initial LangChain hands-on exercises and code.

---

## Local Setup

### Prerequisites
- Python 3.10+

### 1. Clone the repository
```bash
git clone https://github.com/saym146/ai-learning.git
cd ai-learning
```

### 2. Create a virtual environment
```bash
python -m venv ai_env
```

### 3. Activate the virtual environment

**Windows (PowerShell):**
```powershell
.\ai_env\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
ai_env\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source ai_env/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```
> This installs `langchain`, `langchain-google-genai` (default provider), and `pytest`.

### 5. (Optional) Use a different LLM provider
The default setup uses Google Gemini. To switch to a different provider, install the corresponding package and update the model name in the code:

```bash
# OpenAI
pip install langchain-openai

# Anthropic
pip install langchain-anthropic
```

### 6. Set your API key
```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your_api_key_here"

# Linux / macOS
export GOOGLE_API_KEY="your_api_key_here"
```

### 7. Run the chat loop
```bash
python langchain/non-agentic/chat_loop_with_tools.py
```

### 8. Run tests
```bash
pytest tests/
```
