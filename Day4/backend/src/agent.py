import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional
from dataclasses import dataclass, field

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

# Paths
CONTENT_PATH = Path(__file__).parent.parent / "shared-data" / "day4_tutor_content.json"
PROGRESS_PATH = Path(__file__).parent / "tutor_progress.json"


@dataclass
class UserData:
    """Stores data and agents to be shared across the session"""
    personas: dict[str, Agent] = field(default_factory=dict)
    prev_agent: Optional[Agent] = None
    current_concept: Optional[dict] = None
    tutor_content: list[dict] = field(default_factory=list)
    ctx: Optional[JobContext] = None

    def summarize(self) -> str:
        if self.current_concept:
            return f"Currently learning about: {self.current_concept['title']}"
        return "Active recall tutor - ready to help you learn!"


RunContext_T = RunContext[UserData]


def load_tutor_content() -> list[dict]:
    """Load tutor content from JSON file."""
    if not CONTENT_PATH.exists():
        logger.error(f"Content file not found: {CONTENT_PATH}")
        return []
    
    try:
        with open(CONTENT_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading tutor content: {e}")
        return []


def load_progress() -> dict:
    """Load learning progress from JSON file."""
    if not PROGRESS_PATH.exists():
        return {"sessions": [], "concept_mastery": {}}
    
    try:
        with open(PROGRESS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading progress: {e}")
        return {"sessions": [], "concept_mastery": {}}


def save_progress(data: dict) -> bool:
    """Save learning progress to JSON file."""
    try:
        with open(PROGRESS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving progress: {e}")
        return False


def log_session(concept_id: str, mode: str, score: Optional[int] = None, feedback: Optional[str] = None):
    """Log a learning session to progress file."""
    data = load_progress()
    
    # Add session entry
    session = {
        "timestamp": datetime.now().isoformat(),
        "concept_id": concept_id,
        "mode": mode
    }
    if score is not None:
        session["score"] = score
    if feedback:
        session["feedback"] = feedback
    
    data["sessions"].append(session)
    
    # Update concept mastery
    if concept_id not in data["concept_mastery"]:
        data["concept_mastery"][concept_id] = {
            "teach_back_scores": [],
            "average_score": None,
            "times_learned": 0,
            "times_quizzed": 0,
            "times_taught_back": 0,
            "last_activity": None
        }
    
    mastery = data["concept_mastery"][concept_id]
    mastery["last_activity"] = datetime.now().isoformat()
    
    if mode == "learn":
        mastery["times_learned"] += 1
    elif mode == "quiz":
        mastery["times_quizzed"] += 1
    elif mode == "teach_back":
        mastery["times_taught_back"] += 1
        if score is not None:
            mastery["teach_back_scores"].append(score)
            mastery["average_score"] = round(sum(mastery["teach_back_scores"]) / len(mastery["teach_back_scores"]), 1)
    
    save_progress(data)
    return True


class BaseAgent(Agent):
    """Base agent class with shared functionality for all learning agents."""
    
    async def on_enter(self) -> None:
        """Called when this agent becomes active."""
        agent_name = self.__class__.__name__
        logger.info(f"Entering {agent_name}")
        
        userdata: UserData = self.session.userdata
        if userdata.ctx and userdata.ctx.room:
            await userdata.ctx.room.local_participant.set_attributes({"agent": agent_name})
        
        # Preserve context from previous agent
        chat_ctx = self.chat_ctx.copy()
        
        if userdata.prev_agent:
            items_copy = self._truncate_chat_ctx(
                userdata.prev_agent.chat_ctx.items, keep_function_call=True
            )
            existing_ids = {item.id for item in chat_ctx.items}
            items_copy = [item for item in items_copy if item.id not in existing_ids]
            chat_ctx.items.extend(items_copy)
        
        chat_ctx.add_message(
            role="system",
            content=f"You are the {agent_name}. {userdata.summarize()}"
        )
        await self.update_chat_ctx(chat_ctx)
        self.session.generate_reply()
    
    def _truncate_chat_ctx(
        self,
        items: list,
        keep_last_n_messages: int = 6,
        keep_system_message: bool = False,
        keep_function_call: bool = False,
    ) -> list:
        """Truncate the chat context to keep the last n messages."""
        def _valid_item(item) -> bool:
            if not keep_system_message and item.type == "message" and item.role == "system":
                return False
            if not keep_function_call and item.type in ["function_call", "function_call_output"]:
                return False
            return True
        
        new_items = []
        for item in reversed(items):
            if _valid_item(item):
                new_items.append(item)
            if len(new_items) >= keep_last_n_messages:
                break
        new_items = new_items[::-1]
        
        while new_items and new_items[0].type in ["function_call", "function_call_output"]:
            new_items.pop(0)
        
        return new_items
    
    async def _transfer_to_agent(self, name: str, context: RunContext_T) -> Agent:
        """Transfer to another agent while preserving context."""
        userdata = context.userdata
        current_agent = context.session.current_agent
        next_agent = userdata.personas[name]
        userdata.prev_agent = current_agent
        
        return next_agent


class GreeterAgent(BaseAgent):
    """Initial agent that greets users and routes them to learning modes."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly Active Recall Coach greeter. Your role is to welcome users and help them choose a learning mode.

AVAILABLE MODES:
1. LEARN mode - I'll explain programming concepts to you
2. QUIZ mode - I'll ask you questions to test your understanding
3. TEACH-BACK mode - You explain concepts to me and I'll evaluate your understanding

AVAILABLE CONCEPTS (use these EXACT IDs in your function calls):
- "variables" for Variables
- "loops" for Loops
- "functions" for Functions
- "conditionals" for Conditionals

YOUR WORKFLOW:
1. Greet the user warmly
2. If they have previous progress, mention it
3. Ask which mode they'd like to try
4. Ask which concept they want to work on
5. Use the transfer tools with the EXACT concept ID

CRITICAL - When calling transfer functions:
- User says "variables" → use concept_id="variables"
- User says "loops" → use concept_id="loops"  
- User says "functions" → use concept_id="functions"
- User says "conditionals" → use concept_id="conditionals"
- NEVER use numbers like "1", "2" as concept IDs

CONVERSATION STYLE:
- Friendly and encouraging
- Keep it brief and clear
- Help them make a choice if they're unsure"""
        )
    
    @function_tool
    async def get_progress_summary(self, context: RunContext_T) -> str:
        """Show the user's learning progress summary."""
        data = load_progress()
        mastery = data.get("concept_mastery", {})
        
        if not mastery:
            return "You're just getting started! No progress recorded yet."
        
        summary = "Your learning progress:\n\n"
        for concept_id, stats in mastery.items():
            # Find concept title
            concept_title = concept_id
            userdata = context.userdata
            for c in userdata.tutor_content:
                if c['id'] == concept_id:
                    concept_title = c['title']
                    break
            
            summary += f"📚 {concept_title}:\n"
            if stats.get('average_score'):
                summary += f"  - Average teach-back score: {stats['average_score']}/100\n"
            summary += f"  - Learned {stats['times_learned']} times\n"
            summary += f"  - Quizzed {stats['times_quizzed']} times\n"
            summary += f"  - Taught back {stats['times_taught_back']} times\n\n"
        
        return summary
    
    @function_tool
    async def transfer_to_learn(
        self, 
        context: RunContext_T,
        concept_id: Annotated[str, "Concept ID: must be 'variables', 'loops', 'functions', or 'conditionals'"]
    ) -> Agent:
        """Transfer to Learn mode with Matthew voice to explain a concept."""
        userdata = context.userdata
        
        # Find the concept
        concept = next((c for c in userdata.tutor_content if c['id'] == concept_id), None)
        if not concept:
            await self.session.say(f"Sorry, I couldn't find the concept  '{concept_id}'. Valid concepts are: variables, loops, functions, conditionals.")
            return None
        
        userdata.current_concept = concept
        await self.session.say(f"Great! Connecting you to Matthew in Learn mode to teach you about {concept['title']}.")
        return await self._transfer_to_agent("learn", context)
    
    @function_tool
    async def transfer_to_quiz(
        self,
        context: RunContext_T,
        concept_id: Annotated[str, "Concept ID: must be 'variables', 'loops', 'functions', or 'conditionals'"]
    ) -> Agent:
        """Transfer to Quiz mode with Alicia voice to test knowledge."""
        userdata = context.userdata
        
        concept = next((c for c in userdata.tutor_content if c['id'] == concept_id), None)
        if not concept:
            await self.session.say(f"Sorry, I couldn't find the concept '{concept_id}'. Valid concepts are: variables, loops, functions, conditionals.")
            return None
        
        userdata.current_concept = concept
        await self.session.say(f"Perfect! Connecting you to Alicia in Quiz mode to test your knowledge of {concept['title']}.")
        return await self._transfer_to_agent("quiz", context)
    
    @function_tool
    async def transfer_to_teach_back(
        self,
        context: RunContext_T,
        concept_id: Annotated[str, "Concept ID: must be 'variables', 'loops', 'functions', or 'conditionals'"]
    ) -> Agent:
        """Transfer to Teach-Back mode with Ken voice for evaluation."""
        userdata = context.userdata
        
        concept = next((c for c in userdata.tutor_content if c['id'] == concept_id), None)
        if not concept:
            await self.session.say(f"Sorry, I couldn't find the concept '{concept_id}'. Valid concepts are: variables, loops, functions, conditionals.")
            return None
        
        userdata.current_concept = concept
        await self.session.say(f"Excellent! Connecting you to Ken in Teach-Back mode. You'll explain {concept['title']} to him.")
        return await self._transfer_to_agent("teach_back", context)


class LearnAgent(BaseAgent):
    """Teaching agent that explains concepts using Matthew voice."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Matthew, a patient and enthusiastic learning coach. Your role is to EXPLAIN programming concepts clearly.

YOUR APPROACH:
1. Introduce yourself: "Hi, I'm Matthew, your learning coach!"
2. Explain the current concept using the summary provided in the context
3. Break down complex ideas into simple terms
4. Give practical examples and analogies
5. Ask if they have questions
6. When ready, offer to switch to quiz mode or teach-back mode

TEACHING STYLE:
- Clear and beginner-friendly
- Use real-world analogies
- Provide code examples when helpful
- Be encouraging and patient

REMEMBER: Your job is to TEACH, not test."""
        )
    
    @function_tool
    async def transfer_to_quiz(self, context: RunContext_T) -> Agent:
        """Switch to Quiz mode to test understanding of the SAME concept."""
        userdata = context.userdata
        if not userdata.current_concept:
            return None
        
        log_session(userdata.current_concept['id'], "learn")
        await self.session.say(f"Great! Let's test your understanding. Connecting you to Alicia in Quiz mode.")
        return await self._transfer_to_agent("quiz", context)
    
    @function_tool
    async def transfer_to_teach_back(self, context: RunContext_T) -> Agent:
        """Switch to Teach-Back mode so user can explain the SAME concept."""
        userdata = context.userdata
        if not userdata.current_concept:
            return None
        
        log_session(userdata.current_concept['id'], "learn")
        await self.session.say(f"Excellent! Now let's see if you can teach it back. Connecting you to Ken.")
        return await self._transfer_to_agent("teach_back", context)


class QuizAgent(BaseAgent):
    """Quiz agent that asks questions using Alicia voice."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Alicia, an encouraging quiz master. Your role is to TEST users' understanding.

YOUR APPROACH:
1. Introduce yourself: "Hi, I'm Alicia, your quiz coach!"
2. Start with the sample question from the concept
3. Provide feedback: clarify if wrong, praise if correct
4. Ask follow-up questions to deepen understanding
5. When ready, offer to switch modes

QUIZ STYLE:
- Start easier, build to harder questions
- Give constructive feedback
- Explain WHY answers are correct/incorrect
- Be encouraging even when they struggle

REMEMBER: Your job is to TEST, not teach. If struggling, suggest Learn mode."""
        )
    
    @function_tool
    async def transfer_to_learn(self, context: RunContext_T) -> Agent:
        """Switch to Learn mode if user needs more explanation."""
        userdata = context.userdata
        if not userdata.current_concept:
            return None
        
        log_session(userdata.current_concept['id'], "quiz")
        await self.session.say(f"No problem! Let's review the concept. Connecting you to Matthew in Learn mode.")
        return await self._transfer_to_agent("learn", context)
    
    @function_tool
    async def transfer_to_teach_back(self, context: RunContext_T) -> Agent:
        """Switch to Teach-Back mode so user can explain the concept."""
        userdata = context.userdata
        if not userdata.current_concept:
            return None
        
        log_session(userdata.current_concept['id'], "quiz")
        await self.session.say(f"Great job! Now let's see if you can teach it back. Connecting you to Ken.")
        return await self._transfer_to_agent("teach_back", context)


class TeachBackAgent(BaseAgent):
    """Evaluation agent that asks users to teach back concepts using Ken voice."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Ken, a thoughtful evaluator. Your role is to have users TEACH concepts back and evaluate their understanding.

YOUR APPROACH:
1. Introduce yourself: "Hi, I'm Ken, your evaluation coach!"
2. Ask the user to explain the current concept in their own words
3. Listen to their COMPLETE explanation without interrupting
4. Evaluate: Was it complete? Accurate? Clear?
5. Provide a score (0-100) and constructive feedback
6. Use the score_explanation tool to record
7. Offer to try again or switch modes

EVALUATION STYLE:
- Be patient, let them finish
- Highlight what they did well first
- Gently correct misconceptions
- Give specific, actionable feedback

SCORING GUIDE:
- 90-100: Excellent, all key points covered
- 75-89: Good, minor gaps
- 60-74: Decent, missing depth
- 40-59: Partial understanding
- 0-39: Need review

REMEMBER: Be supportive but honest."""
        )
    
    @function_tool
    async def score_explanation(
        self,
        context: RunContext_T,
        score: Annotated[int, "Score from 0-100"],
        feedback: Annotated[str, "Specific constructive feedback"]
    ) -> str:
        """Score the user's teach-back explanation and log it."""
        userdata = context.userdata
        if not userdata.current_concept:
            return "No concept is currently active."
        
        concept_id = userdata.current_concept['id']
        concept_title = userdata.current_concept['title']
        score = max(0, min(100, score))
        
        log_session(concept_id, "teach_back", score=score, feedback=feedback)
        return f"✓ Recorded your teach-back score for {concept_title}: {score}/100. {feedback}"
    
    @function_tool
    async def transfer_to_learn(self, context: RunContext_T) -> Agent:
        """Switch to Learn mode to review the concept."""
        userdata = context.userdata
        if not userdata.current_concept:
            return None
        
        await self.session.say(f"Let's review the concept together. Connecting you to Matthew in Learn mode.")
        return await self._transfer_to_agent("learn", context)
    
    @function_tool
    async def transfer_to_quiz(self, context: RunContext_T) -> Agent:
        """Switch to Quiz mode to practice more."""
        userdata = context.userdata
        if not userdata.current_concept:
            return None
        
        await self.session.say(f"Let's practice with some questions. Connecting you to Alicia in Quiz mode.")
        return await self._transfer_to_agent("quiz", context)


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    
    # Load tutor content
    tutor_content = load_tutor_content()
    if not tutor_content:
        logger.error("Failed to load tutor content! Check shared-data/day4_tutor_content.json")
    
    # Create shared userdata
    userdata = UserData(tutor_content=tutor_content, ctx=ctx)
    
    # Create all agent personas
    greeter = GreeterAgent()
    learn = LearnAgent()
    quiz = QuizAgent()
    teach_back = TeachBackAgent()
    
    # Store in userdata for handoffs
    userdata.personas = {
        "greeter": greeter,
        "learn": learn,
        "quiz": quiz,
        "teach_back": teach_back
    }
    
    # Set up voice AI pipeline
    session = AgentSession[UserData](
        userdata=userdata,
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
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
        logger.info(f"Usage: {summary}")
    
    ctx.add_shutdown_callback(log_usage)
    
    # Start the session with GreeterAgent
    await session.start(
        agent=greeter,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
