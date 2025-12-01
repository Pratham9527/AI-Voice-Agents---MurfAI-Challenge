# Improv Battle - Frontend

> 🎭 **Day 10 of the Murf AI Voice Agents Challenge**
>
> Interactive improv game show frontend built with Next.js and LiveKit.
> See the [main README](../README.md) for complete setup instructions and game details.

A voice-first improv game show interface built with [LiveKit Agents](https://docs.livekit.io/agents) and the [LiveKit JavaScript SDK](https://github.com/livekit/client-sdk-js).

**Game:** "Improv Battle" - Face 3 creative improv scenarios, perform in character, and get real-time feedback from an AI game show host!

**Based on:** [livekit-examples/agent-starter-react](https://github.com/livekit-examples/agent-starter-react)

### Features:

- 🎭 Real-time voice interaction with AI improv host
- 🎲 3 rounds of unique improv scenarios per game
- 🎤 Natural conversation and scene detection
- 📊 Varied host reactions (positive, critical, mixed, surprised)
- 🎨 Custom Improv Battle branding and purple theme
- 🌓 Light/dark mode support
- ⚡ Fast, responsive Next.js interface

This template is built with Next.js and customized for the Improv Battle game.

### Project structure

```
frontend/
├── app/
│   ├── (app)/
│   │   └── page.tsx           # Main entry point
│   ├── api/
│   │   └── connection-details/ # LiveKit connection API
│   └── layout.tsx
├── components/
│   ├── app/
│   │   ├── app.tsx            # Main app component
│   │   ├── welcome-view.tsx   # Updated with Improv Battle theme
│   │   ├── session-view.tsx   # Game session view
│   │   └── ...
│   └── livekit/               # LiveKit UI components
├── app-config.ts              # Improv Battle configuration
├── public/
└── package.json
```

## Getting started

### Prerequisites

- Node.js 18+ and npm/pnpm
- Backend agent running (see [backend README](../backend/AGENTS.md))

### Installation

1. **Install dependencies:**

```bash
npm install
# or
pnpm install
```

2. **Configure environment** (`.env.local`):

```bash
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=https://your-livekit-server-url
```

3. **Run the frontend:**

```bash
npm run dev
# or
pnpm dev
```

4. **Open** http://localhost:3000 in your browser

5. **Start the game:**
   - Click "🎭 Start Improv Battle"
   - Tell the host your name
   - Perform 3 improv scenarios
   - Get feedback and have fun!

## Configuration

The app is configured in [`app-config.ts`](./app-config.ts) with Improv Battle-specific settings:

#### Current Configuration

```ts
export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Improv Battle',
  pageTitle: 'Improv Battle - Voice Improv Game',
  pageDescription: 'Test your improv skills with AI! Face scenarios, perform in character, and get real-time feedback.',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#8b5cf6',  // Purple for entertainment/theater
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#a78bfa',  // Light purple for dark mode
  startButtonText: '🎭 Start Improv Battle',

  sandboxId: undefined,
  agentName: undefined,
};
```

You can customize these values to change branding, colors, and UI text.

#### Environment Variables

Configure your LiveKit credentials in `.env.local`:

```env
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-livekit-server-url
```

These are required for the voice agent connection.

## Key Customizations for Improv Battle

### Updated Components:

1. **`welcome-view.tsx`**
   - Changed text to "🎭 Welcome to Improv Battle"
   - Updated description for improv game concept

2. **`app-config.ts`**
   - Purple theme (#8b5cf6) for entertainment
   - "Start Improv Battle" button text
   - Game-specific page title and description

### Backend Connection:

The frontend connects to the Improv Battle agent (see [backend/AGENTS.md](../backend/AGENTS.md)) which:
- Hosts 3 rounds of improv scenarios
- Provides varied, realistic feedback
- Manages game state and flow

## Tech Stack

- **Framework**: Next.js 15 with Turbopack
- **LiveKit**: Client SDK for voice connections
- **Styling**: Tailwind CSS with custom theme
- **TypeScript**: Full type safety

---

**Built for Day 10 of the Murf AI Voice Agents Challenge** 🎭
