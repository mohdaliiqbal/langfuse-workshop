# Lab 0: Setup

Before you can start building, you need a running Langfuse instance and an OpenAI API key.

---

## Step 1: OpenAI API Key

If you don't have one, create an account at [platform.openai.com](https://platform.openai.com) and generate an API key.

---

## Step 2: Langfuse Account

You have two options:

### Option A: Langfuse Cloud (recommended for workshops)

1. Go to [cloud.langfuse.com](https://cloud.langfuse.com) and create a free account.
2. Create a new **project**.
3. Go to **Settings → API Keys** and create a new key pair.
4. Note your `Public Key`, `Secret Key`, and the host URL (`https://cloud.langfuse.com` for EU, `https://us.cloud.langfuse.com` for US).

### Option B: Self-Hosted (Docker)

```bash
# Clone and start Langfuse locally
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker compose up -d
```

The UI will be available at `http://localhost:3000`. Use `http://localhost:3000` as your `LANGFUSE_BASE_URL`.

---

## Step 3: Bootstrap the Project

```bash
# Clone the workshop repo (if you haven't already)
git clone <repo-url>
cd langfuse-workshop

# Run the setup script
chmod +x setup.sh
./setup.sh
```

This will:
- Create a Python virtual environment in `.venv/`
- Install all dependencies
- Copy `.env.example` to `.env`

---

## Step 4: Configure Environment Variables

Open `.env` and fill in your credentials:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com

OPENAI_API_KEY=sk-...
```

---

## Step 5: Verify Setup

Activate the virtual environment and run the baseline app:

```bash
source .venv/bin/activate
python -m app.main
```

Try asking: *"How do I get started with DataStream?"*

You should get a helpful response. No Langfuse data will appear yet — that's what Lab 1 is for.

---

## Step 6: Verify Langfuse Connection

Make sure your virtual environment is active (you should see `(.venv)` in your terminal prompt). Then open a Python shell:

```bash
source .venv/bin/activate   # skip if already active from Step 5
python
```

You'll see a `>>>` prompt. Paste in the following line by line:

```python
from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client
langfuse = get_client()
print(langfuse.auth_check())  # Should print True
```

Type `exit()` or press `Ctrl+D` to close the shell when done.

---

## Checkpoint

- [ ] `python -m app.main` starts and responds to questions
- [ ] `langfuse.auth_check()` returns `True`

Once both pass, move on to **Lab 1**.
