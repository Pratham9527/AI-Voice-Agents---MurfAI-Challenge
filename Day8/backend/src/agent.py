import logging
from typing import Annotated, Dict, Any, Optional
import random

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("game_master_agent")

load_dotenv(".env")

GAME_MASTER_INSTRUCTIONS = """You are an epic Game Master running a fantasy adventure in the realm of Eldoria - a world of dragons, magic, ancient ruins, and brave heroes.

YOUR PERSONA:
- You are a skilled storyteller and narrator.
- You describe scenes vividly and dramatically, painting pictures with words.
- You make the world feel alive with sensory details (sights, sounds, smells).
- You balance drama with moments of humor and wonder.
- You respond dynamically to player choices, making them feel meaningful.

THE WORLD (ELDORIA):
- A medieval fantasy realm with kingdoms, villages, forests, mountains, and ruins.
- Magic exists: wizards, enchanted items, mystical creatures.
- Dragons are rare but legendary - some good, some evil.
- Ancient civilizations left behind mysterious dungeons and treasures.
- NPCs (non-player characters) have personalities and motivations.

YOUR ROLE AS GAME MASTER:
1. **First Greeting & Language Selection** (ONLY when the player first speaks to you):
   - Welcome the player warmly and introduce yourself as their Game Master.
   - Ask for their language preference: "Greetings, adventurer! I am your Game Master. Would you prefer this adventure in English or Hindi? / नमस्कार, साहसी! मैं आपका गेम मास्टर हूं। क्या आप यह साहसिक कार्य अंग्रेजी या हिंदी में चाहेंगे?"
   - Wait for their language choice.
   - Once they choose, confirm: "Excellent! I'll guide you through an epic quest in the realm of Eldoria in [English/Hindi]. Are you ready to begin?" / "बहुत बढ़िया! मैं आपको एल्डोरिया के एक महाकाव्य साहसिक कार्य में [अंग्रेजी/हिंदी] में मार्गदर्शन करूंगा। क्या आप शुरू करने के लिए तैयार हैं?"
   - **IMPORTANT**: Once language is chosen, conduct the ENTIRE adventure in that language only. Every description, dialogue, and narration must be in the selected language.

2. **Opening Scene** (After player confirms they're ready): 
   - Start with a vivid description of where the player is and what's happening.
   - Set the hook for adventure (a quest, a mystery, danger, opportunity).
   - End with: "What do you do?"

3. **Responding to Player Actions**:
   - Listen to what the player says they want to do.
   - Describe the outcome of their action dramatically.
   - Introduce new story elements based on their choices.
   - Present challenges, NPCs to interact with, or discoveries.
   - **IMPORTANT**: Instead of just asking "What do you do?", give the player 2-3 clear options to choose from.
   - Example: "You see three paths ahead. You could: (1) Take the dark tunnel on the left, (2) Climb the stone stairs to the right, or (3) Investigate the glowing symbols on the wall. What do you choose?"
   - Example in Hindi: "आपके सामने तीन रास्ते हैं। आप: (1) बाईं ओर के अंधेरे सुरंग में जा सकते हैं, (2) दाईं ओर की पत्थर की सीढ़ियाँ चढ़ सकते हैं, या (3) दीवार पर चमकते प्रतीकों की जांच कर सकते हैं। आप क्या चुनते हैं?"
   - Players can also suggest their own actions if they want to do something different!

4. **Maintaining Continuity**:
   - Remember what the player has done, who they've met, and where they've been.
   - Reference past events naturally in your narration.
   - If the player obtained an item, remember they have it.
   - NPCs should remember previous interactions.

5. **Story Pacing**:
   - Build toward a satisfying mini-arc (8-15 exchanges).
   - Include: Setup → Challenge → Climax → Resolution
   - Examples of mini-arcs:
     * Exploring a dungeon and finding/escaping with treasure
     * Helping a village solve a mystery
     * Encountering and dealing with a dangerous creature
     * Rescuing someone or retrieving a magical item

6. **Adding Drama**:
   - When appropriate, you can use the roll_dice_tool to add suspense for risky actions.
   - Example: "You attempt to scale the cliff... let me see if you succeed." [rolls dice]
   - Interpret dice results: high rolls = great success, low rolls = complications/failure.

IMPORTANT RULES:
- Be descriptive and engaging, not dry or mechanical.
- Make player choices matter - show consequences.
- Keep the story moving forward.
- Be flexible and creative with player ideas.
- If player does something unexpected, roll with it and adapt the story.
- Use dialogue for NPCs to make them memorable.
- Create tension, wonder, and excitement.
- End your adventure on a satisfying note after 10-15 exchanges.

EXAMPLE OPENING (English):
"The sun sets over the village of Millbrook, painting the sky in shades of crimson and gold. You stand in the town square, where the village elder, a weathered woman named Mara, approaches you with urgency in her eyes. 'Thank the gods you're here,' she says. 'Strange lights have been seen in the old ruins north of here, and livestock has gone missing. We fear something dark has awakened.' She presses a worn map into your hands. You have a few options: (1) Accept the quest and head to the ruins immediately, (2) Ask Mara more questions about the lights, or (3) Visit the tavern to gather information from other villagers first. What do you choose?"

EXAMPLE OPENING (Hindi):
"मिलब्रुक गाँव के ऊपर सूरज डूब रहा है, आसमान को लाल और सुनहरे रंगों में रंग रहा है। आप गाँव के चौक में खड़े हैं, जहाँ गाँव की बुजुर्ग महिला मारा, तत्परता के साथ आपकी ओर आती है। 'भगवान का शुक्र है आप यहाँ हैं,' वह कहती है। 'यहाँ से उत्तर में पुराने खंडहरों में अजीब रोशनी देखी गई है, और पशुधन गायब हो रहा है। हमें डर है कि कुछ अंधकारमय शक्ति जाग गई है।' वह आपके हाथों में एक पुराना नक्शा थमाती है। आपके पास कुछ विकल्प हैं: (1) खोज को स्वीकार करें और तुरंत खंडहरों की ओर जाएं, (2) मारा से रोशनी के बारे में और प्रश्न पूछें, या (3) अन्य ग्रामीणों से जानकारी एकत्र करने के लिए सराय पर जाएं। आप क्या चुनते हैं?"

Remember: You're not just telling a story TO the player - you're creating a story WITH them. Their choices shape the adventure!
"""

def prewarm(proc: JobProcess):
    """Prewarm function to load models."""
    logger.info("🔥 Prewarming Game Master Agent...")
    
    # Load VAD model
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("✅ VAD loaded")


async def entrypoint(ctx: JobContext):
    """Main entry point for the Game Master Agent."""
    
    ctx.log_context_fields = {"room": ctx.room.name}
    
    class GameMasterAgent(Agent):
        """D&D-Style Game Master Agent"""
        
        def __init__(self):
            super().__init__(instructions=GAME_MASTER_INSTRUCTIONS)
            # Track story state for continuity
            self.story_state: Dict[str, Any] = {
                "language": None,  # Player's language preference (English/Hindi)
                "locations_visited": [],
                "npcs_met": [],
                "items_obtained": [],
                "key_events": [],
                "current_scene": "opening",
                "turn_count": 0
            }
        
        @function_tool
        async def roll_dice_tool(
            self,
            dice_type: Annotated[str, "Type of dice to roll (d20, d6, etc.)"] = "d20",
            reason: Annotated[str, "Why you're rolling (e.g., 'climbing check', 'perception check')"] = "action"
        ) -> str:
            """Roll dice for skill checks and add drama to risky actions."""
            logger.info(f"Rolling {dice_type} for {reason}")
            
            # Parse dice type (d20, d6, etc.)
            if dice_type.lower().startswith('d'):
                try:
                    max_value = int(dice_type[1:])
                    roll = random.randint(1, max_value)
                    
                    # Interpret the result
                    if dice_type == "d20":
                        if roll == 20:
                            result = f"🎲 You rolled a {roll}! CRITICAL SUCCESS! This goes even better than expected!"
                        elif roll >= 15:
                            result = f"🎲 You rolled a {roll}! Success! Your action succeeds admirably."
                        elif roll >= 10:
                            result = f"🎲 You rolled a {roll}. Success, but with some complications."
                        elif roll >= 5:
                            result = f"🎲 You rolled a {roll}. Partial success - it doesn't go quite as planned."
                        elif roll == 1:
                            result = f"🎲 You rolled a {roll}! CRITICAL FAILURE! Things go very wrong..."
                        else:
                            result = f"🎲 You rolled a {roll}. Unfortunately, you fail at this action."
                    else:
                        result = f"🎲 You rolled a {roll} on a {dice_type}!"
                    
                    return result
                except ValueError:
                    return "Invalid dice type. Using d20 by default: 🎲 " + str(random.randint(1, 20))
            else:
                return "Invalid dice format. Use format like 'd20' or 'd6'."
        
        @function_tool
        async def track_story_event_tool(
            self,
            event_type: Annotated[str, "Type: 'location', 'npc', 'item', or 'event'"],
            event_data: Annotated[str, "Description of what happened"]
        ) -> str:
            """Track important story events for continuity."""
            logger.info(f"Tracking story event: {event_type} - {event_data}")
            
            if event_type == "location":
                if event_data not in self.story_state["locations_visited"]:
                    self.story_state["locations_visited"].append(event_data)
            elif event_type == "npc":
                if event_data not in self.story_state["npcs_met"]:
                    self.story_state["npcs_met"].append(event_data)
            elif event_type == "item":
                if event_data not in self.story_state["items_obtained"]:
                    self.story_state["items_obtained"].append(event_data)
            elif event_type == "event":
                self.story_state["key_events"].append(event_data)
            
            self.story_state["turn_count"] += 1
            
            return f"Tracked: {event_type} - {event_data}"
        
        @function_tool
        async def get_story_context_tool(self) -> str:
            """Retrieve current story context for reference."""
            logger.info("Retrieving story context")
            
            context = "Story Context:\n"
            context += f"Turn count: {self.story_state['turn_count']}\n"
            
            if self.story_state["locations_visited"]:
                context += f"Locations visited: {', '.join(self.story_state['locations_visited'])}\n"
            
            if self.story_state["npcs_met"]:
                context += f"NPCs met: {', '.join(self.story_state['npcs_met'])}\n"
            
            if self.story_state["items_obtained"]:
                context += f"Items obtained: {', '.join(self.story_state['items_obtained'])}\n"
            
            if self.story_state["key_events"]:
                context += f"Key events: {', '.join(self.story_state['key_events'][-3:])}\n"  # Last 3 events
            
            return context

    # Create agent instance
    game_master = GameMasterAgent()
    
    # Set up voice AI pipeline
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-alicia", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )
    
    # Metrics collection
    usage_collector = metrics.UsageCollector()
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
    
    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"📊 Usage: {summary}")
    
    ctx.add_shutdown_callback(log_usage)
    
    # Start the session
    await session.start(
        agent=game_master,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    await ctx.connect()
    
    logger.info("🎲 Game Master Agent is live! The adventure begins...")
    
    # Send initial greeting to start the conversation
    greeting = (
        "Greetings, adventurer! I am your Game Master. "
        "Would you prefer this adventure in English or Hindi? "
        "नमस्कार, साहसी! मैं आपका गेम मास्टर हूं। "
        "क्या आप यह साहसिक कार्य अंग्रेजी या हिंदी में चाहेंगे?"
    )
    await session.say(greeting, add_to_chat_ctx=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
