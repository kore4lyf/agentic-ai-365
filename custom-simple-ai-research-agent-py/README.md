# Simple AI Research Agent (Python)

A single-agent research assistant built in Python with ReAct-style tool calling and keyword-based retrieval.

## How It Works

```
User Question
       │
       ▼
┌──────────────┐
│ Retrieve     │  Keyword matching with word frequency scoring
│ Memory       │  Returns top-2 relevant chunks
└──────┬───────┘
       │ context
       ▼
┌──────────────┐
│ LLM + Tools  │  Think → Act → Observe loop
│              │  Invokes calculator when math is needed
└──────────────┘
```

## Tech Stack

- Python 3.10+
- httpx (HTTP client)
- OpenAI-compatible tool calling API
- OpenAI-compatible API (JAN, Ollama, LM Studio, vLLM, OpenAI, etc.)

## Prerequisites

- An OpenAI-compatible LLM backend running (default: [JAN](https://jan.ai/) at `http://127.0.0.1:1337`)
- Python 3.10+

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python agent.py
```

Type your question and press Enter. Type `exit` to quit.

## Example

```
You: What is 12 * 45?
Agent: Calculator result: 540

You: What is the ReAct loop?
Agent: The ReAct loop is a reasoning framework...
```

## Tool Calling

The agent uses OpenAI-compatible function calling to invoke tools:

| Tool | Description |
|------|-------------|
| `calculate` | Evaluates math expressions (supports sqrt, pi, abs, round, basic operators) |

The calculator uses a restricted `eval()` with only math functions allowed for safe evaluation.

## Test Script

Test JAN API connectivity:

```bash
python test_requests.py
```

## Key Features

- ReAct-style agent loop (Think → Act → Observe)
- Keyword-based retrieval with word frequency scoring
- Calculator tool via function calling
- Safe math evaluation with restricted environment
- Debug logging for request/response inspection
