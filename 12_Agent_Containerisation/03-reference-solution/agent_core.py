"""
Agent core — tool definitions and executor factory.
Separated from the HTTP layer so it can be imported cleanly by app.py.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

load_dotenv()

DOCS_DIR = Path(__file__).parent / "sample_documents"

# Module-level cache so we build the agent once per process, not per request.
_executor: AgentExecutor | None = None


# ---------- Tools ----------

@tool
def list_documents() -> str:
    """List all documents available in the document folder."""
    if not DOCS_DIR.exists():
        return "No document folder found."
    files = sorted(f.name for f in DOCS_DIR.iterdir() if f.is_file())
    if not files:
        return "No documents available."
    return "Available documents:\n" + "\n".join(f"- {name}" for name in files)


@tool
def read_document(filename: str) -> str:
    """Read the full text of a document by filename.

    Args:
        filename: The document file name, e.g. 'leave_policy.txt'.
    """
    file_path = DOCS_DIR / filename
    if not file_path.exists():
        return f"Error: Document '{filename}' not found."
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"Error reading '{filename}': {exc}"


# ---------- Agent factory ----------

SYSTEM_PROMPT = (
    "You are a helpful internal document assistant. "
    "Use the available tools to find and read documents before answering. "
    "If the user asks about a topic, first call list_documents to see what is available, "
    "then call read_document on the most relevant file. "
    "Answer concisely and always name the document you used as your source."
)


def build_agent() -> AgentExecutor:
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        temperature=0,
    )

    tools = [list_documents, read_document]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False)


def get_executor() -> AgentExecutor:
    """Return a cached AgentExecutor, creating it on first call."""
    global _executor
    if _executor is None:
        _executor = build_agent()
    return _executor
