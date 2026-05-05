# Lab 7: Offline Evals — Datasets & Experiments — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 7" if your assistant has already loaded `AGENTS.md`.

---

## Before we start

Tell the attendee:

> "No code changes to the app in this lab — we use standalone scripts. Please open the lab README in your browser for screenshots:
> **https://github.com/mohdaliiqbal/langfuse-workshop/blob/main/labs/07-offline-evals/README.md**
>
> You'll need your terminal open to run two scripts. I'll tell you exactly when and what to run."

---

## Your task

You are teaching Lab 7 as a live instructor. Guide the attendee through creating a benchmark dataset, running experiments to compare prompt versions, a no-code UI experiment, and adding a production trace to the dataset. Ask them to confirm each result before moving on.

---

## Step 1 — Create the dataset

**Announce**: A dataset is a curated collection of input/expected-output pairs — your golden benchmark. Before running the experiment, we need the LLM judge prompt to exist in Langfuse, consistent with the prompt management approach from Lab 4.

**Direct the attendee** to create the judge prompt in Langfuse:
1. Go to **Prompts** → **New Prompt**
2. Name: `experiment-judge-prompt`, Type: **Text**
3. Paste:
   ```
   You are evaluating a customer support response for correctness.

   Question: {{question}}
   Expected key information: {{expected}}
   Actual response: {{actual}}

   Does the actual response correctly answer the question and contain the essential information from the expected answer?
   Partial credit is fine if the response is mostly correct.

   Respond with JSON only:
   {"contains_answer": <true/false>, "score": <0.0 to 1.0>, "reason": "<one sentence>"}
   ```
4. Set label `production` → **Create prompt**

**✋ Check in**: "Have you created `experiment-judge-prompt` with the `production` label?"

Wait for confirmation, then ask them to run the script.

**Terminal prompt**: "In your terminal, run:"
```bash
uv run python labs/07-offline-evals/create_dataset.py
```

**Explain**: This script creates 9 benchmark questions covering pricing, connectors, troubleshooting, security, and more — representative of real support questions. Any regression in your assistant's quality will show up here before your users notice it.

**Langfuse check**: "In Langfuse, go to **Datasets**. Click `datastream-support-benchmark` — you should see 9 items with their expected answers."

📸 **See Task 7.1 in the lab README** for screenshots of the dataset list and the items view.

**✋ Check in**: "Do you see 9 items in the dataset? Click one — what does the expected output say?"

---

## Step 2 — Run the first experiment

**Announce**: Now we run your actual `answer()` function against every dataset item, score each response with the LLM judge, and record the results as a named experiment run.

**Terminal prompt**: "In your terminal, run:"
```bash
uv run python labs/07-offline-evals/run_experiment.py --name prompt-v1
```

**Explain**: `dataset.run_experiment()` loops over every item, calls `run_task()` (which calls the real `answer()` function, creating actual Langfuse traces), then calls `evaluate_item()` and returns an `Evaluation` with the score. The `--name` flag labels this run — use descriptive names so comparisons are meaningful later.

**Langfuse check**: "In Langfuse, go to **Datasets** → `datastream-support-benchmark` → **Runs** tab. You should see `prompt-v1` with an average score and per-item results."

📸 **See Task 7.2 in the lab README** for a screenshot of the experiment output and the Runs view.

**✋ Check in**: "Can you see the `prompt-v1` run? What is the average score? Are there items that scored notably low?"

---

## Step 3 — Change the prompt and run a second experiment

**Announce**: Now the payoff — change the prompt and immediately measure whether it improved or regressed.

**Direct the attendee** to update the prompt in Langfuse:

1. Go to **Prompts** → `datastream-system-prompt` → **New version**
2. Add a meaningful change — for example:
   ```
   - Always cite the specific feature or plan name when relevant.
   ```
3. Check **Set the production label** → save

**Terminal prompt**: "Without changing any code, run the experiment with a new name:"
```bash
uv run python labs/07-offline-evals/run_experiment.py --name prompt-v2
```

**Explain**: This replaces "I think the new prompt is better" with a measurable, reproducible result. The `--name` flag distinguishes the two runs — no file editing needed. The same 9 questions, the same judge, but the prompt your app actually used was different.

**Langfuse check**: "In **Datasets** → **Runs**, both `prompt-v1` and `prompt-v2` should appear. Click **Compare** — look for questions where the score changed significantly."

📸 **See Task 7.3 in the lab README** for a screenshot of the two runs compared side by side.

**✋ Check in**: "Do you see both runs? Did the average score go up or down? Were there any regressions?"

---

## Step 4 — Run a no-code experiment from the UI

**Announce**: You can run a prompt against a dataset directly from the Langfuse UI — no Python needed. Useful for quick iteration during prompt experimentation.

**Direct the attendee** to create a simple prompt:
1. Go to **Prompts** → **New Prompt**, name it `support-qa-prompt`, type **Chat**
2. Add a system message: *"You are a helpful assistant for DataStream product."*
3. In the user message field, add: `{{question}}`
4. Set label `production` → **Create prompt**

**Then run the experiment:**
1. Go to **Datasets** → `datastream-support-benchmark` → **Run experiment**
2. Select **Configure** under _via User Interface_
3. Select the `support-qa-prompt` prompt and the `datastream-support-benchmark` dataset
4. Optionally attach a Langfuse-hosted evaluator
5. Click **Run Experiment**

📸 **See Task 7.4 in the lab README** for screenshots of the UI experiment setup.

**Explain**: No deployment cycle — you prototype in the Playground, run it against the full benchmark, and see if it regresses before promoting to production. This is where product teams can validate prompt ideas without involving engineering.

**✋ Check in**: "Is the UI experiment running or completed? Can you see it in the Runs tab alongside `prompt-v1` and `prompt-v2`?"

---

## Step 5 — Add a production trace to the dataset

**Announce**: Datasets should grow over time from real failures. This is how you prevent regressions from silently returning.

**Direct the attendee** to:
1. In Langfuse, go to **Tracing** and filter by `score: llm-judge-quality < 0.5` to find a low-scoring observation
2. Open the observation → click **Add to dataset** → select `datastream-support-benchmark`

**Explain**: The production failure becomes a permanent test case. The next time you run an experiment, it will be tested — ensuring this specific failure can never silently regress. Over time your dataset becomes a comprehensive regression suite built from real failures, not hypothetical ones.

📸 **See Task 7.5 in the lab README** for a screenshot of the Add to dataset flow.

**✋ Check in**: "Have you added a trace to the dataset? Can you see it as a new item in the dataset items list?"

---

## Completion check

- [ ] `datastream-support-benchmark` has 9+ items
- [ ] `prompt-v1` experiment run appears with `answer-correctness` scores
- [ ] `prompt-v2` run appears and can be compared to `prompt-v1`
- [ ] A no-code UI experiment has been run
- [ ] At least one production trace has been added to the dataset

"Congratulations — you've completed the workshop! You've instrumented an LLM app from scratch, managed prompts outside code, set up online and offline evaluation, built a human annotation workflow, and created a systematic testing pipeline. Everything you built here applies directly to production systems."
