"""
Chapter 4: Dynamic Prompts
===========================
The system prompt changes at runtime based on the context of each request.
A hotfix to main gets a different review depth than a feature branch to dev.

Concept: Middleware intercepts each invocation and reshapes the system prompt
on the fly — without the caller needing to know anything about prompt logic.
"""

from pathlib import Path
from deepagents import create_deep_agent
from langchain.agents.middleware import dynamic_prompt
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=6000,
    timeout=None,
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


@dynamic_prompt
def pr_context_prompt(request):
    """Adapt the review depth and urgency based on PR metadata."""
    runtime = getattr(request, "runtime", None)
    ctx = getattr(runtime, "context", None) or {}

    pr_type      = ctx.get("pr_type", "feature")        # feature | bugfix | hotfix | security
    target_branch = ctx.get("target_branch", "main")    # main | release/* | dev
    repo_size    = ctx.get("repo_size", "medium")        # small | medium | large

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


agent = create_deep_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    memory=[str(Path(__file__).parent / "AGENTS.md")],
    skills=[str(Path(__file__).parent / "skills" / "github-review")],
    middleware=[pr_context_prompt],
)

SAMPLE_PR_DIFF = """
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

result = agent.invoke(
    {"messages": [
        {"role": "user", "content": f"Review this pull request:\n\n{SAMPLE_PR_DIFF}"}
    ]},
    config={"configurable": {"context": {
        "pr_type": "feature",
        "target_branch": "main",
        "repo_size": "medium",
    }}},
)

print(result["messages"][-1].content)