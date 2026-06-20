import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any

import httpx


# -----------------------------
# Configuration
# -----------------------------

OLLAMA_URL = "http://127.0.0.1:1337/v1/chat/completions"
MODEL_NAME = "LFM2_5-350M-Q4_K_M"


# -----------------------------
# Utility: Ollama Chat
# -----------------------------

def call_llm(system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }

    with httpx.Client(timeout=120) as client:
        response = client.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


# -----------------------------
# Simple Retrieval
# -----------------------------

def load_chunks(file_path: str) -> List[str]:
    text = Path(file_path).read_text(encoding="utf-8")
    return [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]


def tokenize(text: str) -> List[str]:
    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


def cosine_similarity(a: Counter, b: Counter) -> float:
    common = set(a.keys()) & set(b.keys())
    numerator = sum(a[word] * b[word] for word in common)

    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return numerator / (norm_a * norm_b)


def retrieve_relevant_chunks(query: str, chunks: List[str], top_k: int = 4) -> List[str]:
    query_vec = Counter(tokenize(query))
    scored = []

    for chunk in chunks:
        chunk_vec = Counter(tokenize(chunk))
        score = cosine_similarity(query_vec, chunk_vec)
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k] if score > 0]


# -----------------------------
# Agent Prompts
# -----------------------------

RESEARCH_AGENT_PROMPT = """
You are a Research Agent.

Your job:
- Gather the most relevant information for the given topic.
- Use only the provided knowledge base context.
- Organize findings into concise bullet points.
- Focus on relevance, clarity, and completeness.
- Do not write a final article or report.
- Do not invent facts outside the provided context.
""".strip()


ANALYSIS_AGENT_PROMPT = """
You are an Analysis Agent.

Your job:
- Review the research notes.
- Identify key patterns, themes, contrasts, and implications.
- Produce clear insights, not just summaries.
- Organize your response into:
  1. Key Insights
  2. Risks / Limitations
  3. Strategic Takeaways
- Be clear and practical.
""".strip()


WRITER_AGENT_PROMPT = """
You are a Writer Agent.

Your job:
- Turn the research and analysis into a polished report.
- Write clearly and professionally.
- Use this structure:
  1. Title
  2. Introduction
  3. Main Insights
  4. Practical Implications
  5. Conclusion
- Keep the writing concise but valuable.
""".strip()


REVIEWER_AGENT_PROMPT = """
You are a Reviewer Agent.

Your job:
- Review the draft report critically.
- Look for weak logic, missing clarity, redundancy, or gaps.
- Then provide:
  1. Review Notes
  2. Improved Final Version
- Make the final version better, clearer, and more polished.
""".strip()


# -----------------------------
# Agent Functions
# -----------------------------

def research_agent(topic: str, kb_chunks: List[str]) -> str:
    relevant_chunks = retrieve_relevant_chunks(topic, kb_chunks, top_k=4)
    context = "\n\n".join(f"- {chunk}" for chunk in relevant_chunks) if relevant_chunks else "No relevant context found."

    user_prompt = f"""
Topic:
{topic}

Knowledge base context:
{context}

Create research notes in bullet points.
""".strip()

    return call_llm(RESEARCH_AGENT_PROMPT, user_prompt)


def analysis_agent(topic: str, research_notes: str) -> str:
    user_prompt = f"""
Topic:
{topic}

Research notes:
{research_notes}

Analyze the material and produce insights.
""".strip()

    return call_llm(ANALYSIS_AGENT_PROMPT, user_prompt)


def writer_agent(topic: str, research_notes: str, analysis_output: str) -> str:
    user_prompt = f"""
Topic:
{topic}

Research notes:
{research_notes}

Analysis:
{analysis_output}

Write the report.
""".strip()

    return call_llm(WRITER_AGENT_PROMPT, user_prompt)


def reviewer_agent(topic: str, draft_report: str) -> str:
    user_prompt = f"""
Topic:
{topic}

Draft report:
{draft_report}

Review and improve the draft.
""".strip()

    return call_llm(REVIEWER_AGENT_PROMPT, user_prompt)


# -----------------------------
# Orchestration Logic
# -----------------------------

def run_workflow(topic: str, kb_chunks: List[str]) -> Dict[str, Any]:
    state: Dict[str, Any] = {
        "topic": topic,
        "research_notes": "",
        "analysis_output": "",
        "draft_report": "",
        "final_output": "",
    }

    print("\n[1/4] Running Research Agent...")
    state["research_notes"] = research_agent(topic, kb_chunks)

    print("[2/4] Running Analysis Agent...")
    state["analysis_output"] = analysis_agent(topic, state["research_notes"])

    print("[3/4] Running Writer Agent...")
    state["draft_report"] = writer_agent(
        topic,
        state["research_notes"],
        state["analysis_output"]
    )

    print("[4/4] Running Reviewer Agent...")
    state["final_output"] = reviewer_agent(topic, state["draft_report"])

    return state


# -----------------------------
# Main App
# -----------------------------

def main() -> None:
    kb_chunks = load_chunks(Path(__file__).parent / "knowledge_base.txt")

    print("\nMulti-Agent Workflow System")
    print("Type 'exit' to quit.\n")

    while True:
        topic = input("Enter a topic: ").strip()

        if topic.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        try:
            result = run_workflow(topic, kb_chunks)

            print("\n" + "=" * 80)
            print("RESEARCH NOTES")
            print("=" * 80)
            print(result["research_notes"])

            print("\n" + "=" * 80)
            print("ANALYSIS OUTPUT")
            print("=" * 80)
            print(result["analysis_output"])

            print("\n" + "=" * 80)
            print("DRAFT REPORT")
            print("=" * 80)
            print(result["draft_report"])

            print("\n" + "=" * 80)
            print("FINAL OUTPUT")
            print("=" * 80)
            print(result["final_output"])
            print("\n")

        except Exception as e:
            print(f"\nWorkflow error: {e}\n")


if __name__ == "__main__":
    main()
