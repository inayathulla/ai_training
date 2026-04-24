"""
Single-Agent CLI Demo — Document Reader & Summarizer
Runs a LangChain tool-calling agent backed by Azure OpenAI.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from openai import NotFoundError

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

DOCS_DIR = BASE_DIR / "sample_documents"


def _normalize_azure_endpoint(endpoint: str) -> str:
    endpoint = endpoint.strip().rstrip("/")
    if "/openai" in endpoint:
        endpoint = endpoint.split("/openai", 1)[0]
    return endpoint


def _get_azure_config() -> dict[str, str]:
    config = {
        "azure_endpoint": _normalize_azure_endpoint(
            os.getenv("AZURE_OPENAI_ENDPOINT", "")
        ),
        "api_key": os.getenv("AZURE_OPENAI_API_KEY", "").strip(),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21").strip(),
        "azure_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip(),
    }

    missing = [name for name, value in config.items() if not value]
    if missing:
        missing_vars = ", ".join(missing)
        raise ValueError(
            f"Missing Azure OpenAI settings in {ENV_FILE}: {missing_vars}"
        )

    return config


def _format_not_found_error() -> str:
    config = _get_azure_config()
    deployment = config["azure_deployment"]
    deployment_hint = ""
    if deployment.startswith(("gpt-", "o1", "o3", "text-embedding-")):
        deployment_hint = (
            "\n- `AZURE_OPENAI_DEPLOYMENT` often needs your Azure deployment name, "
            f"not the base model name. You currently have `{deployment}`."
        )

    return (
        "Azure OpenAI returned 404 `Resource not found`.\n"
        "Check these values the app is using:\n"
        f"- endpoint: {config['azure_endpoint']}\n"
        f"- deployment: {deployment}\n"
        f"- api_version: {config['api_version']}\n"
        "Most likely causes:\n"
        "- `AZURE_OPENAI_ENDPOINT` must be the base resource URL, for example "
        "`https://<resource>.openai.azure.com`.\n"
        "- `AZURE_OPENAI_DEPLOYMENT` must match an existing Azure OpenAI deployment.\n"
        "- `AZURE_OPENAI_API_VERSION` must be supported by that resource."
        f"{deployment_hint}"
    )


# ---------- Tools the agent can call ----------

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


# ---------- Agent setup ----------

SYSTEM_PROMPT = (
    "You are a helpful internal document assistant. "
    "Use the available tools to find and read documents before answering. "
    "If the user asks about a topic, first call list_documents to see what is available, "
    "then call read_document on the most relevant file. "
    "Answer concisely and always name the document you used as your source."
)


def build_agent() -> AgentExecutor:
    config = _get_azure_config()

    llm = AzureChatOpenAI(
        azure_endpoint=config["azure_endpoint"],
        api_key=config["api_key"],
        api_version=config["api_version"],
        azure_deployment=config["azure_deployment"],
        temperature=0,
    )

    tools = [list_documents, read_document]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


# ---------- CLI loop ----------

def main() -> None:
    try:
        executor = build_agent()
    except ValueError as exc:
        print(f"\nConfiguration error: {exc}\n")
        return

    print("\nDocument Assistant — ask me about our internal policies.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break

        try:
            result = executor.invoke({"input": user_input})
        except NotFoundError:
            print(f"\nConfiguration error:\n{_format_not_found_error()}\n")
            continue
        print(f"\nAgent: {result['output']}\n")


if __name__ == "__main__":
    main()
