"""Enums representing stages and decisions in a text-based adventure game."""

from enum import Enum


class Stage(Enum):
    """Enumeration of the various stages in the adventure game.

    Each stage represents a unique location or scenario the player can encounter.
    """

    FOREST = "forest"
    MOUNTAIN = "mountain"
    RIVER = "river"
    CAVE = "cave"
    END = "end"


class Decision(Enum):
    """Enumeration of possible decisions a player can make.

    These decisions guide the player's journey through different stages of the game.
    """

    NORTH = "north"
    SOUTH = "south"
    ENTER = "enter"
    GO_BACK = "go back"
    SWIM = "swim"
    OPEN = "open"
    LEAVE = "leave"
    QUIT = "quit"
    EXIT = "exit"
