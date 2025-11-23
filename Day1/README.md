# Murf AI Voice Agents Challenge 2025 - Day 1

## 🎙️ What This Is
A real-time conversational voice agent that listens, thinks, and responds instantly. Built for **Murf AI's 10 Days of Voice Agents Challenge 2025** using the new **Murf Falcon** TTS model.

Not a chatbot—an actual voice pipeline with ultra-low latency (130ms response time).

> **Credit:** Based on the official [Murf AI starter kit](https://github.com/murf-ai/ten-days-of-voice-agents-2025). 
  I configured, debugged, and deployed it locally for Day 1.

---

## ⚡ The Stack

**Real-time Audio Pipeline:**
- **STT (Ear):** Deepgram – converts speech to text
- **LLM (Brain):** Google Gemini Flash – processes and generates responses
- **TTS (Voice):** Murf Falcon – streams audio back instantly
- **Orchestration:** LiveKit – handles WebSocket connections for real-time streaming

**Architecture:**
- **Backend:** Python (LiveKit Agents)
- **Frontend:** Next.js + TypeScript

---

## 🚀 Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- API Keys: Murf AI, LiveKit Cloud, Deepgram, Google Gemini

---

### 1. Clone the Repo
```bash
git clone <YOUR_REPO_URL>
cd ten-days-of-voice-agents-2025
```

---

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

**Create `.env` file:**
```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
MURF_API_KEY=your_murf_key
DEEPGRAM_API_KEY=your_deepgram_key
GOOGLE_API_KEY=your_google_key
```

**Download models & start:**
```bash
# First time only
python src/agent.py download-files

# Run the agent
python src/agent.py dev
```

---

### 3. Frontend Setup

Open a new terminal:
```bash
cd frontend
npm install
```

**Create `.env.local` file:**
```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

**Start the frontend:**
```bash
npm run dev
```

---

## 🎮 Run It

1. Make sure both backend (`agent.py`) and frontend (`npm run dev`) are running
2. Open `http://localhost:3000` in your browser
3. Click **Connect**
4. Start talking to test the voice agent

---

## 🐛 Common Issues

**"Environment variable not found"**
- Double-check your `.env` and `.env.local` files
- Make sure variable names match exactly

**Audio not streaming**
- Verify LiveKit credentials are correct in both backend and frontend
- Check browser console for WebSocket errors

**Missing dependencies**
- Run `python src/agent.py download-files` if models aren't loading

---

## 📚 What I Learned

- Setting up real-time audio pipelines is harder than it looks
- Environment variable management across frontend/backend is crucial
- Murf Falcon is genuinely fast compared to traditional TTS APIs
- WebSocket orchestration makes or breaks the user experience

---

## 🔗 Links

- [Murf AI Challenge Repo](https://github.com/murf-ai/ten-days-of-voice-agents-2025)
- [Day 1 Task Details](https://github.com/murf-ai/ten-days-of-voice-agents-2025/blob/main/challenges/Day%201%20Task.md)

---

## 📜 License

Built as part of the Murf AI Voice Agents Challenge. Uses code from the official Murf AI repository.

#BuildwithMurf #10DaysOfVoiceAgents
