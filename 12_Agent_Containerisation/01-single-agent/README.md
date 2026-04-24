# 01 — Single-Agent CLI Demo

A minimal LangChain tool-calling agent that answers questions about internal
documents. Runs as a command-line program.

## What it does

The agent has two tools:

1. `list_documents()` — lists files in `sample_documents/`
2. `read_document(filename)` — returns the text of a file

You ask a question. The agent decides which tool(s) to call, reads the right
file, and answers.

## Prerequisites

- Python 3.10+
- An Azure OpenAI deployment (GPT-4o or GPT-4o-mini recommended)

## Setup

```powershell
# From this folder, create a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy the env file and fill in your Azure OpenAI details
copy .env.example .env
notepad .env
```

## Run

```powershell
python agent.py
```

## Try these

- "What is our leave policy?"
- "How many sick leave days do I get?"
- "What's the per diem limit for Bengaluru?"
- "What documents do you have?"
