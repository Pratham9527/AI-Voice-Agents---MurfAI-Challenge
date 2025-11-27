# AGENTS.md - Day 6: Fraud Alert Voice Agent

This is a LiveKit Agents project implementing a **Fraud Alert Voice Agent** for a fictional bank. The agent verifies suspicious transactions with customers using a database of fraud cases.

## Overview

Day 6's agent focuses on **database integration** and **secure verification flows**. It uses a single-agent pattern with function tools to:
- Load fraud case details from a SQLite database.
- Verify user identity using security questions.
- Read out suspicious transaction details.
- Update the case status (Safe/Fraud) based on user input.

### Key Features

1.  **Fraud Analyst Persona** - Professional, calm, and reassuring.
2.  **Database Integration** - SQLite database (`data/fraud_cases.db`) stores case details.
3.  **Security Verification** - Verifies user identity via security questions stored in the DB.
4.  **Transaction Review** - Reads out merchant, amount, and time details.
5.  **Status Updates** - Updates the database with the final outcome (Safe/Fraud).

## Project Structure

This Python project uses the `uv` package manager.

### Key Files

```
Day6/backend/
├── src/
│   ├── agent.py              # Main Fraud Agent with tools
│   └── database.py           # SQLite database handler
├── data/
│   └── fraud_cases.db        # SQLite database (auto-created)
└── .env                      # Environment variables
```

## Database Schema

The `fraud_cases` table includes:
- `username` (PK)
- `security_identifier`
- `card_ending`
- `transaction_name`
- `transaction_amount`
- `transaction_time`
- `security_question`
- `security_answer`
- `status` (pending_review, confirmed_safe, confirmed_fraud, verification_failed)
- `outcome_note`

## Agent Tools

The agent has 2 function tools:

### 1. `load_case_tool(username)`

**Purpose**: Retrieve fraud case details.

**How it works**:
- Queries the database for the username.
- Returns transaction details and the security question/answer to the Agent (LLM).
- The Agent then asks the security question to the user.

### 2. `update_case_tool(status, outcome_note)`

**Purpose**: Update the case status after the call.

**When to use**:
- After verification fails.
- After the user confirms or denies the transaction.

## Conversation Flow

1.  **Introduction**: Agent introduces itself and asks for username.
2.  **Verification**: Agent asks the security question associated with the username.
3.  **Review**: Agent reads the transaction details.
4.  **Decision**: User says Yes (Safe) or No (Fraud).
5.  **Conclusion**: Agent updates DB and ends the call.

## Running the Agent

### Development Mode

```bash
cd Day6/backend
python src/agent.py dev
```

### Demo Users

The database is seeded with two sample users:
1.  **John** (Security Answer: "Smith")
2.  **Alice** (Security Answer: "Fluffy")

## Environment Variables

Required in `.env`:
```
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
LIVEKIT_URL=
MURF_API_KEY=
GOOGLE_API_KEY=
DEEPGRAM_API_KEY=
```
