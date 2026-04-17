## GitHub Project Conventions

### Branching
- Feature branches: `feat/<ticket-id>-short-description`
- Bug fixes: `fix/<ticket-id>-short-description`
- Releases: `release/v<major>.<minor>`
- Hotfixes: `hotfix/<ticket-id>-short-description`

### Pull Requests
- Max 400 lines changed per PR — larger PRs must be split.
- Every PR needs at least one reviewer assigned before merging.
- Required labels: one of `bug`, `feature`, `chore`, `docs`, `security`.
- PRs targeting `main` or `release/*` require two approvals.
- PR descriptions must include: what changed, why, and how to test.

### Issues
- All bugs must include: steps to reproduce, expected vs actual behaviour, environment info.
- Triage labels: `P0` (production down), `P1` (major), `P2` (minor), `P3` (nice to have).
- Issues older than 90 days without activity are auto-closed.

## Review Format
Respond in this format only:

### Blockers
- [issue] — [why it matters] — [fixed code]

### Suggestions
- [issue] — [why it matters]

### What's good
- [one or two things done well]