# Day 8 Game Master Agent

## Overview

This agent is a **D&D-style Game Master** that runs interactive fantasy adventures through voice interaction. It tells stories in the realm of **Eldoria**, a world of dragons, magic, ancient ruins, and heroes.

## Agent Capabilities

### Core Functionality

1. **Interactive Storytelling**
   - Describes vivid scenes with sensory details
   - Responds dynamically to player choices
   - Maintains dramatic pacing and tension
   - Creates memorable NPCs with dialogue

2. **Story Continuity**
   - Tracks locations visited
   - Remembers NPCs encountered
   - Records items obtained
   - Maintains key story events
   - References past decisions naturally

3. **Game Mechanics**
   - Dice rolling (d20, d6, etc.) for skill checks
   - Success/failure interpretation
   - Critical successes and failures
   - Drama and suspense generation

### Tools

The Game Master has access to these tools:

#### `roll_dice_tool(dice_type, reason)`
Rolls dice for skill checks and dramatic moments.
- **dice_type**: Type of die (d20, d6, d12, etc.)
- **reason**: Why rolling (e.g., "perception check", "climbing attempt")
- **Returns**: Roll result with success interpretation

#### `track_story_event_tool(event_type, event_data)`
Tracks important story elements for continuity.
- **event_type**: 'location', 'npc', 'item', or 'event'
- **event_data**: Description of what happened
- **Returns**: Confirmation of tracking

#### `get_story_context_tool()`
Retrieves current story state.
- **Returns**: Summary of locations, NPCs, items, and recent events

## Persona

**Role**: Epic Game Master and storyteller  
**Tone**: Dramatic, vivid, engaging with moments of humor and wonder  
**Universe**: Eldoria - medieval fantasy with magic, dragons, and ancient civilizations  
**Goal**: Create satisfying mini-arc adventures lasting 10-15 exchanges

### Conversation Flow

1. **Opening**: Set dramatic scene, introduce quest/mystery, end with "What do you do?"
2. **Gameplay Loop**: Listen to player → Describe outcome → Present new situation → Prompt for action
3. **Climax**: Build toward a dramatic moment or challenge
4. **Resolution**: Provide satisfying conclusion (treasure found, danger escaped, etc.)

## Example Interactions

### Opening Scene
```
GM: "The sun sets over the village of Millbrook, painting the sky in shades of 
crimson and gold. You stand in the town square, where the village elder, Mara, 
approaches you with urgency. 'Strange lights have been seen in the old ruins 
north of here,' she says. 'Will you investigate?' What do you do?"

Player: "I accept the quest and ask her what kind of lights"

GM: "Mara nods gravely. 'Blue lights, like cold fire, dancing among the stones. 
And there's more - those who venture too close report hearing whispers in a 
language long forgotten.' She hands you a worn map. The path north is marked 
clearly. It's about an hour's walk through the forest. What do you do?"
```

### Dice Roll Example
```
Player: "I try to climb the cliff wall"

GM: "You approach the rocky cliff face, searching for handholds. Let me see if 
you can make the climb..."
[Calls roll_dice_tool(d20, "climbing check")]
GM: "🎲 You rolled a 16! Success! Your fingers find purchase in the stone, and 
you scale the cliff with practiced ease. At the top, you see smoke rising from 
a cave entrance. What do you do?"
```

## Technical Implementation

### Voice Pipeline
- **STT**: Deepgram Nova-3 (speech recognition)
- **LLM**: Google Gemini 2.5 Flash (storytelling and responses)
- **TTS**: Murf (en-US-alicia voice with conversational style)
- **VAD**: Silero (voice activity detection)
- **Turn Detection**: Multilingual Model

### Story State
The agent maintains a `story_state` dictionary:
```python
{
    "locations_visited": [],  # List of location names
    "npcs_met": [],          # List of NPC names
    "items_obtained": [],    # List of item names
    "key_events": [],        # List of significant events
    "current_scene": "opening",
    "turn_count": 0
}
```

## Design Decisions

1. **No Complex State Management**: Unlike Day 7's cart system, this agent relies primarily on chat history and a simple state dict
2. **Optional Tools**: The GM can choose whether to roll dice or track events - it's not required for every action
3. **Flexible Storytelling**: The LLM has creative freedom to respond to unexpected player actions
4. **Mini-Arc Structure**: Adventures are designed to complete in one session (10-15 turns) rather than requiring save/load

## Configuration

System prompt defines:
- **Universe**: Eldoria fantasy realm
- **Tone**: Dramatic with humor
- **Persona**: Skilled storyteller
- **Rules**: Make choices matter, maintain continuity, build satisfying arcs

## Usage

```powershell
# Start the agent
cd Day8/backend
python src/agent.py dev
```

The agent will greet the player with an opening scene and begin the adventure!

---

**Part of the Murf AI Voice Agents Challenge - Day 8**
