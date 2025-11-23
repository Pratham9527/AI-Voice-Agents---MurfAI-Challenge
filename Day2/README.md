☕ Murf AI Voice Agents Challenge 2025 - Day 2: The Barista Agent

🌟 Day 2 Goal: State Management and Function Calling

This project advances the voice agent from a simple assistant (Day 1) into a functional Coffee Shop Barista Agent. The core improvement is the agent's ability to maintain a conversation, extract structured data using AI tools, and save the final, validated order to a persistent file.

Key Features Added (Day 2)

Feature

Description

Technical Implementation

Barista Persona

The agent adopts the personality of a friendly coffee shop barista.

Updated system instructions within BaristaAgent class.

Order State (Memory)

The agent tracks the order (drinkType, size, milk, name) across multiple turns.

self.order_state dictionary inside BaristaAgent.

Function Calling

The LLM actively calls a Python function, update_order, to parse and store details every time the user speaks.

@function_tool decorator on the update_order method.

Persistence

Once all required fields are collected, the agent triggers a final save operation.

order.json file output on completion.

Technical Challenge Insight

Getting the LLM to reliably call the tool without errors was the main hurdle. This required carefully balancing strict type hints (like Annotated[str, ...] and Literal[...]) with the need to prevent Pydantic Validation Errors when the LLM passed unexpected or empty values. The solution involved making the tool code more robust against the LLM's unpredictable output, ensuring stable conversational flow.

Order Data Structure

The final order is saved to order.json in the following format:

{
  "drinkType": "string",
  "size": "string",
  "milk": "string",
  "extras": ["string"],
  "name": "string"
}


🛠️ Core Tech Stack (Unchanged from Day 1)

TTS: Murf Falcon (Used for ultra-low latency conversational voice output).

STT: Deepgram (Speech-to-Text).

LLM (Brain): Google Gemini Flash.

Orchestration: LiveKit (for real-time WebSocket communication and agents framework).

Language: Python 3.10+ and Node.js (Frontend).

🚀 Setup & Execution

Backend Changes: The core logic resides in backend/src/agent.py.

Configuration: Ensure your .env file in the backend folder contains all necessary API keys (MURF_API_KEY, GOOGLE_API_KEY, LIVEKIT_URL, etc.).

Run Backend:

cd backend
python src/agent.py dev


Run Frontend:

cd frontend
npm run dev


Test: Connect via http://localhost:3000 and place a full coffee order (e.g., "I'd like a small latte with almond milk for Alex").
