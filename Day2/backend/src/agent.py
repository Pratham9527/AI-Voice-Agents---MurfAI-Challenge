import logging
import json
import os
from typing import Annotated, Literal

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    tokenize,
    function_tool,
)
from livekit.plugins import murf, deepgram, google
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env")

logger = logging.getLogger("barista-agent")

# --- JSON HELPER ---
def save_order(data):
    with open("order.json", "w") as f:
        json.dump(data, f, indent=2)

# --- MAIN AGENT ---
class BaristaAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
                You are a friendly barista at 'Neon Grind Coffee'.
                Your goal is to take a complete coffee order.
                
                You MUST obtain these 4 fields:
                1. Drink Type (e.g. Latte, Cappuccino)
                2. Size (Small, Medium, Large)
                3. Milk Preference (Whole, Oat, Almond, None)
                4. Name for the order.
                
                Ask clarifying questions if any information is missing.
                
                IMPORTANT: 
                - Call 'update_order' every time you get new info.
                - Do NOT stop asking until the tool returns "Order Saved".
                - Once saved, confirm with the user and say goodbye.
            """
        )
        # Memory
        self.order_state = {
            "drinkType": None,
            "size": None,
            "milk": None,
            "extras": [],
            "name": None
        }

    # --- THE TOOL ---
    # KEY FIX 1: Added 'async' keyword (Fixes the 'str object can't be awaited' error)
    @function_tool
    async def update_order(
        self,
        drink_type: Annotated[str, "Type of drink"] = None,
        # KEY FIX 2: Changed to str to be forgiving (Fixes the 'Validation Error')
        size: Annotated[str, "Size (Small, Medium, Large)"] = None,
        milk: Annotated[str, "Milk preference"] = None,
        extras: Annotated[str, "Any extras"] = None,
        name: Annotated[str, "Customer Name"] = None,
    ) -> str:
        """Update order details. Call this whenever the user provides info."""
        
        # Update State (Robust checks)
        if drink_type: self.order_state["drinkType"] = drink_type
        if size and size in ["Small", "Medium", "Large"]: self.order_state["size"] = size
        if milk: self.order_state["milk"] = milk
        if name: self.order_state["name"] = name
        
        if extras and extras not in self.order_state["extras"]:
            self.order_state["extras"].append(extras)

        # Check Completion
        is_complete = all([
            self.order_state["drinkType"],
            self.order_state["size"],
            self.order_state["milk"],
            self.order_state["name"]
        ])

        # Save if done
        if is_complete:
            save_order(self.order_state)
            return f"Order Saved! Final State: {self.order_state}. Tell user it's confirmed."
        
        return f"Updated. Current State: {self.order_state}. Ask for missing fields."


# --- ENTRYPOINT ---
async def entrypoint(ctx: JobContext):
    await ctx.connect()

    # Day 1 Setup Style (Proven to work)
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
    )

    # Start the agent (Tool is included inside BaristaAgent class)
    await session.start(agent=BaristaAgent(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))