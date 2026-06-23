# Simple AI Research Agent (JavaScript)

A single-agent research assistant built in Node.js with ReAct-style tool calling and cosine similarity retrieval.

## How It Works

```
User Question
       │
       ▼
┌──────────────┐
│ Retrieve     │  Cosine similarity search over knowledge base
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

- Node.js 18+
- axios (HTTP client)
- OpenAI-compatible tool calling API
- OpenAI-compatible API (JAN, Ollama, LM Studio, vLLM, OpenAI, etc.)

## Prerequisites

- An OpenAI-compatible LLM backend running (default: [JAN](https://jan.ai/) at `http://127.0.0.1:1337`)
- Node.js 18+

## Setup

```bash
npm install
```

## Run

```bash
node agent.js
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
| `calculate` | Evaluates math expressions (+, -, *, /, %, **, parentheses) |

When the LLM determines a math operation is needed, it returns a `tool_call`. The agent executes it, sends the result back, and the LLM incorporates it into its final answer.

## Key Features

- ReAct-style agent loop (Think → Act → Observe)
- Cosine similarity retrieval (no external embeddings)
- Calculator tool via function calling
- Handles sequential tool calls
- Debug logging for request/response inspection
