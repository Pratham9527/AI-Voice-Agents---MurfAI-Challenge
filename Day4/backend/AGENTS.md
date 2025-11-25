# AGENTS.md - Day 4: Active Recall Coach

This is a LiveKit Agents project implementing a **Teach-the-Tutor** active recall coach system. The agent helps users learn programming concepts through three interactive modes: **Learn**, **Quiz**, and **Teach-Back**.

## Overview

Day 4's agent uses a **multi-agent handoff pattern** where specialized agents handle different learning modes. Each agent has:
- A distinct personality and role
- A unique Murf voice (Matthew, Alicia, Ken)
- Specific tools for their mode
- Ability to hand off to other agents

### The Four Agents

1. **GreeterAgent** - Routes users to learning modes, shows progress
2. **LearnAgent** (Matthew voice) - Explains programming concepts
3. **QuizAgent** (Alicia voice) - Tests understanding with questions
4. **TeachBackAgent** (Ken voice) - Evaluates user explanations with LLM scoring

## Project Structure

This Python project uses the `uv` package manager. You should always use `uv` to install dependencies, run the agent, and run tests.

### Key Files

```
Day4/backend/
├── src/
│   ├── agent.py              # Main agent file with all 4 agents + handoff logic
│   └── tutor_progress.json   # Progress tracking (auto-created on first run)
├── shared-data/
│   └── day4_tutor_content.json  # Learning content for 4 concepts
└── .env                       # Environment variables (LIVEKIT_API_KEY, etc.)
```

**Important**: All agent code is in a single `agent.py` file. This includes:
- `BaseAgent` class with shared handoff functionality
- All 4 agent classes
- Progress tracking helpers
- Entry point and session setup

## Learning Content

Concepts are defined in `shared-data/day4_tutor_content.json`:

```json
[
  {
    "id": "variables",
    "title": "Variables",
    "summary": "Detailed explanation for teaching...",
    "sample_question": "What is a variable and why would you use one?"
  },
  // ... more concepts
]
```

To add new concepts:
1. Add a new object to the JSON array
2. Include: `id`, `title`, `summary`, `sample_question`
3. Restart the agent

## Progress Tracking

All learning sessions are logged to `src/tutor_progress.json`:

```json
{
  "sessions": [
    {
      "timestamp": "2025-11-25T07:30:00Z",
      "concept_id": "variables",
      "mode": "teach_back",
      "score": 85,
      "feedback": "Great explanation! You covered..."
    }
  ],
  "concept_mastery": {
    "variables": {
      "teach_back_scores": [65, 75, 85],
      "average_score": 75,
      "times_learned": 2,
      "times_quizzed": 3,
      "times_taught_back": 3,
      "last_activity": "2025-11-25T07:40:00Z"
    }
  }
}
```

The system tracks:
- **Sessions**: Chronological log of all activities
- **Concept Mastery**: Aggregated stats including teach-back scores and averages

## Agent Handoff Pattern

The system uses LiveKit's agent handoff pattern for seamless transitions:

### Flow Example

```
User connects → GreeterAgent
                    ↓
          "I want to learn about variables"
                    ↓
    [Greeter calls transfer_to_learn tool with concept_id="variables"]
                    ↓
                LearnAgent (Matthew voice)
                    ↓
          Explains variables concept
                    ↓
          "Ready to test your knowledge?"
                    ↓
    [Learn calls transfer_to_quiz tool]
                    ↓
                QuizAgent (Alicia voice)
                    ↓
          Asks questions, provides feedback
                    ↓
          "Let's see if you can teach it back"
                    ↓
    [Quiz calls transfer_to_teach_back tool]
                    ↓
            TeachBackAgent (Ken voice)
                    ↓
    Listens to explanation, scores with LLM (0-100)
```

### Context Preservation

When agents hand off:
1. Current agent calls a transfer function tool
2. Tool returns the next agent instance
3. New agent's `on_enter()` method:
   - Copies chat history from previous agent
   - Truncates to prevent token overflow (keeps last 6 messages)
   - Adds context about current concept
   - Generates initial greeting

### Mode Switching with Concept Choice

Users can switch modes at any time. Agents ask:
- "Would you like to continue with [current concept] or switch to a different topic?"

Options:
- **Same concept**: Mode changes, concept stays (e.g., Learn variables → Quiz variables)
- **New concept**: Both change (e.g., Quiz variables → Teach-back loops)

Tools support this via:
- `transfer_to_X()` - Switch mode, keep concept
- `switch_mode_and_concept(mode, concept_id)` - Switch both

## Agent Personalities & Instructions

### GreeterAgent

**Role**: Welcome and route users  
**Voice**: Default  
**Key Instructions**:
- Explain the three available modes
- Reference past performance if available
- Help user choose a mode and concept
- Use transfer tools to connect to specialists

### LearnAgent (Matthew)

**Role**: Teach concepts clearly  
**Voice**: `en-US-matthew` (Murf)  
**Key Instructions**:
- Explain concepts from the JSON summary
- Use beginner-friendly language
- Give examples and analogies
- Ask if they have questions
- Offer mode switching when ready
- Focus on TEACHING, not testing

### QuizAgent (Alicia)

**Role**: Test understanding  
**Voice**: `en-US-alicia` (Murf)  
**Key Instructions**:
- Ask questions based on sample_question
- Provide feedback on answers (correct/incorrect)
- Vary question difficulty
- Be encouraging but thorough
- Focus on TESTING, suggest Learn mode if struggling

### TeachBackAgent (Ken)

**Role**: Evaluate explanations  
**Voice**: `en-US-ken` (Murf)  
**Key Instructions**:
- Ask user to explain concept in their own words
- Listen to COMPLETE explanation without interrupting
- Evaluate on: completeness, accuracy, clarity
- Score 0-100 using LLM reasoning
- Provide specific, constructive feedback
- Log score and feedback to progress file

**Scoring Guide**:
- 90-100: Excellent, all key points covered
- 75-89: Good, minor gaps
- 60-74: Decent, missing depth
- 40-59: Partial understanding
- 0-39: Need review

## Running the Agent

### Development Mode

```bash
cd Day4/backend
python src/agent.py dev
```

This starts the agent on localhost and prints a connection URL.

### Testing the Agent

1. Start the agent in dev mode
2. Open the printed URL in your browser
3. Join the voice room
4. Test each flow:
   - Ask for different modes
   - Switch between modes
   - Test concept selection
   - Verify voices change (Matthew, Alicia, Ken)
   - Complete a teach-back and check score in `tutor_progress.json`

### Voice Configuration

Each agent can override the default TTS voice:

```python
class LearnAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            instructions="...",
            # Override happens here - but currently using session-level TTS
        )
```

**Note**: In the current implementation, voice switching between agents requires updating the session TTS configuration. See [LiveKit docs on agent voice overrides](https://docs.livekit.io/agents/build/agents-handoffs/#override-plugins).

## Important Design Patterns

### Handoffs and Workflows

Voice AI agents are highly sensitive to latency. This multi-agent design:
- Keeps each agent's instructions focused and concise
- Reduces irrelevant context in LLM requests
- Provides faster, more reliable responses
- Makes agents easier to maintain and extend

**Avoid**: Single agent with massive instructions covering all modes  
**Use**: Specialized agents with handoffs (as implemented)

### Tool Definitions

Each agent has focused tools for:
1. **Logging**: Record sessions to progress file
2. **Transferring (same concept)**: Switch mode, keep concept
3. **Switching (new concept)**: Change mode AND concept

Tools are clearly described so the LLM knows when to use them.

### Error Handling

- If concept_id not found, agents inform user and suggest listing concepts
- Progress file is auto-created if missing
- Content file must exist or agent logs error

## Extending the System

### Adding a New Concept

Edit `shared-data/day4_tutor_content.json`:

```json
{
  "id": "arrays",
  "title": "Arrays",
  "summary": "Arrays are collections that store multiple values...",
  "sample_question": "What is an array and when would you use one?"
}
```

### Adding a New Mode/Agent

1. Create new agent class extending `BaseAgent`
2. Define instructions and tools
3. Add voice override if needed
4. Register in `userdata.personas` dict
5. Add transfer tools in other agents

### Customizing Scoring

The `TeachBackAgent.score_explanation` tool accepts:
- `score` (0-100)
- `feedback` (string)

The LLM decides the score based on the instructions. You can:
- Adjust scoring criteria in instructions
- Add rubric details for more consistent scoring
- Implement additional validation logic

## LiveKit Documentation

LiveKit Agents is a fast-evolving project. Always refer to the latest documentation:
- [Agent Handoffs](https://docs.livekit.io/agents/build/agents-handoffs/)
- [Building Workflows](https://docs.livekit.io/agents/build/workflows/)
- [Tool Definitions](https://docs.livekit.io/agents/build/tools/)

### LiveKit Docs MCP Server

For easy documentation access, install the LiveKit MCP server:

```bash
gemini mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

## Testing

When possible, add tests for agent behavior:

```bash
uv run pytest
```

**TDD Approach**: When modifying agent behavior:
1. Write tests for desired behavior first
2. Iterate on implementation until tests pass
3. Ensures reliable, working agents

## Deployment

See the Dockerfile for production deployment configuration. The agent is designed to run on LiveKit Cloud.

## Code Formatting

Maintain code quality with ruff:

```bash
uv run ruff format  # Format code
uv run ruff check   # Lint code
```
