# Weekly Reflection Feature

## Overview

The wellness companion can now analyze your check-in history and provide insights about your mood, energy levels, and goal-setting patterns over the past week.

## How It Works

### Asking for Insights

Simply ask the agent questions like:
- **"How has my mood been this week?"**
- **"Did I follow through on my goals?"**
- **"Show me my weekly summary"**
- **"How am I doing?"**

The agent will automatically use the `get_weekly_reflection` tool to analyze your data.

### What You'll Get

**Example Response:**
```
Here's what I see from the past week:

📊 Mood: Averaging 6.6/10 - that's moderate, with ups and downs.
⚡ Energy: Averaging 6.0/10 - moderate energy.
🎯 Goals: You set objectives on 5 out of 5 days (excellent consistency). 
    That's about 2.4 goals per day on average.

You're doing well! Keep up the positive momentum. 😊
```

## Analytics Provided

### 1. **Mood Average**
- Calculates average mood score from 1-10 scale
- Provides qualitative description:
  - 7-10: "pretty good overall"
  - 5-6.9: "moderate, with ups and downs"
  - Below 5: "challenging lately"

### 2. **Energy Average**
- Calculates average energy level from 1-10 scale
- Describes energy patterns:
  - 7-10: "good energy levels"
  - 5-6.9: "moderate energy"
  - Below 5: "lower energy than usual"

### 3. **Goal Consistency**
- Counts days with objectives vs total check-ins
- Calculates average objectives per day
- Assesses consistency:
  - 80%+: "excellent consistency"
  - 50-79%: "pretty consistent"
  - Below 50%: "some goal-setting"

### 4. **Supportive Summary**
- Tailored encouragement based on your data
- Always non-judgmental and uplifting
- Acknowledges both progress and challenges

## Requirements for Analysis

### Minimum Data
- **At least 3 check-ins** required for meaningful insights
- If fewer, agent responds: *"I need at least 3 check-ins to provide meaningful insights"*

### Numeric Scales Work Best
For best results, use numeric scales when checking in:
- ✅ **Good:** "I'm feeling about 7/10 today"
- ✅ **Good:** "My energy is 6 out of 10"
- ⚠️ **Okay:** "I'm feeling great" (harder to quantify)

The agent can extract numbers from formats like:
- "7/10"
- "7 out of 10"
- "about 7"
- Just "7"

## Technical Details

### Time Range
- **Default:** Last 7 days (1 week)
- **Customizable:** Agent can analyze different ranges if asked

### Data Source
- Reads from `wellness_log.json`
- Uses timestamp field to filter last N days
- Handles missing or malformed data gracefully

### Privacy
- All analysis happens locally
- No external APIs or cloud services
- Data never leaves your device

## Example Use Cases

### Weekly Check-In
```
User: "Show me how I did this week"

Agent: *Provides mood/energy averages, goal consistency, supportive summary*
```

### Mood Tracking
```
User: "Has my mood improved?"

Agent: "Your average mood this week is 7.2/10, which is pretty good! 
        That's up from your earlier check-ins."
```

### Goal Accountability
```
User: "Am I being consistent with my goals?"

Agent: "You've set objectives on 6 out of 7 days this week - 
        that's excellent consistency! You're averaging 2.5 goals 
        per day."
```

## Limitations (By Design)

### What It Does NOT Do:
- ❌ Track goal completion (would need follow-up feature)
- ❌ Compare to previous weeks (single week analysis only)
- ❌ Predict future mood/energy
- ❌ Provide medical/clinical interpretations
- ❌ Use complex sentiment analysis

### What It DOES Do:
- ✅ Simple averages of numeric scores
- ✅ Basic counting and consistency metrics
- ✅ Supportive, plain-language summaries
- ✅ Non-judgmental encouragement

## Tips for Better Insights

1. **Be Consistent:** Check in daily for more meaningful trends
2. **Use Numbers:** "7/10" is better than "pretty good" for analytics
3. **Be Honest:** The agent is here to support, not judge
4. **Ask Often:** Request weekly summaries regularly to track progress

---

**Implementation:** Uses `analyze_weekly_data()` helper function with regex-based numeric extraction from text fields.
