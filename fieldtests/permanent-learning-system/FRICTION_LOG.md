# Friction log

One entry per observation. Sources: the human's notes during the run, and the observer's review of the transcript, commits and `state.yaml`.

## Categories

| Code | Meaning |
|---|---|
| `IGNORED` | The agent broke or skipped a spec rule. |
| `IN-THE-WAY` | Following a rule made the conversation worse or slower without a matching benefit. |
| `STATE` | Recording something in `state.yaml` or through the tools was awkward, lossy or impossible. |
| `TOOLING` | Setup, commands, branches, approvals or CI got in the way. |
| `GOOD` | A rule clearly improved the outcome. Worth keeping when the spec is trimmed. |

## Entry format

```markdown
### <ID> <CODE> <short title>
- Gate / stage: <e.g. Gate 1, capture intent>
- Where: <transcript message, commit SHA or state record>
- Rule: <file and section, if a rule is involved>
- What happened: <facts>
- Impact: <low / medium / high, and why>
- Proposed action: <fix now / eval / trim / later>
```

## Gate 1 — Intent Captured

_No entries yet._

## Gate 2 — Ambition Explored

_No entries yet._
