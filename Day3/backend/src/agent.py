import logging
import json
from todoist_api_python.api import TodoistAPI
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


def get_todoist_api():
    """Get Todoist API client if token is configured."""
    api_key = os.getenv("TODOIST_API_KEY")
    if api_key:
        try:
            return TodoistAPI(api_key)
        except Exception as e:
            logger.error(f"Error initializing Todoist API: {e}")
            return None
    return None


def extract_numeric_score(text: str) -> float | None:
    """Extract numeric score from text like '7/10' or 'around 6' or just '8'."""
    if not text:
        return None
    
    import re
    # Try to find patterns like "7/10" or "7 out of 10"
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:/|out of)\s*10', str(text))
    if match:
        return float(match.group(1))
    
    # Try to find standalone numbers
    match = re.search(r'(\d+(?:\.\d+)?)', str(text))
    if match:
        num = float(match.group(1))
        # If number is already 0-10 scale, use it; otherwise assume 1-10
        return num if num <= 10 else None
    
    return None


def analyze_weekly_data(entries: list, days: int = 7) -> dict:
    """Analyze wellness data for the specified number of days.
    
    Returns dict with:
    - mood_avg: average mood score
    - energy_avg: average energy score
    - days_with_goals: count of days with objectives
    - total_days: total entries analyzed
    - total_objectives: total number of objectives set
    """
    from datetime import datetime, timedelta
    
    if not entries:
        return {
            "mood_avg": None,
            "energy_avg": None,
            "days_with_goals": 0,
            "total_days": 0,
            "total_objectives": 0
        }
    
    # Filter entries from last N days
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_entries = []
    
    for entry in entries:
        try:
            entry_date = datetime.fromisoformat(entry.get("timestamp", ""))
            if entry_date >= cutoff_date:
                recent_entries.append(entry)
        except:
            # If timestamp parsing fails, include it anyway
            recent_entries.append(entry)
    
    if not recent_entries:
        return {
            "mood_avg": None,
            "energy_avg": None,
            "days_with_goals": 0,
            "total_days": 0,
            "total_objectives": 0
        }
    
    # Extract mood scores
    mood_scores = []
    for entry in recent_entries:
        mood = entry.get("mood", "")
        score = extract_numeric_score(mood)
        if score is not None:
            mood_scores.append(score)
    
    # Extract energy scores
    energy_scores = []
    for entry in recent_entries:
        energy = entry.get("energy_level", "")
        score = extract_numeric_score(energy)
        if score is not None:
            energy_scores.append(score)
    
    # Count days with goals and total objectives
    days_with_goals = 0
    total_objectives = 0
    for entry in recent_entries:
        objectives = entry.get("daily_objectives", [])
        if objectives:
            days_with_goals += 1
            total_objectives += len(objectives)
    
    # Calculate averages
    mood_avg = sum(mood_scores) / len(mood_scores) if mood_scores else None
    energy_avg = sum(energy_scores) / len(energy_scores) if energy_scores else None
    
    return {
        "mood_avg": round(mood_avg, 1) if mood_avg else None,
        "energy_avg": round(energy_avg, 1) if energy_avg else None,
        "days_with_goals": days_with_goals,
        "total_days": len(recent_entries),
        "total_objectives": total_objectives
    }


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
9. TODOIST INTEGRATION (Optional): If user has stated objectives, offer to create Todoist tasks:
   - Ask: "Would you like me to add these to your Todoist so you can track them?"
   - Only call create_todoist_tasks if user explicitly agrees
   - If they agree, confirm: "Done! I've created N tasks in Todoist."
10. Call save_daily_checkin tool to record the session

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
- Validate their feelings before offering advice

WEEKLY REFLECTIONS:
- If user asks about trends, patterns, or "how they've been doing", use get_weekly_reflection tool
- Examples: "How has my mood been?", "Did I follow through?", "Show me my weekly summary", "How am I doing?"
- This provides supportive insights about mood, energy, and goal consistency
- Always present insights in an encouraging, non-judgmental way{context_note}""",
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
    async def get_weekly_reflection(
        self,
        context: RunContext,
        days: Annotated[int, "Number of days to analyze (default 7 for week)"] = 7
    ):
        """Analyze wellness data and provide insights about mood, energy, and goals.
        
        Call this when user asks questions like:
        - "How has my mood been this week?"
        - "Did I follow through on my goals?"
        - "Show me my weekly summary"
        - "How am I doing?"
        
        Args:
            days: Number of days to analyze (default 7 for past week)
        """
        logger.info(f"Analyzing {days} days of wellness data")
        
        data = load_wellness_log()
        entries = data.get("entries", [])
        
        # Check if we have enough data
        if len(entries) < 3:
            return f"I only have {len(entries)} check-in(s) on record so far. I need at least 3 check-ins to provide meaningful insights. Keep checking in daily, and soon I'll be able to show you patterns and trends!"
        
        # Analyze the data
        analysis = analyze_weekly_data(entries, days=days)
        
        # Build supportive summary
        time_label = "week" if days == 7 else f"{days} days"
        summary = f"Here's what I see from the past {time_label}:\\n\\n"
        
        # Mood summary
        if analysis["mood_avg"] is not None:
            mood_avg = analysis["mood_avg"]
            if mood_avg >= 7:
                mood_desc = "pretty good overall"
            elif mood_avg >= 5:
                mood_desc = "moderate, with ups and downs"
            else:
                mood_desc = "challenging lately"
            summary += f"📊 Mood: Averaging {mood_avg}/10 - that's {mood_desc}.\\n"
        else:
            summary += "📊 Mood: Not enough numeric data yet. Try using the 1-10 scale for better insights.\\n"
        
        # Energy summary
        if analysis["energy_avg"] is not None:
            energy_avg = analysis["energy_avg"]
            if energy_avg >= 7:
                energy_desc = "good energy levels"
            elif energy_avg >= 5:
                energy_desc = "moderate energy"
            else:
                energy_desc = "lower energy than usual"
            summary += f"⚡ Energy: Averaging {energy_avg}/10 - {energy_desc}.\\n"
        else:
            summary += "⚡ Energy: Not enough numeric data yet.\\n"
        
        # Goal consistency summary
        total_days = analysis["total_days"]
        days_with_goals = analysis["days_with_goals"]
        total_objectives = analysis["total_objectives"]
        
        if days_with_goals > 0:
            consistency_pct = (days_with_goals / total_days) * 100
            avg_objectives = total_objectives / days_with_goals
            
            if consistency_pct >= 80:
                consistency_desc = "excellent consistency"
            elif consistency_pct >= 50:
                consistency_desc = "pretty consistent"
            else:
                consistency_desc = "some goal-setting"
            
            summary += f"🎯 Goals: You set objectives on {days_with_goals} out of {total_days} days ({consistency_desc}). "
            summary += f"That's about {avg_objectives:.1f} goals per day on average.\\n"
        else:
            summary += f"🎯 Goals: No objectives set in the past {time_label}. It's okay - every day is a fresh start!\\n"
        
        # Supportive closing
        summary += "\\n"
        if analysis["mood_avg"] and analysis["mood_avg"] >= 6.5:
            summary += "You're doing well! Keep up the positive momentum. 😊"
        elif analysis["mood_avg"] and analysis["mood_avg"] < 5.5:
            summary += "I notice things have been tough. Remember to be kind to yourself - small steps count. 💙"
        else:
            summary += "Remember, wellness is a journey with ups and downs. You're making progress by showing up. 🌟"
        
        return summary

    @function_tool
    async def create_todoist_tasks(
        self,
        context: RunContext,
        task_list: Annotated[list[str], "List of tasks to create in Todoist"]
    ):
        """Create tasks in Todoist from the user's daily objectives.
        
        Only call this if the user explicitly agrees to create tasks in Todoist.
        Always ask for permission before calling this tool.
        
        Args:
            task_list: List of task descriptions to create
        """
        logger.info(f"Creating {len(task_list)} tasks in Todoist")
        
        api = get_todoist_api()
        if not api:
            return "Todoist is not configured. To use this feature, please set up your TODOIST_API_KEY."
        
        try:
            created_tasks = []
            for task_content in task_list:
                task = api.add_task(content=task_content)
                created_tasks.append(task.content)
                logger.info(f"Created Todoist task: {task.content}")
            
            return f"✓ Successfully created {len(created_tasks)} tasks in Todoist: {', '.join(created_tasks)}"
        except Exception as e:
            logger.error(f"Error creating Todoist tasks: {e}")
            return f"Sorry, I couldn't create tasks in Todoist. Error: {str(e)}"

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
