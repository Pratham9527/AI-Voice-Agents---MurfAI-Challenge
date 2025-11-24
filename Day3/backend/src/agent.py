import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Annotated

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
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env")

# Path to wellness log
WELLNESS_LOG_PATH = Path(__file__).parent / "wellness_log.json"


def load_wellness_log() -> dict:
    """Load the wellness log from JSON file."""
    if not WELLNESS_LOG_PATH.exists():
        return {"entries": []}
    
    try:
        with open(WELLNESS_LOG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading wellness log: {e}")
        return {"entries": []}


def save_wellness_log(data: dict) -> bool:
    """Save the wellness log to JSON file."""
    try:
        with open(WELLNESS_LOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving wellness log: {e}")
        return False


def get_recent_entries(days: int = 2) -> list:
    """Get the most recent N entries from wellness log."""
    data = load_wellness_log()
    entries = data.get("entries", [])
    
    # Return last N entries
    return entries[-days:] if len(entries) > 0 else []


class WellnessAssistant(Agent):
    def __init__(self) -> None:
        # Load previous check-ins for context
        recent_entries = get_recent_entries(days=2)
        context_note = ""
        
        if recent_entries:
            last_entry = recent_entries[-1]
            context_note = f"\n\nIMPORTANT CONTEXT: Last check-in was on {last_entry.get('date', 'recently')}. User reported mood as '{last_entry.get('mood', 'not specified')}' with energy level {last_entry.get('energy_level', 'not specified')}."
            
            if len(recent_entries) > 1:
                prev_entry = recent_entries[-2]
                context_note += f" Previous session: mood was '{prev_entry.get('mood', 'not specified')}'."
        
        super().__init__(
            instructions=f"""You are a supportive Health & Wellness Voice Companion. Your role is to conduct daily check-ins with users about their mental and physical wellness in a warm, non-judgmental way.

CRITICAL GUIDELINES:
- You are NOT a medical professional or therapist
- NEVER diagnose conditions or provide medical advice
- Keep conversations supportive, realistic, and grounded
- This is a daily wellness check-in, not clinical assessment

YOUR CONVERSATION FLOW:
1. Greet warmly and reference previous check-ins if available
2. Ask about MOOD: "How are you feeling today?" (encourage both description and 1-10 scale)
3. Ask about ENERGY: "What's your energy like today?" (1-10 scale helpful)
4. Ask about STRESS/CONCERNS: "Anything stressing you out or on your mind?"
5. Ask about DAILY INTENTIONS: "What are 1-3 things you'd like to accomplish today?"
6. Offer SIMPLE, ACTIONABLE ADVICE:
   - Break large goals into smaller steps
   - Suggest short breaks or 5-minute walks
   - Encourage self-care activities
   - Provide grounding techniques
7. RECAP: Summarize their mood, energy, and main objectives
8. Ask: "Does this sound right?"
9. Call save_daily_checkin tool to record the session

CONVERSATION STYLE:
- Warm, conversational, and supportive
- Use natural voice-friendly language (no emojis or special formatting)
- Ask one question at a time
- Listen actively and validate feelings
- Keep responses concise and helpful
- Be encouraging without being dismissive

OFFERING ADVICE:
- Make suggestions small and achievable
- Examples: "take a 10-minute walk", "try a 2-minute breathing exercise", "break that task into 3 smaller steps"
- Always frame as gentle suggestions, never commands
- Validate their feelings before offering advice{context_note}""",
        )

    @function_tool
    async def get_previous_checkins(
        self,
        context: RunContext,
        days: Annotated[int, "Number of previous days to retrieve (default 2)"] = 2
    ):
        """Retrieve previous wellness check-in entries from the log.
        
        Use this tool to reference past check-ins and provide continuity in conversations.
        
        Args:
            days: Number of recent entries to retrieve (1-7)
        """
        logger.info(f"Retrieving previous {days} check-ins")
        
        entries = get_recent_entries(days=min(days, 7))
        
        if not entries:
            return "No previous check-ins found. This appears to be the user's first session."
        
        summary = f"Found {len(entries)} previous check-in(s):\n\n"
        for i, entry in enumerate(entries, 1):
            summary += f"Session {i} ({entry.get('date', 'unknown date')}):\n"
            summary += f"  - Mood: {entry.get('mood', 'not recorded')}\n"
            summary += f"  - Energy: {entry.get('energy_level', 'not recorded')}\n"
            summary += f"  - Objectives: {', '.join(entry.get('daily_objectives', ['none']))}\n"
            if entry.get('agent_summary'):
                summary += f"  - Summary: {entry['agent_summary']}\n"
            summary += "\n"
        
        return summary

    @function_tool
    async def save_daily_checkin(
        self,
        context: RunContext,
        mood: Annotated[str, "User's mood description"],
        energy_level: Annotated[str, "User's energy level (preferably as a scale like '7/10' or description)"],
        daily_objectives: Annotated[list[str], "List of 1-3 daily objectives or goals"],
        agent_summary: Annotated[str, "Brief summary of the check-in session"] = ""
    ):
        """Save the daily wellness check-in to the JSON log.
        
        Call this at the END of each check-in conversation, after gathering all information
        and providing a recap to the user.
        
        Args:
            mood: The user's self-reported mood (text description)
            energy_level: Energy level, ideally as a scale (e.g., "7/10") or description
            daily_objectives: List of things the user wants to accomplish
            agent_summary: Optional brief summary of the session
        """
        logger.info("Saving daily wellness check-in")
        
        # Create new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mood": mood,
            "energy_level": energy_level,
            "daily_objectives": daily_objectives,
            "agent_summary": agent_summary or f"User reported {mood} mood with {energy_level} energy. Goals: {', '.join(daily_objectives)}"
        }
        
        # Load existing data and append
        data = load_wellness_log()
        data["entries"].append(entry)
        
        # Save to file
        success = save_wellness_log(data)
        
        if success:
            return f"✓ Check-in saved successfully! Entry recorded for {entry['date']}. I'll remember this for our next conversation."
        else:
            return "There was an issue saving the check-in. The conversation data may not persist."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline
    session = AgentSession(
        # Speech-to-text
        stt=deepgram.STT(model="nova-3"),
        # Large Language Model
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech with Murf
        tts=murf.TTS(
                voice="en-US-matthew", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # Turn detection
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # Preemptive generation for faster responses
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
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session with WellnessAssistant
    await session.start(
        agent=WellnessAssistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
