---
name: GitHub PR review checklist
description: >
  Detailed review criteria for GitHub pull requests. Load when reviewing
  PR diffs or any code changes in a GitHub context.
---

## Security checks
- No hardcoded secrets, API keys, or credentials in source code
- SQL queries use parameterised statements or ORM — never f-string/`%` interpolation
- No use of `eval()`, `exec()`, or `pickle` on untrusted user input
- Authentication and authorisation checks present on all sensitive endpoints
- Sensitive routes must not be reachable without a valid session or token

## Performance checks
- N+1 query patterns in ORM code (check loops that call `.get()` or `.filter()`)
- Unnecessary full-table loads: `db.query(Model).all()` then filtering in Python
- Per-row `db.commit()` inside a loop — batch commits instead
- Missing database indexes on frequently-filtered or joined columns

## Async checks
- No blocking I/O (`requests`, `open()`) inside `async def` functions — use `httpx`/`aiofiles`
- `asyncio.gather()` used for concurrent calls, not sequential `await`
- Unclosed connections or sessions — use async context managers

## Code quality checks
- Missing type hints on public functions (required per team conventions)
- Raw `dict` used where a Pydantic model would be safer
- Bare `except:` clauses that swallow all errors silently
- Dead code, commented-out blocks, or debug `print()` statements left in
