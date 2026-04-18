"""
Lab 4 Solution: main.py
Same as Lab 3 — no changes needed in main.py for prompt management.
"""

import uuid
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from langfuse import get_client
from app.assistant import answer

console = Console()


def main():
    console.print(Panel.fit(
        "[bold cyan]DataStream Support Assistant[/bold cyan]\n"
        "[dim]Type your question or 'quit' to exit[/dim]",
        border_style="cyan"
    ))

    session_id = str(uuid.uuid4())
    user_id = "workshop-user-1"
    history = []

    while True:
        question = Prompt.ask("\n[bold green]You[/bold green]")

        if question.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break

        if not question.strip():
            continue

        with console.status("[dim]Thinking...[/dim]"):
            response = answer(question, history, session_id=session_id, user_id=user_id)

        console.print(f"\n[bold blue]Assistant[/bold blue]: {response}")

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": response})

    get_client().flush()


if __name__ == "__main__":
    main()
