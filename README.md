# AI Customer Support Automation

## Project Overview

AI Customer Support Automation is a Python application that processes customer complaints, classifies requests, searches company knowledge-base documents, generates support responses, and records ticket details for future reference.

The project uses AutoGen agents, Streamlit, Python, and CSV-based ticket logging.

## Features

- **Customer Query Agent:** Identifies complaint category, urgency, sentiment, and a short summary.
- **Knowledge Base Agent:** Searches company Markdown documents for relevant policy information.
- **Resolution Agent:** Generates a polite response using retrieved information and recommends escalation when needed.
- **Log Agent:** Records ticket details, responses, status, and escalation reasons in a CSV file.
- **Streamlit Interface:** Allows users to submit complaints and view agent outputs.
- **Ticket History:** Displays logged tickets and supports CSV download.
- **Escalation:** Flags high-urgency complaints and cases requiring human support.

## Technology Stack

- Python 3.12
- AutoGen AgentChat
- OpenAI model API
- Streamlit
- Pandas
- Python-dotenv
- CSV file storage

## Project Structure

```text
customer-support-agents/
├── agents/
│   ├── query_agent.py
│   ├── knowledge_agent.py
│   ├── resolution_agent.py
│   ├── log_agent.py
│   └── support_workflow.py
├── knowledge_base/
│   ├── shipping_policy.md
│   ├── refund_policy.md
│   ├── account_and_login.md
│   └── product_faq.md
├── logs/
│   └── tickets.csv
├── screenshots/
│   ├── resolved_ticket.png
│   ├── escalated_ticket.png
│   └── ticket_log.png
├── app.py
├── team.py
├── test_query_agent.py
├── test_knowledge_agent.py
├── test_resolution_agent.py
├── test_log_agent.py
├── test_support_workflow.py
├── test_team.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd customer-support-agents
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository URL.

### 2. Create and activate a virtual environment

Windows CMD:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```cmd
pip install -r requirements.txt
```

### 4. Configure the API key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Replace the placeholder with your own API key. Never commit `.env` or expose your API key publicly.

### 5. Run the Streamlit application

```cmd
streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## How It Works

The primary Streamlit workflow processes a complaint in this order:

1. The Customer Query Agent analyzes the complaint.
2. The Knowledge Base Agent searches relevant company documents.
3. The Resolution Agent drafts a response and determines whether escalation is recommended.
4. The Log Agent records the ticket in `logs/tickets.csv`.

The separate `team.py` module demonstrates AutoGen team orchestration using `RoundRobinGroupChat` and a `LOGGED` termination marker.

## Ticket Logging

Each ticket records fields such as:

- Ticket ID and timestamp
- Customer name and order ID
- Complaint and category
- Urgency and sentiment
- Knowledge-base sources
- Generated response
- Ticket status and escalation reason

Ticket records are stored locally in CSV format.

## Testing

Run the individual tests from the project root:

```cmd
python test_query_agent.py
python test_knowledge_agent.py
python test_resolution_agent.py
python test_log_agent.py
python test_support_workflow.py
python test_team.py
```

Tests involving the OpenAI API require a valid API key and an available API connection.

## Screenshots

The `screenshots/` folder contains evidence of:

- A successfully resolved customer ticket
- An escalated customer ticket
- The ticket log table

## Limitations

- The knowledge base contains sample policies created for this project.
- Keyword-based retrieval may not find every relevant passage.
- AI-generated responses should be reviewed for important or sensitive cases.
- Ticket history is stored locally and is not a production-grade database.
- The AutoGen team test is separate from the primary Streamlit workflow unless the two are explicitly integrated.

## Future Improvements

- Semantic search using embeddings and a vector database
- Human approval for sensitive resolutions
- Persistent database storage
- Analytics dashboard
- Cloud or VPS deployment
- Authentication and role-based access control

## Security

Keep API keys in `.env`. Do not commit secrets, virtual environments, or private customer information.

## Disclaimer

This is an educational demonstration using fictional company policies. It is not intended to replace human review of sensitive customer-support cases.
