import logging
from typing import Dict, Any, Optional
import json
from pathlib import Path
from datetime import datetime
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
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("improv_battle_agent")

load_dotenv(".env")

# ============================================================================
# IMPROV SCENARIOS
# ============================================================================

IMPROV_SCENARIOS = [
    "You are a time-travelling tour guide explaining modern smartphones to someone from the 1800s.",
    "You are a restaurant waiter who must calmly tell a customer that their order has escaped the kitchen.",
    "You are a customer trying to return an obviously cursed object to a very skeptical shop owner.",
    "You are a barista who has to tell a customer that their latte is actually a portal to another dimension.",
    "You are a librarian who must explain to a confused visitor that the books in your library are alive and moody.",
    "You are a pizza delivery person who needs to convince someone that you're delivering their pizza from the future.",
    "You are a museum tour guide explaining why one of the statues keeps moving when no one is looking.",
    "You are a tech support agent helping someone troubleshoot their magic wand.",
    "You are a fitness instructor teaching yoga to a group of very sleepy zombies.",
    "You are a car salesman trying to sell a vehicle that only runs on compliments.",
    "You are a doctor explaining to a patient that they've contracted a case of spontaneous musical numbers.",
    "You are a teacher addressing your classroom of students who have all suddenly become cats.",
]

# ============================================================================
# GAME STATE
# ============================================================================

class ImprovState:
    """Manages the state of the improv battle game"""
    
    def __init__(self):
        self.player_name: Optional[str] = None
        self.current_round: int = 0
        self.max_rounds: int = 3
        self.rounds: list[Dict[str, str]] = []
        self.phase: str = "intro"  # intro | awaiting_improv | reacting | done
        self.scenarios_used: list[str] = []
        self.awaiting_scene_end: bool = False
        self.user_turn_count: int = 0
    
    def get_next_scenario(self) -> str:
        """Get a random unused scenario"""
        available = [s for s in IMPROV_SCENARIOS if s not in self.scenarios_used]
        if not available:
            # If we've used all scenarios, reset
            self.scenarios_used.clear()
            available = IMPROV_SCENARIOS
        
        scenario = random.choice(available)
        self.scenarios_used.append(scenario)
        return scenario
    
    def add_round(self, scenario: str, reaction: str):
        """Record a completed round"""
        self.rounds.append({
            "scenario": scenario,
            "reaction": reaction
        })
    
    def get_summary(self) -> str:
        """Generate a summary of the game"""
        if not self.rounds:
            return "No rounds completed."
        
        summary = f"Game summary for {self.player_name or 'Player'}:\n\n"
        for i, round_data in enumerate(self.rounds, 1):
            summary += f"Round {i}: {round_data['scenario'][:50]}...\n"
            summary += f"Host reaction: {round_data['reaction']}\n\n"
        
        return summary

# Global state instance
improv_state = ImprovState()

# ============================================================================
# AGENT INSTRUCTIONS
# ============================================================================

IMPROV_HOST_INSTRUCTIONS = """You are the host of a TV improv show called "Improv Battle"!

YOUR PERSONA:
- You are high-energy, witty, and charismatic like a game show host
- You're clear about the rules and keep the game moving
- Your reactions are REALISTIC and VARIED - not always supportive
- Sometimes you're amused, sometimes unimpressed, sometimes pleasantly surprised
- You can tease and give honest critique, but you're always respectful and never abusive
- You celebrate good improv and gently critique what could be better

THE GAME FLOW:

**Phase 1 - Introduction (Only do this once at the start):**
- Welcome the player warmly and with energy!
- Briefly explain the game: "I'll give you improv scenarios, you act them out, and I'll react to your performance"
- Ask for their name if they haven't introduced themselves
- Tell them how many rounds you'll do (3 rounds)
- Then immediately start Round 1

**Phase 2 - Each Improv Round (Repeat 3 times):**
1. **Set the scene**: Announce the round number and present a clear, specific improv scenario
   - Be enthusiastic: "Alright, Round 1! Here's your scenario..."
   - Clearly describe who they are, what's happening, and what the challenge is
   - End with "Action!" or "Go ahead!" to signal they should start

2. **Player performs**: Listen to them improvise in character
   - Let them perform without interrupting
   - Pay attention to their creativity, commitment, and humor

3. **Detect scene end**: The player will either:
   - Say explicit end phrases like "End scene", "Scene", "Done", "That's it"
   - Make it clear they've finished (e.g., long pause, asking "How was that?")
   - After they've had a reasonable turn to perform

4. **React authentically**: Give feedback that's honest and varied
   - **Sometimes positive**: "That was brilliant! I loved how you..."
   - **Sometimes critical**: "Hmm, that felt a bit rushed. You could have leaned more into..."
   - **Sometimes mixed**: "Good commitment to the character, but the premise could have been pushed further"
   - **Sometimes surprised**: "Wow! I did NOT expect you to go there with..."
   - Mix up your tone to keep it realistic
   - Keep reactions concise (2-3 sentences max)

5. **Move to next round**: After reacting, immediately transition:
   - "Okay, moving on to Round 2!" (or Round 3)
   - Present the next scenario
   - Keep the energy up!

**Phase 3 - Closing (After 3 rounds):**
- Announce that the game is complete
- Give a short summary of their improv style:
  - Comment on patterns you noticed (character work, absurdity, emotional range, etc.)
  - Mention 1-2 specific moments that stood out
  - Keep it to 3-4 sentences total
- Thank them for playing and sign off with energy

IMPORTANT RULES:
1. **Never skip rounds** - Always do exactly 3 rounds unless the player asks to stop
2. **Keep it moving** - Don't over-explain, keep the energy high
3. **Vary your reactions** - Use different tones (impressed, critical, amused, neutral)
4. **Be concise** - Short, punchy responses. This is a fast-paced show!
5. **Stay in character** - You're a game show host, not a therapist or teacher
6. **Recognize end signals** - When players say "end scene" or similar, that's your cue to react

EARLY EXIT:
If the player says they want to stop, quit, or end the game:
- Acknowledge it gracefully: "No problem! Thanks for playing!"
- Give a very brief summary of what they did
- Sign off warmly

Remember: You're creating a fun, dynamic improv experience. Keep the energy high, reactions real, and the game moving forward!
"""

# ============================================================================
# PREWARM
# ============================================================================

def prewarm(proc: JobProcess):
    """Prewarm function to load models."""
    logger.info("🔥 Prewarming Improv Battle Agent...")
    
    # Load VAD model
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("✅ VAD loaded")

# ============================================================================
# MAIN AGENT
# ============================================================================

async def entrypoint(ctx: JobContext):
    """Main entry point for the Improv Battle Agent."""
    
    ctx.log_context_fields = {"room": ctx.room.name}
    
    # Reset state for new session
    global improv_state
    improv_state = ImprovState()
    
    class ImprovBattleAgent(Agent):
        """Voice Improv Battle Game Show Host"""
        
        def __init__(self):
            super().__init__(instructions=IMPROV_HOST_INSTRUCTIONS)
            self.current_scenario: Optional[str] = None
        
        async def handle_user_message(self, message: str):
            """Process user messages and manage game state"""
            message_lower = message.lower().strip()
            
            # Check for explicit end scene signals
            end_scene_phrases = ["end scene", "scene", "done", "that's it", "finished", "end"]
            is_end_signal = any(phrase in message_lower for phrase in end_scene_phrases)
            
            # Check for early exit request
            exit_phrases = ["stop game", "end game", "quit", "stop show", "end show", "exit"]
            wants_exit = any(phrase in message_lower for phrase in exit_phrases)
            
            if wants_exit:
                improv_state.phase = "done"
                return
            
            # Track user turns during improv performance
            if improv_state.phase == "awaiting_improv":
                improv_state.user_turn_count += 1
                
                # If we detect an end signal OR they've had several turns, move to reacting
                if is_end_signal or improv_state.user_turn_count >= 3:
                    improv_state.phase = "reacting"
                    improv_state.user_turn_count = 0
    
    # Create agent instance
    improv_host = ImprovBattleAgent()
    
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
    
    # Event handlers for managing game flow
    @session.on("user_speech_committed")
    def on_user_speech(message):
        """Process user speech for game state management"""
        import asyncio
        asyncio.create_task(improv_host.handle_user_message(message.text))
    
    # Start the session
    await session.start(
        agent=improv_host,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    await ctx.connect()
    
    logger.info("🎭 Improv Battle Agent is live! Let the show begin...")
    
    # Send initial greeting
    greeting = (
        "Welcome to Improv Battle! "
        "I'm your host, and I'm here to test your improv skills! "
        "Here's how it works: I'll give you a scenario, you act it out in character, "
        "and I'll react to your performance. We'll do 3 rounds. "
        "First, what's your name?"
    )
    
    improv_state.phase = "intro"
    await session.say(greeting, add_to_chat_ctx=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
