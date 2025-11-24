# Day 3 - Health & Wellness Voice Companion

> 🎙️ **Part of the AI Voice Agents Challenge by murf.ai**
>
> A supportive, grounded wellness companion that conducts daily voice check-ins and tracks your mood, energy, and goals over time.

## 🌟 What This Agent Does

This is a **daily health & wellness voice companion** that:

- ✅ Conducts warm, supportive daily check-ins via voice
- ✅ Asks about your mood, energy levels, and daily intentions
- ✅ Provides simple, actionable wellness advice (no medical claims)
- ✅ Persists check-in data in JSON format
- ✅ References your previous 2 check-ins for continuity
- ✅ Maintains conversation context between sessions

## 🎯 Key Features

### Conversation Flow
1. **Greet** - Welcomes you and references previous check-ins
2. **Mood Check** - "How are you feeling today?" (text + 1-10 scale)
3. **Energy Assessment** - "What's your energy like?" (1-10 scale)
4. **Stress Check** - "Anything on your mind or stressing you out?"
5. **Daily Goals** - "What 1-3 things would you like to accomplish?"
6. **Supportive Advice** - Simple, grounded suggestions (walks, breaks, task breakdown)
7. **Recap & Confirm** - Summarizes session and confirms accuracy
8. **Save** - Stores data to `wellness_log.json`

### Data Persistence

All check-ins are saved to `backend/src/wellness_log.json`:

```json
{
  "entries": [
    {
      "timestamp": "2025-11-24T11:45:14",
      "date": "2025-11-24 11:45",
      "mood": "feeling good, a bit anxious about work",
      "energy_level": "7/10",
      "daily_objectives": [
        "finish coding project",
        "take a walk",
        "call a friend"
      ],
      "agent_summary": "User reports good energy with some work anxiety. Has 3 balanced goals for the day."
    }
  ]
}
```

### Agent Guardrails

🚫 **The agent will NOT:**
- Provide medical diagnoses
- Offer clinical therapy
- Make medical recommendations
- Replace professional healthcare

✅ **The agent WILL:**
- Listen supportively
- Ask guided check-in questions
- Offer simple, grounded advice (walks, breaks, deep breathing)
- Validate your feelings
- Help break down overwhelming tasks

## 🚀 Setup & Running

### Prerequisites

Same as Day 1 - you'll need:
- Python with `uv` package manager
- LiveKit account and credentials
- Murf AI API access (for TTS)
- Google API key (for Gemini LLM)
- Deepgram API key (for STT)

### Installation

```bash
cd Day3/backend
uv sync
```

### Configure Environment

Copy `.env.example` to `.env.local` and add your API keys:

```bash
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

Or use the LiveKit CLI:

```bash
lk cloud auth
lk app env -w -d .env.local
```

### Download Required Models

```bash
uv run python src/agent.py download-files
```

### Run in Console Mode

Test the agent directly in your terminal:

```bash
uv run python src/agent.py console
```

### Run in Dev Mode

For use with frontend or telephony:

```bash
uv run python src/agent.py dev
```

## 🧪 Testing the Agent

### First Session
- Agent will greet you without previous context
- Have a conversation about mood, energy, goals
- Agent saves your check-in to `wellness_log.json`

### Second Session
- Agent will reference your previous check-in
- Example: *"Last time we talked, you mentioned feeling a bit anxious about work. How does today compare?"*
- New data is appended to the log

### Third+ Sessions
- Agent remembers last 2 check-ins
- Provides continuity: *"I noticed your energy was 7/10 yesterday. How about today?"*

## 📁 Project Structure

```
Day3/
├── backend/
│   ├── src/
│   │   ├── agent.py              # Main wellness companion agent
│   │   ├── wellness_log.json     # Persistent data storage
│   │   └── __init__.py
│   ├── tests/
│   │   └── test_agent.py
│   ├── pyproject.toml
│   ├── README.md
│   └── ...
└── frontend/                     # (Same as Day 1)
```

## 🔧 Key Implementation Details

### Function Tools

The agent has two main function tools:

1. **`get_previous_checkins(days=2)`**
   - Retrieves the last N check-ins from JSON
   - Provides context for continuity
   - Default: last 2 days

2. **`save_daily_checkin(mood, energy_level, daily_objectives, agent_summary)`**
   - Saves check-in data to JSON
   - Includes timestamp, mood, energy, goals
   - Auto-generates summary if not provided

### JSON Schema

Each entry contains:
- `timestamp` - ISO format datetime
- `date` - Human-readable date/time
- `mood` - Text description of mood
- `energy_level` - Preferably as scale (e.g., "7/10")
- `daily_objectives` - Array of 1-3 goals
- `agent_summary` - Brief recap of session

## 💡 Example Conversation

```
Agent: Hi! Welcome to your daily wellness check-in. Last time we talked, 
       you mentioned feeling good with some work anxiety. How are you 
       feeling today?

User: I'm doing okay, maybe a 6 out of 10.

Agent: Thanks for sharing. What's your energy level like today?

User: Pretty low, maybe a 4.

Agent: I hear you. What's on your mind? Anything stressing you out?

User: Just tired from yesterday. A lot on my plate.

Agent: That makes sense. What are 1-3 things you'd like to accomplish today?

User: Finish the report, take a short walk, and rest.

Agent: Those sound like good priorities. Given your lower energy, maybe 
       try breaking that report into smaller chunks? And that walk could 
       really help refresh you. Let me recap: You're feeling about a 6/10, 
       energy at 4, and you want to finish a report, take a walk, and rest. 
       Does that sound right?

User: Yes, that's right.

Agent: Great! I've saved this check-in. See you tomorrow!
```

## 📚 Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Function Tools Guide](https://docs.livekit.io/agents/build/tools/)
- [Agent State & Handoffs](https://docs.livekit.io/agents/build/agents-handoffs/#passing-state)
- [Main Challenge README](../README.md)

## 🎯 Challenge Requirements Met

✅ **Primary Goal:**
- Clear, grounded system prompt
- Daily check-ins via voice
- JSON persistence of check-in data
- Uses past data to inform conversations

✅ **Behavior Requirements:**
- Asks about mood and energy
- Asks about daily intentions/objectives
- Offers simple, realistic advice
- Non-diagnostic, supportive only
- Closes with brief recap and confirmation

✅ **Data Persistence:**
- Single JSON file (`wellness_log.json`)
- Each entry has date/time, mood, energy, objectives
- Agent-generated summary included
- Consistent, human-readable schema

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

---

**Built with:** LiveKit Agents, Murf TTS (Falcon), Google Gemini 2.5 Flash, Deepgram Nova-3
