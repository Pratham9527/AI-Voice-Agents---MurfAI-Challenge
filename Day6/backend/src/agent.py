import logging
import os
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
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import our custom modules
import database

logger = logging.getLogger("fraud_agent")

load_dotenv(".env")

# Global state to hold the current case for the session (optional, but good for context)
# In a real scenario, we might store this in the agent instance or context.

FRAUD_AGENT_INSTRUCTIONS = """You are a Fraud Detection Representative for the Bank of Murf.
Your job is to verify a suspicious transaction with the customer.

YOUR PERSONA:
- Professional, calm, and reassuring.
- You take security seriously but are polite.
- You NEVER ask for full card numbers, PINs, or passwords.

CONVERSATION FLOW:
1. **Introduction**:
   - Introduce yourself as calling from the Bank of Murf Fraud Department.
   - Ask the user for their username to locate their file.

2. **Lookup & Verification**:
   - Use the `load_case_tool` with the provided username.
   - If found, say you have a transaction to verify, but first need to ask a security question.
   - Ask the `security_question` returned by the tool.
   - Verify the user's answer against the `security_answer`.
   - If the answer is WRONG: Politely apologize, say you cannot proceed, and use `update_case_tool` to mark as "verification_failed" and end the call.
   - If the answer is RIGHT: Thank them and proceed.

3. **Transaction Review**:
   - Read out the transaction details: Merchant, Amount, Time, and Card Ending (e.g., "card ending in 1234").
   - Ask: "Did you authorize this transaction?"

4. **Outcome**:
   - **If User Confirms (Yes)**:
     - Mark case as "confirmed_safe" using `update_case_tool`.
     - Tell the user the transaction is cleared and thank them.
   - **If User Denies (No)**:
     - Mark case as "confirmed_fraud" using `update_case_tool`.
     - Tell the user you have blocked the card and raised a dispute. Assure them they are not liable.

5. **Closing**:
   - Confirm the action taken.
   - Wish them a good day and end the call.

IMPORTANT:
- Always use the tools to load and update data.
- Be concise.
- If the user asks for the username, say "For this demo, you can say 'John' or 'Alice'."
"""

def prewarm(proc: JobProcess):
    """Prewarm function to initialize database and load models."""
    logger.info("🔥 Prewarming Fraud Agent...")
    
    # Initialize Database
    try:
        database.init_db()
        database.seed_db()
        logger.info("✅ Database initialized and seeded")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")

    # Load VAD model
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("✅ VAD loaded")


async def entrypoint(ctx: JobContext):
    """Main entry point for the Fraud Agent."""
    
    ctx.log_context_fields = {"room": ctx.room.name}
    
    class FraudAgent(Agent):
        """Fraud Agent with database tools"""
        
        def __init__(self):
            super().__init__(instructions=FRAUD_AGENT_INSTRUCTIONS)
            self.current_case = None
        
        @function_tool
        async def load_case_tool(
            self,
            username: Annotated[str, "The username provided by the user"]
        ) -> str:
            """Load the fraud case details for a given username."""
            logger.info(f"Loading case for: {username}")
            case = database.get_case(username)
            if case:
                self.current_case = case
                # Return details to the LLM so it can speak them and verify the security answer
                return (f"Case found. Details: {case}. "
                        f"Security Question: '{case['security_question']}'. "
                        f"Expected Answer: '{case['security_answer']}'. "
                        "Ask the security question now.")
            else:
                return "Case not found. Please ask the user to repeat their username (valid demo users: John, Alice)."

        @function_tool
        async def update_case_tool(
            self,
            status: Annotated[str, "The new status: 'confirmed_safe', 'confirmed_fraud', or 'verification_failed'"],
            outcome_note: Annotated[str, "A brief note about the outcome"]
        ) -> str:
            """Update the fraud case status in the database."""
            if not self.current_case:
                return "No case currently loaded."
            
            username = self.current_case['username']
            database.update_case(username, status, outcome_note)
            return f"Case for {username} updated to {status}. You may now end the call."

    # Create agent instance
    fraud_agent = FraudAgent()
    
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
        agent=fraud_agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    await ctx.connect()
    
    logger.info("🎙️ Fraud Alert Agent is live!")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
