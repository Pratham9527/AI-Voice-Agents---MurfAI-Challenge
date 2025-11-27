# Day 6: Fraud Alert Voice Agent 🚨

A voice agent that acts as a bank fraud representative, verifying suspicious transactions with customers using a database.

## Features
- **Database Backed**: Loads and updates fraud cases from a SQLite database.
- **Secure Verification**: Asks security questions before discussing sensitive details.
- **Transaction Review**: Reads out transaction details for user confirmation.
- **Outcome Tracking**: Marks cases as Safe or Fraud based on user input.

## Quick Start

1.  **Navigate to backend**:
    ```bash
    cd backend
    ```

2.  **Install dependencies** (if not already installed):
    ```bash
    uv sync
    ```

3.  **Run the agent**:
    ```bash
    python src/agent.py dev
    ```

4.  **Connect**:
    - Open the LiveKit Agent Playground (link printed in terminal).
    - Speak to the agent.
    - **Demo Users**:
        - Say "My name is **John**" (Security Answer: **Smith**)
        - Say "My name is **Alice**" (Security Answer: **Fluffy**)

## Documentation
See [backend/AGENTS.md](backend/AGENTS.md) for full details on architecture and configuration.
