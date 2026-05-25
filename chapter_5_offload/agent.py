"""
Chapter 5: Context Offloading
===============================
Large PRs can span dozens of files and overwhelm the context window. The
agent offloads per-file review notes to disk and synthesises them at the
end — keeping the active context lean throughout.

Concept: A FilesystemBackend gives the agent a read/write scratch-pad.
Instead of holding all findings in memory at once, it writes intermediate
results to files and reads them back only when synthesising.
"""

from pathlib import Path
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import dynamic_prompt
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import sys
sys.path.insert(0, str(Path(__file__).parent))
from example import SAMPLE_PR_DIFF  # Large multi-file PR diff (in same directory)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=6000,
    max_retries=2,
)

SYSTEM_PROMPT = """
You are a senior engineer performing code reviews on GitHub pull requests.
Your goal: help the author improve their code, not just find faults.

Always:
- Identify the 1-2 highest-impact issues first
- Suggest the fixed code, not just the problem
- Distinguish blockers (must fix) from suggestions (nice to fix)
- Keep feedback concise — engineers are busy

Never:
- Flag style issues already handled by a linter
- Repeat the same point twice
- Give vague feedback like "improve error handling"
"""

REVIEW_STRATEGY = """
When reviewing a PR with more than 3 files changed:
1. Read each file's diff and use write_file to save per-file findings:
   write_file("review/db_queries.md", "## db/queries.py\n- ...")
2. After all files are reviewed, read_file each findings file.
3. Synthesise into a single structured PR review — never quote raw diffs.

This strategy keeps the active context clean when reviewing large GitHub
PRs that span many files.
"""


@dynamic_prompt
def pr_context_prompt(request):
    """Adapt the review depth and urgency based on PR metadata."""
    runtime = getattr(request, "runtime", None)
    ctx = getattr(runtime, "context", None) or {}

    pr_type       = ctx.get("pr_type", "feature")
    target_branch = ctx.get("target_branch", "main")
    repo_size     = ctx.get("repo_size", "medium")

    type_guide = {
        "feature":  "Focus on design, scalability, and test coverage.",
        "bugfix":   "Focus on root cause. Is this a full fix or just a workaround?",
        "hotfix":   "Speed matters. Flag regressions only. Approve if production-safe.",
        "security": "Treat this as P0. Check for injection, auth bypass, and data exposure.",
    }

    urgency = ""
    if target_branch == "main":
        urgency = "This targets main — be thorough, catch everything."
    elif target_branch.startswith("release"):
        urgency = "Release branch — blockers only, no feature suggestions."

    scale_note = ""
    if repo_size == "large":
        scale_note = "Large repo: flag cross-service impact and backward compatibility risks."

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"PR type: {type_guide.get(pr_type, type_guide['feature'])}\n"
        f"{urgency}\n"
        f"{scale_note}"
    )


HERE = Path(__file__).parent

agent = create_deep_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT + REVIEW_STRATEGY,
    memory=[str(HERE / "AGENTS.md")],
    skills=[str(HERE / "skills" / "github-review")],
    middleware=[pr_context_prompt],
    # FilesystemBackend gives the agent a scratch-pad for per-file notes.
    backend=FilesystemBackend(root_dir=str(HERE), virtual_mode=True),
)

result = agent.invoke(
    {"messages": [
        {"role": "user", "content": f"Review this large pull request:\n\n{SAMPLE_PR_DIFF}"}
    ]},
    config={"configurable": {"context": {
        "pr_type": "feature",
        "target_branch": "main",
        "repo_size": "large",
    }}},
)

print(result["messages"][-1].content)