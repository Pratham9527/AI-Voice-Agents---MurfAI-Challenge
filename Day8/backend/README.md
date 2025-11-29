# D&D Voice Game Master - Day 8

An interactive fantasy adventure powered by voice AI. Built with LiveKit Agents and Murf TTS.

## 🎲 What is this?

This is a **D&D-style Game Master** that runs a fantasy adventure through voice interaction. The AI acts as your Dungeon Master, describing scenes, responding to your choices, and maintaining story continuity throughout your quest.

### Features

- **Bilingual Support**: Choose between English or Hindi for your entire adventure! / अपनी पूरी साहसिक यात्रा के लिए अंग्रेजी या हिंदी चुनें!
- **Interactive Storytelling**: The GM describes vivid scenes and asks "What do you do?"
- **Player Agency**: Your spoken actions shape the story
- **Story Continuity**: The agent remembers past decisions, NPCs met, items obtained, and locations visited
- **Dice Mechanics**: Roll d20 for skill checks and dramatic moments
- **Fantasy Setting**: Adventure in the realm of **Eldoria** - a world of dragons, magic, and ancient mysteries
- **Mini-Arc Adventures**: Complete satisfying stories in 10-15 exchanges

### How It Works

1. **Start the adventure** - Click "⚔️ Begin Adventure" and allow microphone access
2. **Choose your language** - Select English or Hindi when the GM asks
3. **Listen to the GM** - The Game Master sets the scene and describes your situation (in your chosen language)
4. **Speak your action** - Tell the GM what you want to do (e.g., "I search the room", "I talk to the innkeeper")
5. **Watch the story unfold** - The GM responds to your choices and continues the narrative
6. **Complete your quest** - Reach a satisfying conclusion (find treasure, solve mystery, escape danger)

## 🚀 Running the Project

### Backend (Game Master Agent)

```powershell
cd Day8/backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/agent.py dev
```

### Frontend (UI)

```powershell
cd Day8/frontend
npm install
npm run dev
```

Then open http://localhost:3000

## 🎭 The Game Master

The GM is powered by:
- **Google Gemini 2.5 Flash** for intelligent storytelling and responses
- **Deepgram Nova-3** for speech-to-text
- **Murf TTS** for natural voice narration
- **LiveKit Agents** for real-time voice interaction

### Sample Adventure Opening

> "The sun sets over the village of Millbrook, painting the sky in shades of crimson and gold. You stand in the town square, where the village elder, a weathered woman named Mara, approaches you with urgency in her eyes. 'Thank the gods you're here,' she says. 'Strange lights have been seen in the old ruins north of here, and livestock has gone missing. We fear something dark has awakened.' She presses a worn map into your hands. 'Will you investigate?' What do you do?"

## 📝 Technical Details

### Tools Available to the GM

1. **`roll_dice_tool`** - Roll dice (d20, d6, etc.) for skill checks and add drama
2. **`track_story_event_tool`** - Track important story elements (locations, NPCs, items, events)
3. **`get_story_context_tool`** - Retrieve current story state for continuity

### Story State Tracking

The agent maintains:
- Language preference (English or Hindi)
- Locations visited
- NPCs encountered
- Items obtained
- Key events
- Turn count

This ensures the GM remembers what happened earlier in your adventure!

## 🎯 Day 8 Requirements

✅ **Clear Game Master persona** - Dramatic storytelling in a fantasy universe  
✅ **Interactive story** - GM describes scenes and prompts for player action  
✅ **Voice-driven** - Fully controlled by speaking  
✅ **Continuity** - Remembers past decisions and story elements  
✅ **Mini-arc structure** - Adventures last 10-15 exchanges with satisfying conclusions  
✅ **UI display** - Shows GM narration and player's transcribed speech

## 📚 Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [LiveKit Prompting Guide](https://docs.livekit.io/agents/build/prompting/)
- [LiveKit Tools Guide](https://docs.livekit.io/agents/build/tools/)

---

**Murf AI Voice Agents Challenge - Day 8/10**
