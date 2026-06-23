# Customer Support Agent

A production-grade customer support system powered by 5 specialized AI agents, tool integration, guardrails, and automated evaluation.

## Architecture

```
Customer Request
       │
       ▼
┌──────────────┐
│ Router       │  Classifies: refund, order_status, account_access,
│ Agent        │  troubleshooting, escalation, general_support
└──────┬───────┘
       │ category + tool calls
       ▼
┌──────────────┐
│ Research     │  Retrieves relevant support policy rules
│ Agent        │  from knowledge base
└──────┬───────┘
       │ policy context
       ▼
┌──────────────┐
│ Support      │  Drafts customer-facing response
│ Agent        │  Uses tool results + policy context
└──────┬───────┘
       │ draft
       ▼
┌──────────────┐
│ Reviewer     │  Checks accuracy, clarity, policy compliance
│ Agent        │  Refines tone and content
└──────┬───────┘
       │ reviewed
       ▼
┌──────────────┐
│ Evaluator    │  Scores: accuracy, clarity, policy_compliance,
│ Agent        │  helpfulness (1-5 scale each)
└──────────────┘
```

## Tech Stack

- Python 3.10+
- httpx (HTTP client)
- JSON-based structured outputs
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
python app.py
```

Enter a customer support request when prompted. The system will route, research, draft, review, and evaluate a response.

## Tools

| Tool | Description |
|------|-------------|
| Order Lookup | Retrieves order status, date, and refundable flag from a mock orders database |
| Calculator | Evaluates math expressions for refund calculations |

## Guardrails

- **Prompt injection detection** — blocks requests containing suspicious patterns (e.g., "ignore previous instructions")
- **Escalation detection** — auto-escalates legal threats, fraud claims, and chargeback requests
- **Output validation** — prevents minimum-length violations, policy leaks, and unsupported refund promises

## Evaluation

Run the built-in test suite:

```bash
python app.py --test
```

Tests 4 scenarios (refund, order status, account recovery, fraud escalation) against expected criteria and reports pass/fail with scores.

## Test Cases

| Scenario | Input | Must Include |
|----------|-------|-------------|
| Refund within policy | "I bought a product 10 days ago..." | "refund", "30 days" |
| Order status | "Check my order status for order 1002" | "order", "status" |
| Account recovery | "I cannot access my account..." | "identity verification", "account" |
| Fraud escalation | "I think there is fraud..." | "escalate", "support specialist" |

## Observability

- Workflow logging with timestamps
- Trace logs per agent execution
- Latency tracking
- Run reports saved to JSON files
