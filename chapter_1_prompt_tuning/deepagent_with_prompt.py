"""
Chapter 1: Prompt Tuning
=========================
Same agent, same model — but a crafted system prompt dramatically changes
what the agent notices, how it prioritises, and what it outputs.

Concept: The system prompt is the single highest-leverage context engineering
lever. Get this right before adding anything else.
"""

from deepagents import create_deep_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=6000,
    reasoning_format="parsed",
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

agent = create_deep_agent(model=llm, system_prompt=SYSTEM_PROMPT)

# Realistic fake PR diff — no API key needed
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