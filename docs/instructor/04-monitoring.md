---
title: "Workshop: Instructor Notes for Monitoring"
description: "Facilitator notes for the monitoring overview, error analysis, topics, and the disagreement and all-caps signal evaluators."
---

# 04 Monitoring

Learner guide: [04 Monitoring](../learner/04-monitoring.md)

- [4.1 Error analysis](../learner/04-monitoring/error-analysis.md)
- [4.2 Detect topics and issues](../learner/04-monitoring/topics.md)
- [4.3 Capturing signals](../learner/04-monitoring/capturing-signals.md)

## Instructor notes

The overview has no code change. Dashboards are a link out. Sections 4.1, 4.2, and 4.3 are the labs. Each section seeds its own traces. Do not seed on the overview.

Demo order: error analysis while the room still has to read traces, then topics on the 200 traces that section seeds, then capturing signals so the evaluators are the last thing they turn on. Learners add the OpenAI connection in topics. Capturing signals reuses it.

### 4.1 Error analysis

- `uv run python scripts/seed_error_analysis.py` writes 20 traces. Seven are ordinary one-turn answers. The other 13 each have one failure: 5 out-of-scope replies, 2 family-voice replies, 2 "I'm your kid." identity replies, and 4 long unstructured replies. The failure is only on the latest answer.
- The seed is not an OpenTelemetry replay of `data/seed-traffic-followups-traces.json`. That file stays in the TypeScript repo. The scenarios and the trace shape (`dad-it-support-chat-turn`, tools, messages input) match.
- The queue is named `error analysis` with `open coding` (Text) and `pass or fail` (Categorical: pass and fail). The annotation script looks for those exact names.
- `uv run python scripts/seed_error_analysis_annotations.py` fills the queue for a short demo. Notes do not name the clusters. A second run updates the same scores.
- Do not hand out the cluster names before open coding. The collapsed list in the lesson is a check, not the Halo prompt.
- Do not publish the more specific prompt in this lab. That happens in 07. Close with one line into topics.

### 4.2 Detect topics and issues

- This is a configuration-and-reading walkthrough. Add the OpenAI connection, seed, then open the empty Topics page and click **Set up topics**. Keep Intent, Sentiment, Outcome, and Issues with the recommended models, filter **Query** to `tags:topics-seed` so the map contains the 200 workshop traces, keep sampling at 100%, review the matching-trace count, and click **Start analyzing**. After the first map exists, use **Edit map** for later changes. Do not assume every project map has all four facets.
- `uv run python scripts/seed_topics_traces.py` writes 200 traces tagged `topics-seed`. 110 are ordinary iPhone requests. 60 are laptop requests, 30 about printing and paper and 30 about the laptop's Wi-Fi, and each answer offers a Windows path and an Apple path because Specs does not know which laptop Dad has. 30 are stuck follow-ups that repeat the same steps after Dad says they failed. 100 of the 200 (at least 40%) have Dad sounding frustrated. The seed is not idempotent. The newest trace is about 10 minutes old and the batch spans about five days, so it sits inside the 7-day matching window.
- The seed is not an OpenTelemetry replay of the upstream template corpus. It sends the same 200 scenarios, in the same order, to the Langfuse OpenTelemetry endpoint with explicit timestamps, because the SDK's observation helpers always start now. `--check` and `--dry-run` need no keys.
- The wizard's review screen currently reports the last 30 days; after a map exists, the **Edit map** preview can report the last 7 days. New traces can take about 5 minutes after their last activity to appear. If the count is empty, do not save an empty map. Check the seed, the filter, and the window first. A map marked **PAUSED** is not analyzing new traces.
- After analysis fills in, compare Treemap and Scatter, try the **Unassigned** toggle, click one tile on each enabled facet, and use **Open in Tracing**. The groups are close to deterministic. A model names and describes them afterward, so labels and counts vary. Ask learners to check each label in Tracing.
- Land the insights in this order. First walk the facets as a map of how the system is used, including groups where the product is working. On Intent, laptop Wi-Fi and laptop printing are missing context: the answers hedge between Windows and Apple, and the fix is adding the laptop to `DEFAULT_SUPPORT_CONTEXT` in `app/support_data.py`. Read the suggested prompt that names the phone and the laptop. Do not publish it. The prompt published in 07 is the error-analysis one. On Sentiment, connect unresolved Wi-Fi conversations, all-caps lines, and "No, that menu isn't there" to the disagreement and all-caps scores. On Issues, repeated failed troubleshooting is a possible prompt fix, and mismatched searches are a question about the help library. Halo can open a group, point at the step that led to an issue, and flag false positives.

### 4.3 Capturing signals

- **Detect User Disagreement** is LLM-as-a-judge. **Detect User Frustration (ALL CAPS)** is a deterministic code evaluator that runs as TypeScript inside Langfuse. Learners do not port that snippet to Python. The observation input is the messages array either way.
- They added the OpenAI connection in topics. If they skipped that section, they add it here, then pick **5.6 Luna** (`gpt-5.6-luna`).
- Both evaluators target the root `dad-it-support-chat-turn` agent observation.
- Bind `conversation_history` to **Input → messages** and `last_user_message` to **Input → messages → last** with **Use**. Do not type a JSONPath.
- **Execute** is what turns the evaluator on. New turns are the check, not the seeded batch.
- The bonus template is **Detect conversation signals**. Do not replace the two evaluators with it.

## Watch for

- Re-running the error-analysis seed or the topics seed. Each run mints new trace IDs.
- Treating a topics tile name or count as exact. The groups are close to deterministic. A model names and describes them afterward.
- Publishing the laptop prompt in this lab. The prompt published in 07 is the error-analysis one.
- Saving a map with an empty matching-trace count. Check the seed, the filter, and the last 7 days first.
- Treating a **PAUSED** map as if it were analyzing new traces.
- Narrowing the topics filter on this project until the seeded traces drop out. A `tags:topics-seed` or empty filter is the setup.
- Seeding topics in a project where the 4.3 evaluators already run, for example on a second pass. They score all 200 new traces, which means 200 LLM-judge calls on the project's OpenAI connection. The ALL CAPS template needs more than 70% capitals, so the mixed-case all-caps lines in this seed score 0.
- Selecting a child generation instead of the root agent observation.
- Mapping `conversation_history` to a single message.
- Clicking **Create evaluator** and not **Execute**.
- Treating the all-caps score as proof of anger.
