# MUST AI Inbox Helper

An AI-assisted inbox tool that helps the MUST Company HR team review candidate messages, classify their intent, and prepare professional reply drafts. It uses company-provided knowledge to keep responses grounded and flags candidate-specific or unavailable information for HR verification.

> **Human-in-the-loop:** This application does not send emails or make hiring decisions. Every generated reply must be reviewed and approved by a human.

## Features

- **Multiple input options:** Paste one or more candidate messages, or upload a CSV file.
- **Batch processing:** Separate pasted messages with a line containing `---EMAIL---`.
- **AI message classification:** Assigns a short category based on each candidate's message.
- **Context-grounded reply drafting:** Uses the information in `company_knowledge.json` to draft concise, professional replies.
- **HR verification flags:** Marks questions requiring candidate-specific information or details not available in the company knowledge base.
- **Editable drafts and review decisions:** HR can edit each draft and mark it Pending, Approved, or Rejected.
- **CSV exports:** Download all results or only HR-approved drafts.

## How it works

1. HR pastes candidate messages or uploads a CSV file.
2. The application processes each message using the Gemini model.
3. The AI returns a category, review status, reason, and suggested reply.
4. HR reviews and edits each draft, then records an approval decision.
5. Results can be downloaded as CSV files.

## Tech stack

- Python
- Streamlit
- Google Gemini API (`google-genai`)
- Pandas
- JSON-based company knowledge

## Project structure

```text
Ai_Mail_Inbox_Helper/
├── app.py
├── ai_engine.py
├── company_knowledge.json
└── requirements.txt
```

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/hamadalikhan723/Ai_Mail_Inbox_Helper.git
cd Ai_Mail_Inbox_Helper
```

### 2. Install dependencies

It is recommended to use a virtual environment.

```bash
python -m venv .venv
```

Activate it:

- **Windows (PowerShell):** `.venv\\Scripts\\Activate.ps1`
- **macOS/Linux:** `source .venv/bin/activate`

Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Configure the Gemini API key

Create a Streamlit secrets file at `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
```

Alternatively, set the `GEMINI_API_KEY` environment variable.

**Important:** Keep your API key private. Do not commit `secrets.toml`, API keys, or other credentials to GitHub.

### 4. Run the application

```bash
streamlit run app.py
```

Streamlit will provide a local URL in the terminal, usually `http://localhost:8501`.

## Input format

### Option A: Paste messages

Paste one message, or separate multiple messages using this exact delimiter on its own line:

```text
Hello, I applied for the AI Engineer position. Could you share an update?
---EMAIL---
Could you please confirm whether the role is remote or on-site?
```

### Option B: Upload a CSV

Upload a CSV file containing a required `message` column. The optional `candidate_name` column is used to label candidates; if it is absent, the app assigns names such as Candidate 1.

Example:

| candidate_name | message |
|---|---|
| Candidate A | I applied for the AI Engineer position. Could you share an update? |
| Candidate B | Could you confirm the work arrangement for this vacancy? |

## Review statuses

- **General Reply - Human Approval Required:** The reply can be drafted using the available general company information, but still requires HR approval.
- **Needs HR Verification:** The message asks for candidate-specific or unavailable information that must be checked by HR.
- **Processing Error:** The message could not be processed; it should be reviewed manually.

The HR decision is tracked separately as Pending, Approved, or Rejected. Approval is a review record only; it does not send an email.

## Company knowledge

The assistant reads company information and recruitment guidance from `company_knowledge.json`. Update this file when approved company information changes. The AI is instructed not to invent details such as salary, interview dates, application status, working hours, benefits, or vacancy-specific requirements.

## Limitations and responsible use

- This is an AI-assisted drafting and review tool, not an email client or applicant tracking system.
- It does not connect to an inbox, send messages, or make hiring decisions.
- Generated content may be inaccurate or incomplete. HR must verify facts and approve every reply before using it.
- Avoid uploading unnecessary personal or sensitive candidate information, and follow your organization's data-handling policies.

## License

No license has been specified for this repository yet.
