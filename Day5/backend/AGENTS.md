# AGENTS.md - Day 5: Razorpay SDR Voice Agent

This is a LiveKit Agents project implementing a **Sales Development Representative (SDR)** voice agent for Razorpay. The agent answers FAQ questions, captures lead information naturally, and generates verbal summaries.

## Overview

Day 5's agent uses a **single-agent pattern** with function tools to:
- Answer product/pricing questions using FAQ search
- Collect lead information conversationally  
- Generate verbal summaries at call end
- Store leads in a master database

### Key Features

1. **SDR Persona** - Warm, professional Sales Development Representative
2. **FAQ System** - Keyword-based search across 15 Razorpay FAQs
3. **Lead Capture** - Natural collection of 7 key prospect fields
4. **Verbal Summary** - Auto-generated summary at end of call
5. **Master Database** - All leads saved to `leads/leads_database.json`

## Project Structure

This Python project uses the `uv` package manager. You should always use `uv` to install dependencies, run the agent, and run tests.

### Key Files

```
Day5/backend/
├── src/
│   ├── agent.py              # Main SDR agent with tools
│   ├── faq_handler.py         # FAQ search with keyword matching
│   └── lead_capture.py        # Lead data collection & storage
├── data/
│   └── company_faq.json       # Razorpay FAQ database (15 FAQs)
├── leads/
│   └── leads_database.json    # Master leads database
└── .env                       # Environment variables
```

**Important**: Unlike Day 4's multi-agent pattern, this uses a single agent with three function tools.

## Company FAQ Data

Razorpay FAQ data is defined in `data/company_faq.json`:

```json
{
  "company": {
    "name": "Razorpay",
    "tagline": "Power your finance, grow your business",
    "description": "..."
  },
  "products": [
    {
      "name": "Payment Gateway",
      "description": "...",
      "keywords": ["payment", "gateway", "online"]
    }
  ],
  "faqs": [
    {
      "id": "faq_001",
      "question": "What does Razorpay do?",
      "answer": "...",
      "category": "general",
      "keywords": ["what", "does", "razorpay", "product"]
    }
  ],
  "pricing": {...}
}
```

To add new FAQs:
1. Add a new object to the `faqs` array
2. Include: `id`, `question`, `answer`, `category`, `keywords`
3. Restart the agent (FAQ is preloaded)

## Lead Capture System

All leads are saved to `leads/leads_database.json`:

```json
{
  "leads": [
    {
      "timestamp": "2025-11-26T18:30:00+05:30",
      "name": "Rahul Sharma",
      "company": "TechStartup India",
      "email": "rahul@techstartup.in",
      "role": "CTO",
      "use_case": "payment gateway for SaaS product",
      "team_size": "15",
      "timeline": "soon"
    }
  ]
}
```

### Lead Fields

The agent collects 7 key fields:
- **name** - Prospect's full name
- **company** - Company name
- **email** - Contact email (validated format)
- **role** - Job title/position
- **use_case** - What they want to use Razorpay for
- **team_size** - Team size (e.g., "5", "10-20", "50+")
- **timeline** - When they plan to start: "now", "soon", or "later"

## Agent Tools

The agent has 3 function tools:

### 1. `search_faq(query)`

**Purpose**: Answer user questions from FAQ database

**When to use**:
- User asks about products ("What does Razorpay do?")
- Pricing questions ("What's your pricing?")
- Technical details ("Do you support UPI?")
- Integration questions ("How long does integration take?")

**How it works**:
- Simple keyword matching algorithm
- Scores FAQs based on keyword matches
- Returns best matching answer
- Falls back to "connect with team" if no match

### 2. `save_lead_field(field_name, value)`

**Purpose**: Store lead information as it's collected

**When to use**:
- User shares their name, company, email, etc.
- Call it immediately when information is provided
- Don't wait to collect all fields at once

**Example**:
```python
# User says: "I'm Rahul from TechStartup"
save_lead_field("name", "Rahul")
save_lead_field("company", "TechStartup")
```

**Validation**:
- Email format validated automatically
- Empty/whitespace values rejected

### 3. `end_call_and_summarize()`

**Purpose**: Generate verbal summary and save lead to database

**When to use**:
- User says "that's all", "thanks", "goodbye"
- Conversation naturally concludes
- Enough information collected

**What it does**:
1. Generates human-readable verbal summary
2. Saves complete lead to `leads_database.json`
3. Professional closing with follow-up expectations

## SDR Persona & Instructions

The agent follows a consultative SDR approach:

### Conversation Flow

```
1. OPENING (0-30s)
   ├─ Warm greeting
   ├─ "What brings you here today?"
   └─ "Tell me about your business"

2. DISCOVERY (Understanding)
   ├─ Listen to pain points
   ├─ Ask clarifying questions
   └─ Build rapport

3. EDUCATE (Answer questions)
   ├─ User asks → search_faq tool
   ├─ Provide clear answers
   └─ Don't make up info

4. QUALIFY (Collect info)
   ├─ Naturally weave questions
   ├─ save_lead_field as info shared
   └─ Not interrogation-style

5. CLOSE (End call)
   ├─ User signals done
   ├─ end_call_and_summarize tool
   └─ Professional closing
```

### Key Personality Traits

- **Friendly & Warm**: Not robotic or scripted
- **Consultative**: Understand needs before pitching
- **Curious**: Genuinely interested in their business
- **Helpful**: Provide value even if not a fit
- **Natural**: Conversational, not a questionnaire

### Guidelines

✓ **DO**:
- Ask one question at a time
- Use tools (search_faq, save_lead_field)
- Listen more than talk early on
- Be conversational and natural
- Show enthusiasm without overselling

✗ **DON'T**:
- Ask all questions at once
- Be pushy or aggressive
- Make up product details
- End call abruptly
- Forget to save information

## FAQ Keyword Matching

The `faq_handler.py` implements simple keyword matching:

### Scoring Algorithm

```python
score = 0

# Keyword matches (high weight)
score += keyword_matches * 3.0

# Question text matches (medium weight)  
score += question_word_matches * 2.0

# Answer text matches (low weight)
score += answer_word_matches * 0.5

# Exact phrase match (bonus)
if query in question:
    score += 10.0
```

### Why Keyword Matching?

- **Fast**: No API calls or embeddings needed
- **Simple**: Easy to understand and debug
- **Sufficient**: Works well for 15 well-structured FAQs
- **Preloaded**: FAQ data loaded during prewarm for instant responses

## Running the Agent

### Development Mode

```bash
cd Day5/backend
python src/agent.py dev
```

This starts the agent on localhost and prints a connection URL.

### Testing Modules Individually

Test FAQ handler:
```bash
python src/faq_handler.py
```

Test lead capture:
```bash
python src/lead_capture.py
```

### Voice Configuration

The agent uses **Raveena** voice (Indian English) for authenticity:

```python
tts=murf.TTS(
    voice="en-IN-raveena",  # Indian English
    style="Conversation",
    text_pacing=True
)
```

## Prewarm Pattern

The `prewarm()` function loads resources before sessions start:

```python
def prewarm(proc: JobProcess):
    # Load VAD model
    proc.userdata["vad"] = silero.VAD.load()
    
    # Load FAQ handler (from JSON)
    faq_handler = create_faq_handler(str(DATA_DIR))
    
    # Initialize lead capture system
    lead_capture = create_lead_capture(str(LEADS_DIR))
```

**Benefits**:
- FAQ data preloaded → instant responses
- No cold start latency
- Resources ready before first user connects

## Important Design Decisions

### Single Agent vs Multi-Agent

**Day 4** used multi-agent handoff for different learning modes.

**Day 5** uses single agent because:
- SDR flow is linear (not branching modes)
- Tools handle complexity (FAQ, lead capture)
- Simpler to maintain for this use case
- No voice changes needed

### Master Database vs Individual Files

All leads stored in one `leads_database.json` file:

**Pros**:
- Single source of truth
- Easy to export and analyze
- Simple append-only structure
- No file management needed

**Cons**:
- Could grow large (use DB for production)
- Manual concurrent access handling

### Verbal Summary Only

Summary is spoken, not saved to text file:

**Why**:
- More natural for voice interaction
- Lead data already in database
- Immediate feedback to user
- Reduces file clutter

## Extending the System

### Adding More FAQs

Edit `data/company_faq.json`:

```json
{
  "id": "faq_016",
  "question": "Do you offer refunds?",
  "answer": "...",
  "category": "pricing",
  "keywords": ["refund", "money", "back", "return"]
}
```

Restart agent to load new FAQs.

### Adding Lead Scoring

Modify `lead_capture.py` to add scoring:

```python
def calculate_lead_score(self) -> int:
    """Calculate lead score based on fields."""
    score = 0
    
    if self.get_field('timeline') == 'now':
        score += 50
    if self.get_field('team_size') and int(self.get_field('team_size')) > 20:
        score += 30
    # ... more scoring logic
    
    return score
```

### CRM Integration

Add tool to push lead to CRM:

```python
@function_tool
async def push_to_crm() -> str:
    """Push collected lead to Salesforce/HubSpot."""
    # API call to CRM
    # ...
    return "Lead synced to CRM!"
```

## Testing

### Manual Testing Flow

1. Start agent: `python src/agent.py dev`
2. Join voice room via printed URL
3. Test scenarios:
   - Ask FAQ questions → verify correct answers
   - Share lead info → verify saved correctly
   - Say "that's all" → verify summary & database update
4. Check `leads/leads_database.json` for saved lead

### Automated Tests

```bash
uv run pytest
```

Test cases to add:
- FAQ keyword matching accuracy
- Email validation
- Lead database persistence
- Summary generation

## Deployment

See the Dockerfile for production deployment configuration. The agent is designed to run on LiveKit Cloud.

### Environment Variables

Required in `.env`:
```
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
LIVEKIT_URL=
MURF_API_KEY=
GOOGLE_API_KEY=
DEEPGRAM_API_KEY=
```

## Code Formatting

Maintain code quality with ruff:

```bash
uv run ruff format  # Format code
uv run ruff check   # Lint code
```

## LiveKit Documentation

LiveKit Agents is a fast-evolving project. Always refer to the latest documentation:
- [Function Tools](https://docs.livekit.io/agents/build/tools/)
- [Building Agents](https://docs.livekit.io/agents/build/)
- [Prewarm Pattern](https://docs.livekit.io/agents/build/turns/vad/#prewarm)

### LiveKit Docs MCP Server

For easy documentation access:

```bash
gemini mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

## Key Learnings from Day 5

1. **Voice agents need natural prompts** - Avoid robotic questionnaire style
2. **Tool calling should be invisible** - User shouldn't notice when tools are used
3. **Lead qualification is conversational** - Weave questions naturally into dialogue
4. **Prewarm improves UX** - Preload FAQ data for instant responses
5. **Verbal summaries feel better** - More natural than silent data collection
6. **Simple keyword search works** - Don't over-engineer with embeddings for small FAQ sets

## Future Improvements

- **Semantic search** - Use embeddings for better FAQ matching
- **CRM integration** - Auto-sync leads to Salesforce/HubSpot  
- **Lead scoring** - Score based on signals (timeline, team size)
- **Email automation** - Send follow-up emails automatically
- **Multi-language** - Support Hindi, Tamil, etc.
- **Analytics dashboard** - Visualize lead pipeline

---

**Built for the Murf AI Voice Agents Challenge - Day 5** 🎙️💼
