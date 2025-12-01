# Day 10 - Voice Improv Battle 🎭

A voice-first improv game show where an AI host presents scenarios and provides real-time feedback on your performance!

## 🎮 Game Concept

"Improv Battle" is a single-player improv performance game where:
- The AI host presents you with 3 unique improv scenarios
- You perform each scenario in character
- The host reacts with varied, realistic feedback (praise, critique, or surprise)
- At the end, you get a summary of your improv style

## 🚀 Quick Start

### Backend (Terminal 1)
```bash
cd backend
python src/agent.py dev
```

### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:3000 and click "🎭 Start Improv Battle"!

## ✨ Features

### 🎭 **Improv Host Persona**
- High-energy, witty game show host
- Provides realistic, varied reactions
- Can tease and give honest critique while staying respectful

### 🎲 **12 Unique Scenarios**
Including favorites like:
- Time-travelling tour guide explaining smartphones to someone from the 1800s
- Restaurant waiter telling a customer their order escaped the kitchen
- Customer returning a cursed object to a skeptical shop owner
- And 9 more creative scenarios!

### 🎯 **Smart Game Flow**
- Automatic scene end detection
- Varied host reactions (positive, critical, mixed, surprised)
- Closing summary of your improv style
- Early exit support

### 🔊 **Voice Pipeline**
- **STT**: Deepgram Nova-3
- **LLM**: Google Gemini 2.5 Flash
- **TTS**: Murf (en-US-alicia, Conversation style)
- **Turn Detection**: Multilingual model
- **Noise Cancellation**: BVC

## 🎪 How It Works

### Phase 1: Introduction
1. Host welcomes you
2. Explains the game
3. Asks for your name
4. Announces 3 rounds

### Phase 2: Each Round (3x)
1. Host presents a scenario
2. You perform in character
3. Host detects when you finish
4. Host reacts authentically
5. Moves to next round

### Phase 3: Closing
1. Game completion announcement
2. Summary of your improv style
3. Memorable moments highlighted
4. Warm sign-off

## 🎨 Technical Highlights

### Game State Management
- Tracks current round (0-3)
- Manages game phases (intro → awaiting_improv → reacting → done)
- Prevents scenario repetition
- Records all rounds and reactions

### Scene End Detection
Recognizes when you're done through:
- Explicit phrases: "end scene", "done", "that's it"
- Natural completion indicators
- Turn count (automatically after 3+ user turns)

### Varied Reactions
Host mixes up feedback types:
- **Positive**: "That was brilliant! I loved how you..."
- **Critical**: "Hmm, that felt a bit rushed..."
- **Mixed**: "Good commitment, but could push further..."
- **Surprised**: "Wow! I did NOT expect..."

## 📁 Project Structure

```
Day10/
├── backend/
│   ├── src/
│   │   └── agent.py           # Improv battle agent
│   ├── .env                    # Environment variables
│   ├── AGENTS.md               # Agent documentation
│   └── requirements.txt        # Dependencies
└── frontend/
    ├── app/
    │   └── (app)/page.tsx      # Main page
    ├── components/
    │   └── app/
    │       ├── welcome-view.tsx  # Updated for improv
    │       └── ...
    ├── app-config.ts           # Updated config
    └── package.json
```

## 🔧 Environment Variables

Create a `.env` file in the `backend` directory:

```env
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
MURF_API_KEY=your_murf_key
GOOGLE_API_KEY=your_google_key
DEEPGRAM_API_KEY=your_deepgram_key
```

## 🎯 Primary Goal Achievement

✅ **All requirements met:**
- [x] Single-player improv battle
- [x] Browser-based join
- [x] AI game show host persona
- [x] Multiple improv scenarios
- [x] Varied, realistic host reactions
- [x] Game state management
- [x] Round progression (3 rounds)
- [x] Closing summary
- [x] Early exit handling

## 🎬 Play Tips

1. **Commit to the character** - The host appreciates full commitment
2. **Be creative** - Unexpected choices get positive reactions
3. **Say "end scene"** when done to trigger host feedback
4. **Have fun** - It's improv, there are no wrong answers!

## 📝 Notes

- The host's reactions are intentionally varied to feel realistic
- Scenarios are randomly selected without repetition
- The game always runs 3 rounds unless you request early exit
- Your improv style summary is generated based on all your performances

---

**Built for Day 10 of the Murf AI Voice Agents Challenge** 🎭
