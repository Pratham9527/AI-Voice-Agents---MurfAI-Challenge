# Todoist MCP Integration Guide

## Overview

Day 3 wellness companion now includes **optional** Todoist integration, allowing users to convert their daily wellness objectives into actionable Todoist tasks.

## Setup Instructions

### 1. Create Todoist Account (Free)
- Visit https://todoist.com
- Sign up for a free account (or log in if you already have one)

### 2. Get Your API Token
- Go to https://todoist.com/app/settings/integrations/developer
- Scroll to **API token** section
- Click "Copy to clipboard"

### 3. Add Token to Environment
Edit `Day3/backend/.env` and add:

```env
# Todoist MCP Integration (optional)
TODOIST_API_KEY=your_copied_api_token_here
```

### 4. Restart the Agent
```bash
cd Day3/backend
# Stop current agent (Ctrl+C if running)
uv run python src/agent.py dev
```

## How It Works

### User Experience

**During Check-In:**
```
User: "I want to finish my report, take a walk, and call my family"

Agent: "Those sound like great goals! Would you like me to add 
        these to your Todoist so you can track them?"

User: "Yes please"

Agent: "Done! I've created 3 tasks in Todoist: finish my report, 
        take a walk, and call my family."
```

**In Your Todoist:**
- ✅ Task: "finish my report" (appears in Inbox)
- ✅ Task: "take a walk" (appears in Inbox)
- ✅ Task: "call my family" (appears in Inbox)

### Technical Details

**Function Tool:** `create_todoist_tasks(task_list)`
- Takes list of task descriptions
- Creates tasks in Todoist default Inbox
- Returns confirmation message
- Handles errors gracefully

**Features:**
- ✅ Creates tasks from stated objectives
- ✅ Only asks once per session
- ✅ Requires explicit user permission
- ✅ Works even if Todoist is not configured (graceful fallback)

**Current Limitations (Minimal Implementation):**
- Tasks created in default Inbox (no project selection)
- No due dates set automatically
- No priority levels
- No task completion tracking from agent

## Testing

### Test 1: Happy Path
1. Complete wellness check-in
2. State 2-3 objectives
3. Say "Yes" when agent offers Todoist
4. **Verify:** Check Todoist app - tasks should appear

### Test 2: Without Configuration
1. Remove/clear `TODOIST_API_KEY` from `.env`
2. Complete check-in
3. **Verify:** Agent says "Todoist is not configured"

### Test 3: Decline Offer
1. Complete check-in
2. Say "No" when agent offers Todoist
3. **Verify:** Check-in still saves to JSON normally

## Troubleshooting

**Tasks not appearing in Todoist:**
- Check API token is correct in `.env`
- Verify agent was restarted after adding token
- Check agent logs for "Created Todoist task" messages

**Error: "Todoist is not configured":**
- Ensure `TODOIST_API_KEY` is set in `backend/.env`
- Token should have no quotes around it
- Restart agent after adding token

**API Token Invalid:**
- Token may have expired - generate new one
- Check for extra spaces/characters when copying

## Future Enhancements (Not Implemented)

Possible extensions for this integration:
- Mark yesterday's objectives as complete
- Fetch today's tasks from Todoist during check-in
- Set due dates ("today", "tomorrow")
- Add to specific projects
- Set priority levels
- Sync task completion back to wellness log

---

**Built with:** [Todoist REST API Python SDK](https://github.com/Doist/todoist-api-python)
