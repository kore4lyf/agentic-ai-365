const axios = require('axios');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// ── Configuration ────────────────────────────────────────────────────────

const JAN_URL = "http://127.0.0.1:1337/v1/chat/completions";
const MODEL_NAME = "LFM2_5-350M-Q4_K_M";

const SYSTEM_PROMPT = `
You are an AI Research Assistant.

Your job:
- Help explain AI agent concepts clearly.
- Use the provided memory context when it is relevant.
- Use the calculator tool when math is needed.
- If memory context is provided, prioritize it over guessing.
- Be concise, clear, and practical.
- If you do not know something, say so honestly.

When helpful, structure answers with short sections.
`.trim();

// ── Memory & Retrieval ───────────────────────────────────────────────────

function loadKnowledgeBase(filePath = "knowledge_base.txt") {
  const text = fs.readFileSync(filePath, 'utf-8');
  const chunks = text
    .split('\n\n')
    .map(c => c.trim())
    .filter(c => c.length > 0);
  return chunks;
}

function tokenize(text) {
  return text.toLowerCase().match(/\b[a-z0-9]+\b/g) || [];
}

function cosineSimilarity(a, b) {
  const aTokens = new Map();
  const bTokens = new Map();

  a.forEach(token => {
    aTokens.set(token, (aTokens.get(token) || 0) + 1);
  });

  b.forEach(token => {
    bTokens.set(token, (bTokens.get(token) || 0) + 1);
  });

  const common = new Set([...aTokens.keys()].filter(k => bTokens.has(k)));
  
  let numerator = 0;
  common.forEach(word => {
    numerator += aTokens.get(word) * bTokens.get(word);
  });

  const normA = Math.sqrt([...aTokens.values()].reduce((sum, v) => sum + v * v, 0));
  const normB = Math.sqrt([...bTokens.values()].reduce((sum, v) => sum + v * v, 0));

  if (normA === 0 || normB === 0) return 0;

  return numerator / (normA * normB);
}

function searchKnowledge(query, chunks, topK = 2) {
  const queryTokens = tokenize(query);
  const scored = chunks.map(chunk => {
    const chunkTokens = tokenize(chunk);
    const score = cosineSimilarity(queryTokens, chunkTokens);
    return { score, chunk };
  });

  scored.sort((a, b) => b.score - a.score);
  
  const results = scored
    .slice(0, topK)
    .filter(item => item.score > 0)
    .map(item => item.chunk);

  return results.length > 0 ? results.join('\n\n') : '';
}

// ── Tools ────────────────────────────────────────────────────────────────

const TOOLS = [
  {
    type: "function",
    function: {
      name: "calculate",
      description: "Evaluate a math expression. Supports +, -, *, /, %, **, parentheses.",
      parameters: {
        type: "object",
        properties: {
          expression: {
            type: "string",
            description: "The math expression to evaluate, e.g. '(3 + 5) * 2'"
          }
        },
        required: ["expression"]
      }
    }
  }
];

const TOOL_MAP = {
  calculate
};

function calculate(expression) {
  try {
    const cleaned = expression.replace(/[^\d\s+\-*/(). %^sqrt]/g, '').replace(/\^/g, '**');
    const result = Function('"use strict"; return (' + cleaned + ')')();
    return `Calculator result: ${result}`;
  } catch (e) {
    return `Calculator error: ${e.message}`;
  }
}

// ── API Helpers ──────────────────────────────────────────────────────────

async function chat(messages, tools = null) {
  const payload = {
    model: MODEL_NAME,
    messages: messages,
    stream: false,
  };

  if (tools) {
    payload.tools = tools;
  }

  console.log(`\n[DEBUG] Sending request to ${JAN_URL}`);
  console.log(`[DEBUG] Tools included: ${tools !== null}`);

  try {
    console.log('[DEBUG] Making POST request...');
    const response = await axios.post(JAN_URL, payload, { timeout: 300000 });
    console.log(`[DEBUG] Response status: ${response.status}`);
    console.log('[DEBUG] Response received successfully');
    return response.data;
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      console.log('[DEBUG] ❌ REQUEST TIMED OUT after 300 seconds');
    } else {
      console.log(`[DEBUG] ❌ ERROR: ${error.message}`);
    }
    throw error;
  }
}

function getText(response) {
  try {
    return response.choices[0].message.content || '';
  } catch (e) {
    return 'Error: Could not read response.';
  }
}

// ── Main Agent Loop ──────────────────────────────────────────────────────

async function agentTurn(userInput, kbChunks) {
  // Step 1: Retrieve relevant memory
  const memoryContext = searchKnowledge(userInput, kbChunks, 2);
  const memoryText = memoryContext 
    ? `Relevant memory:\n${memoryContext}` 
    : 'No relevant memory found.';

  // Step 2: Build the prompt
  const messages = [
    { role: 'system', content: SYSTEM_PROMPT },
    {
      role: 'user',
      content: `
${memoryText}

User question:
${userInput}

Answer using the memory when relevant. If the user asks for math, calculate it and include the result in your answer.
`.trim()
    }
  ];

  // Step 3: Send to JAN with tools
  let response = await chat(messages, TOOLS);
  let message = response.choices[0].message;

  // Step 4: Handle tool calls
  while (message.tool_calls && message.tool_calls.length > 0) {
    messages.push(message);

    for (const toolCall of message.tool_calls) {
      const fnName = toolCall.function.name;
      const fnArgs = JSON.parse(toolCall.function.arguments);
      console.log(`[TOOL] Calling ${fnName}(${JSON.stringify(fnArgs)})`);

      const fn = TOOL_MAP[fnName];
      const result = fn ? fn(fnArgs.expression) : `Unknown tool: ${fnName}`;
      console.log(`[TOOL] Result: ${result}`);

      messages.push({
        role: "tool",
        tool_call_id: toolCall.id,
        content: result
      });
    }

    response = await chat(messages, TOOLS);
    message = response.choices[0].message;
  }

  // Step 5: Return the answer
  return getText(response);
}

async function main() {
  const kbChunks = loadKnowledgeBase('knowledge_base.txt');

  console.log('\n🤖 AI Research Assistant is ready.');
  console.log("Type 'exit' to quit.\n");

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const askQuestion = () => {
    rl.question('You: ', async (userInput) => {
      if (userInput.toLowerCase() === 'exit' || userInput.toLowerCase() === 'quit') {
        console.log('Goodbye! 👋');
        rl.close();
        return;
      }

      if (!userInput.trim()) {
        askQuestion();
        return;
      }

      try {
        const answer = await agentTurn(userInput, kbChunks);
        console.log(`\nAgent: ${answer}\n`);
      } catch (error) {
        console.log(`\n❌ Agent error: ${error.message}\n`);
      }

      askQuestion();
    });
  };

  askQuestion();
}

// ── Run ──────────────────────────────────────────────────────────────────

main().catch(console.error);