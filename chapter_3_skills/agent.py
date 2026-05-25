"""
Chapter 3: Skills
==================
Skills are on-demand knowledge files loaded mid-conversation. Unlike memory
(always loaded), skills are fetched only when relevant — keeping other
contexts uncluttered.

Concept: The agent loads the GitHub PR review checklist skill only when it's
actually reviewing a PR. In a multi-task agent this avoids polluting planning
or issue-triage contexts with review-specific instructions.
"""

from pathlib import Path
from deepagents import create_deep_agent
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

agent = create_deep_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    memory=[str(Path(__file__).parent / "AGENTS.md")],
    # The github-review skill is loaded on demand — not injected upfront.
    skills=[str(Path(__file__).parent / "skills" / "github-review"),
    str(Path(__file__).parent / "skills" / "Python-review"),
    ],
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

result = agent.invoke({
    "messages": [
        {"role": "user", "content": f"Review this pull request:\n\n{SAMPLE_PR_DIFF}"}
    ]
})

print(result["messages"][-1].content)