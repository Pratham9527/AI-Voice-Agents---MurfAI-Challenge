# Day 4 - Active Recall Coach 🎓

**Teach-the-Tutor: Multi-Agent Voice Learning System**

A sophisticated voice AI system that helps you learn programming concepts through active recall. The agent uses three distinct learning modes, each powered by a different AI personality with unique voices.

## 🎯 Overview

This project implements a **teach-back learning system** where the best way to learn is to teach. The AI explains concepts, quizzes you, and then asks you to explain topics back—scoring your understanding using LLM-based evaluation.

### Core Features

✅ **Three Learning Modes**
- **Learn Mode** (Matthew) - AI explains concepts clearly
- **Quiz Mode** (Alicia) - AI tests your understanding with questions
- **Teach-Back Mode** (Ken) - You explain concepts, AI scores you (0-100)

✅ **Multi-Agent Architecture**
- 4 specialized agents with focused responsibilities
- Seamless handoffs with context preservation
- Distinct Murf AI voices for each mode

✅ **Content-Driven Learning**
- 4 programming concepts: Variables, Loops, Functions, Conditionals
- Easily extensible JSON-based content structure

✅ **Progress Tracking**
- Automatic session logging
- Teach-back score history
- Concept mastery calculations
- Performance analytics

## 🏗️ Architecture

```
GreeterAgent (Default Voice)
    ↓
    Asks user preference
    ↓
┌───────────┬──────────────┬─────────────┐
│           │              │             │
Learn       Quiz        Teach-Back    Continue
(Matthew)   (Alicia)    (Ken)         Same Topic
│           │              │             │
└───────────┴──────────────┴─────────────┘
         ↑ Seamless Mode Switching
```

### Agent Roles

| Agent | Voice | Purpose | Key Features |
|-------|-------|---------|-------------|
| **GreeterAgent** | Default | Routes users | Progress summary, mode selection |
| **LearnAgent** | Matthew | Teaches concepts | Explanations, examples, analogies |
| **QuizAgent** | Alicia | Tests knowledge | Questions, feedback, difficulty scaling |
| **TeachBackAgent** | Ken | Evaluates understanding | LLM scoring (0-100), specific feedback |

## 📁 Project Structure

```
Day4/
├── backend/
│   ├── src/
│   │   ├── agent.py                 # Multi-agent system
│   │   └── tutor_progress.json      # Learning progress (auto-created)
│   ├── shared-data/
│   │   └── day4_tutor_content.json  # Learning content (4 concepts)
│   ├── AGENTS.md                    # Architecture documentation
│   └── .env                         # Environment variables
└── frontend/
    └── (LiveKit React UI)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- LiveKit Cloud account
- Murf AI API access

### Backend Setup

1. **Navigate to backend**
   ```bash
   cd Day4/backend
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment**
   
   Create/update `.env`:
   ```env
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   MURF_API_KEY=your_murf_key
   DEEPGRAM_API_KEY=your_deepgram_key
   ```

4. **Run the agent**
   ```bash
   python src/agent.py dev
   ```

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd Day4/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```

4. **Open browser**
   ```
   http://localhost:3000
   ```

## 💡 How to Use

### Basic Flow

1. **Connect** to the voice room
2. **Greeter** welcomes you and asks which mode you prefer
3. **Choose a mode**: "I want to learn about variables"
4. **Interact** with the specialized agent (Matthew, Alicia, or Ken)
5. **Switch modes** anytime: "Quiz me" or "Let me teach it back"

### Example Conversations

**Starting Learn Mode:**
```
You: "I want to learn about loops"
Greeter: "Great! Connecting you to Matthew..."
Matthew: "Hi, I'm Matthew! Loops allow you to repeat code..."
```

**Switching to Quiz:**
```
You: "Quiz me on this"
Matthew: "Let's test your understanding..."
Alicia: "Hi! What's the difference between for and while loops?"
```

**Teach-Back Session:**
```
You: "I want to teach it back"
Ken: "Explain loops to me in your own words..."
You: [Provides explanation]
Ken: "Score: 85/100. Great job! You covered..."
```

## 📊 Progress Tracking

The system automatically tracks:

### Session Logs
Every interaction is logged with timestamp, mode, and optional scores:

```json
{
  "timestamp": "2025-11-25T19:00:00Z",
  "concept_id": "variables",
  "mode": "teach_back",
  "score": 85,
  "feedback": "Excellent explanation! You covered..."
}
```

### Concept Mastery
Aggregated stats per concept:

```json
{
  "variables": {
    "teach_back_scores": [65, 75, 85],
    "average_score": 75.0,
    "times_learned": 3,
    "times_quizzed": 5,
    "times_taught_back": 3,
    "last_activity": "2025-11-25T19:00:00Z"
  }
}
```

**View your progress**: Ask the Greeter "Show me my progress"

## 📚 Learning Content

### Available Concepts

| Concept | Description |
|---------|-------------|
| **Variables** | Containers that store data values |
| **Loops** | Repeating code blocks (for/while loops) |
| **Functions** | Reusable code blocks with parameters |
| **Conditionals** | Decision-making with if/else statements |

### Adding New Concepts

Edit `shared-data/day4_tutor_content.json`:

```json
{
  "id": "arrays",
  "title": "Arrays",
  "summary": "Arrays are collections that store multiple values of the same type...",
  "sample_question": "What is an array and when would you use one?"
}
```

Then restart the agent.

## 🔧 Configuration

### Murf Voice Settings

Current voices (configurable in `agent.py`):
- **Matthew** (Learn): Patient, teaching tone
- **Alicia** (Quiz): Encouraging, inquisitive tone
- **Ken** (Teach-Back): Thoughtful, evaluative tone

### LLM Settings

- **Model**: Gemini 2.5 Flash
- **STT**: Deepgram Nova-3
- **Turn Detection**: Multilingual Model

## 🧪 Testing

### Manual Testing Checklist

- [ ] Greeter welcomes and offers modes
- [ ] Learn mode explains concepts (Matthew voice)
- [ ] Quiz mode asks questions (Alicia voice)
- [ ] Teach-back evaluates with scores (Ken voice)
- [ ] Mode switching works smoothly
- [ ] Progress is tracked in `tutor_progress.json`
- [ ] All 4 concepts are accessible

### Test Commands

```bash
# Run agent in development mode
python src/agent.py dev

# View progress file
cat src/tutor_progress.json
```

## 📖 Key Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Agent Handoffs Guide](https://docs.livekit.io/agents/build/agents-handoffs/)
- [Murf AI Voice API](https://murf.ai/)
- [Implementation Details](./backend/AGENTS.md)

## 🐛 Troubleshooting

### Common Issues

**"Concept not found" error**
- Ensure you're using exact concept IDs: `"variables"`, `"loops"`, `"functions"`, `"conditionals"`
- Not numbers like "1", "2"

**Agent not starting**
- Check all API keys in `.env`
- Verify `day4_tutor_content.json` exists
- Ensure Python dependencies are installed (`uv sync`)

**Voice not changing between agents**
- Currently voices use session-level TTS
- Future: Implement per-agent voice overrides

**Progress not saving**
- Check write permissions for `src/tutor_progress.json`
- Verify JSON is valid after manual  edits

## 📝 Development Notes

### Design Decisions

**Why Multi-Agent?**
- Focused instructions per mode (faster LLM responses)
- Natural distinct personalities
- Easier to maintain and extend
- Better context management

**Why JSON Content?**
- Easy to add new concepts without code changes
- Non-technical users can contribute content
- Supports multiple learning domains

**Why Teach-Back?**
- Active recall proven most effective for retention
- LLM scoring provides objective feedback
- Tracks actual understanding vs. passive learning

## 🎯 Future Enhancements

- [ ] Per-agent voice overrides
- [ ] More programming concepts (OOP, recursion, etc.)
- [ ] Spaced repetition scheduling
- [ ] Visual aids/diagrams support
- [ ] Multi-language content
- [ ] Study streak tracking
- [ ] Peer comparison analytics

## 📄 License

[Your License Here]

## 👥 Contributors

Built as part of the MurfAI Voice Agents Challenge - Day 4

---

**Happy Learning! 🚀** Remember: The best way to learn is to teach!
