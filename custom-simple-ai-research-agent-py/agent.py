import json
import math
import re
import httpx
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List



OLLAMA_URL = "http://127.0.0.1:1337/v1/chat/completions"
MODEL_NAME = "LFM2_5-350M-Q4_K_M"


SYSTEM_PROMPT = """
You are an AI Research Assistant.

Your job:
- Help explain AI agent concepts clearly.
- Use the provided memory context when it is relevant.
- Use the calculator tool when math is needed.
- If memory context is provided, prioritize it over guessing.
- Be concise, clear, and practical.
- If you do not know something, say so honestly.

When helpful, structure answers with short sections.
""".strip()


# ── Memory & Retrieval ─────────────────────────────────────────

def load_knowledge_base(path: str = "knowledge_base.txt") -> List[str]:
    """Load and split knowledge base into chunks."""
    text = Path(path).read_text(encoding="utf-8")
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    return chunks


def search_knowledge(query: str, chunks: List[str], top_k: int = 2) -> str:
    """Find the most relevant chunks using keyword matching."""
    query_words = set(re.findall(r'\w+', query.lower()))
    
    scores = []
    for chunk in chunks:
        chunk_words = re.findall(r'\w+', chunk.lower())
        chunk_counter = Counter(chunk_words)
        score = sum(chunk_counter[word] for word in query_words if word in chunk_counter)
        scores.append((score, chunk))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    top_chunks = [chunk for score, chunk in scores[:top_k] if score > 0]
    
    if not top_chunks:
        return ""
    
    return "\n\n".join(top_chunks)

# ── Tools ──────────────────────────────────────────────────────

def calculate(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        # Clean the expression
        cleaned = re.sub(r'[^\d\s\+\-\*\/\(\)\.\%\^sqrt]', '', expression)
        cleaned = cleaned.replace('^', '**')
        
        # Allow safe math functions
        safe_env = {
            "sqrt": math.sqrt,
            "pi": math.pi,
            "abs": abs,
            "round": round,
            "__builtins__": {}
        }
        
        result = eval(cleaned, safe_env)
        return f"Calculator result: {result}"
    
    except Exception as e:
        return f"Calculator error: {str(e)}"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Use this tool to evaluate math expressions like '25 * 4' or 'sqrt(144)'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A math expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# ── API Helpers ────────────────────────────────────────────────

def chat(messages: List[Dict[str, Any]], tools=None) -> Dict[str, Any]:
    """Send messages to JAN and return the full response."""
    payload: Dict[str, Any] = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
    }

    if tools:
        payload["tools"] = tools

    print(f"\n[DEBUG] Sending request to {OLLAMA_URL}")
    print(f"[DEBUG] Tools included: {tools is not None}")
    
    try:
        print("[DEBUG] Making POST request...")
        with httpx.Client(timeout=300) as client:
            response = client.post(OLLAMA_URL, json=payload)
        print(f"[DEBUG] Response status: {response.status_code}")
        response.raise_for_status()
        result = response.json()
        print(f"[DEBUG] Response received successfully")
        return result
    except httpx.TimeoutException:
        print("[DEBUG] ❌ REQUEST TIMED OUT after 300 seconds")
        raise
    except Exception as e:
        print(f"[DEBUG] ❌ ERROR: {e}")
        raise


def get_text(response: Dict[str, Any]) -> str:
    """Extract the assistant's reply text from the API response."""
    try:
        return response["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError):
        return "Error: Could not read response."


# ── Main Agent Loop ────────────────────────────────────────────

def run_tool(tool_name: str, args: Dict[str, Any]) -> str:
    """Execute a tool and return the result."""
    if tool_name == "calculate":
        expression = args.get("expression", "")
        return calculate(expression)
    return "Error: unknown tool."


def agent_turn(user_input: str, kb_chunks: List[str]) -> str:
    """
    One full agent turn:
    1. Retrieve relevant memory
    2. Build prompt with context
    3. Send to JAN
    4. Handle tool calls if needed
    5. Return final answer
    """
    
    # Step 1: Retrieve relevant memory
    memory_context = search_knowledge(user_input, kb_chunks, top_k=2)
    memory_text = f"Relevant memory:\n{memory_context}" if memory_context else "No relevant memory found."
    
    # Step 2: Build the initial prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
{memory_text}

User question:
{user_input}

Answer using the memory when relevant. Use the calculator tool if math is needed.
""".strip()
        }
    ]
    
    # Step 3: Send to JAN (first turn)
    response = chat(messages, tools=TOOLS)
    assistant_message = response["choices"][0]["message"]
    
    # Step 4: Check if JAN wants to call a tool
    tool_calls = assistant_message.get("tool_calls", [])
    
    if tool_calls:
        # JAN decided to use a tool — add its message to history
        messages.append(assistant_message)
        
        # Run each tool call
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"]["arguments"]
            
            # Parse arguments if they're a string
            if isinstance(tool_args, str):
                try:
                    tool_args = json.loads(tool_args)
                except json.JSONDecodeError:
                    tool_args = {"expression": tool_args}
            
            # Run the tool
            tool_result = run_tool(tool_name, tool_args)
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "name": tool_name,
                "content": tool_result
            })
        
        # Step 5: Send back to JAN with tool results
        final_response = chat(messages, tools=TOOLS)
        return get_text(final_response)
    
    # No tool needed — return the answer directly
    return get_text(response)






def main() -> None:
    """Main conversation loop."""
    kb_chunks = load_knowledge_base("knowledge_base.txt")
    
    print("\n🤖 AI Research Assistant is ready.")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye! 👋")
            break
        
        if not user_input:
            continue
        
        try:
            answer = agent_turn(user_input, kb_chunks)
            print(f"\nAgent: {answer}\n")
        except Exception as e:
            print(f"\n❌ Agent error: {e}\n")


if __name__ == "__main__":
    main()