# Quick Start Guide - Day 3 Wellness Companion

## 🚀 Running the Agent

### 1. Navigate to Day3 Backend
```bash
cd Day3/backend
```

### 2. Install Dependencies (if not already done)
```bash
uv sync
```

### 3. Download Models (first time only)
```bash
uv run python src/agent.py download-files
```

### 4. Run in Console Mode
```bash
uv run python src/agent.py console
```

### 5. Run in Dev Mode (with frontend)
```bash
uv run python src/agent.py dev
```

Then open the frontend in your browser.

---

## 📝 Example Conversation

**Agent:** Hi! Welcome to your daily wellness check-in. How are you feeling today?

**You:** I'm feeling pretty good, maybe a 7 out of 10.

**Agent:** That's great to hear! And what's your energy level like today?

**You:** Around 6 out of 10. A bit tired.

**Agent:** I understand. Is there anything stressing you out or on your mind right now?

**You:** Just work deadlines coming up.

**Agent:** That's totally understandable. What are 1 to 3 things you'd like to accomplish today?

**You:** Finish the Day 3 agent, take a walk, and maybe read for a bit.

**Agent:** Those sound like great goals! For those work deadlines, maybe try breaking them into smaller tasks? And that walk will definitely help with energy. Let me recap: You're feeling about a 7/10, energy is around 6, dealing with work deadlines, and you want to finish the Day 3 agent, take a walk, and read. Does that sound right?

**You:** Yes, exactly!

**Agent:** Perfect! I've saved this check-in. See you tomorrow!

---

## 🔍 Check Your Data

After the conversation, check the JSON file:

```bash
cat backend/src/wellness_log.json
```

You should see your check-in saved with:
- Timestamp
- Mood ("feeling pretty good, 7/10")
- Energy level ("6/10")
- Daily objectives (list)
- Agent summary

---

## 🧪 Testing Multiple Sessions

### Day 1 Test
- Run the agent → No previous context
- Complete check-in → JSON created

### Day 2 Test  
- Run the agent → References Day 1
- Complete check-in → New entry appended

### Day 3 Test
- Run the agent → References Day 1 & Day 2
- Complete check-in → Full history maintained

---

## ⚡ Quick Troubleshooting

**Agent won't start:**
- Check `.env.local` has all required API keys
- Run `uv sync` to install dependencies

**No voice input/output:**
- Ensure microphone permissions are granted
- Check audio device settings

**JSON not saving:**
- Check `backend/src/` folder permissions
- Look for error logs in console

---

## 📚 Next Steps

1. Test in console mode
2. Verify JSON persistence
3. Test multi-day continuity
4. Try with frontend
5. Deploy to production (optional)

Enjoy your wellness companion! 🌟
