# Agentic AI Intro

A hands-on collection of AI agent projects built during the Agentic AI Bootcamp (School of AI). Each project demonstrates a different approach to building agents that reason, retrieve, and act — from simple single-agent assistants to multi-agent production workflows with guardrails.

All projects use an **OpenAI-compatible API** (chat completions endpoint). The default is [JAN](https://jan.ai/) at `http://127.0.0.1:1337` with the `LFM2_5-350M-Q4_K_M` model, but you can point any project at any OpenAI-compatible backend — Ollama, LM Studio, vLLM, OpenAI, etc. Just update the URL and model name in the config section of each file.

## Projects

| Project | Language | Agents | Tool Calling | Guardrails | Complexity |
|---------|----------|--------|-------------|------------|------------|
| [custom-adv-research-agent](./custom-adv-research-agent) | Python | 4 | No | No | Advanced |
| [custom-customer-support-agent](./custom-customer-support-agent) | Python | 5 | Yes | Yes | Production |
| [custom-simple-ai-research-agent-js](./custom-simple-ai-research-agent-js) | JavaScript | 1 | Yes | No | Simple |
| [custom-simple-ai-research-agent-py](./custom-simple-ai-research-agent-py) | Python | 1 | Yes | No | Simple |

### Advanced Research Agent
A multi-agent pipeline that chains Research → Analysis → Writer → Reviewer agents to produce polished research reports from a knowledge base.

### Customer Support Agent
A production-grade system with 5 agents (Router, Research, Support, Reviewer, Evaluator), tool integration (order lookup, calculator), guardrails (prompt injection detection, escalation handling), and automated evaluation.

### Simple Research Agent (JS)
A Node.js single-agent assistant with ReAct-style tool calling for math and cosine similarity retrieval over a knowledge base.

### Simple Research Agent (Py)
The Python equivalent of the JS agent — same architecture, keyword-based retrieval, and calculator tool via safe `eval()`.

## Prerequisites

1. **An OpenAI-compatible LLM backend** — [JAN](https://jan.ai/), Ollama, LM Studio, vLLM, or OpenAI API (default: JAN at `http://127.0.0.1:1337`)
2. **Python 3.10+** (for Python projects)
3. **Node.js 18+** (for the JS project)

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd agentic-ai-intro

# Run any Python project
cd custom-adv-research-agent
pip install -r requirements.txt
python app.py

# Or the JS project
cd custom-simple-ai-research-agent-js
npm install
node agent.js
```

## Project Structure

```
agentic-ai-intro/
├── custom-adv-research-agent/        # 4-agent research pipeline
│   ├── app.py
│   ├── knowledge_base.txt
│   └── requirements.txt
├── custom-customer-support-agent/    # 5-agent support system
│   ├── app.py
│   ├── knowledge_base.txt
│   ├── requirements.txt
│   └── test_cases.json
├── custom-simple-ai-research-agent-js/  # JS single-agent
│   ├── agent.js
│   ├── knowledge_base.txt
│   └── package.json
└── custom-simple-ai-research-agent-py/  # Python single-agent
    ├── agent.py
    ├── knowledge_base.txt
    └── requirements.txt
```
