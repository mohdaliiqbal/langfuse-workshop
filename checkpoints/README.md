# Checkpoints

`checkpoints/` holds the milestone files for each chapter. `scripts/use_checkpoint.py` copies a snapshot over `app/server.py`, `app/support_agent.py`, and `app/tools.py`.

| Chapter | Snapshot | What the code can do |
| --- | --- | --- |
| 00 Setup, 01 Base app, 02 Tracing | `00-setup` | Untraced OpenAI tool loop |
| 03 Prompt management | `03-prompt-management` | Traced agent and tools, local system prompt |
| 04 Monitoring through 08 Wrap-up | `reference` | Traced agent, Langfuse prompt fetch, user and session attributes |

`checkpoints/reference/` must stay identical to those three files in `app/`. `scripts/use_checkpoint.py --check` fails when they drift.

Restore the finished app with:

```bash
uv run python scripts/use_checkpoint.py reference
```
