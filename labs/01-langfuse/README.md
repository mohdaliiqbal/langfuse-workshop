# Lab 1: Langfuse UI Overview

Before writing any code, let's get familiar with the Langfuse interface. Understanding the layout and key concepts will make the later labs much easier to follow — you'll know exactly where to look when traces start appearing.

---

## Organizations and Projects

When you sign in to Langfuse, you land inside an **Organization**. An organization is the top-level container — it represents your company or team and holds billing, members, and settings.

Within an organization you create **Projects**. Each project is an isolated workspace with its own:
- API keys
- Traces and observations
- Prompts
- Datasets
- Evaluation scores

> **How to think about it**: Organization = company. Project = one application or environment (e.g. `my-app-production`, `my-app-staging`). Everything you'll build in this workshop lives inside a single project.

---

## Main Navigation

<!-- Screenshot: full Langfuse UI with sidebar labels annotated -->

The left sidebar is your main navigation. Here's what each section does:

### Observability

| Section | What it shows |
|---------|--------------|
| **Tracing** | Every trace your application has produced — the core view for debugging |
| **Sessions** | Traces grouped by conversation/session — for multi-turn apps |
| **Users** | Traces grouped by user ID — for per-user debugging and usage tracking |

### Prompt Management

Manage, version, and deploy your LLM prompts without touching code. You'll use this in Lab 4.

### Evaluation

| Section | What it shows |
|---------|--------------|
| **Scores** | Quality signals attached to traces (user feedback, automated evals) |
| **Annotation Queues** | Human review queues for labeling and spot-checking traces |
| **Datasets** | Curated test sets for benchmarking your application |

---

## The Tracing View

<!-- Screenshot: Tracing list view -->

This is where you'll spend most of your time in the early labs. Each row is one trace — one end-to-end request through your application. The columns show:
- **Name** — the trace name (set by your code)
- **Timestamp** — when it ran
- **Input / Output** — a preview of what went in and came out
- **Latency** — how long the full request took
- **Cost** — estimated USD cost based on token usage

---

## The Trace Detail View

<!-- Screenshot: Trace detail panel -->

Click any trace to open the detail panel. This is where you inspect what actually happened:
- The **timeline** on the left shows all spans and generations nested in the order they ran
- Clicking a node shows its **Input**, **Output**, and **Metadata**
- Generations show **model name**, **token counts**, and **cost**

---

## Project Settings & API Keys

<!-- Screenshot: Settings > API Keys -->

Go to **Settings → API Keys** to find your project's credentials. You need three values for your `.env` file:
- `LANGFUSE_PUBLIC_KEY` — starts with `pk-lf-`
- `LANGFUSE_SECRET_KEY` — starts with `sk-lf-`
- `LANGFUSE_BASE_URL` — `https://cloud.langfuse.com` (EU) or `https://us.cloud.langfuse.com` (US)

These are scoped to this project — traces sent with these keys will only appear here.

---

## Checkpoint

- [ ] You can identify your Organization name and Project name in the UI
- [ ] You know where to find Tracing, Sessions, and Users in the sidebar
- [ ] You have your API keys copied into `.env`
- [ ] You can open a trace and navigate its spans (try clicking through the demo data if your project has any)

Once you're comfortable navigating the UI, move on to **Lab 2: Basic Tracing** where you'll start generating your own traces.
