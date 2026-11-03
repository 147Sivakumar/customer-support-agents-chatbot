# AI Customer Support Chatbot Dashboard

An AI-powered customer support application built using Python, AutoGen, OpenAI, and Streamlit. The application allows users to submit support requests, select a department, receive AI-generated responses, and manage ticket history through a simple dashboard.

## Features

- **Five Department Agents:** IT, Admin, HR, Accountant, and Complex Issues.
- **Department Selection:** Select a department manually or use automatic department detection.
- **AI-Generated Responses:** Generate helpful responses using the selected department agent.
- **Knowledge Base:** Search available Markdown documents for relevant information.
- **Dashboard Metrics:** View total tickets, open/other tickets, escalated tickets, and resolved/closed tickets.
- **Ticket Management:** Record complaints, department, urgency, response, and ticket status.
- **Ticket History:** View previously recorded requests.
- **CSV Export:** Download ticket history for reporting.
- **Clear Ticket History:** Remove old saved ticket records after confirmation.
- **Escalation Support:** Recommend human review for high-risk or unresolved requests.

## Technology Stack

- Python
- AutoGen AgentChat
- OpenAI API
- Streamlit
- Pandas
- Python-dotenv
- CSV file storage
## Project Structure

```text
customer-support-agents-chatbot/
│
├── agents/
│   ├── knowledge_agent.py
│   ├── log_agent.py
│   ├── query_agent.py
│   ├── resolution_agent.py
│   └── support_workflow.py
│
├── knowledge_base/
│   ├── account_and_login.md
│   ├── product_faq.md
│   ├── refund_policy.md
│   └── shipping_policy.md
│
├── Support-Desk-Dashboard-1.png
├── Support Desk Dashboard - Google Chrome 2026-11-03 07-14-45.mp4
├── support_tickets.xlsx
│
├── app.py
├── team.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── test_knowledge_agent.py
├── test_log_agent.py
├── test_query_agent.py
├── test_resolution_agent.py
├── test_support_workflow.py
└── test_team.py
```

**Note:** The image, video, and Excel filenames above are examples based on the names you provided. Use the exact filenames and extensions shown in your GitHub repository. The Excel file contains exported ticket data; ensure it doesn't expose personal information or confidential customer details.


**Note:** The `logs/` directory and `tickets.csv` file are generated locally when tickets are recorded. Runtime logs and screenshots are not required for the application to run. The structure above reflects the project's main files; check the repository if additional files have been added.

## Installation and Setup

### 1. Clone the repository

```bat
git clone https://github.com/147Sivakumar/customer-support-agents-chatbot.git
cd customer-support-agents-chatbot
```

### 2. Create and activate a virtual environment

For Windows Command Prompt:

```bat
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bat
pip install -r requirements.txt
```

### 4. Configure the OpenAI API key

Create a `.env` file in the project root directory:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

Replace the placeholder with your own OpenAI API key.

**Security:** Never upload your real `.env` file or API key to GitHub. Keep `.env` excluded through `.gitignore`. Only commit `.env.example` with a placeholder value.

### 5. Run the dashboard

```bat
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

`http://localhost:8501`

## How to Use

1. Open the Support Desk Dashboard.
2. Enter the customer or employee name.
3. Enter an optional ticket reference.
4. Select a department or choose **Auto-detect department**.
5. Describe the support issue.
6. Click **Submit Request**.
7. Review the department, urgency, sentiment, suggested response, and ticket status.
8. View ticket history and download it as a CSV file.
9. To remove old records, open **Manage Ticket Records**, confirm the action, and click **Clear Ticket History**.

## Sample Test Cases

| Department | Example request |
|---|---|
| IT | My laptop cannot connect to office Wi-Fi. |
| Admin | My office ID card is not working. |
| HR | How can I ask about my leave balance? |
| Accountant | I need help with my reimbursement claim. |
| Complex Issues | I reported a security breach and it is still unresolved. |

## Testing

Run the available test scripts from the project root:

```bat
python test_knowledge_agent.py
python test_log_agent.py
python test_query_agent.py
python test_resolution_agent.py
python test_support_workflow.py
python test_team.py
```

Tests that call the OpenAI API require a valid API key and an available API connection.

## Knowledge Base

The current knowledge-base files contain account, product, refund, and shipping information. For better departmental responses, add approved guidance for IT, Administration, HR, and Accounts.

Do not treat sample information as official company policy. The system should recommend human review when relevant guidance is unavailable or an issue is sensitive.

## Limitations

- Automatic department detection uses keyword-based routing and may misclassify unclear requests.
- Response quality depends on the relevance of the available knowledge-base documents.
- AI-generated responses should be reviewed for sensitive or high-risk issues.
- Ticket records are stored locally in CSV format rather than in a production database.
- Clearing ticket history permanently removes the local saved log.

## Future Improvements

- Add authentication and role-based access.
- Add ticket search, filtering, and assignment.
- Store tickets in a database.
- Add a human-review workflow.
- Expand the knowledge base with approved departmental policies.
- Deploy the application to a cloud server.

## Author

Sivakumar

## Purpose

Educational project demonstrating AI-assisted support, department routing, knowledge retrieval, ticket logging, and a Streamlit dashboard.
