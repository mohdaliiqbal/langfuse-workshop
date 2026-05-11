# Lab 7: Offline Evals — Datasets & Experiments — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 7" if your assistant has already loaded `AGENTS.md`.

---

## Before we start

Tell the attendee:

> "No code changes to the app in this lab — we use a standalone script for the experiment, and you'll configure the evaluator in the Langfuse UI. Open the lab README in your browser for screenshots:
> **https://github.com/mohdaliiqbal/langfuse-workshop/blob/main/labs/07-offline-evals/README.md**
>
> You'll need your terminal open. I'll tell you exactly when and what to run."

---

## Your task

You are teaching Lab 7 as a live instructor. The framing for this whole lab:

> *"To systematically evaluate and improve your application you need two things: a set of **examples** that cover the scope your system is expected to handle, and a set of **evaluators** that tell you whether the system meets your expectations on those examples."*

The full loop we'll walk through:

1. **Scope the dataset** — what the system is expected to cover (we've prepped this for you)
2. **Seed the dataset** in Langfuse via a script
3. **Configure a platform LLM-as-a-judge** evaluator in the Langfuse UI to score experiment runs
4. **Run it as an experiment** — your real `answer()` against every item; the platform evaluator scores automatically
5. **Look at the items that failed** — concrete signal, not vibes
6. **Iterate on the prompt** and re-run — measure the change

Guide the attendee through this loop, asking them to confirm each result before moving on.

---

## Step 1 — Scope and seed the dataset

**Announce**: A dataset is a curated collection of input/expected-output pairs covering the scope your assistant needs to handle. We've prepared 9 representative DataStream questions covering pricing, connectors, troubleshooting, security, and more — enough to spot regressions in any of those areas.

**Terminal prompt**: "In your terminal, run:"
```bash
uv run python labs/07-offline-evals/create_dataset.py
```

**Explain**: The script calls `langfuse.create_dataset_item()` once per question. Each item has an **input** (the question your app will see) and an **expected_output** (the essential information a correct answer should contain). The expected output is your *opinion* of what good looks like — without it, you have nothing to evaluate against.

**Langfuse check**: "In Langfuse, go to **Datasets**. Click `datastream-support-benchmark` — you should see 9 items with their expected answers."

📸 **See Task 7.1 in the lab README** for screenshots of the dataset and item views.

**✋ Check in**: "Do you see 9 items in the dataset? Click one — what does the expected output say?"

---

## Step 2 — Configure the LLM-as-a-judge evaluator in Langfuse

**Announce**: Before we run any experiment we set up the evaluator that will score each run. We do this in the Langfuse UI — no code — so the rubric is configurable and shared across all future runs against this dataset.

**Direct the attendee** through these UI steps:

1. Go to **Evaluation** → **LLM-as-a-Judge** → **Create Evaluator**
2. Choose **Custom** and name it `answer-correctness`
3. Set **Run on** to **Dataset Runs** (not Observations — this is the key difference from Lab 5's evaluator)
4. Select the dataset `datastream-support-benchmark`
5. Paste this rubric as the evaluator prompt:
   ```
   You are evaluating a customer support response for correctness against
   an expected answer.

   Question: {{input}}
   Expected key information: {{expected_output}}
   Actual response: {{output}}

   Does the actual response correctly answer the question and contain the
   essential information from the expected answer? Partial credit is fine
   if the response is mostly correct.

   Respond with JSON only:
   {"contains_answer": <true/false>, "score": <0.0 to 1.0>, "reason": "<one sentence>"}
   ```
6. Map variables to dataset run fields:
   - `input` → dataset item input → JsonPath: `$["question"]`
   - `expected_output` → dataset item expected output → JsonPath: `$` (the full expected output string)
   - `output` → experiment item output → JsonPath: `$`
7. Set sampling to `100%` → **Execute**

📸 **See Task 7.2 in the lab README** for screenshots of the evaluator configuration.

**Explain**: The Lab 5 evaluator ran on **Observations** — every live production trace. This one runs on **Dataset Runs** — every experiment item recorded against `datastream-support-benchmark`. Same evaluator type, different scope. Because the evaluator lives in Langfuse, the rubric can be tuned without changing code, and every future experiment run automatically gets the same scoring.

**✋ Check in**: "Is the `answer-correctness` evaluator active in the LLM-as-a-Judge list, scoped to Dataset Runs?"

Wait for confirmation, then move to running the experiment.

---

## Step 3 — Run the first experiment

**Announce**: Now we run the experiment. The script calls your real `answer()` function against each dataset item — scoring happens automatically once the experiment items hit Langfuse and the platform evaluator picks them up.

**Terminal prompt**: "In your terminal, run:"
```bash
uv run python labs/07-offline-evals/run_experiment.py --name prompt-v1
```

**Explain**: `dataset.run_experiment()` loops over every item, calls `run_task()` (which calls your real `answer()` function, creating actual Langfuse traces), and records the result as a named run against the dataset. There is no `evaluators=` argument in the call — the platform evaluator you configured in Step 2 handles scoring as the items arrive. The `--name` flag labels this run so you can compare it to future runs.

**Langfuse check**: "In Langfuse, go to **Datasets** → `datastream-support-benchmark` → **Runs** tab. You should see `prompt-v1`. After 30–60 seconds, refresh — the `answer-correctness` scores should appear on each item."

📸 **See Task 7.3 in the lab README** for a screenshot of the run with platform-evaluator scores.

**✋ Check in**: "Can you see the `prompt-v1` run? Once scores appear, what is the average `answer-correctness`?"

---

## Step 4 — Inspect the failures

**Announce**: Average scores are useful but the value is in the failures. Open the run and look at the lowest-scoring items — those are the concrete things to fix.

**Direct the attendee** to:

1. In Langfuse → **Datasets** → `datastream-support-benchmark` → **Runs** → open `prompt-v1`
2. Sort by `answer-correctness` ascending, or expand any item with a score < 0.5
3. For each low-scoring item, look at:
   - The **question** (input)
   - The **expected** information
   - What the assistant actually returned (output)
   - The judge's **reason** comment — why it scored low

**Explain**: This replaces "the answers feel a bit off" with a concrete list: "for these specific questions, the assistant is leaving out pricing details / not citing the plan / using the wrong connector name." Now you can write a prompt change targeted at exactly those failures — not a guess.

**✋ Check in**: "What patterns do you see in the low-scoring items? Is there a common kind of mistake — wrong number, missing detail, off-topic answer?"

Wait for them to describe a pattern, then move to the next step.

---

## Step 5 — Iterate on the prompt and re-run

**Announce**: Now the loop closes. Change the system prompt based on what you saw in the failures, run the experiment again under a new name, and **measure** whether it actually helped.

**Direct the attendee** to update the prompt in Langfuse:

1. Go to **Prompts** → `datastream-system-prompt` → **New version**
2. Add a guideline targeting the failure pattern they identified. Examples that often help:
   - `- Always cite the specific plan name and price when discussing pricing.`
   - `- When the user mentions an error code, restate where to find the setting (e.g. "Settings > Credentials").`
   - `- Prefer concrete numbers from the docs over generalisations.`
3. Check **Set the production label** → save

**Terminal prompt**: "Without changing any code, run the experiment with a new name:"
```bash
uv run python labs/07-offline-evals/run_experiment.py --name prompt-v2
```

**Explain**: Same dataset, same evaluator, same code — the only thing that changed is the prompt version your app fetched from Langfuse. The platform evaluator scores `prompt-v2` with the same rubric it used for `prompt-v1`, which is what makes the comparison fair.

**Langfuse check**: "In **Datasets** → **Runs**, both `prompt-v1` and `prompt-v2` should appear. Click **Compare** — look for items whose score changed."

📸 **See Task 7.4 in the lab README** for a screenshot of the two runs compared side by side.

**✋ Check in**: "Did the average score go up or down? Were the items you targeted actually fixed? Were there any regressions on items that previously scored well?"

---

## Step 6 — Run a no-code experiment from the UI

**Announce**: You can also run a prompt against a dataset directly from the Langfuse UI — no Python needed. Useful for quick iteration when a PM or designer wants to try a prompt without involving engineering.

**Direct the attendee**:

1. Go to **Prompts** → **New Prompt**, name it `support-qa-prompt`, type **Chat**
2. Add a system message: *"You are a helpful assistant for DataStream product."*
3. In the user message field, add: `{{question}}`
4. Set label `production` → **Create prompt**

**Then run the experiment:**

1. Go to **Datasets** → `datastream-support-benchmark` → **Run experiment**
2. Select **Configure** under _via User Interface_
3. Select the `support-qa-prompt` prompt and the `datastream-support-benchmark` dataset
4. Your `answer-correctness` evaluator already runs on every dataset run, so it'll score this one too
5. Click **Run Experiment**

📸 **See Task 7.5 in the lab README** for screenshots of the UI experiment setup.

**Explain**: Same dataset, same evaluator, just driven from the UI instead of a script. It's where product teams can validate prompt ideas without a deploy.

**✋ Check in**: "Is the UI experiment running or completed? Can you see it in the Runs tab alongside `prompt-v1` and `prompt-v2`?"

---

## Step 7 — Add a production trace to the dataset

**Announce**: Datasets should grow over time from real production failures. This is how you prevent regressions from silently returning.

**Direct the attendee** to:

1. In Langfuse, go to **Tracing** and find a trace where the assistant gave a wrong or unhelpful answer (in Lab 5 we set up `in-scope` and `user-feedback` scores — filter by those to surface bad traces fast)
2. Open the trace → click **Add to dataset** → select `datastream-support-benchmark`

**Explain**: The production failure becomes a permanent test case. The next time you run an experiment, the `answer-correctness` evaluator will score it — ensuring this specific failure cannot silently regress. Over time the dataset grows into a comprehensive regression suite built from real failures, not hypothetical ones.

📸 **See Task 7.6 in the lab README** for a screenshot of the Add to dataset flow.

**✋ Check in**: "Have you added a trace to the dataset? Can you see it as a new item in the dataset items list?"

---

## Completion check

- [ ] `datastream-support-benchmark` has 9+ items
- [ ] `answer-correctness` LLM-as-a-judge evaluator is active and scoped to Dataset Runs
- [ ] `prompt-v1` experiment run appears with `answer-correctness` scores from the platform evaluator
- [ ] You inspected the failing items and identified a pattern
- [ ] `prompt-v2` run appears and can be compared to `prompt-v1`
- [ ] A no-code UI experiment has been run
- [ ] At least one production trace has been added to the dataset

"Congratulations — you've completed the workshop! You've instrumented an LLM app from scratch, managed prompts outside code, set up online and offline evaluation, built a human annotation workflow, and run the full *evaluate → fail → iterate → re-run* loop with a platform-managed judge. Everything you built here applies directly to production systems."
