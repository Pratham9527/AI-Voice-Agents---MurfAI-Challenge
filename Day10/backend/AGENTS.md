# Day 10 - Voice Improv Battle Agent

## Overview
This agent hosts "Improv Battle" - a voice-first improv game show where the AI plays the role of an energetic game show host who presents improv scenarios to players and reacts to their performances with varied, realistic feedback.

## Agent Role
The agent is a **high-energy improv game show host** with the following characteristics:
- Witty, charismatic, and clear about rules
- Provides realistic, varied reactions (sometimes amused, sometimes critical, sometimes surprised)
- Can tease and give honest critique while remaining respectful
- Celebrates good improv and provides constructive feedback

## Game Flow

### Phase 1: Introduction
The host:
1. Welcomes the player with energy
2. Explains the game concept briefly
3. Asks for the player's name
4. Announces number of rounds (3)
5. Immediately starts Round 1

### Phase 2: Improv Rounds (3 rounds)
For each round:
1. **Set the scene**: Host announces round number and presents a specific scenario
2. **Player performs**: Player improvises in character
3. **Detect scene end**: Host listens for end signals ("end scene", "done", etc.) or natural completion
4. **React authentically**: Host provides varied feedback (positive, critical, mixed, or surprised)
5. **Transition**: Host moves to next round with energy

### Phase 3: Closing
After 3 rounds:
1. Announces game completion
2. Provides short summary of player's improv style
3. Mentions 1-2 standout moments
4. Thanks player and signs off

## Game State Management

The agent maintains game state through the `ImprovState` class:
- `player_name`: Player's name
- `current_round`: Current round number (0-3)
- `max_rounds`: Total rounds (3)
- `rounds`: List of completed rounds with scenarios and reactions
- `phase`: Current game phase ("intro", "awaiting_improv", "reacting", "done")
- `scenarios_used`: Tracks used scenarios to avoid repetition
- `user_turn_count`: Tracks turns during improv performance

## Improv Scenarios

The agent has 12 pre-defined improv scenarios, including:
- Time-travelling tour guide explaining smartphones to someone from the 1800s
- Restaurant waiter explaining that the order escaped the kitchen
- Customer returning a cursed object to a skeptical shop owner
- Barista revealing a latte is a portal to another dimension
- And 8 more creative scenarios

Scenarios are randomly selected without repetition during a session.

## Key Features

### Varied Host Reactions
The host provides different types of feedback:
- **Positive**: "That was brilliant! I loved how you..."
- **Critical**: "Hmm, that felt a bit rushed. You could have..."
- **Mixed**: "Good commitment, but the premise could have been pushed further"
- **Surprised**: "Wow! I did NOT expect you to go there with..."

### Scene End Detection
The agent recognizes when players finish performing through:
- Explicit phrases: "end scene", "done", "that's it", "finished"
- Natural completion indicators
- Turn count (after 3+ user turns)

### Early Exit Handling
If players want to stop early:
- Agent acknowledges gracefully
- Provides brief summary of what they did
- Signs off warmly

## Technical Implementation

### Voice Pipeline
- **STT**: Deepgram Nova-3 for speech recognition
- **LLM**: Google Gemini 2.5 Flash for response generation
- **TTS**: Murf TTS (en-US-alicia voice, Conversation style)
- **Turn Detection**: Multilingual model
- **Noise Cancellation**: BVC (Background Voice Cancellation)

### Event Handling
The agent uses event handlers to manage game flow:
- `user_speech_committed`: Processes user messages for state management
- Automatically transitions between game phases
- Tracks progress and manages round completion

## Usage

### Starting the Agent
```bash
cd backend
python src/agent.py dev
```

### Frontend
The frontend is a Next.js application that:
1. Provides a simple join screen
2. Collects player name
3. Starts the improv battle session
4. Connects to LiveKit voice agent

### Running Full Application
```bash
# Terminal 1 - Backend
cd backend
python src/agent.py dev

# Terminal 2 - Frontend  
cd frontend
npm install
npm run dev
```

Then open http://localhost:3000 to start playing!

## AI Agent Guidelines

When interacting with this codebase:
1. **Game state is critical**: Always maintain proper state transitions
2. **Keep host persona**: Ensure responses are energetic and varied
3. **Scenario variety**: Don't repeat scenarios in the same session
4. **Natural flow**: Keep the game moving, don't over-explain
5. **Authentic reactions**: Mix positive and critical feedback realistically

## File Structure
```
Day10/
├── backend/
│   ├── src/
│   │   └── agent.py          # Main improv battle agent
│   ├── .env                   # Environment variables
│   └── requirements.txt       # Python dependencies
└── frontend/
    ├── app/
    │   └── page.tsx           # Main UI (needs updating from Day9)
    └── package.json           # Node dependencies
```

## Environment Variables Required
```
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
MURF_API_KEY=your_murf_key
GOOGLE_API_KEY=your_google_key
DEEPGRAM_API_KEY=your_deepgram_key
```

## Next Steps for Complete Implementation
1. Update frontend to show improv-specific UI
2. Add visual indicators for current round
3. Display scenario text on screen
4. Show game progress/state
5. Add end game summary display
