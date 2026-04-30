"""
DataStream Support Assistant - CLI entry point

Entry point for the app. Runs a loop that takes your question from the terminal,
calls answer(), prints the response, and maintains conversation history.
"""

import os
from dotenv import load_dotenv
load_dotenv()

import openai
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from app.assistant import answer

console = Console()


def main():
    if not os.getenv("OPENAI_API_KEY"):
        console.print(Panel.fit(
            "[bold red]OPENAI_API_KEY is not set[/bold red]\n"
            "[dim]Add it to your .env file, then restart the app.[/dim]\n\n"
            "Press [bold]Ctrl+C[/bold] to exit.",
            border_style="red"
        ))
        try:
            input()
        except KeyboardInterrupt:
            pass
        return

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
            try:
                response = answer(question, history)
            except openai.AuthenticationError:
                console.print(Panel.fit(
                    "[bold red]Invalid OpenAI API key[/bold red]\n"
                    "[dim]Check the OPENAI_API_KEY value in your .env file, then restart the app.[/dim]\n\n"
                    "Press [bold]Ctrl+C[/bold] to exit.",
                    border_style="red"
                ))
                try:
                    input()
                except KeyboardInterrupt:
                    pass
                return

        console.print(f"\n[bold blue]Assistant[/bold blue]: {response}")

        # Maintain conversation history
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
