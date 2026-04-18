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

Requires: GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY, GITHUB_REPOSITORY, GOOGLE_API_KEY
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from deepagents import create_deep_agent
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents.backends import FilesystemBackend

from dotenv import load_dotenv

from utils import (
    rename_tool,
    get_documentation_tools,
    get_release_tools,
    get_issue_tools,
    get_code_review_tools,
    get_coding_tools,
)

load_dotenv()

# ── LLM + GitHub tools ──────────────────────────────────────────────────────
HERE = Path(__file__).parent

llm = ChatGoogleGenerativeAI(
    model="gemma-4-31b-it",
    temperature=0,
    max_tokens=6000,
    max_retries=2,
)

github = GitHubAPIWrapper()
toolkit = GitHubToolkit.from_github_api_wrapper(github, include_release_tools=True)
tools = [rename_tool(t) for t in toolkit.get_tools()]

# ── Subagent definitions ─────────────────────────────────────────────────────
# Keep descriptions and system prompts short — they're injected into the
# coordinator's context window on every call.

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
# No memory or skills on the coordinator — it only routes tasks.
# The subagents carry all domain knowledge through their own system prompts.

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
    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": "Review all open pull requests and leave comments.",
            }
        ]
    })
    print(result["messages"][-1].content)
