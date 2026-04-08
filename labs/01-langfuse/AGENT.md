# Lab 1: Langfuse UI — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 1" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through creating a Langfuse account, organization, project, and API keys. Every step in this lab happens in the browser — you cannot do these steps for the attendee. Your role is to tell them exactly what to do, wait for confirmation at each step, and then help them put the keys into `.env`.

---

## Step 1 — Sign up

**Tell the attendee:**
> Go to [cloud.langfuse.com](https://cloud.langfuse.com) in your browser and click **Sign Up** in the top right. Create an account with your email, or sign in with Google or GitHub.
>
> Let me know when you're signed in.

Wait for confirmation before continuing.

---

## Step 2 — Create an organization

**Tell the attendee:**
> You should see an **Organizations** page. Click **New Organization**.
> - Set a name (e.g. `workshop-org`)
> - Set the type to **Educational** or whatever fits
> - Click **Create**
>
> An organization is the top-level container for your team. It holds members, billing, and one or more projects.
>
> Let me know when your organization is created.

Wait for confirmation.

---

## Step 3 — Create a project

**Tell the attendee:**
> Langfuse will walk you through a 3-step wizard. Step 2 is **Invite Members** — you can skip this by clicking **Next**.
>
> Step 3 is **Create Project**. Give it a name (e.g. `langfuse-workshop`) and click **Create**.
>
> A project is an isolated workspace — it holds all the traces, prompts, datasets, and scores for one application. In production you'd have separate projects per environment (production vs staging).
>
> Let me know when your project is created.

Wait for confirmation.

---

## Step 4 — Navigate to API Keys

**Tell the attendee:**
> You're now inside your project. Scroll to the bottom of the left sidebar and click **Settings**. Then in the settings menu, click **API Keys**.
>
> You'll see the API Keys page. Click **Create new API key** in the top right, give it a note (e.g. `langfuse-api`), and click **Create API keys**.
>
> **Important**: The dialog that appears shows your Secret Key only once — you cannot retrieve it after closing. Copy all three values somewhere safe now.
>
> Let me know when you have your keys and tell me:
> 1. Your Public Key (starts with `pk-lf-`)
> 2. Your Secret Key (starts with `sk-lf-`)
> 3. Your Base URL (`https://cloud.langfuse.com` for EU, `https://us.cloud.langfuse.com` for US)

Wait for the attendee to share their keys.

---

## Step 5 — Write keys to `.env`

Once the attendee shares their credentials, write them into `.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

---

## Step 6 — Verify the connection

```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from langfuse import get_client
result = get_client().auth_check()
print('Langfuse connection:', 'OK' if result else 'FAILED')
"
```

If it prints `FAILED`, check the `LANGFUSE_BASE_URL` — the most common mistake is using the EU URL when signed up on US, or vice versa.

---

## Completion check

- [ ] Langfuse account created
- [ ] Organization and project created
- [ ] API keys copied into `.env`
- [ ] Connection check prints `OK`

Once confirmed, tell the attendee they're ready for **Lab 2: Basic Tracing**.
