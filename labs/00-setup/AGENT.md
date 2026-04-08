# Lab 0: Setup — Agent Instructions

> **For the attendee**: If you are using an AI coding assistant, paste this file's contents as your first message. The assistant will guide you through the full setup.

---

## Your task

Guide the attendee through bootstrapping the workshop environment. Langfuse account setup and API key configuration are covered in Lab 1 — do not ask for Langfuse credentials here.

---

## Step 1 — Bootstrap the project

Run the setup script:

```bash
chmod +x setup.sh && ./setup.sh
```

Show the attendee the output and confirm there are no errors.

---

## Step 2 — Add the OpenAI key to `.env`

Ask the attendee for their OpenAI API key and write it into `.env`:

```env
OPENAI_API_KEY=sk-...
```

Leave the `LANGFUSE_*` fields blank for now — those are covered in Lab 1.

---

## Step 3 — Verify the baseline app

Activate the virtual environment and run the app:

```bash
source .venv/bin/activate
python -m app.main
```

Ask the attendee to type a question (e.g. *"How do I get started with DataStream?"*) and confirm they get a response. Then quit with `quit`.

---

## Completion check

- [ ] `./setup.sh` ran without errors
- [ ] `python -m app.main` starts and responds to a question

Once confirmed, tell the attendee they're ready for **Lab 1: Langfuse** to create their account and get their API keys.
