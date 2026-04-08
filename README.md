# Langfuse Workshop

A hands-on workshop for AI engineers covering LLM observability, prompt management, evaluation, and systematic testing using [Langfuse](https://langfuse.com).

---

## What You'll Build

You'll instrument a production-style customer support chatbot step by step, learning how Langfuse solves real problems at each stage:

| Lab | Topic | What you learn |
|-----|-------|----------------|
| [00 - Setup](labs/00-setup/README.md) | Environment | Langfuse account, API keys, running the baseline app |
| [01 - Tracing](labs/01-tracing/README.md) | Basic observability | `@observe` decorator, trace structure, exploring the UI |
| [02 - Instrumentation](labs/02-instrumentation/README.md) | Rich traces | Token tracking, sessions, user IDs, metadata |
| [03 - Prompt Management](labs/03-prompt-management/README.md) | Prompt versioning | Decouple prompts from code, variables, rollback |
| [04 - Evaluation](labs/04-evaluation/README.md) | Quality measurement | User feedback scores, LLM-as-a-judge |
| [05 - Datasets](labs/05-datasets/README.md) | Systematic testing | Golden datasets, experiments, A/B comparisons |

---

## The Baseline App

The app is a customer support assistant for a fictional SaaS product called **DataStream**. It:
- Retrieves relevant documentation for each question (simulated RAG)
- Generates answers using OpenAI
- Supports multi-turn conversations

The baseline has **no Langfuse integration** — you add it lab by lab.

---

## Prerequisites

- Python 3.10+
- An OpenAI API key
- A Langfuse account (free at [cloud.langfuse.com](https://cloud.langfuse.com), or run locally with Docker)

---

## Quick Start

```bash
# 1. Clone this repo
git clone git@github.com:mohdaliiqbal/langfuse-workshop.git
cd langfuse-workshop

# 2. Bootstrap the project
chmod +x setup.sh
./setup.sh
```

`setup.sh` does exactly four things — nothing more:
1. Checks you have Python 3.10+
2. Creates a virtual environment in `.venv/` (isolated, won't affect your system Python)
3. Installs the dependencies listed in `requirements.txt` (`openai`, `langfuse`, `python-dotenv`, `rich`)
4. Copies `.env.example` to `.env` if no `.env` exists yet

It does **not** install anything globally, modify your system, or send any data anywhere.

```bash
# 3. Fill in your API keys
# Edit .env with your LANGFUSE_* and OPENAI_API_KEY values

# 4. Activate the virtual environment
source .venv/bin/activate

# 5. Run the baseline app
python -m app.main
```

Then open [labs/00-setup/README.md](labs/00-setup/README.md) and follow the labs in order.

---

## Project Structure

```
langfuse-workshop/
├── app/                          # Baseline application
│   ├── main.py                   # CLI entrypoint
│   ├── assistant.py              # LLM logic (you'll modify this)
│   └── knowledge_base.py         # In-memory docs + retrieval
├── labs/
│   ├── 00-setup/README.md        # Environment setup
│   ├── 01-tracing/               # Lab 1: @observe decorator
│   ├── 02-instrumentation/       # Lab 2: tokens, sessions, metadata
│   ├── 03-prompt-management/     # Lab 3: prompts in Langfuse
│   ├── 04-evaluation/            # Lab 4: scoring & LLM-as-judge
│   └── 05-datasets/              # Lab 5: datasets & experiments
├── .env.example                  # Environment variable template
├── requirements.txt
└── setup.sh                      # One-command bootstrap
```

Each lab contains a `README.md` with step-by-step instructions and a `solution.py` reference implementation.

---

## Key Concepts

**Trace** — A complete record of one request through your system (inputs, outputs, timing, cost).

**Span** — A step within a trace (e.g., retrieval, processing).

**Generation** — A special span for LLM calls that tracks model, tokens, and cost.

**Score** — A quality signal attached to a trace (user feedback, automated eval, human annotation).

**Session** — A group of traces from one conversation.

**Prompt** — A versioned, managed prompt template in Langfuse, fetched at runtime.

**Dataset** — A curated set of test cases used to benchmark your application.

**Experiment** — A run of your app against a dataset, producing comparable results.
