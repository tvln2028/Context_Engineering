"""
Chapter 6: Multi-Agent Capstone
================================
A coordinator agent delegates to five specialist subagents.
The coordinator never touches GitHub directly — it only routes work.

Subagents:
  - documentation_agent  — writes README files and API docs
  - release_notes_agent  — generates release notes from PRs and tags
  - issue_agent          — searches, reads, and comments on issues
  - code_review_agent    — reviews open PRs and file diffs
  - coding_agent         — implements code changes and opens PRs

Requires (live GitHub): GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY, GITHUB_REPOSITORY, OPENAI_API_KEY
Without GitHub credentials, runs in demo mode with sample PR data (like chapters 0–5).
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")
load_dotenv(HERE / ".env")

from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from deepagents.backends import FilesystemBackend

from utils import (
    rename_tool,
    get_documentation_tools,
    get_release_tools,
    get_issue_tools,
    get_code_review_tools,
    get_coding_tools,
)

GITHUB_ENV_VARS = ("GITHUB_REPOSITORY", "GITHUB_APP_ID", "GITHUB_APP_PRIVATE_KEY")

DEMO_PR_DIFF = """
PR #87: Add user search endpoint
Branch: feat/user-search → main
Author: bob (mid-level)

diff --git a/src/api/users.py b/src/api/users.py
+@router.get("/users/search")
+def search_users(name: str, db: Session = Depends(get_db)):
+    query = f"SELECT * FROM users WHERE name LIKE '%{name}%'"
+    results = db.execute(query).fetchall()
+    return results
"""

LIVE_USER_MESSAGE = "Review all open pull requests and leave comments."

DEMO_USER_MESSAGE = (
    "Review this pull request and provide feedback. "
    "Delegate to code_review_agent.\n\n"
    f"{DEMO_PR_DIFF}"
)


def github_configured() -> bool:
    return all(os.getenv(key) for key in GITHUB_ENV_VARS)


def resolve_github_private_key_path() -> None:
    """Resolve relative private-key paths (e.g. resources/key.pem) to an absolute file."""
    key = os.getenv("GITHUB_APP_PRIVATE_KEY")
    if not key:
        return
    path = Path(key)
    if path.is_file():
        os.environ["GITHUB_APP_PRIVATE_KEY"] = str(path.resolve())
        return
    for base in (HERE, ROOT, Path.cwd()):
        candidate = (base / path).resolve()
        if candidate.is_file():
            os.environ["GITHUB_APP_PRIVATE_KEY"] = str(candidate)
            return


def build_tools():
    from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
    from langchain_community.utilities.github import GitHubAPIWrapper

    resolve_github_private_key_path()
    github = GitHubAPIWrapper()
    toolkit = GitHubToolkit.from_github_api_wrapper(github, include_release_tools=True)
    return [rename_tool(t) for t in toolkit.get_tools()]


# ── LLM ──────────────────────────────────────────────────────────────────────

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=6000,
    max_retries=2,
)

DEMO_MODE = not github_configured()
tools = [] if DEMO_MODE else build_tools()

if DEMO_MODE:
    print(
        "Demo mode: GitHub credentials not set. "
        "Set GITHUB_REPOSITORY, GITHUB_APP_ID, and GITHUB_APP_PRIVATE_KEY in .env "
        "for live GitHub access.\n",
        flush=True,
    )
else:
    print(f"Live GitHub mode: {os.getenv('GITHUB_REPOSITORY')}\n", flush=True)

# ── Subagent definitions ─────────────────────────────────────────────────────

documentation_agent = {
    "name": "documentation_agent",
    "description": "Writes and updates README files and API docs.",
    "system_prompt": (
        "Write and maintain project documentation. "
        "Read existing files, search code, create or update docs. "
        "Include the full result of your work in your final message."
    ),
    "tools": get_documentation_tools(tools),
}

release_notes_agent = {
    "name": "release_notes_agent",
    "description": "Generates release notes by inspecting the latest releases and PRs.",
    "system_prompt": (
        "Generate clear release notes for new software releases. "
        "Use tools to gather release info, PRs, and issues. "
        "Include the full release notes text in your final message."
    ),
    "tools": get_release_tools(tools),
}

issue_agent = {
    "name": "issue_agent",
    "description": "Searches, reads, and comments on GitHub issues.",
    "system_prompt": (
        "Manage and resolve GitHub issues. "
        "Search, read, and comment using the provided tools. "
        "Include a summary of all actions taken in your final message."
    ),
    "tools": get_issue_tools(tools),
}

code_review_agent = {
    "name": "code_review_agent",
    "description": "Reviews open PRs and provides code quality feedback.",
    "system_prompt": (
        "Review pull requests on GitHub. "
        "List open PRs, examine changed files, and provide concise feedback. "
        "When no GitHub tools are available, review the PR diff included in the task. "
        "Include your full review in your final message."
    ),
    "tools": get_code_review_tools(tools),
}

coding_agent = {
    "name": "coding_agent",
    "description": "Implements code changes on a branch and opens a PR.",
    "system_prompt": (
        "Implement code changes autonomously. "
        "Explore the repo, create a branch, make changes, open a PR. "
        "Include the PR link or summary of changes in your final message."
    ),
    "tools": get_coding_tools(tools),
}

# ── Coordinator ───────────────────────────────────────────────────────────────

COORDINATOR_PROMPT = (
    "You are a GitHub project coordinator. "
    "Delegate every task to the right subagent — never call GitHub tools yourself.\n"
    "- documentation_agent: README and API docs\n"
    "- release_notes_agent: release notes\n"
    "- issue_agent: search, read, comment on issues\n"
    "- code_review_agent: review open PRs\n"
    "- coding_agent: implement changes and open PRs"
)

agent = create_deep_agent(
    model=llm,
    system_prompt=COORDINATOR_PROMPT,
    subagents=[
        documentation_agent,
        release_notes_agent,
        issue_agent,
        code_review_agent,
        coding_agent,
    ],
    backend=FilesystemBackend(root_dir=str(HERE), virtual_mode=True),
)

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    user_message = DEMO_USER_MESSAGE if DEMO_MODE else LIVE_USER_MESSAGE
    print("Running coordinator agent...", flush=True)
    result = agent.invoke({
        "messages": [{"role": "user", "content": user_message}]
    })
    print(result["messages"][-1].content)
