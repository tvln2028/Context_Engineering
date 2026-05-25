# Context Engineering Tutorial

> **What you'll build**: A fully autonomous GitHub agent that reviews PRs, manages issues, writes documentation, generates release notes, and implements code changes — all in one coordinated multi-agent system.

Context engineering is the discipline of controlling *what an AI agent knows and when it knows it*. A great prompt is table stakes. The difference between a toy agent and a production one is how carefully you manage the context flowing in and out of it.

This tutorial walks through 8 progressive chapters, each adding one context engineering technique on top of the last.

---

## Tutorial Arc

| Chapter | Technique | What you'll learn |
|---|---|---|
| [0 — DeepAgent Basics](#chapter-0) | Raw agent | How a deep agent thinks and acts |
| [1 — Prompt Tuning](#chapter-1) | System prompt | How the prompt shapes every decision |
| [2 — AGENTS.md Memory](#chapter-2) | File memory | Loading persistent context from files |
| [3 — Skills](#chapter-3) | On-demand skills | Loading specialised knowledge on demand |
| [4 — Dynamic Prompts](#chapter-4) | Runtime context | Adapting the prompt to each request at runtime |
| [5 — Context Offloading](#chapter-5) | File scratch-pad | Offloading intermediate results to keep context clean |
| [6 — Multi-Agent Capstone](#chapter-6) | Subagents | Coordinating specialist agents for complex tasks |

---

## Prerequisites

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`
- An [OpenAI API key](https://platform.openai.com/api-keys) (works for all chapters)
- For chapters 6 & 7: a GitHub App with repo access (see setup below)

## Installation

```bash
# Clone and install dependencies
git clone <repo-url>
cd context_engineering
uv sync
```

Run any chapter (no venv activation required):

```bash
uv run python chapter_0_deepagent/simple_deepagent.py
```

On **Windows PowerShell**, if you prefer activating the venv first, use `.venv` (not `venv`):

```powershell
.\.venv\Scripts\Activate.ps1
python chapter_0_deepagent/simple_deepagent.py
```

## Environment Variables

Copy `.env.example` to `.env` in the root:

```bash
OPENAI_API_KEY=your_key_here
```

For **chapter 6**, also set in the chapter's `.env`:

```bash
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
GITHUB_REPOSITORY=owner/repo
OPENAI_API_KEY=your_key_here
```

---

## Chapters 0–5: No GitHub Account Required

All examples in chapters 0–5 use **realistic fake input strings** — a sample PR diff, a fake issue body, etc. You only need an OpenAI API key.

---

<a id="chapter-0"></a>
## Chapter 0 — DeepAgent Basics
`chapter_0_deepagent/`

A bare-minimum deep agent. No system prompt, no tools, no memory — just the model reasoning over a GitHub issue. Shows what a deep agent is and how to invoke it.

```bash
uv run python chapter_0_deepagent/simple_deepagent.py
```

---

<a id="chapter-1"></a>
## Chapter 1 — Prompt Tuning
`chapter_1_prompt_tuning/`

A system prompt transforms a generic reasoner into a focused PR reviewer. Same agent, dramatically different behaviour.

```bash
uv run python chapter_1_prompt_tuning/deepagent_with_prompt.py
```

---

<a id="chapter-2"></a>
## Chapter 2 — AGENTS.md Memory
`chapter_2_agents.md/`

Load persistent project context — branching rules, PR conventions, issue triage labels — from an `AGENTS.md` file. The agent now follows your team's specific rules without being told each time.

```bash
uv run python chapter_2_agents.md/agent_with_md.py
```

---

<a id="chapter-3"></a>
## Chapter 3 — Skills
`chapter_3_skills/`

Skills are on-demand knowledge files loaded mid-conversation. The agent only loads the GitHub PR review checklist when it's actually reviewing a PR — keeping other contexts clean.

```bash
uv run python chapter_3_skills/agent.py
```

---

<a id="chapter-4"></a>
## Chapter 4 — Dynamic Prompts
`chapter_4_dynamic_prompt/`

Runtime context shapes the system prompt *per request*. A hotfix targeting `main` gets a different review depth than a feature branch targeting `dev`.

```bash
uv run python chapter_4_dynamic_prompt/agent.py
```

---

<a id="chapter-5"></a>
## Chapter 5 — Context Offloading
`chapter_5_offload/`

Large PRs exceed context windows. The agent offloads per-file review notes to disk and synthesises them at the end — keeping the active context lean throughout.

```bash
uv run python chapter_5_offload/agent.py
```

---

<a id="chapter-6"></a>
## Chapter 6 — Multi-Agent Capstone ⭐
`chapter_6_capstone/`

Everything comes together. A coordinator agent delegates to five specialist subagents:
- **documentation_agent** — writes README files and API docs
- **release_notes_agent** — generates release notes from PRs and tags
- **issue_agent** — searches, reads, and comments on issues
- **code_review_agent** — reviews open PRs and file diffs
- **coding_agent** — implements code changes and opens PRs

Requires GitHub App credentials for live API access. Without them, the script runs in **demo mode** with sample PR data (same pattern as chapters 0–5).

```bash
# Demo mode (OPENAI_API_KEY only):
uv run python chapter_6_capstone/agent.py

# Live GitHub mode — add to .env:
# GITHUB_APP_ID=...
# GITHUB_APP_PRIVATE_KEY=...
# GITHUB_REPOSITORY=owner/repo
uv run python chapter_6_capstone/agent.py
```

---

## Key Concepts at a Glance

| Term | What it is |
|---|---|
| `create_deep_agent` | Creates a deep agent — a model with planning, memory, skills and tools |
| `memory=["AGENTS.md"]` | Files loaded into the system prompt at startup |
| `skills=["skills/"]` | Files the agent can load on demand mid-conversation |
| `middleware=[fn]` | Functions that modify the prompt/context at runtime |
| `backend=FilesystemBackend` | Gives the agent a read/write scratch-pad for large contexts |
| `subagents=[...]` | Specialist agents the coordinator can delegate tasks to |
