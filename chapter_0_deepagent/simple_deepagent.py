"""
Chapter 0: DeepAgent Basics
============================
The simplest possible deep agent — no system prompt, no tools, no memory.
Just a model that reasons about a GitHub issue.

Concept: What is a deep agent? It's a model that can plan and act over
multiple steps. Even without tools, it reasons more deeply than a single LLM call.
"""

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

agent = create_deep_agent(model=llm)

# Realistic fake GitHub issue — no API key needed
SAMPLE_ISSUE = """
Issue #42: Login fails with OAuth when redirect_uri has query params
Status: open
Labels: bug, auth
Author: alice

Description:
When users log in via GitHub OAuth and the redirect_uri contains query
parameters (e.g. ?next=/dashboard), the OAuth callback handler throws
a 400 Bad Request. The redirect_uri is not being URL-encoded before
being appended to the authorization URL.

Steps to reproduce:
1. Set OAUTH_REDIRECT_URI=https://app.example.com/callback?next=/dashboard
2. Click "Login with GitHub"
3. GitHub returns: 400 redirect_uri_mismatch

Expected: Successful redirect to /dashboard after login
Actual: 400 error from GitHub OAuth
"""

result = agent.invoke({
    "messages": [
        {"role": "user", "content": f"Summarise this GitHub issue and suggest next steps:\n\n{SAMPLE_ISSUE}"}
    ]
})

print(result["messages"][-1].content)