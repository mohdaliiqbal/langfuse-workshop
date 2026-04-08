"""
Lab 4 Solution: Updated main.py with user feedback and background evaluation
"""

import uuid
import threading
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from langfuse import get_client
from labs.lab_04_evaluation.solution import answer
from labs.lab_04_evaluation.evaluator import evaluate_response

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
    langfuse = get_client()

    while True:
        question = Prompt.ask("\n[bold green]You[/bold green]")

        if question.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break

        if not question.strip():
            continue

        with console.status("[dim]Thinking...[/dim]"):
            response, trace_id = answer(question, history, session_id=session_id, user_id=user_id)

        console.print(f"\n[bold blue]Assistant[/bold blue]: {response}")

        # Collect user feedback
        feedback = Prompt.ask(
            "[dim]Was this helpful?[/dim]",
            choices=["y", "n", "skip"],
            default="skip",
        )

        if feedback in ("y", "n") and trace_id:
            langfuse.create_score(
                trace_id=trace_id,
                name="user-feedback",
                value=1 if feedback == "y" else 0,
                data_type="BOOLEAN",
                comment="User thumbs up/down from CLI",
            )

        # Run LLM-as-a-judge evaluation in the background
        if trace_id:
            threading.Thread(
                target=evaluate_response,
                args=(trace_id, question, response),
                daemon=True,
            ).start()

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": response})

    langfuse.flush()


if __name__ == "__main__":
    main()
