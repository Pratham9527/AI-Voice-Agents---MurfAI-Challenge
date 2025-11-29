# Day 8: D&D Voice Game Master 🎲

An interactive fantasy adventure powered by voice AI. The Game Master tells epic stories in the realm of Eldoria, responds to your choices, and maintains story continuity throughout your quest.

## Features
- **Bilingual Support**: Choose between English or Hindi for your entire adventure! / अपनी पूरी साहसिक यात्रा के लिए अंग्रेजी या हिंदी चुनें!
- **Interactive Storytelling**: The GM describes vivid scenes with clear options to choose from
- **Player Agency**: Your spoken actions shape the story
- **Story Continuity**: Remembers past decisions, NPCs met, items obtained, and locations visited
- **Dice Mechanics**: Roll d20 for skill checks and dramatic moments
- **Fantasy Setting**: Adventure in **Eldoria** - a world of dragons, magic, and ancient mysteries
- **Auto-Greeting**: GM speaks first when you connect, asking for language preference

## Quick Start

### 1. Start Backend (Game Master Agent)
```bash
cd backend
python src/agent.py dev
```

### 2. Start Frontend (UI)
```bash
cd frontend
npm run dev
```

### 3. Play the Adventure
- Open http://localhost:3000
- Click **"⚔️ Begin Adventure"** and allow microphone access
- The GM will greet you and ask: **"English or Hindi?"**
- Choose your language
- Listen to the opening scene and choose your adventure!

## Example Gameplay

**GM**: "You stand at the entrance of ancient ruins. You have a few options: (1) Enter the dark tunnel, (2) Climb the stone stairs, or (3) Investigate the symbols on the wall. What do you choose?"

**You**: "I choose option 1" or "I enter the tunnel"

**GM**: Describes what happens next and gives you new options!

## Try These Commands
- "I choose option 2"
- "I investigate the area"
- "I talk to the NPC"
- "I search for treasure"
- Or say anything creative - the GM will adapt!

## Documentation
- [Backend README](backend/README.md) - Full features and technical details
- [AGENTS.md](backend/AGENTS.md) - Game Master capabilities and configuration

---

**Murf AI Voice Agents Challenge - Day 8/10**
