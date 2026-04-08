"""
DataStream Support Assistant - CLI entry point
"""

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from app.assistant import answer

console = Console()


def main():
    console.print(Panel.fit(
        "[bold cyan]DataStream Support Assistant[/bold cyan]\n"
        "[dim]Type your question or 'quit' to exit[/dim]",
        border_style="cyan"
    ))

    history = []

    while True:
        question = Prompt.ask("\n[bold green]You[/bold green]")

        if question.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break

        if not question.strip():
            continue

        with console.status("[dim]Thinking...[/dim]"):
            response = answer(question, history)

        console.print(f"\n[bold blue]Assistant[/bold blue]: {response}")

        # Maintain conversation history
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
