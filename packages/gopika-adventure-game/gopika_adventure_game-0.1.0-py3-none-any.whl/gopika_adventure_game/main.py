"""Main entry point for the text-based adventure game.

This module handles user interaction and displays the game introduction.
"""

import questionary
from gopika_adventure_game.constants import Decision  # type: ignore
from gopika_adventure_game.game_engine import run_game  # type: ignore
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def show_intro() -> None:
    """Display the game introduction using Rich formatting."""
    intro_text = Text()
    intro_text.append("\n" + "=" * 40 + "\n", style="bold green")
    intro_text.append("  Welcome to Adventure! 🌲🗺️\n", style="bold yellow")
    intro_text.append("=" * 40 + "\n", style="bold green")
    intro_text.append("\nYou are an explorer starting in a mysterious forest.\n", style="italic")
    intro_text.append("Your choices will determine your fate.\n\n", style="italic")
    intro_text.append("Let's begin! 🧭", style="bold cyan")

    console.print(Panel(intro_text, expand=False))


def get_stage_choices(message: str) -> list[str]:
    """Determine available choices based on the current stage prompt.

    Args:
        message (str): The prompt message from the game engine.

    Returns:
        list[str]: A list of valid choices for the player to select.
    """
    message = message.lower()
    if "which way do you go" in message or "invalid direction" in message:
        return ["North", "South", "East", "West"]
    if "cave entrance" in message:
        return ["Enter", "Go back"]
    if "wide river" in message:
        return ["Swim", "Go back"]
    if "treasure chest" in message:
        return ["Open", "Leave"]
    return []


def main() -> None:
    """Start and manage the adventure game loop.

    This function initializes the game, displays the intro,
    and continuously interacts with the player by sending inputs
    to the game engine and displaying responses.
    """
    show_intro()
    console.print("\n[bold green]Welcome to Adventure![/bold green]")
    game_gen = run_game()
    message = next(game_gen)

    while True:
        console.print(f"\n[bold yellow]{message}[/bold yellow]")
        choices = get_stage_choices(message)

        if not choices:
            # No choices means the game has ended
            console.print("\n👋 [bold red]Goodbye! Thanks for playing.[/bold red]")
            break

        user_input = questionary.select("Your choice:", choices).ask()

        if not user_input or user_input.lower() in {Decision.QUIT.value, Decision.EXIT.value}:
            game_gen.close()
            console.print("\n👋 [bold red]Goodbye! Thanks for playing.[/bold red]")
            break

        try:
            message = game_gen.send(user_input)
        except ValueError as exc:
            message = game_gen.throw(exc)
        except StopIteration:
            break


if __name__ == "__main__":
    main()
