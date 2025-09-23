"""Main game loop for the text-based adventure game.

This module coordinates the flow of the game by managing transitions between different stages.
"""

from typing import Generator, Optional

from gopika_adventure_game.constants import Stage  # type: ignore
from gopika_adventure_game.stage_logic import (  # type: ignore
    play_cave_stage,
    play_forest_stage,
    play_mountain_stage,
    play_river_stage,
)


def run_game() -> Generator[str, str, Optional[str]]:
    """Runs the interactive loop for the text-based adventure game.

    Yields:
        str: A prompt string asking the player for input.

    Receives:
        str: The player's input sent back into the generator.

    Returns:
        Optional[str]: The final stage name when the game ends, or None if interrupted.

    """
    stages = {
        Stage.FOREST: play_forest_stage,
        Stage.MOUNTAIN: play_mountain_stage,
        Stage.RIVER: play_river_stage,
        Stage.CAVE: play_cave_stage,
    }

    stage_name = Stage.FOREST

    while stage_name != Stage.END:
        stage_gen = stages[stage_name]()
        prompt = next(stage_gen)
        while True:
            try:
                user_input = yield prompt
                prompt = stage_gen.send(user_input)
            except ValueError as exc:
                prompt = stage_gen.throw(exc)
            except StopIteration as exc:
                stage_name = exc.value
                break
    return None
