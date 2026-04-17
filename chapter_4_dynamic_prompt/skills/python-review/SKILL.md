# ---
# name: Python code review checklist
# description: Detailed review criteria for Python code. Load when
#              reviewing .py files or Python snippets.
# ---

## Security checks
- No use of eval(), exec(), or pickle on untrusted input
- SQL queries use parameterised statements, never f-strings
- Secrets never hardcoded — check for API keys, passwords in code

## Performance checks  
- N+1 query patterns in ORM code (check loops with .get() or .filter())
- Unnecessary list materialisation — use generators where possible
- Missing @lru_cache on pure functions called in tight loops

## Async checks
- No blocking I/O (requests, open()) inside async functions
- asyncio.gather() used for concurrent calls, not sequential await
- Missing async context managers on aiohttp sessions