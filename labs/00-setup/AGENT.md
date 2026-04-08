# Lab 0: Setup — Agent Instructions

> **For the attendee**: If you are using an AI coding assistant, paste this file's contents as your first message. The assistant will guide you through the full setup.

---

## Your task

Guide the attendee through bootstrapping the workshop environment. You will run commands, verify results, and ask the attendee to provide their API keys. Some steps require the attendee to act in their browser — tell them clearly when that is the case.

---

## Step 1 — Bootstrap the project

Run the setup script:

```bash
chmod +x setup.sh && ./setup.sh
```

This creates a `.venv/` virtual environment, installs dependencies, and copies `.env.example` to `.env`. Show the attendee the output and confirm there are no errors.

---

## Step 2 — Collect API keys from the attendee

You need two things from the attendee before you can proceed. Ask them:

**"Please provide the following — we'll put them in your `.env` file:"**

1. **OpenAI API key** — from [platform.openai.com](https://platform.openai.com) → API Keys
2. **Langfuse credentials** — Public Key, Secret Key, and Base URL from their Langfuse project (Settings → API Keys). If they don't have a Langfuse account yet, tell them to complete **Lab 1** first and come back.

Wait for the attendee to provide these values before continuing.

---

## Step 3 — Fill in `.env`

Once the attendee provides their keys, write them into `.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com

OPENAI_API_KEY=sk-...
```

> The `LANGFUSE_BASE_URL` is `https://cloud.langfuse.com` for the EU region or `https://us.cloud.langfuse.com` for the US region. Ask the attendee which region they signed up on if unsure.

---

## Step 4 — Verify the environment

Activate the virtual environment and run the baseline app:

```bash
source .venv/bin/activate
python -m app.main
```

Ask the attendee to type a question (e.g. *"How do I get started with DataStream?"*) and confirm they receive a response. Then quit with `quit`.

Now verify the Langfuse connection:

```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from langfuse import get_client
result = get_client().auth_check()
print('Langfuse connection:', 'OK' if result else 'FAILED')
"
```

If the connection check fails, review the `.env` values with the attendee — the most common issues are a wrong `LANGFUSE_BASE_URL` (EU vs US) or a copy-paste error in the keys.

---

## Completion check

- [ ] `./setup.sh` ran without errors
- [ ] `.env` has all four values filled in
- [ ] `python -m app.main` starts and responds to a question
- [ ] Langfuse connection check prints `OK`

Once all pass, tell the attendee they're ready for **Lab 1: Langfuse UI** (if they haven't done it) or **Lab 2: Basic Tracing** (if they already have their Langfuse account set up).
