# Plan & Roadmap

## Goals
1. Show an agent can use real MCP servers without trusting them blindly.
2. Make every security decision observable (audit log) and testable (offline checks).
3. Keep the demo reproducible: pinned versions, recorded hashes, deterministic validator.

## Phases
| Phase | Scope | Status |
|---|---|---|
| 1 | Filesystem + Fetch MCP wiring, sandbox sample project | ✅ Done |
| 2 | Path/URL/argument policy, tool allow-lists | ✅ Done |
| 3 | Environment allow-list (Windows + POSIX), audit log | ✅ Done |
| 4 | Package pinning with npm/PyPI integrity hashes | ✅ Done |
| 5 | Report validator (ranks, category counts) | ✅ Done |
| 6 | Package into a CLI (`python -m`) instead of notebook cells | ⏳ Planned |
| 7 | CI job running the offline policy tests | ⏳ Planned |
| 8 | Hash refresh script for intentional upgrades | ⏳ Planned |

## Design decisions
- **Client-side policy, not prompt rules:** `validate_call` runs before anything is forwarded.
- **Audit records exclude content:** only timestamp, session, trace, call id, server, tool, status.
- **Fail closed:** unknown tools are logged as `unapproved_tool` and blocked.
