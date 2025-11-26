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
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import our custom modules
from faq_handler import create_faq_handler, FAQHandler
from lead_capture import create_lead_capture, LeadCapture

logger = logging.getLogger("sdr_agent")

load_dotenv(".env")

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
LEADS_DIR = Path(__file__).parent.parent / "leads"

# Global instances (loaded during prewarm)
faq_handler: FAQHandler = None
lead_capture: LeadCapture = None


SDR_INSTRUCTIONS = """You are a Sales Development Representative (SDR) for Razorpay, India's leading full-stack financial solutions company.

YOUR PERSONA:
- Friendly, warm, and professional
- Consultative approach (understand needs before pitching)
- Genuinely curious about the prospect's business
- Knowledgeable about Razorpay products but not pushy
- Natural conversationalist (not robotic)

YOUR MAIN GOALS:
1. Build rapport with the prospect
2. Understand their needs and pain points
3. Answer their questions about Razorpay
4. Collect lead information naturally
5. Set expectations for next steps

CONVERSATION FLOW:

**OPENING (First 20-30 seconds):**
- Greet warmly: "Hi! I'm excited to chat with you about Razorpay!"
- Ask discovery questions:
  - "What brings you here today?"
  - "What are you currently working on?"
  - "Tell me a bit about your business"

**DISCOVERY (Build understanding):**
- Listen actively to their needs
- Ask clarifying questions
- Show genuine interest
- Examples:
  - "That's interesting! What challenges are you facing with payments right now?"
  - "How are you currently handling payments?"
  - "What's most important to you - ease of integration, pricing, or support?"

**EDUCATE (Answer questions):**
- When they ask about Razorpay, use the search_faq tool
- Provide clear, helpful answers
- Don't make up information - use the FAQ
- If you don't know something, be honest and offer to connect them with an expert

**QUALIFY (Collect lead info naturally):**
- Weave questions into the conversation naturally
- DON'T interrogate - make it conversational
- Collect these fields using save_lead_field tool:
  * name - "By the way, what's your name?"
  * company - "What company are you with?"
  * email - "What's the best email to reach you at?"
  * role - "What's your role at [company]?"
  * use_case - "What would you primarily use Razorpay for?"
  * team_size - "How large is your team?"
  * timeline - "When are you looking to get started?" (capture as: now/soon/later)

**CLOSING:**
- When they say "that's all", "thanks", "goodbye", or conversation concludes
- Use end_call_and_summarize tool
- Thank them warmly
- Set expectations: "Our team will reach out within 24 hours"

IMPORTANT GUIDELINES:
✓ Be conversational and natural (not a questionnaire)
✓ Listen more than you talk early on
✓ Use the tools: search_faq for answers, save_lead_field for info, end_call_and_summarize when done
✓ Be helpful even if they're just exploring
✓ Show enthusiasm about Razorpay but don't oversell
✓ If they're clearly not a fit, be polite and helpful anyway

✗ Don't ask all questions at once
✗ Don't be pushy or aggressive
✗ Don't make up product details - use search_faq
✗ Don't end the call abruptly
✗ Don't forget to save information as you collect it

CONVERSATION STYLE:
- Short, natural responses (2-3 sentences at a time)
- Ask one question at a time
- Show empathy and understanding
- Be professional but friendly
- Match their energy level

Remember: You're helping them explore if Razorpay is right for them. Focus on understanding their needs first, then positioning Razorpay as the solution."""


def prewarm(proc: JobProcess):
    """Prewarm function to load FAQ and initialize lead capture before sessions start."""
    global faq_handler, lead_capture
    
    logger.info("🔥 Prewarming SDR agent...")
    
    # Load VAD model
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("✅ VAD loaded")
    
    # Load FAQ handler
    try:
        faq_handler = create_faq_handler(str(DATA_DIR))
        logger.info(f"✅ FAQ handler loaded with {len(faq_handler.faq_data.get('faqs', []))} FAQs")
    except Exception as e:
        logger.error(f"❌ Failed to load FAQ handler: {e}")
    
    # Initialize lead capture
    try:
        lead_capture = create_lead_capture(str(LEADS_DIR))
        logger.info("✅ Lead capture system initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize lead capture: {e}")


async def entrypoint(ctx: JobContext):
    """Main entry point for the SDR agent."""
    global lead_capture
    
    ctx.log_context_fields = {"room": ctx.room.name}
    
    # Start new lead capture for this session
    if lead_capture:
        lead_capture.start_new_lead()
    
    # Create SDR agent that extends Agent with tools
    class SDRAgent(Agent):
        """SDR Agent with embedded tools"""
        
        def __init__(self):
            super().__init__(instructions=SDR_INSTRUCTIONS)
        
        @function_tool
        async def search_faq_tool(
            self,
            query: Annotated[str, "User's question about Razorpay products, pricing, or services"]
        ) -> str:
            """Search the FAQ database for answers to user questions."""
            global faq_handler
            if not faq_handler:
                return "I apologize, I'm having trouble accessing our FAQ data right now."
            answer = faq_handler.get_best_answer(query)
            if answer:
                return answer
            else:
                return "That's a great question! I don't have specific details on that in my FAQ, but I'd love to connect you with our team who can provide more information."
        
        @function_tool
        async def save_lead_field_tool(
            self,
            field_name: Annotated[str, "Field name: 'name', 'company', 'email', 'role', 'use_case', 'team_size', or 'timeline'"],
            value: Annotated[str, "The value for this field"]
        ) -> str:
            """Save a piece of lead information when the user provides it."""
            global lead_capture
            if not lead_capture:
                return "Lead capture system not initialized."
            success = lead_capture.add_field(field_name, value)
            if success:
                return f"✓ Noted: {field_name} = {value}"
            else:
                return f"I couldn't save that information. Please try again."
        
        @function_tool
        async def end_call_and_summarize_tool(self) -> str:
            """End the call and generate a summary of the lead."""
            global lead_capture
            if not lead_capture:
                return "Unable to generate summary."
            summary = lead_capture.generate_summary()
            saved = lead_capture.save_to_database()
            if saved:
                return f"Thank you so much for your time! Here's what I have: {summary} Someone from our team will reach out to you soon. Have a great day!"
            else:
                return f"Thank you for your time! {summary} I'll make sure someone from our team follows up with you. Have a great day!"
    
    # Create agent instance
    sdr_agent = SDRAgent()
    
    # Set up voice AI pipeline with Murf TTS
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-alicia",  # Using known working voice
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
    
    # Start the session with the SDR agent
    await session.start(
        agent=sdr_agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    await ctx.connect()
    
    logger.info("🎙️ Razorpay SDR agent is live!")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
