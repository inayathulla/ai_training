# 02 — Flask API (Lab Starter)

The same document agent from `01-single-agent`, refactored into a web API.

You will use this folder as the starting point for **Labs 1, 2, and 3**.

## Project structure

```
02-flask-api/
├── app.py                 # Flask HTTP layer (routes, JSON in/out)
├── agent_core.py          # LangChain agent + tools
├── requirements.txt       # Python dependencies
├── .env.example           # Template for Azure OpenAI credentials
└── sample_documents/      # Files the agent can read
    ├── leave_policy.txt
    ├── expense_policy.txt
    └── security_guidelines.txt
```

In **Lab 2** you will add `Dockerfile` and `.dockerignore` to this folder.
In **Lab 3** you will build an image from it and run a container.

## Endpoints

| Method | Path     | Body                          | Response                              |
|--------|----------|-------------------------------|---------------------------------------|
| GET    | `/health`| —                             | `{"status": "ok"}`                    |
| POST   | `/chat`  | `{"message": "your question"}`| `{"response": "agent answer"}`        |

## Run locally (before containerizing)

```powershell
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
notepad .env

python app.py
```

Then in a separate terminal:

```powershell
curl http://localhost:5000/health

curl -X POST http://localhost:5000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"How many sick leave days do I get?\"}"
```
