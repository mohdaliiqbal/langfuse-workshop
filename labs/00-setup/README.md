# Lab 0: Setup

Get the workshop running on your machine. This lab covers cloning the repo and bootstrapping the environment. Langfuse account setup is covered in **Lab 1**.

---

## Step 1: OpenAI API Key

If you don't have one, create an account at [platform.openai.com](https://platform.openai.com) and generate an API key.

---

## Step 2: Bootstrap the Project

```bash
# Clone the workshop repo
git clone git@github.com:mohdaliiqbal/langfuse-workshop.git
cd langfuse-workshop

# Run the setup script
chmod +x setup.sh
./setup.sh
```

`setup.sh` does exactly four things — nothing more:
1. Checks you have Python 3.10+
2. Creates a virtual environment in `.venv/` (isolated, won't affect your system Python)
3. Installs the dependencies listed in `requirements.txt` (`openai`, `langfuse`, `python-dotenv`, `rich`)
4. Copies `.env.example` to `.env` if no `.env` exists yet

It does **not** install anything globally, modify your system, or send any data anywhere.

---

## Step 3: Add your OpenAI key to `.env`

Open `.env` and fill in your OpenAI key. Leave the Langfuse fields for now — you'll get those in Lab 1.

```env
OPENAI_API_KEY=sk-...
```

---

## Step 4: Verify the baseline app works

Activate the virtual environment and run the app:

```bash
source .venv/bin/activate
python -m app.main
```

Try asking: *"How do I get started with DataStream?"*

You should get a helpful response. No Langfuse data will appear yet — that comes after Lab 1.

---

## Checkpoint

- [ ] `./setup.sh` ran without errors
- [ ] `python -m app.main` starts and responds to a question

Once both pass, move on to **Lab 1: Langfuse** to create your account and get your API keys.
