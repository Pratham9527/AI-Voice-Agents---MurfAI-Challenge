# Day 5: Razorpay SDR Voice Agent 🎙️💼

**Primary Goal**: Build a voice agent Sales Development Representative (SDR) that can answer FAQ questions and capture lead information naturally during conversation.

## 🎯 Project Overview

This project implements an AI-powered SDR voice agent for **Razorpay**, acting as a friendly sales representative who:
- Answers product, pricing, and technical questions using FAQ data
- Collects lead information naturally during conversation
- Generates verbal summaries at the end of calls
- Stores lead data in a master database

## ✨ Key Features

### 1. **SDR Persona** 
- Warm, professional, and consultative approach
- Natural conversation flow (not robotic questionnaire)
- Genuinely curious about prospect's needs
- Knowledgeable about Razorpay products

### 2. **FAQ System**
- 15+ common questions about Razorpay
- Simple keyword-based search
- Covers products, pricing, integrations, security
- Preloaded during agent initialization for fast responses

### 3. **Lead Capture**
Naturally collects 7 key fields:
- **Name** - Prospect's full name
- **Company** - Company they work for
- **Email** - Contact email (with validation)
- **Role** - Job title/position
- **Use Case** - What they want to use Razorpay for
- **Team Size** - Size of their team
- **Timeline** - When they plan to start (now/soon/later)

### 4. **Master Leads Database**
- All leads stored in `leads/leads_database.json`
- Timestamped entries for tracking
- Persistent across sessions

### 5. **End-of-Call Summary**
- Automatic verbal summary generation
- Includes key details: who they are, what they need, timeline
- Professional closing with follow-up expectations

## 🏗️ Architecture

```
Day5/backend/
├── data/
│   └── company_faq.json          # Razorpay FAQ data (15 FAQs)
├── src/
│   ├── agent.py                   # Main SDR agent
│   ├── faq_handler.py             # FAQ search with keyword matching
│   └── lead_capture.py            # Lead data collection & storage
├── leads/
│   └── leads_database.json        # Master leads database
└── .env                           # Environment variables
```

## 🔧 Technology Stack

- **LiveKit Agents** - Voice agent framework
- **Murf.ai TTS** - Indian English voice (Raveena)
- **Deepgram** - Speech-to-text
- **Google Gemini 2.5 Flash** - LLM
- **Python** - Backend logic

## 📊 How It Works

### Conversation Flow

1. **Opening** (0-30s)
   - Warm greeting
   - Discovery questions: "What brings you here?", "What are you working on?"

2. **Discovery** (Understanding needs)
   - Listen to pain points
   - Ask clarifying questions
   - Build rapport

3. **Educate** (Answer questions)
   - User asks about Razorpay → Agent uses `search_faq` tool
   - Provides accurate answers from FAQ database
   - Doesn't make up information

4. **Qualify** (Collect lead info)
   - Naturally weaves questions into conversation
   - Uses `save_lead_field` tool as information is shared
   - Not interrogation-style, conversational

5. **Close** (End call)
   - User signals done ("that's all", "thanks")
   - Agent uses `end_call_and_summarize` tool
   - Verbal summary + save to database

### Tools Used by Agent

1. **`search_faq(query)`**
   - Searches FAQ database for answers
   - Returns best matching answer

2. **`save_lead_field(field_name, value)`**
   - Saves lead information as it's collected
   - Validates email format

3. **`end_call_and_summarize()`**
   - Generates verbal summary
   - Saves lead to master database
   - Professional closing

## 🚀 Setup & Running

### Prerequisites
```bash
# Install dependencies (already in requirements.txt)
pip install livekit-agents livekit-plugins-murf livekit-plugins-deepgram livekit-plugins-google
```

### Environment Variables
Make sure `.env` file has:
```
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=your_url
MURF_API_KEY=your_murf_key
GOOGLE_API_KEY=your_google_key
DEEPGRAM_API_KEY=your_deepgram_key
```

### Run the Agent
```bash
cd backend
python src/agent.py dev
```

Visit the LiveKit playground URL to test!

## 📝 Example Conversation

```
Agent: Hi! I'm excited to chat with you about Razorpay! What brings you here today?

User: I'm building a SaaS product and need a payment solution.

Agent: That's great! What's your product about? 
       [Saves use_case: "payment solution for SaaS product"]

User: It's a project management tool for teams. Do you support subscriptions?

Agent: [Uses search_faq tool]
       Yes! We have a dedicated Subscriptions product that handles recurring 
       billing, automated invoicing, payment retries, and subscription management. 
       It's perfect for SaaS businesses like yours!

Agent: By the way, what's your name?

User: I'm Rahul.

Agent: [Saves name: "Rahul"]
       Nice to meet you, Rahul! What company are you with?

User: TechStartup India.

Agent: [Saves company: "TechStartup India"]
       Great! What's your role at TechStartup India?

User: I'm the CTO.

Agent: [Saves role: "CTO"]
       Perfect! What's the best email to reach you at?

User: rahul@techstartup.in

Agent: [Saves email: "rahul@techstartup.in"]
       Got it! How large is your team currently?

User: We're about 15 people.

Agent: [Saves team_size: "15"]
       Nice size! When are you looking to integrate a payment solution?

User: We need to launch in the next month, so pretty soon.

Agent: [Saves timeline: "soon"]
       Understood! Is there anything else you'd like to know about Razorpay?

User: That's all for now, thanks!

Agent: [Uses end_call_and_summarize tool]
       Thank you so much for your time! Here's what I have: I spoke with Rahul 
       from TechStartup India who is a CTO. They're looking to use Razorpay for 
       payment solution for SaaS product. Their team has 15 members. They're 
       planning to start soon. I can follow up with them at rahul@techstartup.in. 
       Someone from our team will reach out to you soon. Have a great day!
```

## 📈 Lead Data Storage

Leads are stored in `leads/leads_database.json`:

```json
{
  "leads": [
    {
      "timestamp": "2025-11-26T18:30:00+05:30",
      "name": "Rahul",
      "company": "TechStartup India",
      "email": "rahul@techstartup.in",
      "role": "CTO",
      "use_case": "payment solution for SaaS product",
      "team_size": "15",
      "timeline": "soon"
    }
  ]
}
```

## 🎨 Design Decisions

### Why Simple Keyword Matching?
- Fast and efficient for FAQ lookups
- No external dependencies (embeddings, vector DB)
- Sufficient for 15 well-structured FAQs
- Preloaded for instant responses

### Why Master Database?
- Single source of truth for all leads
- Easy to export and analyze
- Persistent across sessions
- Simple append-only structure

### Why Verbal Summary Only?
- More natural for voice interaction
- Reduces file clutter
- Lead data already in database
- Provides immediate feedback

## 🧪 Testing Checklist

- [x] Agent starts with warm greeting
- [x] FAQ search returns accurate answers
- [x] Lead fields saved correctly
- [x] Email validation works
- [x] End-of-call summary generated
- [x] Lead saved to database
- [x] Conversational flow feels natural

## 📚 Company Info

**Razorpay** is India's leading full-stack financial solutions company:
- **Founded**: 2014
- **Headquarters**: Bangalore, India
- **Products**: Payment Gateway, Route, Payroll, Business Banking
- **Pricing**: 2% domestic, 3% international, no setup fees

## 🎯 MVP Completion

✅ Agent behaves like an SDR for Razorpay  
✅ Answers FAQ questions using search  
✅ Naturally collects lead information  
✅ Stores data in master database  
✅ Generates verbal summary at end  

## 🔮 Future Enhancements

- Add sentiment analysis for lead scoring
- Implement semantic search for better FAQ matching
- CRM integration (Salesforce, HubSpot)
- Email automation for follow-ups
- Analytics dashboard for lead insights
- Multi-language support for Indian languages

## 📄 License

Part of the MurfAI Voice Agents Challenge - Day 5

---

**Built with ❤️ for the Murf AI Voice Agents Challenge**
