---
title: "Workshop Delivery Guide"
description: "High-level preparation notes for running the Python Langfuse workshop."
---

# Workshop Delivery Guide

This is the Python port of the Langfuse workshop. The lesson content follows the upstream TypeScript workshop. Commands, file names, and SDK calls in this repo are the Python versions.

## Resources

- Learner lessons: [docs/learner/00-setup.md](../learner/00-setup.md)
- Instructor notes: [docs/instructor/00-setup.md](../instructor/00-setup.md)
- Upstream workshop: [github.com/langfuse/langfuse-workshop](https://github.com/langfuse/langfuse-workshop)
- Slide template: [Google slides](https://docs.google.com/presentation/d/1rrICEwno3P_AphsJyjItZ5iRN5ycejqzzRhYaxdRpgc/edit?usp=sharing)

## Preparation

- Use **Langfuse Cloud**. If someone asks about a company self-hosted instance, steer them to Cloud so the UI matches the lessons.
- Confirm **AI Features** (including Halo) are on under **Organization Settings → General → AI Features**.
- Go through the workshop yourself with `uv sync` and `uv run python -m app.server`.
- Optional: prep a shared OpenAI key, limit spend, and delete it afterwards.
- The upstream workshop changes often. Check [SYNC.md](../../SYNC.md) for the commit this port was last aligned to, and re-sync before a session if that commit is old.

## Audience

- Ideally 20–30 people and 2 instructors.
- Ideally participants have some coding background and have built something with an LLM before.
- Python 3.14 via uv. Node is only needed for the Langfuse CLI.

## Delivery

- Short welcome, then the AI engineering loop.
- Show `docs/learner/` and the checkpoint command `uv run python scripts/use_checkpoint.py <chapter>`.
- Let people work self-paced. Check in every 30–45 minutes, two modules at a time.
- A short session can stop after monitoring. The dataset, experiment, and evaluation chapters are the rest of the loop.
