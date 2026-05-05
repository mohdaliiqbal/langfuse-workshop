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

Ask the attendee to visit https://platform.openai.com/api-keys to generate api keys.

Leave the `LANGFUSE_*` fields blank for now — those are covered in Lab 1.

---

## Step 3 — Verify the baseline app

Run the app:

```bash
uv run gradio app/web.py
```

Tell the attendee:

> "You should see a line like `Running on local URL: http://127.0.0.1:7860` in the terminal. Open **http://localhost:7860** in your browser — the DataStream Support Assistant chat UI will appear."

Ask the attendee to type a question (e.g. *"How do I get started with DataStream?"*) and confirm they get a response in the browser.

To stop the app between labs, press `Ctrl+C` in the terminal. To restart it, run `uv run gradio app/web.py` again.

---

## Completion check

- [ ] `./setup.sh` ran without errors
- [ ] `uv run gradio app/web.py` starts without errors
- [ ] Chat UI opens at http://localhost:7860 and responds to a question

Once confirmed, tell the attendee they're ready for **Lab 1: Langfuse** to create their account and get their API keys.
