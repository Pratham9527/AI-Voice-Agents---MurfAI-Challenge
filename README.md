# 🎙️ 10 Days of AI Voice Agents Challenge (Murf AI)

This repository tracks my progress through the **Murf AI Voice Agents Challenge 2025**. The goal is to build fully functional, low-latency, conversational AI agents using modern tools and the Murf Falcon TTS API over 10 days.

## ⚡ Core Technology Stack

The entire project is built on a real-time, low-latency stack:

- **TTS (Voice)**: Murf Falcon
- **STT (Ears)**: Deepgram Nova-3
- **LLM (Brain)**: Google Gemini 2.5 Flash
- **Orchestration**: LiveKit Agents (Python)

## 🎯 Progress

| Day | Goal | Status | Key Achievement |
|-----|------|--------|-----------------|
| **Day 1** | Get the starter agent running end-to-end | ✅ COMPLETE | Established the foundational voice pipeline (STT → LLM → TTS) |
| **Day 2** | Create a functional Coffee Shop Barista Agent | ✅ COMPLETE | Implemented Function Calling and State Management to track and validate structured orders (Drink, Size, Milk, Name) |
| **Day 3** | Build a Health & Wellness Voice Companion | ✅ COMPLETE | Implemented daily check-ins with JSON persistence, weekly reflection analytics, and Todoist MCP integration for task creation |
| **Day 4** | Create a Teach-the-Tutor Active Recall Coach | ✅ COMPLETE | Built multi-agent system with Learn/Quiz/Teach-Back modes, distinct Murf voices (Matthew/Alicia/Ken), LLM-based scoring (0-100), and progress tracking |
| **Day 5** | Create a Razorpay SDR Voice Agent | ✅ COMPLETE | Built a professional SDR agent with FAQ pre-warming, keyword-based search, and natural lead capture with master database storage |
| **Day 6** | Build a Fraud Alert Voice Agent for Banking | ✅ COMPLETE | Integrated SQLite database for fraud case management with secure verification via security questions and real-time status updates |
| **Day 7** | Build a Food & Grocery Ordering Voice Agent | ✅ COMPLETE | Created comprehensive shopping assistant with 30+ item catalog, intelligent recipe-based ordering, cart management, and JSON order persistence |
| **Day 8** | Build a D&D-Style Voice Game Master | ✅ COMPLETE | Interactive storytelling agent with bilingual support (English/Hindi), option-based gameplay, dice mechanics, and story continuity tracking |
| **Day 9** | Build an E-commerce Voice Shopping Assistant | ✅ COMPLETE | ACP-inspired architecture with 9 products across 3 categories, smart filtering, multi-item cart management, and order persistence to JSON |

## 📂 Repository Structure

```
AI-Voice-Agents---MurfAI-Challenge/
├── Day1/           # Basic voice agent setup
├── Day2/           # Coffee Shop Barista (function calling)
├── Day3/           # Wellness Companion (persistence + MCP)
├── Day4/           # Active Recall Coach (multi-agent + scoring)
├── Day5/           # Razorpay SDR Agent (FAQ + Lead Capture)
├── Day6/           # Fraud Alert Agent (Database Integration)
├── Day7/           # Food & Grocery Ordering (E-commerce Cart)
├── Day8/           # D&D Game Master (Interactive Storytelling + Bilingual)
├── Day9/           # E-commerce Shopping (ACP Pattern + Multi-Category Catalog)
└── README.md       # This file
```

## 🚀 Quick Start

Each day has its own folder with backend and frontend code. To run any day's project:

### Backend
```bash
cd Day[X]/backend
uv sync
python src/agent.py dev
```

### Frontend
```bash
cd Day[X]/frontend
npm install
npm run dev
```

Then open `http://localhost:3000` in your browser.

## 📖 Day-by-Day Details

### Day 1: Foundation
- Set up LiveKit Agents framework
- Integrated Murf Falcon TTS
- Connected Deepgram STT
- Configured Gemini 2.5 Flash LLM
- **Result**: Working voice conversation loop

### Day 2: Coffee Shop Barista
- Implemented function calling with LiveKit
- Created state management for orders
- Added validation logic (size, milk type, drink)
- Built structured data collection flow
- **Result**: Agent that takes complete coffee orders

### Day 3: Wellness Companion
- Daily check-in with mood, energy, sleep tracking
- JSON file persistence for historical data
- Weekly reflection with analytics
- MCP (Model Context Protocol) integration
- Todoist API for creating tasks from user goals
- **Result**: Personal wellness coach with memory

### Day 4: Active Recall Coach
- Multi-agent architecture (4 specialized agents)
- Agent handoffs with context preservation
- Distinct Murf voices per mode:
  - **Matthew** (Learn mode) - Patient teaching
  - **Alicia** (Quiz mode) - Encouraging testing
  - **Ken** (Teach-Back mode) - Thoughtful evaluation
- LLM-based scoring system (0-100 with feedback)
- Content-driven learning from JSON
- Progress tracking with concept mastery
- **Result**: Intelligent tutor that evaluates understanding

### Day 5: Razorpay SDR Voice Agent
- **Pre-warming pattern** for instant FAQ availability
- **Keyword-based search** for fast, reliable answers
- **Natural lead capture** of 7 key fields (name, role, use case, etc.)
- **Master database** storage for all leads
- **Verbal summarization** at the end of calls
- **Indian English voice** (Murf) for authentic localization
- **Result**: Professional SDR that qualifies leads and answers questions

### Day 6: Fraud Alert Voice Agent
- **SQLite database integration** for dynamic fraud case loading
- **Secure verification flow** using security questions (no PINs/passwords)
- **Real-time transaction review** with merchant, amount, and time details
- **Database write operations** to update case status (Safe/Fraud)
- **Professional fraud analyst persona** - calm, reassuring, security-focused
- **Result**: Banking fraud agent that verifies transactions and updates records

### Day 7: Food & Grocery Ordering Voice Agent
- **JSON-based product catalog** with 30+ items across 4 categories (Groceries, Snacks, Prepared Food, Beverages)
- **Intelligent recipe ordering** - "ingredients for pasta" adds multiple items automatically
- **Complete cart management** - add, remove, update quantities, view cart with totals
- **7 function tools** for search, recipe lookup, and cart operations
- **Order persistence** to JSON files with unique order IDs and timestamps
- **Friendly shopping assistant persona** - warm, helpful, knowledgeable
- **Result**: E-commerce shopping agent with smart ingredient bundling and order tracking

### Day 8: D&D-Style Voice Game Master
- **Bilingual storytelling** - Complete adventures in English or Hindi with auto-language detection
- **Interactive narrative** - GM describes vivid fantasy scenes in the realm of Eldoria
- **Option-based gameplay** - GM presents 2-3 numbered choices instead of open-ended questions
- **Story continuity tracking** - Remembers NPCs met, locations visited, items obtained, and key events
- **Dice rolling mechanics** - d20 skill checks with interpreted results (critical success/failure)
- **Auto-greeting system** - GM speaks first, asking for language preference
- **3 specialized tools** - dice rolling, story event tracking, context retrieval
- **Result**: Fantasy adventure Game Master with natural language choices and bilingual support

### Day 9: E-commerce Voice Shopping Assistant
- **ACP-inspired architecture** - Clean separation: conversation → commerce logic → persistence (following Agentic Commerce Protocol pattern)
- **Product catalog** - 9 products across 3 categories (Clothing, Accessories, Home & Kitchen) with size/color variants
- **Smart filtering** - Search by category, price range, color, and size with combined filter support
- **Shopping cart management** - Add, view, remove, clear with real-time total calculations
- **Multi-item orders** - Buy multiple products in a single transaction
- **8 function tools** - browse_catalog, get_product_details, add_to_cart, view_cart, remove_from_cart, clear_cart, place_order, get_last_order
- **Order persistence** - All orders saved to JSON with unique IDs, timestamps, and complete item details
- **Friendly shopping assistant** - Enthusiastic persona that confirms actions and suggests products
- **Result**: Full-featured e-commerce agent with structured commerce flow and order tracking

## 🛠️ Technologies Used

- **Python 3.10+** - Backend language
- **LiveKit Agents SDK** - Voice agent orchestration
- **Murf AI** - Premium Text-to-Speech
- **Deepgram** - Speech-to-Text
- **Google Gemini** - Large Language Model
- **Next.js + React** - Frontend UI
- **Model Context Protocol (MCP)** - External tool integration
- **Todoist API** - Task management (Day 3)

## 📝 Key Learnings

- **Low-latency voice** requires careful orchestration of STT → LLM → TTS
- **Function calling** enables structured data extraction from natural conversations  
- **State management** is critical for multi-turn conversations
- **Multi-agent systems** allow focused instructions and distinct personalities
- **MCP integration** extends agent capabilities with external tools
- **Context preservation** during agent handoffs maintains conversation flow
- **LLM-based evaluation** can provide nuanced feedback on user explanations
- **Pre-warming data** (like FAQs) significantly reduces latency during calls
- **Keyword matching** can be faster and more predictable than semantic search for specific domains
- **Natural lead capture** feels less like a form interrogation and more like a conversation
- **Database integration** transforms agents from passive talkers into active systems that update records
- **Security-first design** requires careful handling of verification without exposing sensitive data
- **E-commerce cart management** requires stateful tracking and clear verbal confirmations for all operations
- **Recipe intelligence** enables natural bundling of related items from simple user requests
- **Bilingual support** requires language-specific prompting and consistent language throughout the conversation
- **Auto-greeting** improves UX by eliminating awkward silences and guiding users immediately
- **Option-based interaction** makes voice agents more accessible by reducing cognitive load on users
- **ACP pattern** provides a clean architecture for commerce: separating conversation, business logic, and data layers
- **Multi-variant products** require careful state management to track size, color, and quantity selections
- **Cart mutations** in Python need proper handling (use .clear() and .extend() instead of reassignment in class methods)
- **Order ID generation** with timestamps ensures uniqueness without external dependencies

## 🔮 Day 10

The final day will focus on:
- Advanced integration patterns
- Production-ready deployment
- Performance optimization
- Real-world use case synthesis

## 📄 License

MIT License - see individual day folders for specific details

## 🙏 Credits

Challenge by [Murf AI](https://murf.ai/)  
Built with [LiveKit](https://livekit.io/)

---

**Follow along** as I build increasingly sophisticated voice AI agents! Each day builds on the previous, creating a comprehensive learning path for voice AI development.
