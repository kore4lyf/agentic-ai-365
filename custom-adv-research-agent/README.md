# Advanced Research Agent

A multi-agent research system that chains 4 specialized AI agents to produce polished research reports from a knowledge base.

## Architecture

```
User Topic
    │
    ▼
┌──────────────┐
│ Research     │  Retrieves relevant chunks via cosine similarity
│ Agent        │  Organizes findings into bullet points
└──────┬───────┘
       │ research notes
       ▼
┌──────────────┐
│ Analysis     │  Identifies patterns, themes, contrasts
│ Agent        │  Produces insights, risks, takeaways
└──────┬───────┘
       │ analysis
       ▼
┌──────────────┐
│ Writer       │  Structures into Title, Intro, Insights,
│ Agent        │  Implications, Conclusion
└──────┬───────┘
       │ draft
       ▼
┌──────────────┐
│ Reviewer     │  Reviews for weak logic, clarity, gaps
│ Agent        │  Produces improved final version
└──────────────┘
```

## Tech Stack

- Python 3.10+
- httpx (HTTP client)
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

Enter a topic when prompted. The system will run through all 4 agents and output a final research report.

## How It Works

1. **Retrieval** — The knowledge base (`knowledge_base.txt`) is split into paragraph chunks. Cosine similarity finds the top-2 most relevant chunks for the topic.
2. **Research** — The Research Agent summarizes findings into organized bullet points.
3. **Analysis** — The Analysis Agent interprets the research, identifying Key Insights, Risks/Limitations, and Strategic Takeaways.
4. **Writing** — The Writer Agent transforms everything into a structured report with title, introduction, main insights, practical implications, and conclusion.
5. **Review** — The Reviewer Agent critically evaluates the draft and produces an improved final version.

## Key Features

- 4-agent sequential pipeline with state passing
- Cosine similarity retrieval (no external embeddings)
- Token-based text matching
- Interactive CLI
- Knowledge base covers Agentic AI concepts
