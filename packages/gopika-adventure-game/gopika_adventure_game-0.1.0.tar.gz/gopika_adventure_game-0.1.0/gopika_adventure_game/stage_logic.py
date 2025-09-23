"""Stage logic for the text-based adventure game.

This module defines the gameplay logic for each stage in the adventure:
- Forest
- Mountain
- River
- Cave
"""

from typing import Generator, Optional

from gopika_adventure_game.constants import Decision, Stage  # type: ignore


def play_forest_stage() -> Generator[str, str, Optional[Stage]]:
    """Handles the forest stage of the game.

    Yields:
        str: A prompt asking the player to choose a direction.

    Receives:
        str: The player's decision (e.g., 'North' or 'South').

    Returns:
        Stage: The next stage (Mountain or River) based on the player's input.

    Raises:
        ValueError: If the input is not 'North' or 'South'.
    """
    while True:
        try:
            response = yield (
                "\n🌲 You're standing in a quiet forest.\n"
                "One path heads North toward distant mountains, "
                "the other South toward the sound of rushing water.\n"
                "Which way do you go?"
            )
            if response.lower() == Decision.NORTH.value:
                return Stage.MOUNTAIN
            elif response.lower() == Decision.SOUTH.value:
                return Stage.RIVER
            else:
                raise ValueError("❌ Invalid direction. Try 'North' or 'South'.")
        except ValueError as e:
            print(str(e))


def play_mountain_stage() -> Generator[str, str, Stage]:
    """Handles the mountain stage of the game.

    Yields:
        str: A prompt asking the player whether to enter the cave or go back.

    Receives:
        str: The player's decision (e.g., 'Enter' or 'Go back').

    Returns:
        Stage: The next stage (Cave or Forest) based on the player's input.

    Raises:
        ValueError: If the input is not 'Enter' or 'Go back'.
    """
    response = yield (
        "\n⛰️ You climb higher, the air cooler with every step. "
        "A dark cave entrance waits ahead.\n"
        "Will you Enter or Go back to the forest?"
    )
    if response.lower() == Decision.ENTER.value:
        return Stage.CAVE
    elif response.lower() == Decision.GO_BACK.value:
        return Stage.FOREST
    else:
        raise ValueError("Unexpected input received in play_mountain_stage")


def play_river_stage() -> Generator[str, str, Stage]:
    """Handles the river stage of the game.

    Yields:
        str: A prompt asking the player whether to swim or go back.

    Receives:
        str: The player's decision (e.g., 'Swim' or 'Go back').

    Returns:
        Stage: The next stage (End or Forest) based on the player's input.

    Raises:
        ValueError: If the input is not 'Swim' or 'Go back'.
    """
    response = yield (
        "\n🌊 You reach a wide river, its current fast and loud.\n"
        "You could Swim across… though it looks risky.\n"
        "Or Go back to the forest. What's your choice?"
    )
    if response.lower() == Decision.SWIM.value:
        yield "\n💀 You dive in, but the current is too strong! The water sweeps you away."
        " Game over."
        return Stage.END
    elif response.lower() == Decision.GO_BACK.value:
        return Stage.FOREST
    else:
        raise ValueError("Unexpected input received in play_river_stage.")


def play_cave_stage() -> Generator[str, str, Stage]:
    """Handles the cave stage of the game.

    Yields:
        str: A prompt asking the player whether to open the treasure chest or leave.

    Receives:
        str: The player's decision (e.g., 'Open' or 'Leave').

    Returns:
        Stage: The next stage (End or Mountain) based on the player's input.

    Raises:
        ValueError: If the input is not 'Open' or 'Leave'.
    """
    response = yield (
        "\n🕸️ Inside the cave, your eyes adjust to the dim light. "
        "In the center, a dusty treasure chest waits.\n"
        "Will you Open it or Leave it alone?"
    )
    if response.lower() == Decision.OPEN.value:
        yield "\n🎉 You lift the lid... it's full of gold! You win!"
        return Stage.END
    elif response.lower() == Decision.LEAVE.value:
        return Stage.MOUNTAIN
    else:
        raise ValueError("Unexpected input received in play_cave_stage.")
