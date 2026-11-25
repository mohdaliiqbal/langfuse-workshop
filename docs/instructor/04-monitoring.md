---
title: "Workshop: Instructor Notes for Monitoring"
description: "Facilitator notes for the monitoring overview, error analysis, and the disagreement and all-caps signal evaluators."
---

# 04 Monitoring

Learner guide: [04 Monitoring](../learner/04-monitoring.md)

- [4.1 Error analysis](../learner/04-monitoring/error-analysis.md)
- [4.2 Capturing signals](../learner/04-monitoring/capturing-signals.md)

## Instructor notes

The overview has no code change. Dashboards are a link out. Sections 4.1 and 4.2 are the labs.

Demo order: error analysis while the room still has to read traces, then capturing signals so the evaluators are the last thing they turn on.

### 4.1 Error analysis

- `uv run python scripts/seed_error_analysis.py` writes 20 traces. Seven are ordinary one-turn answers. The other 13 each have one failure: 5 out-of-scope replies, 2 family-voice replies, 2 "I'm your kid." identity replies, and 4 long unstructured replies. The failure is only on the latest answer.
- The seed is not an OpenTelemetry replay of `data/seed-traffic-followups-traces.json`. That file stays in the TypeScript repo. The scenarios and the trace shape (`dad-it-support-chat-turn`, tools, messages input) match.
- The queue is named `error analysis` with `open coding` (Text) and `pass or fail` (Categorical: pass and fail). The annotation script looks for those exact names.
- `uv run python scripts/seed_error_analysis_annotations.py` fills the queue for a short demo. Notes do not name the clusters. A second run updates the same scores.
- Do not hand out the cluster names before open coding. The collapsed list in the lesson is a check, not the Halo prompt.
- Do not publish the more specific prompt in this lab. That happens in 07.

### 4.2 Capturing signals

- **Detect User Disagreement** is LLM-as-a-judge. **Detect User Frustration (ALL CAPS)** is a deterministic code evaluator that runs as TypeScript inside Langfuse. Learners do not port that snippet to Python. The observation input is the messages array either way.
- They add the OpenAI connection in this section and pick **5.6 Luna** (`gpt-5.6-luna`).
- Both evaluators target the root `dad-it-support-chat-turn` agent observation.
- Bind `conversation_history` to **Input → messages** and `last_user_message` to **Input → messages → last** with **Use**. Do not type a JSONPath.
- **Execute** is what turns the evaluator on. New turns are the check, not the seeded batch.
- The bonus template is **Detect conversation signals**. Do not replace the two evaluators with it.

## Watch for

- Re-running the error-analysis seed. Each run mints new traces.
- Selecting a child generation instead of the root agent observation.
- Mapping `conversation_history` to a single message.
- Clicking **Create evaluator** and not **Execute**.
- Treating the all-caps score as proof of anger.
