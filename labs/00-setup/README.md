# Lab 0: Setup

Get the workshop running on your machine. This lab covers cloning the repo and bootstrapping the environment. Langfuse account setup is covered in **Lab 1**.

---

## Step 1: Install uv

If you don't have `uv` installed, run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` will handle Python 3.14 and all dependencies — no separate Python install needed.

---

## Step 2: OpenAI API Key

If you don't have one, create an account at [platform.openai.com](https://platform.openai.com) and generate an API key.

---

## Step 3: Bootstrap the Project

```bash
# Clone the workshop repo
git clone https://github.com/mohdaliiqbal/langfuse-workshop.git
cd langfuse-workshop

# Run the setup script
chmod +x setup.sh
./setup.sh
```

`setup.sh` does exactly two things — nothing more:
1. Runs `uv sync` — creates `.venv/`, installs Python 3.14, and installs all dependencies (`openai`, `langfuse`, `python-dotenv`, `rich`, `gradio`)
2. Copies `.env.example` to `.env` if no `.env` exists yet

It does **not** install anything globally, modify your system, or send any data anywhere.

---

## Step 4: Add your OpenAI key to `.env`

Open `.env` and fill in your OpenAI key. Leave the Langfuse fields for now — you'll get those in Lab 1.

```env
OPENAI_API_KEY=sk-...
```

---

## Step 5: Verify the baseline app works

Run the app:

```bash
uv run gradio app/web.py
```

You should see output like:

```
Running on local URL: http://127.0.0.1:7860
```

Open **<a href="http://localhost:7860" target="_blank">http://localhost:7860</a>** in your browser. You'll see the DataStream Support Assistant chat UI.

Try asking: *"How do I get started with DataStream?"*

You should get a helpful response. No Langfuse data will appear yet — that comes after Lab 1.

> **To stop the app**: press `Ctrl+C` in the terminal.

---

## Checkpoint

- [ ] `./setup.sh` ran without errors
- [ ] `uv run gradio app/web.py` starts without errors
- [ ] The chat UI opens at <a href="http://localhost:7860" target="_blank">http://localhost:7860</a> and responds to a question

Once both pass, move on to **Lab 1: Langfuse** to create your account and get your API keys.
